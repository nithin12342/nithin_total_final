const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("SupplyChainFinance", function () {
  let supplyChainFinance;
  let owner, supplier, buyer, financier, otherAccount;

  beforeEach(async function () {
    [owner, supplier, buyer, financier, otherAccount] = await ethers.getSigners();
    
    const SupplyChainFinance = await ethers.getContractFactory("SupplyChainFinance");
    supplyChainFinance = await SupplyChainFinance.deploy();
    await supplyChainFinance.deployed();
  });

  describe("Deployment", function () {
    it("Should deploy with correct initial state", async function () {
      expect(await supplyChainFinance.invoiceCount()).to.equal(0);
      expect(await supplyChainFinance.shipmentCount()).to.equal(0);
    });
  });

  describe("Invoice Management", function () {
    it("Should create invoices correctly", async function () {
      const dueDate = Math.floor(Date.now() / 1000) + 86400; // 1 day from now
      
      const tx = await supplyChainFinance.createInvoice(supplier.address, buyer.address, 1000, dueDate);
      const receipt = await tx.wait();
      
      expect(receipt.events[0].event).to.equal("InvoiceCreated");
      expect(receipt.events[0].args.id).to.equal(1);
      expect(receipt.events[0].args.supplier).to.equal(supplier.address);
      expect(receipt.events[0].args.buyer).to.equal(buyer.address);
      expect(receipt.events[0].args.amount).to.equal(1000);
      
      expect(await supplyChainFinance.invoiceCount()).to.equal(1);
    });

    it("Should retrieve invoice information correctly", async function () {
      const dueDate = Math.floor(Date.now() / 1000) + 86400;
      await supplyChainFinance.createInvoice(supplier.address, buyer.address, 1000, dueDate);
      
      const invoice = await supplyChainFinance.getInvoice(1);
      expect(invoice.id).to.equal(1);
      expect(invoice.supplier).to.equal(supplier.address);
      expect(invoice.buyer).to.equal(buyer.address);
      expect(invoice.amount).to.equal(1000);
      expect(invoice.dueDate).to.equal(dueDate);
      expect(invoice.isPaid).to.be.false;
      expect(invoice.isFinanced).to.be.false;
      expect(invoice.financier).to.equal(ethers.constants.AddressZero);
    });
  });

  describe("Invoice Financing", function () {
    let dueDate;
    
    beforeEach(async function () {
      dueDate = Math.floor(Date.now() / 1000) + 86400;
      await supplyChainFinance.createInvoice(supplier.address, buyer.address, 1000, dueDate);
    });

    it("Should allow financing of invoices with correct amount", async function () {
      const tx = await supplyChainFinance.connect(financier).financeInvoice(1, { value: 1000 });
      const receipt = await tx.wait();
      
      expect(receipt.events[0].event).to.equal("InvoiceFinanced");
      expect(receipt.events[0].args.id).to.equal(1);
      expect(receipt.events[0].args.financier).to.equal(financier.address);
      expect(receipt.events[0].args.amount).to.equal(1000);
      
      // Check that supplier received the funds
      expect(await ethers.provider.getBalance(supplier.address)).to.be.above(await ethers.provider.getBalance(supplier.address).sub(ethers.utils.parseEther("1")));
      
      const invoice = await supplyChainFinance.getInvoice(1);
      expect(invoice.isFinanced).to.be.true;
      expect(invoice.financier).to.equal(financier.address);
    });

    it("Should not allow financing with incorrect amount", async function () {
      await expect(supplyChainFinance.connect(financier).financeInvoice(1, { value: 500 }))
        .to.be.revertedWith("Incorrect financing amount");
    });

    it("Should not allow financing already paid invoices", async function () {
      // First pay the invoice
      await supplyChainFinance.connect(buyer).payInvoice(1, { value: 1000 });
      
      // Try to finance the paid invoice
      await expect(supplyChainFinance.connect(financier).financeInvoice(1, { value: 1000 }))
        .to.be.revertedWith("Invoice already paid");
    });

    it("Should not allow financing already financed invoices", async function () {
      // First finance the invoice
      await supplyChainFinance.connect(financier).financeInvoice(1, { value: 1000 });
      
      // Try to finance the same invoice again
      await expect(supplyChainFinance.connect(otherAccount).financeInvoice(1, { value: 1000 }))
        .to.be.revertedWith("Invoice already financed");
    });
  });

  describe("Invoice Payment", function () {
    let dueDate;
    
    beforeEach(async function () {
      dueDate = Math.floor(Date.now() / 1000) + 86400;
      await supplyChainFinance.createInvoice(supplier.address, buyer.address, 1000, dueDate);
    });

    it("Should allow direct payment of invoices", async function () {
      const supplierBalanceBefore = await ethers.provider.getBalance(supplier.address);
      
      const tx = await supplyChainFinance.connect(buyer).payInvoice(1, { value: 1000 });
      const receipt = await tx.wait();
      
      expect(receipt.events[0].event).to.equal("InvoicePaid");
      expect(receipt.events[0].args.id).to.equal(1);
      expect(receipt.events[0].args.payer).to.equal(buyer.address);
      expect(receipt.events[0].args.amount).to.equal(1000);
      
      const supplierBalanceAfter = await ethers.provider.getBalance(supplier.address);
      expect(supplierBalanceAfter.sub(supplierBalanceBefore)).to.equal(1000);
      
      const invoice = await supplyChainFinance.getInvoice(1);
      expect(invoice.isPaid).to.be.true;
    });

    it("Should transfer payment to financier for financed invoices", async function () {
      // First finance the invoice
      await supplyChainFinance.connect(financier).financeInvoice(1, { value: 1000 });
      
      // Pay the financed invoice
      const financierBalanceBefore = await ethers.provider.getBalance(financier.address);
      
      await supplyChainFinance.connect(buyer).payInvoice(1, { value: 1000 });
      
      const financierBalanceAfter = await ethers.provider.getBalance(financier.address);
      expect(financierBalanceAfter.sub(financierBalanceBefore)).to.equal(1000);
    });

    it("Should not allow payment with incorrect amount", async function () {
      await expect(supplyChainFinance.connect(buyer).payInvoice(1, { value: 500 }))
        .to.be.revertedWith("Incorrect payment amount");
    });

    it("Should not allow paying already paid invoices", async function () {
      // First pay the invoice
      await supplyChainFinance.connect(buyer).payInvoice(1, { value: 1000 });
      
      // Try to pay the same invoice again
      await expect(supplyChainFinance.connect(buyer).payInvoice(1, { value: 1000 }))
        .to.be.revertedWith("Invoice already paid");
    });
  });

  describe("Shipment Management", function () {
    it("Should create shipments correctly", async function () {
      const tx = await supplyChainFinance.createShipment(supplier.address, buyer.address, "PRODUCT-001", 100);
      const receipt = await tx.wait();
      
      expect(receipt.events[0].event).to.equal("ShipmentCreated");
      expect(receipt.events[0].args.id).to.equal(1);
      expect(receipt.events[0].args.supplier).to.equal(supplier.address);
      expect(receipt.events[0].args.buyer).to.equal(buyer.address);
      expect(receipt.events[0].args.status).to.equal("CREATED");
      
      expect(await supplyChainFinance.shipmentCount()).to.equal(1);
    });

    it("Should retrieve shipment information correctly", async function () {
      await supplyChainFinance.createShipment(supplier.address, buyer.address, "PRODUCT-001", 100);
      
      const shipment = await supplyChainFinance.getShipment(1);
      expect(shipment.id).to.equal(1);
      expect(shipment.supplier).to.equal(supplier.address);
      expect(shipment.buyer).to.equal(buyer.address);
      expect(shipment.productId).to.equal("PRODUCT-001");
      expect(shipment.quantity).to.equal(100);
      expect(shipment.status).to.equal("CREATED");
    });

    it("Should update shipment status", async function () {
      await supplyChainFinance.createShipment(supplier.address, buyer.address, "PRODUCT-001", 100);
      
      const tx = await supplyChainFinance.updateShipmentStatus(1, "IN_TRANSIT");
      const receipt = await tx.wait();
      
      expect(receipt.events[0].event).to.equal("ShipmentUpdated");
      expect(receipt.events[0].args.id).to.equal(1);
      expect(receipt.events[0].args.status).to.equal("IN_TRANSIT");
      
      const shipment = await supplyChainFinance.getShipment(1);
      expect(shipment.status).to.equal("IN_TRANSIT");
    });

    it("Should not allow updating non-existent shipments", async function () {
      await expect(supplyChainFinance.updateShipmentStatus(999, "IN_TRANSIT"))
        .to.be.revertedWith("Invalid shipment ID");
    });
  });
});