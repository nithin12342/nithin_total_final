// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract SupplyChainFinance is Ownable, ReentrancyGuard {
    struct Invoice {
        uint256 id;
        address supplier;
        address buyer;
        uint256 amount;
        uint256 dueDate;
        bool isPaid;
        bool isFinanced;
        address financier;
    }

    struct ShipmentRecord {
        uint256 id;
        address supplier;
        address buyer;
        string productId;
        uint256 quantity;
        uint256 timestamp;
        string status;
    }

    mapping(uint256 => Invoice) public invoices;
    mapping(uint256 => ShipmentRecord) public shipments;
    uint256 public invoiceCount;
    uint256 public shipmentCount;

    event InvoiceCreated(uint256 indexed id, address supplier, address buyer, uint256 amount);
    event InvoiceFinanced(uint256 indexed id, address financier, uint256 amount);
    event InvoicePaid(uint256 indexed id, address payer, uint256 amount);
    event ShipmentCreated(uint256 indexed id, address supplier, address buyer, string status);
    event ShipmentUpdated(uint256 indexed id, string status);

    constructor() {
        invoiceCount = 0;
        shipmentCount = 0;
    }

    function createInvoice(address _supplier, address _buyer, uint256 _amount, uint256 _dueDate) 
        external 
        returns (uint256) 
    {
        invoiceCount++;
        Invoice storage invoice = invoices[invoiceCount];
        invoice.id = invoiceCount;
        invoice.supplier = _supplier;
        invoice.buyer = _buyer;
        invoice.amount = _amount;
        invoice.dueDate = _dueDate;
        invoice.isPaid = false;
        invoice.isFinanced = false;

        emit InvoiceCreated(invoiceCount, _supplier, _buyer, _amount);
        return invoiceCount;
    }

    function financeInvoice(uint256 _invoiceId) 
        external 
        payable 
        nonReentrant 
    {
        Invoice storage invoice = invoices[_invoiceId];
        require(!invoice.isPaid, "Invoice already paid");
        require(!invoice.isFinanced, "Invoice already financed");
        require(msg.value == invoice.amount, "Incorrect financing amount");

        invoice.isFinanced = true;
        invoice.financier = msg.sender;
        
        payable(invoice.supplier).transfer(msg.value);
        emit InvoiceFinanced(_invoiceId, msg.sender, msg.value);
    }

    function payInvoice(uint256 _invoiceId) 
        external 
        payable 
        nonReentrant 
    {
        Invoice storage invoice = invoices[_invoiceId];
        require(!invoice.isPaid, "Invoice already paid");
        require(msg.value == invoice.amount, "Incorrect payment amount");

        invoice.isPaid = true;
        address payableTo = invoice.isFinanced ? invoice.financier : invoice.supplier;
        payable(payableTo).transfer(msg.value);
        
        emit InvoicePaid(_invoiceId, msg.sender, msg.value);
    }

    function createShipment(
        address _supplier, 
        address _buyer, 
        string memory _productId, 
        uint256 _quantity
    ) 
        external 
        returns (uint256) 
    {
        shipmentCount++;
        ShipmentRecord storage shipment = shipments[shipmentCount];
        shipment.id = shipmentCount;
        shipment.supplier = _supplier;
        shipment.buyer = _buyer;
        shipment.productId = _productId;
        shipment.quantity = _quantity;
        shipment.timestamp = block.timestamp;
        shipment.status = "CREATED";

        emit ShipmentCreated(shipmentCount, _supplier, _buyer, "CREATED");
        return shipmentCount;
    }

    function updateShipmentStatus(uint256 _shipmentId, string memory _status) 
        external 
    {
        require(_shipmentId <= shipmentCount, "Invalid shipment ID");
        ShipmentRecord storage shipment = shipments[_shipmentId];
        shipment.status = _status;
        emit ShipmentUpdated(_shipmentId, _status);
    }

    function getInvoice(uint256 _invoiceId) 
        external 
        view 
        returns (
            uint256 id,
            address supplier,
            address buyer,
            uint256 amount,
            uint256 dueDate,
            bool isPaid,
            bool isFinanced,
            address financier
        ) 
    {
        Invoice memory invoice = invoices[_invoiceId];
        return (
            invoice.id,
            invoice.supplier,
            invoice.buyer,
            invoice.amount,
            invoice.dueDate,
            invoice.isPaid,
            invoice.isFinanced,
            invoice.financier
        );
    }

    function getShipment(uint256 _shipmentId)
        external
        view
        returns (
            uint256 id,
            address supplier,
            address buyer,
            string memory productId,
            uint256 quantity,
            uint256 timestamp,
            string memory status
        )
    {
        ShipmentRecord memory shipment = shipments[_shipmentId];
        return (
            shipment.id,
            shipment.supplier,
            shipment.buyer,
            shipment.productId,
            shipment.quantity,
            shipment.timestamp,
            shipment.status
        );
    }
}
