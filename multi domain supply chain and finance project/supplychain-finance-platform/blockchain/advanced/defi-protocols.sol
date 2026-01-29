// SPDX-License-Identifier: MIT




pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title Advanced DeFi Protocol Suite
 * @dev Demonstrates advanced DeFi concepts including:
 * - Automated Market Maker (AMM)
 * - Yield Farming
 * - Liquidity Mining
 * - Flash Loans
 * - Cross-chain Bridges
 * - Layer 2 Integration
 * 
 * This contract showcases sophisticated DeFi mechanisms
 * for supply chain finance applications
 */
contract AdvancedDeFiProtocols is ReentrancyGuard, Pausable, Ownable {
    using SafeERC20 for IERC20;
    using SafeMath for uint256;

    // ============ STRUCTS ============
    
    struct LiquidityPool {
        address tokenA;
        address tokenB;
        uint256 reserveA;
        uint256 reserveB;
        uint256 totalSupply;
        uint256 k; // Constant product (x * y = k)
        uint256 fee; // Basis points (e.g., 30 = 0.3%)
        bool active;
        uint256 lastUpdateTime;
    }
    
    struct YieldFarm {
        address stakingToken;
        address rewardToken;
        uint256 rewardRate; // Tokens per second
        uint256 periodFinish;
        uint256 lastUpdateTime;
        uint256 rewardPerTokenStored;
        mapping(address => uint256) userRewardPerTokenPaid;
        mapping(address => uint256) rewards;
        uint256 totalStaked;
    }
    
    struct FlashLoan {
        address token;
        uint256 amount;
        address borrower;
        uint256 fee;
        bool active;
    }
    
    struct CrossChainBridge {
        uint256 chainId;
        address token;
        uint256 totalLocked;
        mapping(bytes32 => bool) processedTransactions;
    }

    // ============ STATE VARIABLES ============
    
    mapping(bytes32 => LiquidityPool) public liquidityPools;
    mapping(bytes32 => YieldFarm) public yieldFarms;
    mapping(address => mapping(address => uint256)) public liquidityProviderShares;
    mapping(address => uint256) public flashLoanFees;
    mapping(uint256 => CrossChainBridge) public crossChainBridges;
    
    uint256 public constant BASIS_POINTS = 10000;
    uint256 public constant MAX_FEE = 1000; // 10%
    uint256 public flashLoanFeeRate = 9; // 0.09%
    
    address public feeCollector;
    uint256 public totalFeesCollected;
    
    // Events
    event LiquidityAdded(
        bytes32 indexed poolId,
        address indexed provider,
        uint256 amountA,
        uint256 amountB,
        uint256 shares
    );
    
    event LiquidityRemoved(
        bytes32 indexed poolId,
        address indexed provider,
        uint256 amountA,
        uint256 amountB,
        uint256 shares
    );
    
    event SwapExecuted(
        bytes32 indexed poolId,
        address indexed trader,
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOut
    );
    
    event YieldFarmCreated(
        bytes32 indexed farmId,
        address stakingToken,
        address rewardToken,
        uint256 rewardRate
    );
    
    event Staked(
        bytes32 indexed farmId,
        address indexed user,
        uint256 amount
    );
    
    event RewardsClaimed(
        bytes32 indexed farmId,
        address indexed user,
        uint256 amount
    );
    
    event FlashLoanExecuted(
        address indexed borrower,
        address token,
        uint256 amount,
        uint256 fee
    );
    
    event CrossChainTransfer(
        uint256 indexed fromChain,
        uint256 indexed toChain,
        address indexed user,
        address token,
        uint256 amount,
        bytes32 transactionHash
    );

    // ============ CONSTRUCTOR ============
    
    constructor(address _feeCollector) {
        feeCollector = _feeCollector;
    }

    // ============ LIQUIDITY POOL FUNCTIONS ============
    
    /**
     * @dev Create a new liquidity pool
     * @param tokenA First token address
     * @param tokenB Second token address
     * @param fee Fee in basis points
     */
    function createLiquidityPool(
        address tokenA,
        address tokenB,
        uint256 fee
    ) external onlyOwner returns (bytes32 poolId) {
        require(tokenA != tokenB, "Tokens must be different");
        require(fee <= MAX_FEE, "Fee too high");
        require(tokenA != address(0) && tokenB != address(0), "Invalid token");
        
        poolId = keccak256(abi.encodePacked(tokenA, tokenB, fee));
        require(!liquidityPools[poolId].active, "Pool already exists");
        
        liquidityPools[poolId] = LiquidityPool({
            tokenA: tokenA,
            tokenB: tokenB,
            reserveA: 0,
            reserveB: 0,
            totalSupply: 0,
            k: 0,
            fee: fee,
            active: true,
            lastUpdateTime: block.timestamp
        });
    }
    
    /**
     * @dev Add liquidity to a pool
     * @param poolId Pool identifier
     * @param amountA Amount of token A
     * @param amountB Amount of token B
     */
    function addLiquidity(
        bytes32 poolId,
        uint256 amountA,
        uint256 amountB
    ) external nonReentrant whenNotPaused {
        LiquidityPool storage pool = liquidityPools[poolId];
        require(pool.active, "Pool not active");
        
        IERC20 tokenA = IERC20(pool.tokenA);
        IERC20 tokenB = IERC20(pool.tokenB);
        
        // Transfer tokens from user
        tokenA.safeTransferFrom(msg.sender, address(this), amountA);
        tokenB.safeTransferFrom(msg.sender, address(this), amountB);
        
        uint256 shares;
        
        if (pool.totalSupply == 0) {
            // First liquidity provision
            shares = Math.sqrt(amountA.mul(amountB));
            pool.k = amountA.mul(amountB);
        } else {
            // Maintain ratio
            uint256 expectedAmountB = amountA.mul(pool.reserveB).div(pool.reserveA);
            require(amountB >= expectedAmountB, "Insufficient token B");
            
            shares = amountA.mul(pool.totalSupply).div(pool.reserveA);
            
            // Update reserves
            pool.reserveA = pool.reserveA.add(amountA);
            pool.reserveB = pool.reserveB.add(amountB);
            pool.k = pool.reserveA.mul(pool.reserveB);
        }
        
        pool.totalSupply = pool.totalSupply.add(shares);
        liquidityProviderShares[msg.sender][poolId] = 
            liquidityProviderShares[msg.sender][poolId].add(shares);
        
        emit LiquidityAdded(poolId, msg.sender, amountA, amountB, shares);
    }
    
    /**
     * @dev Remove liquidity from a pool
     * @param poolId Pool identifier
     * @param shares Number of shares to burn
     */
    function removeLiquidity(
        bytes32 poolId,
        uint256 shares
    ) external nonReentrant {
        LiquidityPool storage pool = liquidityPools[poolId];
        require(pool.active, "Pool not active");
        require(shares <= liquidityProviderShares[msg.sender][poolId], "Insufficient shares");
        
        uint256 amountA = shares.mul(pool.reserveA).div(pool.totalSupply);
        uint256 amountB = shares.mul(pool.reserveB).div(pool.totalSupply);
        
        // Update state
        pool.reserveA = pool.reserveA.sub(amountA);
        pool.reserveB = pool.reserveB.sub(amountB);
        pool.totalSupply = pool.totalSupply.sub(shares);
        pool.k = pool.reserveA.mul(pool.reserveB);
        
        liquidityProviderShares[msg.sender][poolId] = 
            liquidityProviderShares[msg.sender][poolId].sub(shares);
        
        // Transfer tokens to user
        IERC20(pool.tokenA).safeTransfer(msg.sender, amountA);
        IERC20(pool.tokenB).safeTransfer(msg.sender, amountB);
        
        emit LiquidityRemoved(poolId, msg.sender, amountA, amountB, shares);
    }
    
    /**
     * @dev Execute a swap in the AMM
     * @param poolId Pool identifier
     * @param tokenIn Input token address
     * @param amountIn Input amount
     * @param minAmountOut Minimum output amount (slippage protection)
     */
    function swap(
        bytes32 poolId,
        address tokenIn,
        uint256 amountIn,
        uint256 minAmountOut
    ) external nonReentrant whenNotPaused {
        LiquidityPool storage pool = liquidityPools[poolId];
        require(pool.active, "Pool not active");
        require(tokenIn == pool.tokenA || tokenIn == pool.tokenB, "Invalid token");
        
        address tokenOut = tokenIn == pool.tokenA ? pool.tokenB : pool.tokenA;
        uint256 reserveIn = tokenIn == pool.tokenA ? pool.reserveA : pool.reserveB;
        uint256 reserveOut = tokenIn == pool.tokenA ? pool.reserveB : pool.reserveA;
        
        // Calculate output amount with fee
        uint256 amountInWithFee = amountIn.mul(BASIS_POINTS.sub(pool.fee));
        uint256 amountOut = amountInWithFee.mul(reserveOut).div(
            reserveIn.mul(BASIS_POINTS).add(amountInWithFee)
        );
        
        require(amountOut >= minAmountOut, "Slippage too high");
        
        // Transfer input token from user
        IERC20(tokenIn).safeTransferFrom(msg.sender, address(this), amountIn);
        
        // Update reserves
        if (tokenIn == pool.tokenA) {
            pool.reserveA = pool.reserveA.add(amountIn);
            pool.reserveB = pool.reserveB.sub(amountOut);
        } else {
            pool.reserveB = pool.reserveB.add(amountIn);
            pool.reserveA = pool.reserveA.sub(amountOut);
        }
        
        // Transfer output token to user
        IERC20(tokenOut).safeTransfer(msg.sender, amountOut);
        
        emit SwapExecuted(poolId, msg.sender, tokenIn, tokenOut, amountIn, amountOut);
    }

    // ============ YIELD FARMING FUNCTIONS ============
    
    /**
     * @dev Create a new yield farm
     * @param stakingToken Token to stake
     * @param rewardToken Token to reward
     * @param rewardRate Reward rate per second
     * @param duration Duration in seconds
     */
    function createYieldFarm(
        address stakingToken,
        address rewardToken,
        uint256 rewardRate,
        uint256 duration
    ) external onlyOwner returns (bytes32 farmId) {
        require(stakingToken != address(0) && rewardToken != address(0), "Invalid token");
        require(rewardRate > 0, "Invalid reward rate");
        
        farmId = keccak256(abi.encodePacked(stakingToken, rewardToken, block.timestamp));
        
        YieldFarm storage farm = yieldFarms[farmId];
        farm.stakingToken = stakingToken;
        farm.rewardToken = rewardToken;
        farm.rewardRate = rewardRate;
        farm.periodFinish = block.timestamp.add(duration);
        farm.lastUpdateTime = block.timestamp;
        farm.rewardPerTokenStored = 0;
        farm.totalStaked = 0;
        
        emit YieldFarmCreated(farmId, stakingToken, rewardToken, rewardRate);
    }
    
    /**
     * @dev Stake tokens in a yield farm
     * @param farmId Farm identifier
     * @param amount Amount to stake
     */
    function stake(bytes32 farmId, uint256 amount) external nonReentrant {
        YieldFarm storage farm = yieldFarms[farmId];
        require(block.timestamp < farm.periodFinish, "Farm ended");
        require(amount > 0, "Amount must be positive");
        
        updateReward(farmId, msg.sender);
        
        IERC20(farm.stakingToken).safeTransferFrom(msg.sender, address(this), amount);
        farm.totalStaked = farm.totalStaked.add(amount);
        
        emit Staked(farmId, msg.sender, amount);
    }
    
    /**
     * @dev Claim rewards from a yield farm
     * @param farmId Farm identifier
     */
    function claimRewards(bytes32 farmId) external nonReentrant {
        YieldFarm storage farm = yieldFarms[farmId];
        
        updateReward(farmId, msg.sender);
        
        uint256 reward = farm.rewards[msg.sender];
        if (reward > 0) {
            farm.rewards[msg.sender] = 0;
            IERC20(farm.rewardToken).safeTransfer(msg.sender, reward);
            
            emit RewardsClaimed(farmId, msg.sender, reward);
        }
    }
    
    /**
     * @dev Update reward calculations
     * @param farmId Farm identifier
     * @param user User address
     */
    function updateReward(bytes32 farmId, address user) internal {
        YieldFarm storage farm = yieldFarms[farmId];
        
        if (block.timestamp > farm.lastUpdateTime) {
            uint256 timeElapsed = Math.min(block.timestamp, farm.periodFinish).sub(farm.lastUpdateTime);
            uint256 rewardPerToken = farm.rewardRate.mul(timeElapsed).mul(1e18).div(farm.totalStaked);
            farm.rewardPerTokenStored = farm.rewardPerTokenStored.add(rewardPerToken);
            farm.lastUpdateTime = Math.min(block.timestamp, farm.periodFinish);
        }
        
        if (user != address(0)) {
            farm.rewards[user] = farm.rewards[user].add(
                farm.totalStaked.mul(farm.rewardPerTokenStored.sub(farm.userRewardPerTokenPaid[user])).div(1e18)
            );
            farm.userRewardPerTokenPaid[user] = farm.rewardPerTokenStored;
        }
    }

    // ============ FLASH LOAN FUNCTIONS ============
    
    /**
     * @dev Execute a flash loan
     * @param token Token to borrow
     * @param amount Amount to borrow
     * @param data Encoded function call data
     */
    function flashLoan(
        address token,
        uint256 amount,
        bytes calldata data
    ) external nonReentrant whenNotPaused {
        require(amount > 0, "Amount must be positive");
        
        uint256 fee = amount.mul(flashLoanFeeRate).div(BASIS_POINTS);
        uint256 totalRepay = amount.add(fee);
        
        // Check if contract has enough tokens
        require(IERC20(token).balanceOf(address(this)) >= amount, "Insufficient liquidity");
        
        // Transfer tokens to borrower
        IERC20(token).safeTransfer(msg.sender, amount);
        
        // Execute callback
        IFlashLoanReceiver(msg.sender).executeOperation(token, amount, fee, data);
        
        // Ensure repayment
        require(IERC20(token).balanceOf(address(this)) >= totalRepay, "Flash loan not repaid");
        
        // Collect fee
        if (fee > 0) {
            IERC20(token).safeTransfer(feeCollector, fee);
            totalFeesCollected = totalFeesCollected.add(fee);
        }
        
        emit FlashLoanExecuted(msg.sender, token, amount, fee);
    }

    // ============ CROSS-CHAIN BRIDGE FUNCTIONS ============
    
    /**
     * @dev Lock tokens for cross-chain transfer
     * @param targetChain Target chain ID
     * @param token Token to transfer
     * @param amount Amount to transfer
     * @param recipient Recipient address on target chain
     */
    function lockTokensForBridge(
        uint256 targetChain,
        address token,
        uint256 amount,
        address recipient
    ) external nonReentrant {
        require(amount > 0, "Amount must be positive");
        require(recipient != address(0), "Invalid recipient");
        
        // Transfer tokens from user
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
        
        // Update bridge state
        CrossChainBridge storage bridge = crossChainBridges[targetChain];
        bridge.chainId = targetChain;
        bridge.token = token;
        bridge.totalLocked = bridge.totalLocked.add(amount);
        
        // Generate transaction hash for verification
        bytes32 txHash = keccak256(abi.encodePacked(
            block.chainid,
            targetChain,
            msg.sender,
            recipient,
            token,
            amount,
            block.timestamp
        ));
        
        emit CrossChainTransfer(
            block.chainid,
            targetChain,
            recipient,
            token,
            amount,
            txHash
        );
    }
    
    /**
     * @dev Release tokens from cross-chain bridge
     * @param sourceChain Source chain ID
     * @param token Token to release
     * @param amount Amount to release
     * @param recipient Recipient address
     * @param txHash Source transaction hash
     * @param signature Validator signature
     */
    function releaseTokensFromBridge(
        uint256 sourceChain,
        address token,
        uint256 amount,
        address recipient,
        bytes32 txHash,
        bytes calldata signature
    ) external nonReentrant {
        require(amount > 0, "Amount must be positive");
        require(recipient != address(0), "Invalid recipient");
        require(!crossChainBridges[sourceChain].processedTransactions[txHash], "Transaction already processed");
        
        // Verify signature (simplified - in production, use proper validator set)
        require(verifyBridgeSignature(sourceChain, token, amount, recipient, txHash, signature), "Invalid signature");
        
        // Mark transaction as processed
        crossChainBridges[sourceChain].processedTransactions[txHash] = true;
        
        // Update bridge state
        CrossChainBridge storage bridge = crossChainBridges[sourceChain];
        bridge.totalLocked = bridge.totalLocked.sub(amount);
        
        // Transfer tokens to recipient
        IERC20(token).safeTransfer(recipient, amount);
        
        emit CrossChainTransfer(
            sourceChain,
            block.chainid,
            recipient,
            token,
            amount,
            txHash
        );
    }
    
    /**
     * @dev Verify bridge transaction signature
     * @param sourceChain Source chain ID
     * @param token Token address
     * @param amount Amount
     * @param recipient Recipient address
     * @param txHash Transaction hash
     * @param signature Validator signature
     */
    function verifyBridgeSignature(
        uint256 sourceChain,
        address token,
        uint256 amount,
        address recipient,
        bytes32 txHash,
        bytes calldata signature
    ) internal pure returns (bool) {
        // Simplified verification - in production, implement proper validator set
        bytes32 messageHash = keccak256(abi.encodePacked(
            sourceChain,
            token,
            amount,
            recipient,
            txHash
        ));
        
        // In production, verify against validator set
        return signature.length == 65; // Placeholder
    }

    // ============ ADMIN FUNCTIONS ============
    
    /**
     * @dev Set flash loan fee rate
     * @param newFeeRate New fee rate in basis points
     */
    function setFlashLoanFeeRate(uint256 newFeeRate) external onlyOwner {
        require(newFeeRate <= 100, "Fee rate too high"); // Max 1%
        flashLoanFeeRate = newFeeRate;
    }
    
    /**
     * @dev Set fee collector address
     * @param newFeeCollector New fee collector address
     */
    function setFeeCollector(address newFeeCollector) external onlyOwner {
        require(newFeeCollector != address(0), "Invalid address");
        feeCollector = newFeeCollector;
    }
    
    /**
     * @dev Pause contract
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause contract
     */
    function unpause() external onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Emergency withdraw
     * @param token Token to withdraw
     * @param amount Amount to withdraw
     */
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner(), amount);
    }
}

/**
 * @title Flash Loan Receiver Interface
 * @dev Interface for contracts that can receive flash loans
 */
interface IFlashLoanReceiver {
    function executeOperation(
        address token,
        uint256 amount,
        uint256 fee,
        bytes calldata data
    ) external;
}
