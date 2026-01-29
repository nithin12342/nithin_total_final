const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CrossChainBridge", function () {
  let crossChainBridge, erc20Token;
  let owner, operator, validator, user1, user2;

  beforeEach(async function () {
    [owner, operator, validator, user1, user2] = await ethers.getSigners();
    
    // Deploy a simple ERC20 token for testing
    const ERC20Token = await ethers.getContractFactory("ERC20Mock");
    erc20Token = await ERC20Token.deploy("Test Token", "TST", owner.address, 1000000);
    await erc20Token.deployed();
    
    // Mint tokens to users for testing
    await erc20Token.mint(user1.address, 100000);
    await erc20Token.mint(user2.address, 100000);
    
    // Deploy CrossChainBridge contract
    const CrossChainBridge = await ethers.getContractFactory("CrossChainBridge");
    crossChainBridge = await CrossChainBridge.deploy();
    await crossChainBridge.deployed();
    
    // Grant roles
    await crossChainBridge.connect(owner).grantRole(await crossChainBridge.OPERATOR_ROLE(), operator.address);
    await crossChainBridge.connect(owner).grantRole(await crossChainBridge.VALIDATOR_ROLE(), validator.address);
    
    // Set operator as fee collector
    await crossChainBridge.connect(owner).setRoleAdmin(await crossChainBridge.OPERATOR_ROLE(), owner.address);
  });

  describe("Deployment", function () {
    it("Should set the right owner and default roles", async function () {
      expect(await crossChainBridge.hasRole(await crossChainBridge.DEFAULT_ADMIN_ROLE(), owner.address)).to.be.true;
      expect(await crossChainBridge.hasRole(await crossChainBridge.OPERATOR_ROLE(), owner.address)).to.be.true;
      expect(await crossChainBridge.hasRole(await crossChainBridge.VALIDATOR_ROLE(), owner.address)).to.be.true;
      expect(await crossChainBridge.hasRole(await crossChainBridge.OPERATOR_ROLE(), operator.address)).to.be.true;
      expect(await crossChainBridge.hasRole(await crossChainBridge.VALIDATOR_ROLE(), validator.address)).to.be.true;
    });

    it("Should support the current chain by default", async function () {
      const chainId = await ethers.provider.getNetwork().then(network => network.chainId);
      expect(await crossChainBridge.supportedChains(chainId)).to.be.true;
    });
  });

  describe("Token Locking", function () {
    it("Should allow users to lock ERC20 tokens for cross-chain transfer", async function () {
      const targetChainId = 2;
      const amount = 1000;
      const recipient = user2.address;
      
      // Approve token transfer
      await erc20Token.connect(user1).approve(crossChainBridge.address, amount);
      
      // Add target chain as supported
      await crossChainBridge.connect(owner).setSupportedChain(targetChainId, true);
      
      const bridgeFee = await crossChainBridge.bridgeFee();
      
      await expect(crossChainBridge.connect(user1).lockTokens(targetChainId, erc20Token.address, amount, recipient, { value: bridgeFee }))
        .to.emit(crossChainBridge, "TokensLocked")
        .withArgs(1, await ethers.provider.getNetwork().then(network => network.chainId), targetChainId, erc20Token.address, amount, user1.address, recipient);
      
      // Check bridge balance
      const chainId = await ethers.provider.getNetwork().then(network => network.chainId);
      expect(await crossChainBridge.getChainTokenBalance(chainId, erc20Token.address)).to.equal(amount);
      
      // Check transfer record
      const transfer = await crossChainBridge.getCrossChainTransfer(1);
      expect(transfer.id).to.equal(1);
      expect(transfer.sourceChainId).to.equal(chainId);
      expect(transfer.targetChainId).to.equal(targetChainId);
      expect(transfer.token).to.equal(erc20Token.address);
      expect(transfer.amount).to.equal(amount);
      expect(transfer.sender).to.equal(user1.address);
      expect(transfer.recipient).to.equal(recipient);
      expect(transfer.completed).to.be.false;
    });

    it("Should allow users to lock ETH for cross-chain transfer", async function () {
      const targetChainId = 2;
      const amount = ethers.utils.parseEther("1");
      const recipient = user2.address;
      
      // Add target chain as supported
      await crossChainBridge.connect(owner).setSupportedChain(targetChainId, true);
      
      const bridgeFee = await crossChainBridge.bridgeFee();
      const totalValue = amount.add(bridgeFee);
      
      await expect(crossChainBridge.connect(user1).lockTokens(targetChainId, ethers.constants.AddressZero, amount, recipient, { value: totalValue }))
        .to.emit(crossChainBridge, "TokensLocked")
        .withArgs(1, await ethers.provider.getNetwork().then(network => network.chainId), targetChainId, ethers.constants.AddressZero, amount, user1.address, recipient);
      
      // Check bridge balance
      const chainId = await ethers.provider.getNetwork().then(network => network.chainId);
      expect(await crossChainBridge.getChainTokenBalance(chainId, ethers.constants.AddressZero)).to.equal(amount);
    });

    it("Should not allow locking tokens to unsupported chains", async function () {
      const targetChainId = 999; // Unsupported chain
      const amount = 1000;
      const recipient = user2.address;
      
      // Approve token transfer
      await erc20Token.connect(user1).approve(crossChainBridge.address, amount);
      
      const bridgeFee = await crossChainBridge.bridgeFee();
      
      await expect(crossChainBridge.connect(user1).lockTokens(targetChainId, erc20Token.address, amount, recipient, { value: bridgeFee }))
        .to.be.revertedWith("Target chain not supported");
    });

    it("Should not allow locking below minimum amount", async function () {
      const targetChainId = 2;
      const amount = 50; // Below minimum of 100
      const recipient = user2.address;
      
      // Approve token transfer
      await erc20Token.connect(user1).approve(crossChainBridge.address, amount);
      
      // Add target chain as supported
      await crossChainBridge.connect(owner).setSupportedChain(targetChainId, true);
      
      const bridgeFee = await crossChainBridge.bridgeFee();
      
      await expect(crossChainBridge.connect(user1).lockTokens(targetChainId, erc20Token.address, amount, recipient, { value: bridgeFee }))
        .to.be.revertedWith("Amount below minimum");
    });

    it("Should not allow locking to zero address", async function () {
      const targetChainId = 2;
      const amount = 1000;
      const recipient = ethers.constants.AddressZero;
      
      // Approve token transfer
      await erc20Token.connect(user1).approve(crossChainBridge.address, amount);
      
      // Add target chain as supported
      await crossChainBridge.connect(owner).setSupportedChain(targetChainId, true);
      
      const bridgeFee = await crossChainBridge.bridgeFee();
      
      await expect(crossChainBridge.connect(user1).lockTokens(targetChainId, erc20Token.address, amount, recipient, { value: bridgeFee }))
        .to.be.revertedWith("Invalid recipient");
    });
  });

  describe("Token Release", function () {
    let targetChainId, amount, recipient, bridgeFee;
    
    beforeEach(async function () {
      targetChainId = 2;
      amount = 1000;
      recipient = user2.address;
      
      // Add target chain as supported
      await crossChainBridge.connect(owner).setSupportedChain(targetChainId, true);
      
      // Approve token transfer
      await erc20Token.connect(user1).approve(crossChainBridge.address, amount);
      
      bridgeFee = await crossChainBridge.bridgeFee();
      
      // Lock tokens
      await crossChainBridge.connect(user1).lockTokens(targetChainId, erc20Token.address, amount, recipient, { value: bridgeFee });
    });

    it("Should allow release of tokens with valid signatures", async function () {
      const sourceChainId = await ethers.provider.getNetwork().then(network => network.chainId);
      const transferId = 1;
      const signatures = [ethers.utils.toUtf8Bytes("signature")]; // Mock signature
      
      // Fund the bridge with tokens for release
      await erc20Token.mint(crossChainBridge.address, amount);
      
      await expect(crossChainBridge.connect(user2).releaseTokens(sourceChainId, transferId, erc20Token.address, amount, recipient, signatures))
        .to.emit(crossChainBridge, "TokensReleased")
        .withArgs(transferId, sourceChainId, await ethers.provider.getNetwork().then(network => network.chainId), erc20Token.address, amount, recipient);
      
      // Check that transfer is marked as completed
      const transfer = await crossChainBridge.getCrossChainTransfer(transferId);
      expect(transfer.completed).to.be.true;
      
      // Check recipient received tokens
      expect(await erc20Token.balanceOf(recipient)).to.equal(101000); // 100000 + 1000
    });

    it("Should not allow release of non-existent transfers", async function () {
      const sourceChainId = await ethers.provider.getNetwork().then(network => network.chainId);
      const transferId = 999; // Non-existent
      const signatures = [ethers.utils.toUtf8Bytes("signature")];
      
      await expect(crossChainBridge.connect(user2).releaseTokens(sourceChainId, transferId, erc20Token.address, amount, recipient, signatures))
        .to.be.revertedWith("Transfer does not exist");
    });

    it("Should not allow release of already completed transfers", async function () {
      const sourceChainId = await ethers.provider.getNetwork().then(network => network.chainId);
      const transferId = 1;
      const signatures = [ethers.utils.toUtf8Bytes("signature")];
      
      // Fund the bridge with tokens for release
      await erc20Token.mint(crossChainBridge.address, amount);
      
      // First release
      await crossChainBridge.connect(user2).releaseTokens(sourceChainId, transferId, erc20Token.address, amount, recipient, signatures);
      
      // Try to release again
      await expect(crossChainBridge.connect(user2).releaseTokens(sourceChainId, transferId, erc20Token.address, amount, recipient, signatures))
        .to.be.revertedWith("Transfer already completed");
    });

    it("Should not allow release with invalid source chain", async function () {
      const sourceChainId = 999; // Invalid source chain
      const transferId = 1;
      const signatures = [ethers.utils.toUtf8Bytes("signature")];
      
      await expect(crossChainBridge.connect(user2).releaseTokens(sourceChainId, transferId, erc20Token.address, amount, recipient, signatures))
        .to.be.revertedWith("Invalid source chain");
    });
  });

  describe("Message Relaying", function () {
    it("Should allow relaying messages with valid signatures", async function () {
      const sourceChainId = 2; // Different chain
      const sender = user1.address;
      const data = ethers.utils.toUtf8Bytes("message_data");
      const signatures = [ethers.utils.toUtf8Bytes("signature")]; // Mock signature
      
      // Add source chain as supported
      await crossChainBridge.connect(owner).setSupportedChain(sourceChainId, true);
      
      await expect(crossChainBridge.connect(user2).relayMessage(sourceChainId, sender, data, signatures))
        .to.emit(crossChainBridge, "MessageRelayed")
        .to.emit(crossChainBridge, "MessageProcessed");
    });

    it("Should not allow relaying messages from unsupported chains", async function () {
      const sourceChainId = 999; // Unsupported chain
      const sender = user1.address;
      const data = ethers.utils.toUtf8Bytes("message_data");
      const signatures = [ethers.utils.toUtf8Bytes("signature")];
      
      await expect(crossChainBridge.connect(user2).relayMessage(sourceChainId, sender, data, signatures))
        .to.be.revertedWith("Source chain not supported");
    });

    it("Should not allow relaying messages from zero address", async function () {
      const sourceChainId = 2;
      const sender = ethers.constants.AddressZero;
      const data = ethers.utils.toUtf8Bytes("message_data");
      const signatures = [ethers.utils.toUtf8Bytes("signature")];
      
      // Add source chain as supported
      await crossChainBridge.connect(owner).setSupportedChain(sourceChainId, true);
      
      await expect(crossChainBridge.connect(user2).relayMessage(sourceChainId, sender, data, signatures))
        .to.be.revertedWith("Invalid sender");
    });

    it("Should not allow relaying the same message twice", async function () {
      const sourceChainId = 2;
      const sender = user1.address;
      const data = ethers.utils.toUtf8Bytes("message_data");
      const signatures = [ethers.utils.toUtf8Bytes("signature")];
      
      // Add source chain as supported
      await crossChainBridge.connect(owner).setSupportedChain(sourceChainId, true);
      
      // First relay
      await crossChainBridge.connect(user2).relayMessage(sourceChainId, sender, data, signatures);
      
      // Try to relay the same message again
      await expect(crossChainBridge.connect(user2).relayMessage(sourceChainId, sender, data, signatures))
        .to.be.revertedWith("Message already processed");
    });
  });

  describe("Configuration Management", function () {
    it("Should allow admin to set bridge fee", async function () {
      const newFee = ethers.utils.parseEther("0.002");
      const oldFee = await crossChainBridge.bridgeFee();
      
      await expect(crossChainBridge.connect(owner).setBridgeFee(newFee))
        .to.emit(crossChainBridge, "BridgeFeeUpdated")
        .withArgs(oldFee, newFee);
      
      expect(await crossChainBridge.bridgeFee()).to.equal(newFee);
    });

    it("Should not allow non-admins to set bridge fee", async function () {
      const newFee = ethers.utils.parseEther("0.002");
      
      await expect(crossChainBridge.connect(user1).setBridgeFee(newFee))
        .to.be.revertedWith("Caller is not admin");
    });

    it("Should allow admin to set minimum transfer amount", async function () {
      const newMin = 500;
      
      await crossChainBridge.connect(owner).setMinTransferAmount(newMin);
      
      expect(await crossChainBridge.minTransferAmount()).to.equal(newMin);
    });

    it("Should allow admin to add/remove supported chains", async function () {
      const chainId = 5;
      
      // Add chain
      await expect(crossChainBridge.connect(owner).setSupportedChain(chainId, true))
        .to.emit(crossChainBridge, "ChainSupported")
        .withArgs(chainId, true);
      
      expect(await crossChainBridge.supportedChains(chainId)).to.be.true;
      
      // Remove chain
      await expect(crossChainBridge.connect(owner).setSupportedChain(chainId, false))
        .to.emit(crossChainBridge, "ChainSupported")
        .withArgs(chainId, false);
      
      expect(await crossChainBridge.supportedChains(chainId)).to.be.false;
    });

    it("Should allow operator to withdraw fees", async function () {
      // Send some ETH to the bridge
      await user1.sendTransaction({
        to: crossChainBridge.address,
        value: ethers.utils.parseEther("1.0")
      });
      
      const operatorBalanceBefore = await ethers.provider.getBalance(operator.address);
      
      await crossChainBridge.connect(operator).withdrawFees(operator.address);
      
      const operatorBalanceAfter = await ethers.provider.getBalance(operator.address);
      expect(operatorBalanceAfter.gt(operatorBalanceBefore)).to.be.true;
      
      // Bridge should have zero ETH balance
      expect(await ethers.provider.getBalance(crossChainBridge.address)).to.equal(0);
    });
  });

  describe("Emergency Functions", function () {
    it("Should allow admin to emergency withdraw tokens", async function () {
      const amount = 1000;
      
      // Send tokens to bridge
      await erc20Token.mint(crossChainBridge.address, amount);
      
      const adminBalanceBefore = await erc20Token.balanceOf(owner.address);
      
      await crossChainBridge.connect(owner).emergencyWithdrawToken(erc20Token.address, owner.address, amount);
      
      const adminBalanceAfter = await erc20Token.balanceOf(owner.address);
      expect(adminBalanceAfter.sub(adminBalanceBefore)).to.equal(amount);
    });

    it("Should allow admin to emergency update transfer status", async function () {
      const targetChainId = 2;
      const amount = 1000;
      const recipient = user2.address;
      
      // Add target chain as supported
      await crossChainBridge.connect(owner).setSupportedChain(targetChainId, true);
      
      // Approve token transfer
      await erc20Token.connect(user1).approve(crossChainBridge.address, amount);
      
      const bridgeFee = await crossChainBridge.bridgeFee();
      
      // Lock tokens
      await crossChainBridge.connect(user1).lockTokens(targetChainId, erc20Token.address, amount, recipient, { value: bridgeFee });
      
      // Emergency update transfer status
      await crossChainBridge.connect(owner).emergencyUpdateTransferStatus(1, true);
      
      const transfer = await crossChainBridge.getCrossChainTransfer(1);
      expect(transfer.completed).to.be.true;
    });

    it("Should not allow non-admins to use emergency functions", async function () {
      await expect(crossChainBridge.connect(user1).emergencyWithdrawToken(erc20Token.address, user1.address, 1000))
        .to.be.revertedWith("Caller is not admin");
      
      await expect(crossChainBridge.connect(user1).emergencyUpdateTransferStatus(1, true))
        .to.be.revertedWith("Caller is not admin");
    });
  });
});