# DEPRECATED FILE - INFORMATION CONSOLIDATED
#
# This README file has been consolidated into the main project README.md
# Please refer to: /README.md for all project information
#
# Blockchain documentation is now in the "Technology Domains" section
# of the main README.md file.
#
# File deprecated as of: October 23, 2025
# Reason: Documentation consolidation for better organization

DEPRECATED - USE MAIN README.md INSTEAD

# Blockchain Smart Contracts Testing

This directory contains the testing framework and security audits for the smart contracts used in the Supply Chain and Finance Platform.

## Smart Contracts Overview

1. **SupplyChain.sol** - Manages product tracking through the supply chain
2. **FinanceSettlement.sol** - Handles invoice financing and payments with ERC20 tokens
3. **SupplyChainFinance.sol** - Combines supply chain and finance functionality with native ETH payments

## Testing Framework

We use Hardhat with Waffle for testing smart contracts. Tests are written in JavaScript and use the Chai assertion library.

### Installation

```bash
npm install
```

### Running Tests

```bash
# Run all tests
npm test

# Run specific test file
npx hardhat test test/SupplyChain.test.js
```

## Test Coverage

The tests cover the following areas:

### SupplyChain.sol
- Role-based access control for suppliers, manufacturers, and distributors
- Product creation and tracking
- Status updates for products in the supply chain
- Product delivery functionality

### FinanceSettlement.sol
- Invoice creation by suppliers
- Invoice financing by financiers with ERC20 token transfers
- Invoice payment by buyers with proper fund distribution
- Validation of financing amounts and payment amounts

### SupplyChainFinance.sol
- Invoice creation and management
- Invoice financing with native ETH
- Invoice payment with proper fund distribution
- Shipment creation and status updates

## Security Audits

Security audits are performed using:
1. Static analysis with Slither
2. Formal verification with Certora Prover
3. Manual security reviews

## Common Vulnerabilities Checked

1. Reentrancy attacks
2. Access control issues
3. Integer overflow/underflow
4. Gas limit issues
5. Front-running vulnerabilities
6. Denial of service attacks
7. Bad randomness usage
8. Time manipulation issues

## Best Practices Implemented

1. Use of OpenZeppelin contracts for standard functionality
2. Proper access control with role-based permissions
3. Event emission for all state-changing operations
4. Input validation and error handling
5. Non-reentrant modifiers for state-changing functions
6. Proper use of require statements for validation
7. Gas optimization techniques