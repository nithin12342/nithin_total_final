// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract SupplyChain is AccessControl, ReentrancyGuard {
    bytes32 public constant SUPPLIER_ROLE = keccak256("SUPPLIER_ROLE");
    bytes32 public constant MANUFACTURER_ROLE = keccak256("MANUFACTURER_ROLE");
    bytes32 public constant DISTRIBUTOR_ROLE = keccak256("DISTRIBUTOR_ROLE");

    enum ProductStatus { Created, InTransit, Delivered, Rejected }

    struct Product {
        uint256 id;
        address supplier;
        string metadata;
        uint256 price;
        ProductStatus status;
        uint256 timestamp;
    }

    mapping(uint256 => Product) public products;
    uint256 public productCount;

    event ProductCreated(uint256 indexed id, address indexed supplier, uint256 price);
    event ProductStatusUpdated(uint256 indexed id, ProductStatus status);
    event ProductDelivered(uint256 indexed id, address indexed recipient);

    constructor() {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function createProduct(string memory metadata, uint256 price) external {
        require(hasRole(SUPPLIER_ROLE, msg.sender), "Caller is not a supplier");
        
        productCount++;
        products[productCount] = Product({
            id: productCount,
            supplier: msg.sender,
            metadata: metadata,
            price: price,
            status: ProductStatus.Created,
            timestamp: block.timestamp
        });

        emit ProductCreated(productCount, msg.sender, price);
    }

    function updateProductStatus(uint256 productId, ProductStatus newStatus) external {
        require(hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "Caller is not an admin");
        require(products[productId].id != 0, "Product does not exist");

        products[productId].status = newStatus;
        emit ProductStatusUpdated(productId, newStatus);
    }

    function deliverProduct(uint256 productId, address recipient) external nonReentrant {
        require(hasRole(DISTRIBUTOR_ROLE, msg.sender), "Caller is not a distributor");
        require(products[productId].id != 0, "Product does not exist");
        require(products[productId].status == ProductStatus.InTransit, "Product not in transit");

        products[productId].status = ProductStatus.Delivered;
        emit ProductDelivered(productId, recipient);
    }

    function getProduct(uint256 productId) external view returns (Product memory) {
        require(products[productId].id != 0, "Product does not exist");
        return products[productId];
    }
}
