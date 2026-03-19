// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title Staking Contract for NXS Token
 * @dev Allows users to stake NXS tokens and earn rewards
 */
contract NXSStaking is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;
    
    IERC20 public immutable token;
    
    // Reward rate per second (5% APY)
    uint256 public rewardRate = 500; // basis points (500 = 5%)
    uint256 public constant BASIS_POINTS = 10000;
    
    // Minimum staking duration
    uint256 public constant MIN_STAKING_DURATION = 1 days;
    
    // Staking info per user
    struct StakeInfo {
        uint256 amount;
        uint256 rewardDebt;
        uint256 pendingRewards;
        uint256 lastStakeTime;
        uint256 lockEndTime;
    }
    
    mapping(address => StakeInfo) public stakes;
    
    // Total staked
    uint256 public totalStaked;
    
    // Reward pool address
    address public rewardPool;
    
    // Events
    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event RewardsClaimed(address indexed user, uint256 amount);
    event RewardRateUpdated(uint256 newRate);
    
    constructor(address _token, address _rewardPool) Ownable(msg.sender) {
        token = IERC20(_token);
        rewardPool = _rewardPool;
    }
    
    /**
     * @dev Stake tokens
     */
    function stake(uint256 amount) external nonReentrant {
        require(amount > 0, "Cannot stake 0");
        
        // Claim pending rewards first
        _claimRewards(msg.sender);
        
        // Update stake
        StakeInfo storage stake = stakes[msg.sender];
        stake.amount += amount;
        stake.lastStakeTime = block.timestamp;
        
        // Lock for minimum duration if first stake
        if (stake.lockEndTime < block.timestamp) {
            stake.lockEndTime = block.timestamp + MIN_STAKING_DURATION;
        }
        
        totalStaked += amount;
        
        // Transfer tokens
        token.safeTransferFrom(msg.sender, address(this), amount);
        
        emit Staked(msg.sender, amount);
    }
    
    /**
     * @dev Unstake tokens
     */
    function unstake(uint256 amount) external nonReentrant {
        StakeInfo storage stake = stakes[msg.sender];
        
        require(stake.amount >= amount, "Insufficient staked balance");
        require(block.timestamp >= stake.lockEndTime, "Tokens are locked");
        
        // Claim pending rewards first
        _claimRewards(msg.sender);
        
        stake.amount -= amount;
        totalStaked -= amount;
        
        // Transfer tokens
        token.safeTransfer(msg.sender, amount);
        
        emit Unstaked(msg.sender, amount);
    }
    
    /**
     * @dev Claim pending rewards
     */
    function claimRewards() external nonReentrant {
        _claimRewards(msg.sender);
    }
    
    /**
     * @dev Internal function to claim rewards
     */
    function _claimRewards(address user) internal {
        StakeInfo storage stake = stakes[user];
        
        // Calculate pending rewards
        uint256 pending = _calculatePendingRewards(user);
        
        if (pending > 0) {
            stake.pendingRewards -= pending;
            stake.rewardDebt = block.timestamp;
            
            // Transfer rewards from reward pool
            token.safeTransferFrom(rewardPool, user, pending);
            
            emit RewardsClaimed(user, pending);
        }
    }
    
    /**
     * @dev Calculate pending rewards for a user
     */
    function _calculatePendingRewards(address user) internal view returns (uint256) {
        StakeInfo storage stake = stakes[user];
        
        if (stake.amount == 0) {
            return 0;
        }
        
        uint256 timeElapsed = block.timestamp - stake.rewardDebt;
        uint256 reward = (stake.amount * rewardRate * timeElapsed) / (BASIS_POINTS * 365 days);
        
        return stake.pendingRewards + reward;
    }
    
    /**
     * @dev Get pending rewards for a user
     */
    function pendingRewards(address user) external view returns (uint256) {
        return _calculatePendingRewards(user);
    }
    
    /**
     * @dev Get stake info for a user
     */
    function getStakeInfo(address user) external view returns (
        uint256 amount,
        uint256 pending,
        uint256 lastStakeTime,
        uint256 lockEndTime
    ) {
        StakeInfo storage stake = stakes[user];
        return (
            stake.amount,
            _calculatePendingRewards(user),
            stake.lastStakeTime,
            stake.lockEndTime
        );
    }
    
    /**
     * @dev Update reward rate (owner only)
     */
    function setRewardRate(uint256 _newRate) external onlyOwner {
        require(_newRate <= 2000, "Rate too high"); // Max 20%
        rewardRate = _newRate;
        emit RewardRateUpdated(_newRate);
    }
    
    /**
     * @dev Update reward pool address (owner only)
     */
    function setRewardPool(address _rewardPool) external onlyOwner {
        rewardPool = _rewardPool;
    }
    
    /**
     * @dev Emergency withdraw (only if contract is compromised)
     */
    function emergencyWithdraw() external nonReentrant {
        StakeInfo storage stake = stakes[msg.sender];
        uint256 amount = stake.amount;
        
        require(amount > 0, "No staked balance");
        
        stake.amount = 0;
        stake.pendingRewards = 0;
        totalStaked -= amount;
        
        token.safeTransfer(msg.sender, amount);
        
        emit Unstaked(msg.sender, amount);
    }
}
