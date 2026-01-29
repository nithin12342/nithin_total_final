const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("SupplyChainZKP", function () {
  let supplyChainZKP;
  let owner, verifier, supplier, otherAccount;

  beforeEach(async function () {
    [owner, verifier, supplier, otherAccount] = await ethers.getSigners();
    
    const SupplyChainZKP = await ethers.getContractFactory("SupplyChainZKP");
    supplyChainZKP = await SupplyChainZKP.deploy();
    await supplyChainZKP.deployed();
    
    // Grant roles to accounts
    await supplyChainZKP.connect(owner).grantVerifierRole(verifier.address);
    await supplyChainZKP.connect(owner).grantSupplierRole(supplier.address);
  });

  describe("Deployment", function () {
    it("Should set the right owner and default roles", async function () {
      expect(await supplyChainZKP.hasRole(await supplyChainZKP.DEFAULT_ADMIN_ROLE(), owner.address)).to.be.true;
      expect(await supplyChainZKP.hasRole(await supplyChainZKP.VERIFIER_ROLE(), owner.address)).to.be.true;
      expect(await supplyChainZKP.hasRole(await supplyChainZKP.VERIFIER_ROLE(), verifier.address)).to.be.true;
      expect(await supplyChainZKP.hasRole(await supplyChainZKP.SUPPLIER_ROLE(), supplier.address)).to.be.true;
    });
  });

  describe("ZKP Request Management", function () {
    it("Should allow suppliers to create ZKP requests", async function () {
      const circuitId = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("supply_chain_origin"));
      const publicInputs = ethers.utils.toUtf8Bytes("public_inputs");
      const proof = ethers.utils.toUtf8Bytes("proof_data");
      
      await expect(supplyChainZKP.connect(supplier).createZKPRequest(circuitId, publicInputs, proof))
        .to.emit(supplyChainZKP, "ZKPRequestCreated")
        .withArgs(1, supplier.address, circuitId);
      
      const request = await supplyChainZKP.zkpRequests(1);
      expect(request.id).to.equal(1);
      expect(request.requester).to.equal(supplier.address);
      expect(request.circuitId).to.equal(circuitId);
      expect(request.verified).to.be.false;
    });

    it("Should not allow non-suppliers to create ZKP requests", async function () {
      const circuitId = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("supply_chain_origin"));
      const publicInputs = ethers.utils.toUtf8Bytes("public_inputs");
      const proof = ethers.utils.toUtf8Bytes("proof_data");
      
      await expect(supplyChainZKP.connect(otherAccount).createZKPRequest(circuitId, publicInputs, proof))
        .to.be.revertedWith("Caller is not a supplier");
    });

    it("Should prevent proof replay", async function () {
      const circuitId = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("supply_chain_origin"));
      const publicInputs = ethers.utils.toUtf8Bytes("public_inputs");
      const proof = ethers.utils.toUtf8Bytes("proof_data");
      
      // Create first request
      await supplyChainZKP.connect(supplier).createZKPRequest(circuitId, publicInputs, proof);
      
      // Try to create second request with same proof
      await expect(supplyChainZKP.connect(supplier).createZKPRequest(circuitId, publicInputs, proof))
        .to.be.revertedWith("Proof already used");
    });
  });

  describe("ZKP Verification", function () {
    let circuitId, publicInputs, proof;
    
    beforeEach(async function () {
      circuitId = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("supply_chain_origin"));
      publicInputs = ethers.utils.toUtf8Bytes("public_inputs");
      proof = ethers.utils.toUtf8Bytes("proof_data");
      
      await supplyChainZKP.connect(supplier).createZKPRequest(circuitId, publicInputs, proof);
    });

    it("Should allow verifiers to verify ZKP requests", async function () {
      await expect(supplyChainZKP.connect(verifier).verifyZKP(1))
        .to.emit(supplyChainZKP, "ZKPVerified")
        .withArgs(1, true);
      
      const request = await supplyChainZKP.zkpRequests(1);
      expect(request.verified).to.be.true;
    });

    it("Should not allow non-verifiers to verify ZKP requests", async function () {
      await expect(supplyChainZKP.connect(otherAccount).verifyZKP(1))
        .to.be.revertedWith("Caller is not a verifier");
    });

    it("Should not allow verification of non-existent requests", async function () {
      await expect(supplyChainZKP.connect(verifier).verifyZKP(999))
        .to.be.revertedWith("Request does not exist");
    });

    it("Should not allow re-verification of already verified requests", async function () {
      await supplyChainZKP.connect(verifier).verifyZKP(1);
      
      await expect(supplyChainZKP.connect(verifier).verifyZKP(1))
        .to.be.revertedWith("Request already verified");
    });
  });

  describe("Supply Chain Verification", function () {
    let circuitId, publicInputs, proof;
    
    beforeEach(async function () {
      circuitId = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("supply_chain_origin"));
      publicInputs = ethers.utils.toUtf8Bytes("public_inputs");
      proof = ethers.utils.toUtf8Bytes("proof_data");
      
      await supplyChainZKP.connect(supplier).createZKPRequest(circuitId, publicInputs, proof);
      await supplyChainZKP.connect(verifier).verifyZKP(1);
    });

    it("Should allow suppliers to record supply chain verification", async function () {
      const productId = 12345;
      const originHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("origin_data"));
      const compliant = true;
      const requestId = 1;
      
      await expect(supplyChainZKP.connect(supplier).recordSupplyChainVerification(productId, originHash, compliant, requestId))
        .to.emit(supplyChainZKP, "SupplyChainVerified")
        .withArgs(1, productId, compliant);
      
      const verification = await supplyChainZKP.supplyChainVerifications(1);
      expect(verification.productId).to.equal(productId);
      expect(verification.supplier).to.equal(supplier.address);
      expect(verification.originHash).to.equal(originHash);
      expect(verification.compliant).to.equal(compliant);
    });

    it("Should not allow recording verification for unverified ZKP", async function () {
      // Create a new unverified request
      await supplyChainZKP.connect(supplier).createZKPRequest(circuitId, publicInputs, proof);
      
      const productId = 12345;
      const originHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("origin_data"));
      const compliant = true;
      const requestId = 2; // Unverified request
      
      await expect(supplyChainZKP.connect(supplier).recordSupplyChainVerification(productId, originHash, compliant, requestId))
        .to.be.revertedWith("ZKP not verified");
    });

    it("Should not allow non-requesters to record verification", async function () {
      const productId = 12345;
      const originHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("origin_data"));
      const compliant = true;
      const requestId = 1;
      
      await expect(supplyChainZKP.connect(otherAccount).recordSupplyChainVerification(productId, originHash, compliant, requestId))
        .to.be.revertedWith("Only requester can record verification");
    });
  });

  describe("Verification Queries", function () {
    let circuitId, publicInputs, proof;
    
    beforeEach(async function () {
      circuitId = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("supply_chain_origin"));
      publicInputs = ethers.utils.toUtf8Bytes("public_inputs");
      proof = ethers.utils.toUtf8Bytes("proof_data");
      
      await supplyChainZKP.connect(supplier).createZKPRequest(circuitId, publicInputs, proof);
      await supplyChainZKP.connect(verifier).verifyZKP(1);
      await supplyChainZKP.connect(supplier).recordSupplyChainVerification(12345, ethers.utils.keccak256(ethers.utils.toUtf8Bytes("origin_data")), true, 1);
    });

    it("Should correctly check if product is verified", async function () {
      expect(await supplyChainZKP.isProductVerified(12345)).to.be.true;
      expect(await supplyChainZKP.isProductVerified(99999)).to.be.false;
    });

    it("Should correctly check if product is compliant", async function () {
      expect(await supplyChainZKP.isProductCompliant(12345)).to.be.true;
      expect(await supplyChainZKP.isProductCompliant(99999)).to.be.false;
    });

    it("Should return correct verification information", async function () {
      const verification = await supplyChainZKP.getSupplyChainVerification(1);
      expect(verification.productId).to.equal(12345);
      expect(verification.supplier).to.equal(supplier.address);
      expect(verification.compliant).to.be.true;
    });
  });

  describe("Role Management", function () {
    it("Should allow admin to grant verifier role", async function () {
      await expect(supplyChainZKP.connect(owner).grantVerifierRole(otherAccount.address))
        .to.emit(supplyChainZKP, "RoleGranted");
      
      expect(await supplyChainZKP.hasRole(await supplyChainZKP.VERIFIER_ROLE(), otherAccount.address)).to.be.true;
    });

    it("Should allow admin to grant supplier role", async function () {
      await expect(supplyChainZKP.connect(owner).grantSupplierRole(otherAccount.address))
        .to.emit(supplyChainZKP, "RoleGranted");
      
      expect(await supplyChainZKP.hasRole(await supplyChainZKP.SUPPLIER_ROLE(), otherAccount.address)).to.be.true;
    });

    it("Should not allow non-admins to grant roles", async function () {
      await expect(supplyChainZKP.connect(verifier).grantVerifierRole(otherAccount.address))
        .to.be.revertedWith("Caller is not admin");
    });
  });
});