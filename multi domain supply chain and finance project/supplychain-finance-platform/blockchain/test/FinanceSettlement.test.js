const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("FinanceSettlement", function () {
  let financeSettlement, erc20Token;
  let owner, supplier, buyer, financier, otherAccount;

  beforeEach(async function () {
    [owner, supplier, buyer, financier, otherAccount] = await ethers.getSigners();
    
    // Deploy a simple ERC20 token for testing
    const ERC20Token = await ethers.getContractFactory("ERC20Mock");
    erc20Token = await ERC20Token.deploy("Test Token", "TST", owner.address, 1000000);
    await erc20Token.deployed();
    
    // Mint tokens to accounts for testing
    await erc20Token.mint(supplier.address, 100000);
    await erc20Token.mint(buyer.address, 100000);
    await erc20Token.mint(financier.address, 100000);
    
    // Deploy FinanceSettlement contract
    const FinanceSettlement = await ethers.getContractFactory("FinanceSettlement");
    financeSettlement = await FinanceSettlement.deploy(erc20Token.address);
    await financeSettlement.deployed();
    
    // Grant roles to accounts
    await financeSettlement.connect(owner).grantRole(await financeSettlement.SUPPLIER_ROLE(), supplier.address);
    await financeSettlement.connect(owner).grantRole(await financeSettlement.FINANCIER_ROLE(), financier.address);
  });

  describe("Deployment", function () {
    it("Should set the right owner and payment token", async function () {
      expect(await financeSettlement.hasRole(await financeSettlement.DEFAULT_ADMIN_ROLE(), owner.address)).to.be.true;
      expect(await financeSettlement.paymentToken()).to.equal(erc20Token.address);
    });
  });

  describe("Invoice Creation", function () {
    it("Should allow suppliers to create invoices", async function () {
      const dueDate = Math.floor(Date.now() / 1000) + 86400; // 1 day from now
      
      await expect(financeSettlement.connect(supplier).createInvoice(buyer.address, 1000, dueDate))
        .to.emit(financeSettlement, "InvoiceCreated")
        .withArgs(1, supplier.address, buyer.address, 1000);
      
      const invoice = await financeSettlement.getInvoice(1);
      expect(invoice.id).to.equal(1);
      expect(invoice.supplier).to.equal(supplier.address);
      expect(invoice.buyer).to.equal(buyer.address);
      expect(invoice.amount).to.equal(1000);
      expect(invoice.dueDate).to.equal(dueDate);
      expect(invoice.isPaid).to.be.false;
      expect(invoice.isFinanced).to.be.false;
      expect(invoice.financingAmount).to.equal(0);
      expect(invoice.financier).to.equal(ethers.constants.AddressZero);
    });

    it("Should not allow non-suppliers to create invoices", async function () {
      const dueDate = Math.floor(Date.now() / 1000) + 86400;
      
      await expect(financeSettlement.connect(otherAccount).createInvoice(buyer.address, 1000, dueDate))
        .to.be.revertedWith("Caller is not a supplier");
    });

    it("Should increment invoice count correctly", async function () {
      const dueDate = Math.floor(Date.now() / 1000) + 86400;
      
      await financeSettlement.connect(supplier).createInvoice(buyer.address, 1000, dueDate);
      await financeSettlement.connect(supplier).createInvoice(buyer.address, 2000, dueDate);
      
      expect(await financeSettlement.invoiceCount()).to.equal(2);
    });
  });

  describe("Invoice Financing", function () {
    let dueDate;
    
    beforeEach(async function () {
      dueDate = Math.floor(Date.now() / 1000) + 86400;
      await financeSettlement.connect(supplier).createInvoice(buyer.address, 1000, dueDate);
      
      // Approve token transfer for financier
      await erc20Token.connect(financier).approve(financeSettlement.address, 1000);
    });

    it("Should allow financiers to finance invoices", async function () {
      await expect(financeSettlement.connect(financier).financeInvoice(1, 800))
        .to.emit(financeSettlement, "InvoiceFinanced")
        .withArgs(1, financier.address, 800);
      
      const invoice = await financeSettlement.getInvoice(1);
      expect(invoice.isFinanced).to.be.true;
      expect(invoice.financingAmount).to.equal(800);
      expect(invoice.financier).to.equal(financier.address);
    });

    it("Should transfer tokens from financier to supplier when financing", async function () {
      const supplierBalanceBefore = await erc20Token.balanceOf(supplier.address);
      const financierBalanceBefore = await erc20Token.balanceOf(financier.address);
      
      await financeSettlement.connect(financier).financeInvoice(1, 800);
      
      const supplierBalanceAfter = await erc20Token.balanceOf(supplier.address);
      const financierBalanceAfter = await erc20Token.balanceOf(financier.address);
      
      expect(supplierBalanceAfter.sub(supplierBalanceBefore)).to.equal(800);
      expect(financierBalanceBefore.sub(financierBalanceAfter)).to.equal(800);
    });

    it("Should not allow non-financiers to finance invoices", async function () {
      await expect(financeSettlement.connect(otherAccount).financeInvoice(1, 800))
        .to.be.revertedWith("Caller is not a financier");
    });

    it("Should not allow financing already paid invoices", async function () {
      // First pay the invoice
      await erc20Token.connect(buyer).approve(financeSettlement.address, 1000);
      await financeSettlement.connect(buyer).payInvoice(1);
      
      // Try to finance the paid invoice
      await expect(financeSettlement.connect(financier).financeInvoice(1, 800))
        .to.be.revertedWith("Invoice already paid");
    });

    it("Should not allow financing already financed invoices", async function () {
      await financeSettlement.connect(financier).financeInvoice(1, 800);
      
      // Try to finance the same invoice again
      await expect(financeSettlement.connect(financier).financeInvoice(1, 500))
        .to.be.revertedWith("Invoice already financed");
    });

    it("Should not allow financing amount exceeding invoice amount", async function () {
      await expect(financeSettlement.connect(financier).financeInvoice(1, 1200))
        .to.be.revertedWith("Financing amount exceeds invoice amount");
    });
  });

  describe("Invoice Payment", function () {
    let dueDate;
    
    beforeEach(async function () {
      dueDate = Math.floor(Date.now() / 1000) + 86400;
      await financeSettlement.connect(supplier).createInvoice(buyer.address, 1000, dueDate);
      
      // Approve token transfer for buyer
      await erc20Token.connect(buyer).approve(financeSettlement.address, 1000);
    });

    it("Should allow buyer to pay invoice directly", async function () {
      await expect(financeSettlement.connect(buyer).payInvoice(1))
        .to.emit(financeSettlement, "InvoicePaid")
        .withArgs(1);
      
      const invoice = await financeSettlement.getInvoice(1);
      expect(invoice.isPaid).to.be.true;
    });

    it("Should transfer tokens from buyer to supplier when paying directly", async function () {
      const supplierBalanceBefore = await erc20Token.balanceOf(supplier.address);
      const buyerBalanceBefore = await erc20Token.balanceOf(buyer.address);
      
      await financeSettlement.connect(buyer).payInvoice(1);
      
      const supplierBalanceAfter = await erc20Token.balanceOf(supplier.address);
      const buyerBalanceAfter = await erc20Token.balanceOf(buyer.address);
      
      expect(supplierBalanceAfter.sub(supplierBalanceBefore)).to.equal(1000);
      expect(buyerBalanceBefore.sub(buyerBalanceAfter)).to.equal(1000);
    });

    it("Should transfer tokens from buyer to financier when paying financed invoice", async function () {
      // First finance the invoice
      await erc20Token.connect(financier).approve(financeSettlement.address, 1000);
      await financeSettlement.connect(financier).financeInvoice(1, 800);
      
      // Pay the financed invoice
      const financierBalanceBefore = await erc20Token.balanceOf(financier.address);
      const buyerBalanceBefore = await erc20Token.balanceOf(buyer.address);
      
      await financeSettlement.connect(buyer).payInvoice(1);
      
      const financierBalanceAfter = await erc20Token.balanceOf(financier.address);
      const buyerBalanceAfter = await erc20Token.balanceOf(buyer.address);
      
      expect(financierBalanceAfter.sub(financierBalanceBefore)).to.equal(1000);
      expect(buyerBalanceBefore.sub(buyerBalanceAfter)).to.equal(1000);
    });

    it("Should not allow non-buyers to pay invoice", async function () {
      await expect(financeSettlement.connect(otherAccount).payInvoice(1))
        .to.be.revertedWith("Only buyer can pay");
    });

    it("Should not allow paying already paid invoices", async function () {
      await financeSettlement.connect(buyer).payInvoice(1);
      
      // Try to pay the same invoice again
      await expect(financeSettlement.connect(buyer).payInvoice(1))
        .to.be.revertedWith("Invoice already paid");
    });
  });

  describe("Get Invoice", function () {
    let dueDate;
    
    beforeEach(async function () {
      dueDate = Math.floor(Date.now() / 1000) + 86400;
      await financeSettlement.connect(supplier).createInvoice(buyer.address, 1000, dueDate);
    });

    it("Should return correct invoice information", async function () {
      const invoice = await financeSettlement.getInvoice(1);
      expect(invoice.id).to.equal(1);
      expect(invoice.supplier).to.equal(supplier.address);
      expect(invoice.buyer).to.equal(buyer.address);
      expect(invoice.amount).to.equal(1000);
      expect(invoice.dueDate).to.equal(dueDate);
      expect(invoice.isPaid).to.be.false;
      expect(invoice.isFinanced).to.be.false;
      expect(invoice.financingAmount).to.equal(0);
      expect(invoice.financier).to.equal(ethers.constants.AddressZero);
    });
  });
});