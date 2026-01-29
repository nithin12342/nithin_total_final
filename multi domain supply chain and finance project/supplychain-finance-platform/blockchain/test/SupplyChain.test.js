const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("SupplyChain", function () {
  let supplyChain;
  let owner, supplier, manufacturer, distributor, otherAccount;

  beforeEach(async function () {
    [owner, supplier, manufacturer, distributor, otherAccount] = await ethers.getSigners();
    
    const SupplyChain = await ethers.getContractFactory("SupplyChain");
    supplyChain = await SupplyChain.deploy();
    await supplyChain.deployed();
    
    // Grant roles to accounts
    await supplyChain.connect(owner).grantRole(await supplyChain.SUPPLIER_ROLE(), supplier.address);
    await supplyChain.connect(owner).grantRole(await supplyChain.MANUFACTURER_ROLE(), manufacturer.address);
    await supplyChain.connect(owner).grantRole(await supplyChain.DISTRIBUTOR_ROLE(), distributor.address);
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await supplyChain.hasRole(await supplyChain.DEFAULT_ADMIN_ROLE(), owner.address)).to.be.true;
    });
  });

  describe("Product Creation", function () {
    it("Should allow suppliers to create products", async function () {
      await expect(supplyChain.connect(supplier).createProduct("Test Product", 100))
        .to.emit(supplyChain, "ProductCreated")
        .withArgs(1, supplier.address, 100);
      
      const product = await supplyChain.getProduct(1);
      expect(product.id).to.equal(1);
      expect(product.supplier).to.equal(supplier.address);
      expect(product.metadata).to.equal("Test Product");
      expect(product.price).to.equal(100);
      expect(product.status).to.equal(0); // Created
    });

    it("Should not allow non-suppliers to create products", async function () {
      await expect(supplyChain.connect(otherAccount).createProduct("Test Product", 100))
        .to.be.revertedWith("Caller is not a supplier");
    });

    it("Should increment product count correctly", async function () {
      await supplyChain.connect(supplier).createProduct("Product 1", 100);
      await supplyChain.connect(supplier).createProduct("Product 2", 200);
      
      expect(await supplyChain.productCount()).to.equal(2);
    });
  });

  describe("Product Status Updates", function () {
    beforeEach(async function () {
      await supplyChain.connect(supplier).createProduct("Test Product", 100);
    });

    it("Should allow admins to update product status", async function () {
      await expect(supplyChain.connect(owner).updateProductStatus(1, 1)) // 1 = InTransit
        .to.emit(supplyChain, "ProductStatusUpdated")
        .withArgs(1, 1);
      
      const product = await supplyChain.getProduct(1);
      expect(product.status).to.equal(1); // InTransit
    });

    it("Should not allow non-admins to update product status", async function () {
      await expect(supplyChain.connect(supplier).updateProductStatus(1, 1))
        .to.be.revertedWith("Caller is not an admin");
    });

    it("Should fail when updating status of non-existent product", async function () {
      await expect(supplyChain.connect(owner).updateProductStatus(999, 1))
        .to.be.revertedWith("Product does not exist");
    });
  });

  describe("Product Delivery", function () {
    beforeEach(async function () {
      await supplyChain.connect(supplier).createProduct("Test Product", 100);
      await supplyChain.connect(owner).updateProductStatus(1, 1); // Set to InTransit
    });

    it("Should allow distributors to deliver products", async function () {
      await expect(supplyChain.connect(distributor).deliverProduct(1, otherAccount.address))
        .to.emit(supplyChain, "ProductDelivered")
        .withArgs(1, otherAccount.address);
      
      const product = await supplyChain.getProduct(1);
      expect(product.status).to.equal(3); // Delivered
    });

    it("Should not allow non-distributors to deliver products", async function () {
      await expect(supplyChain.connect(supplier).deliverProduct(1, otherAccount.address))
        .to.be.revertedWith("Caller is not a distributor");
    });

    it("Should fail when delivering non-existent product", async function () {
      await expect(supplyChain.connect(distributor).deliverProduct(999, otherAccount.address))
        .to.be.revertedWith("Product does not exist");
    });

    it("Should fail when delivering product not in transit", async function () {
      // First deliver the product to change its status
      await supplyChain.connect(distributor).deliverProduct(1, otherAccount.address);
      
      // Try to deliver again (should fail)
      await expect(supplyChain.connect(distributor).deliverProduct(1, otherAccount.address))
        .to.be.revertedWith("Product not in transit");
    });
  });

  describe("Get Product", function () {
    beforeEach(async function () {
      await supplyChain.connect(supplier).createProduct("Test Product", 100);
    });

    it("Should return correct product information", async function () {
      const product = await supplyChain.getProduct(1);
      expect(product.id).to.equal(1);
      expect(product.supplier).to.equal(supplier.address);
      expect(product.metadata).to.equal("Test Product");
      expect(product.price).to.equal(100);
      expect(product.status).to.equal(0); // Created
    });

    it("Should fail when getting non-existent product", async function () {
      await expect(supplyChain.getProduct(999))
        .to.be.revertedWith("Product does not exist");
    });
  });
});