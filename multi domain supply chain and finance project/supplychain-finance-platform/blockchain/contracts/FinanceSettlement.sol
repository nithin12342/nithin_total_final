// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract FinanceSettlement is AccessControl, ReentrancyGuard {
    bytes32 public constant FINANCIER_ROLE = keccak256("FINANCIER_ROLE");
    bytes32 public constant SUPPLIER_ROLE = keccak256("SUPPLIER_ROLE");

    struct Invoice {
        uint256 id;
        address supplier;
        address buyer;
        uint256 amount;
        uint256 dueDate;
        bool isPaid;
        bool isFinanced;
        uint256 financingAmount;
        address financier;
    }

    mapping(uint256 => Invoice) public invoices;
    uint256 public invoiceCount;

    IERC20 public paymentToken;

    event InvoiceCreated(uint256 indexed id, address indexed supplier, address indexed buyer, uint256 amount);
    event InvoiceFinanced(uint256 indexed id, address indexed financier, uint256 amount);
    event InvoicePaid(uint256 indexed id);

    constructor(address _paymentToken) {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        paymentToken = IERC20(_paymentToken);
    }

    function createInvoice(
        address buyer,
        uint256 amount,
        uint256 dueDate
    ) external {
        require(hasRole(SUPPLIER_ROLE, msg.sender), "Caller is not a supplier");
        
        invoiceCount++;
        invoices[invoiceCount] = Invoice({
            id: invoiceCount,
            supplier: msg.sender,
            buyer: buyer,
            amount: amount,
            dueDate: dueDate,
            isPaid: false,
            isFinanced: false,
            financingAmount: 0,
            financier: address(0)
        });

        emit InvoiceCreated(invoiceCount, msg.sender, buyer, amount);
    }

    function financeInvoice(uint256 invoiceId, uint256 financingAmount) external nonReentrant {
        require(hasRole(FINANCIER_ROLE, msg.sender), "Caller is not a financier");
        Invoice storage invoice = invoices[invoiceId];
        require(!invoice.isPaid, "Invoice already paid");
        require(!invoice.isFinanced, "Invoice already financed");
        require(financingAmount <= invoice.amount, "Financing amount exceeds invoice amount");

        // Transfer tokens from financier to supplier
        require(
            paymentToken.transferFrom(msg.sender, invoice.supplier, financingAmount),
            "Token transfer failed"
        );

        invoice.isFinanced = true;
        invoice.financingAmount = financingAmount;
        invoice.financier = msg.sender;

        emit InvoiceFinanced(invoiceId, msg.sender, financingAmount);
    }

    function payInvoice(uint256 invoiceId) external nonReentrant {
        Invoice storage invoice = invoices[invoiceId];
        require(!invoice.isPaid, "Invoice already paid");
        require(msg.sender == invoice.buyer, "Only buyer can pay");

        uint256 paymentAmount = invoice.amount;
        address paymentRecipient = invoice.isFinanced ? invoice.financier : invoice.supplier;

        require(
            paymentToken.transferFrom(msg.sender, paymentRecipient, paymentAmount),
            "Token transfer failed"
        );

        invoice.isPaid = true;
        emit InvoicePaid(invoiceId);
    }

    function getInvoice(uint256 invoiceId) external view returns (Invoice memory) {
        return invoices[invoiceId];
    }
}
