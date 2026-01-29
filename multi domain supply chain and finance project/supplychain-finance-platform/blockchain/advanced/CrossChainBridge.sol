// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title CrossChainBridge
 * @dev Cross-chain bridge implementation for multi-blockchain support
 * This contract enables the transfer of assets and data between different blockchain networks
 */
contract CrossChainBridge is AccessControl, ReentrancyGuard {
    using SafeERC20 for IERC20;

    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");
    bytes32 public constant VALIDATOR_ROLE = keccak256("VALIDATOR_ROLE");

    // Struct to represent a cross-chain transfer
    struct CrossChainTransfer {
        uint256 id;
        uint256 sourceChainId;
        uint256 targetChainId;
        address token;
        uint256 amount;
        address sender;
        address recipient;
        bytes32 transactionHash;
        bool completed;
        uint256 timestamp;
    }

    // Struct to represent a relayed message
    struct RelayedMessage {
        bytes32 messageId;
        uint256 sourceChainId;
        address sender;
        bytes data;
        bool processed;
        uint256 timestamp;
    }

    mapping(uint256 => CrossChainTransfer) public transfers;
    mapping(bytes32 => RelayedMessage) public relayedMessages;
    mapping(uint256 => mapping(address => uint256)) public chainTokenBalances;
    mapping(uint256 => bool) public supportedChains;
    
    uint256 public transferCount;
    uint256 public messageCount;
    uint256 public bridgeFee = 0.001 ether; // Base bridge fee
    uint256 public minTransferAmount = 100; // Minimum transfer amount

    // Events
    event TokensLocked(
        uint256 indexed transferId,
        uint256 indexed sourceChain,
        uint256 indexed targetChain,
        address token,
        uint256 amount,
        address sender,
        address recipient
    );
    
    event TokensReleased(
        uint256 indexed transferId,
        uint256 indexed sourceChain,
        uint256 indexed targetChain,
        address token,
        uint256 amount,
        address recipient
    );
    
    event MessageRelayed(
        bytes32 indexed messageId,
        uint256 indexed sourceChain,
        address sender,
        bytes data
    );
    
    event MessageProcessed(
        bytes32 indexed messageId,
        uint256 indexed sourceChain,
        address sender
    );
    
    event BridgeFeeUpdated(uint256 oldFee, uint256 newFee);
    event ChainSupported(uint256 chainId, bool supported);

    constructor() {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(OPERATOR_ROLE, msg.sender);
        _setupRole(VALIDATOR_ROLE, msg.sender);
        
        // Support the current chain by default
        supportedChains[block.chainid] = true;
    }

    /**
     * @dev Lock tokens for cross-chain transfer
     * @param targetChainId Target chain ID
     * @param token Token address
     * @param amount Amount to transfer
     * @param recipient Recipient address on target chain
     */
    function lockTokens(
        uint256 targetChainId,
        address token,
        uint256 amount,
        address recipient
    ) external payable nonReentrant {
        require(supportedChains[targetChainId], "Target chain not supported");
        require(amount >= minTransferAmount, "Amount below minimum");
        require(recipient != address(0), "Invalid recipient");
        require(msg.value >= bridgeFee, "Insufficient bridge fee");
        
        // Transfer tokens from user
        if (token == address(0)) {
            // Native token (ETH) transfer
            require(msg.value >= amount + bridgeFee, "Insufficient ETH sent");
            // Refund excess ETH (bridge fee is kept)
            if (msg.value > amount + bridgeFee) {
                payable(msg.sender).transfer(msg.value - amount - bridgeFee);
            }
        } else {
            // ERC20 token transfer
            IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
        }
        
        // Update bridge balance
        chainTokenBalances[block.chainid][token] += amount;
        
        // Generate transaction hash
        bytes32 txHash = keccak256(abi.encodePacked(
            block.chainid,
            targetChainId,
            token,
            amount,
            msg.sender,
            recipient,
            block.timestamp
        ));
        
        transferCount++;
        transfers[transferCount] = CrossChainTransfer({
            id: transferCount,
            sourceChainId: block.chainid,
            targetChainId: targetChainId,
            token: token,
            amount: amount,
            sender: msg.sender,
            recipient: recipient,
            transactionHash: txHash,
            completed: false,
            timestamp: block.timestamp
        });
        
        // Send bridge fee to operator
        if (bridgeFee > 0) {
            payable(getRoleMember(OPERATOR_ROLE, 0)).transfer(bridgeFee);
        }
        
        emit TokensLocked(
            transferCount,
            block.chainid,
            targetChainId,
            token,
            amount,
            msg.sender,
            recipient
        );
    }

    /**
     * @dev Release tokens on target chain
     * @param sourceChainId Source chain ID
     * @param transferId Transfer ID
     * @param token Token address
     * @param amount Amount to release
     * @param recipient Recipient address
     * @param signatures Validator signatures
     */
    function releaseTokens(
        uint256 sourceChainId,
        uint256 transferId,
        address token,
        uint256 amount,
        address recipient,
        bytes[] calldata signatures
    ) external nonReentrant {
        require(supportedChains[sourceChainId], "Source chain not supported");
        require(recipient != address(0), "Invalid recipient");
        
        CrossChainTransfer storage transfer = transfers[transferId];
        require(transfer.id != 0, "Transfer does not exist");
        require(!transfer.completed, "Transfer already completed");
        require(transfer.sourceChainId == sourceChainId, "Invalid source chain");
        require(transfer.token == token, "Invalid token");
        require(transfer.amount == amount, "Invalid amount");
        require(transfer.recipient == recipient, "Invalid recipient");
        
        // Verify validator signatures
        require(signatures.length > 0, "No signatures provided");
        require(verifySignatures(
            sourceChainId,
            transferId,
            token,
            amount,
            recipient,
            signatures
        ), "Invalid signatures");
        
        // Check if bridge has sufficient balance
        require(chainTokenBalances[block.chainid][token] >= amount, "Insufficient bridge balance");
        
        // Update bridge balance
        chainTokenBalances[block.chainid][token] -= amount;
        
        // Mark transfer as completed
        transfer.completed = true;
        
        // Transfer tokens to recipient
        if (token == address(0)) {
            // Native token (ETH) transfer
            payable(recipient).transfer(amount);
        } else {
            // ERC20 token transfer
            IERC20(token).safeTransfer(recipient, amount);
        }
        
        emit TokensReleased(
            transferId,
            sourceChainId,
            block.chainid,
            token,
            amount,
            recipient
        );
    }

    /**
     * @dev Relay a message from another chain
     * @param sourceChainId Source chain ID
     * @param sender Sender address
     * @param data Message data
     * @param signatures Validator signatures
     */
    function relayMessage(
        uint256 sourceChainId,
        address sender,
        bytes calldata data,
        bytes[] calldata signatures
    ) external {
        require(supportedChains[sourceChainId], "Source chain not supported");
        require(sender != address(0), "Invalid sender");
        
        bytes32 messageId = keccak256(abi.encodePacked(
            sourceChainId,
            sender,
            data,
            block.timestamp
        ));
        
        // Check if message already processed
        require(!relayedMessages[messageId].processed, "Message already processed");
        
        // Verify validator signatures
        require(signatures.length > 0, "No signatures provided");
        require(verifyMessageSignatures(
            sourceChainId,
            sender,
            data,
            signatures
        ), "Invalid signatures");
        
        messageCount++;
        relayedMessages[messageId] = RelayedMessage({
            messageId: messageId,
            sourceChainId: sourceChainId,
            sender: sender,
            data: data,
            processed: true,
            timestamp: block.timestamp
        });
        
        emit MessageRelayed(messageId, sourceChainId, sender, data);
        emit MessageProcessed(messageId, sourceChainId, sender);
    }

    /**
     * @dev Verify validator signatures for token release
     * @param sourceChainId Source chain ID
     * @param transferId Transfer ID
     * @param token Token address
     * @param amount Amount
     * @param recipient Recipient address
     * @param signatures Validator signatures
     * @return Whether signatures are valid
     */
    function verifySignatures(
        uint256 sourceChainId,
        uint256 transferId,
        address token,
        uint256 amount,
        address recipient,
        bytes[] calldata signatures
    ) internal view returns (bool) {
        bytes32 message = keccak256(abi.encodePacked(
            sourceChainId,
            transferId,
            token,
            amount,
            recipient
        ));
        
        // In a real implementation, this would verify against a validator set
        // For demonstration, we'll check if signatures exist
        // In production, use proper signature verification
        if (signatures.length > 0 && signatures[0].length > 0) {
            // In production, implement proper ECDSA verification
            // This is just a placeholder
            return true;
        }
        
        return false;
    }

    /**
     * @dev Verify validator signatures for message relay
     * @param sourceChainId Source chain ID
     * @param sender Sender address
     * @param data Message data
     * @param signatures Validator signatures
     * @return Whether signatures are valid
     */
    function verifyMessageSignatures(
        uint256 sourceChainId,
        address sender,
        bytes calldata data,
        bytes[] calldata signatures
    ) internal view returns (bool) {
        bytes32 message = keccak256(abi.encodePacked(
            sourceChainId,
            sender,
            data
        ));
        
        // In a real implementation, this would verify against a validator set
        // For demonstration, we'll check if signatures exist
        if (signatures.length > 0 && signatures[0].length > 0) {
            // In production, implement proper ECDSA verification
            // This is just a placeholder
            return true;
        }
        
        return false;
    }

    /**
     * @dev Set bridge fee
     * @param newFee New bridge fee
     */
    function setBridgeFee(uint256 newFee) external {
        require(hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "Caller is not admin");
        uint256 oldFee = bridgeFee;
        bridgeFee = newFee;
        emit BridgeFeeUpdated(oldFee, newFee);
    }

    /**
     * @dev Set minimum transfer amount
     * @param newMin New minimum transfer amount
     */
    function setMinTransferAmount(uint256 newMin) external {
        require(hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "Caller is not admin");
        minTransferAmount = newMin;
    }

    /**
     * @dev Add or remove supported chain
     * @param chainId Chain ID
     * @param supported Whether chain is supported
     */
    function setSupportedChain(uint256 chainId, bool supported) external {
        require(hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "Caller is not admin");
        supportedChains[chainId] = supported;
        emit ChainSupported(chainId, supported);
    }

    /**
     * @dev Get bridge balance for a token and chain
     * @param chainId Chain ID
     * @param token Token address
     * @return Balance of the token on the chain
     */
    function getChainTokenBalance(uint256 chainId, address token) external view returns (uint256) {
        return chainTokenBalances[chainId][token];
    }

    /**
     * @dev Withdraw bridge fees
     * @param to Address to send fees to
     */
    function withdrawFees(address payable to) external {
        require(hasRole(OPERATOR_ROLE, msg.sender), "Caller is not operator");
        uint256 balance = address(this).balance;
        require(balance > 0, "No fees to withdraw");
        
        to.transfer(balance);
    }

    // Fallback function to receive ETH
    receive() external payable {}

    // Emergency functions - only for admin
    
    /**
     * @dev Emergency withdraw of tokens
     * @param token Token address
     * @param to Recipient address
     * @param amount Amount to withdraw
     */
    function emergencyWithdrawToken(
        address token,
        address to,
        uint256 amount
    ) external {
        require(hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "Caller is not admin");
        
        if (token == address(0)) {
            // Native token
            payable(to).transfer(amount);
        } else {
            // ERC20 token
            IERC20(token).safeTransfer(to, amount);
        }
    }

    /**
     * @dev Emergency update of transfer status
     * @param transferId Transfer ID
     * @param status New status
     */
    function emergencyUpdateTransferStatus(uint256 transferId, bool status) external {
        require(hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "Caller is not admin");
        transfers[transferId].completed = status;
    }

    /**
     * @dev Get cross-chain transfer information
     * @param transferId Transfer ID
     * @return The transfer data
     */
    function getCrossChainTransfer(uint256 transferId) external view returns (CrossChainTransfer memory) {
        return transfers[transferId];
    }

    /**
     * @dev Get relayed message information
     * @param messageId Message ID
     * @return The message data
     */
    function getRelayedMessage(bytes32 messageId) external view returns (RelayedMessage memory) {
        return relayedMessages[messageId];
    }
}