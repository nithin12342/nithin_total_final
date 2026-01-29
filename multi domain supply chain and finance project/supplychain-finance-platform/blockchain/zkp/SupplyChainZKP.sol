// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title SupplyChainZKP
 * @dev Zero-Knowledge Proof implementation for supply chain privacy
 * This contract demonstrates how ZKPs can be used to verify supply chain
 * information without revealing sensitive details
 */
contract SupplyChainZKP is AccessControl, ReentrancyGuard {
    bytes32 public constant VERIFIER_ROLE = keccak256("VERIFIER_ROLE");
    bytes32 public constant SUPPLIER_ROLE = keccak256("SUPPLIER_ROLE");

    // Struct to represent a ZKP verification request
    struct ZKPRequest {
        uint256 id;
        address requester;
        bytes32 circuitId; // Identifier for the ZKP circuit used
        bytes publicInputs; // Public inputs for verification
        bytes proof; // The ZKP proof
        bool verified;
        uint256 timestamp;
    }

    // Struct to represent supply chain verification data
    struct SupplyChainVerification {
        uint256 productId;
        address supplier;
        uint256 originTimestamp;
        bytes32 originHash; // Hash of origin information
        bool compliant; // Whether the product meets compliance standards
        uint256 verificationTimestamp;
    }

    mapping(uint256 => ZKPRequest) public zkpRequests;
    mapping(uint256 => SupplyChainVerification) public supplyChainVerifications;
    mapping(bytes32 => bool) public verifiedProofs; // To prevent proof replay
    
    uint256 public requestCount;
    uint256 public verificationCount;

    // Events
    event ZKPRequestCreated(uint256 indexed requestId, address indexed requester, bytes32 circuitId);
    event ZKPVerified(uint256 indexed requestId, bool verified);
    event SupplyChainVerified(uint256 indexed verificationId, uint256 productId, bool compliant);

    constructor() {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(VERIFIER_ROLE, msg.sender);
    }

    /**
     * @dev Create a ZKP verification request
     * @param circuitId Identifier for the ZKP circuit
     * @param publicInputs Public inputs for verification
     * @param proof The ZKP proof
     */
    function createZKPRequest(
        bytes32 circuitId,
        bytes memory publicInputs,
        bytes memory proof
    ) external {
        require(hasRole(SUPPLIER_ROLE, msg.sender), "Caller is not a supplier");
        
        // Check if proof has already been used (replay protection)
        bytes32 proofHash = keccak256(proof);
        require(!verifiedProofs[proofHash], "Proof already used");
        
        requestCount++;
        zkpRequests[requestCount] = ZKPRequest({
            id: requestCount,
            requester: msg.sender,
            circuitId: circuitId,
            publicInputs: publicInputs,
            proof: proof,
            verified: false,
            timestamp: block.timestamp
        });
        
        emit ZKPRequestCreated(requestCount, msg.sender, circuitId);
    }

    /**
     * @dev Verify a ZKP request
     * In a real implementation, this would call a ZKP verification library
     * For this demonstration, we'll simulate verification
     * @param requestId The ID of the request to verify
     */
    function verifyZKP(uint256 requestId) external {
        require(hasRole(VERIFIER_ROLE, msg.sender), "Caller is not a verifier");
        ZKPRequest storage request = zkpRequests[requestId];
        require(request.id != 0, "Request does not exist");
        require(!request.verified, "Request already verified");
        
        // In a real implementation, this would call a ZKP verification library
        // For demonstration purposes, we'll simulate verification
        bool isValid = simulateZKPVerification(
            request.circuitId,
            request.publicInputs,
            request.proof
        );
        
        request.verified = isValid;
        
        // Mark proof as used to prevent replay
        if (isValid) {
            bytes32 proofHash = keccak256(request.proof);
            verifiedProofs[proofHash] = true;
        }
        
        emit ZKPVerified(requestId, isValid);
    }

    /**
     * @dev Simulate ZKP verification
     * In a real implementation, this would use a ZKP library like snarkjs or circom
     * @param circuitId The circuit identifier
     * @param publicInputs Public inputs
     * @param proof The proof to verify
     * @return Whether the proof is valid
     */
    function simulateZKPVerification(
        bytes32 circuitId,
        bytes memory publicInputs,
        bytes memory proof
    ) internal pure returns (bool) {
        // This is a simplified simulation
        // In reality, this would call a ZKP verification library
        
        // For demonstration, we'll return true for specific circuit IDs
        // In practice, this would perform actual cryptographic verification
        if (circuitId == keccak256("supply_chain_origin") || 
            circuitId == keccak256("compliance_verification") ||
            circuitId == keccak256("authenticity_proof")) {
            // Simple validation - in reality, this would be cryptographic verification
            return proof.length > 0 && publicInputs.length > 0;
        }
        
        return false;
    }

    /**
     * @dev Record supply chain verification based on ZKP
     * @param productId The product ID
     * @param originHash Hash of origin information
     * @param compliant Whether the product is compliant
     * @param requestId The ZKP request ID (must be verified)
     */
    function recordSupplyChainVerification(
        uint256 productId,
        bytes32 originHash,
        bool compliant,
        uint256 requestId
    ) external nonReentrant {
        ZKPRequest storage request = zkpRequests[requestId];
        require(request.verified, "ZKP not verified");
        require(request.requester == msg.sender, "Only requester can record verification");
        
        verificationCount++;
        supplyChainVerifications[verificationCount] = SupplyChainVerification({
            productId: productId,
            supplier: msg.sender,
            originTimestamp: block.timestamp,
            originHash: originHash,
            compliant: compliant,
            verificationTimestamp: block.timestamp
        });
        
        emit SupplyChainVerified(verificationCount, productId, compliant);
    }

    /**
     * @dev Get supply chain verification information
     * @param verificationId The verification ID
     * @return The verification data
     */
    function getSupplyChainVerification(uint256 verificationId) 
        external 
        view 
        returns (SupplyChainVerification memory) 
    {
        return supplyChainVerifications[verificationId];
    }

    /**
     * @dev Check if a product has been verified
     * @param productId The product ID
     * @return Whether the product has been verified
     */
    function isProductVerified(uint256 productId) external view returns (bool) {
        for (uint256 i = 1; i <= verificationCount; i++) {
            if (supplyChainVerifications[i].productId == productId) {
                return true;
            }
        }
        return false;
    }

    /**
     * @dev Check if a product is compliant
     * @param productId The product ID
     * @return Whether the product is compliant
     */
    function isProductCompliant(uint256 productId) external view returns (bool) {
        for (uint256 i = 1; i <= verificationCount; i++) {
            if (supplyChainVerifications[i].productId == productId) {
                return supplyChainVerifications[i].compliant;
            }
        }
        return false;
    }

    /**
     * @dev Grant verifier role
     * @param account The account to grant role to
     */
    function grantVerifierRole(address account) external {
        require(hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "Caller is not admin");
        grantRole(VERIFIER_ROLE, account);
    }

    /**
     * @dev Grant supplier role
     * @param account The account to grant role to
     */
    function grantSupplierRole(address account) external {
        require(hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "Caller is not admin");
        grantRole(SUPPLIER_ROLE, account);
    }
}