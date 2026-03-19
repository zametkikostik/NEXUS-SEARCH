// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title NEXUS Search Token
 * @dev ERC20 token for NEXUS Search ecosystem
 * 
 * Tokenomics:
 * - Total Supply: 1,000,000,000 NXS
 * - Users Rewards: 30% (300,000,000)
 * - Team: 20% (200,000,000) - 4 year vesting
 * - Investors: 20% (200,000,000) - 2 year vesting
 * - Ecosystem: 20% (200,000,000)
 * - Liquidity: 10% (100,000,000)
 */
contract NXSToken is ERC20, ERC20Burnable, ERC20Votes, Ownable, Pausable {
    uint256 public constant TOTAL_SUPPLY = 1_000_000_000 * 10**18; // 1 billion tokens
    uint256 public constant DECIMALS = 18;
    
    // Vesting schedules
    struct VestingSchedule {
        uint256 totalAmount;
        uint256 released;
        uint256 startTime;
        uint256 duration;
        bool active;
    }
    
    mapping(address => VestingSchedule) public vestingSchedules;
    
    // Team vesting (4 years)
    uint256 public constant TEAM_ALLOCATION = 200_000_000 * 10**18;
    uint256 public constant TEAM_VESTING_DURATION = 4 * 365 days;
    
    // Investor vesting (2 years)
    uint256 public constant INVESTOR_ALLOCATION = 200_000_000 * 10**18;
    uint256 public constant INVESTOR_VESTING_DURATION = 2 * 365 days;
    
    // Ecosystem fund
    uint256 public constant ECOSYSTEM_ALLOCATION = 200_000_000 * 10**18;
    
    // User rewards pool
    uint256 public constant USER_REWARDS_ALLOCATION = 300_000_000 * 10**18;
    
    // Liquidity pool
    uint256 public constant LIQUIDITY_ALLOCATION = 100_000_000 * 10**18;
    
    // Addresses
    address public teamMultisig;
    address public investorMultisig;
    address public ecosystemFund;
    address public rewardsPool;
    address public liquidityPool;
    
    // Events
    event VestingScheduleCreated(address indexed beneficiary, uint256 amount, uint256 duration);
    event TokensReleased(address indexed beneficiary, uint256 amount);
    event RewardsDistributed(uint256 amount);
    
    constructor(
        address _teamMultisig,
        address _investorMultisig,
        address _ecosystemFund,
        address _rewardsPool,
        address _liquidityPool
    ) ERC20("NEXUS Search", "NXS") Ownable(msg.sender) {
        teamMultisig = _teamMultisig;
        investorMultisig = _investorMultisig;
        ecosystemFund = _ecosystemFund;
        rewardsPool = _rewardsPool;
        liquidityPool = _liquidityPool;
        
        // Mint total supply
        _mint(address(this), TOTAL_SUPPLY);
        
        // Create team vesting schedule
        _createVestingSchedule(
            teamMultisig,
            TEAM_ALLOCATION,
            TEAM_VESTING_DURATION
        );
        
        // Create investor vesting schedule
        _createVestingSchedule(
            investorMultisig,
            INVESTOR_ALLOCATION,
            INVESTOR_VESTING_DURATION
        );
        
        // Transfer ecosystem tokens
        _transfer(address(this), ecosystemFund, ECOSYSTEM_ALLOCATION);
        
        // Transfer rewards pool tokens
        _transfer(address(this), rewardsPool, USER_REWARDS_ALLOCATION);
        
        // Transfer liquidity pool tokens
        _transfer(address(this), liquidityPool, LIQUIDITY_ALLOCATION);
        
        emit VestingScheduleCreated(teamMultisig, TEAM_ALLOCATION, TEAM_VESTING_DURATION);
        emit VestingScheduleCreated(investorMultisig, INVESTOR_ALLOCATION, INVESTOR_VESTING_DURATION);
    }
    
    /**
     * @dev Create a vesting schedule for a beneficiary
     */
    function _createVestingSchedule(
        address beneficiary,
        uint256 amount,
        uint256 duration
    ) internal {
        vestingSchedules[beneficiary] = VestingSchedule({
            totalAmount: amount,
            released: 0,
            startTime: block.timestamp,
            duration: duration,
            active: true
        });
    }
    
    /**
     * @dev Release vested tokens
     */
    function releaseVestedTokens() external {
        VestingSchedule storage schedule = vestingSchedules[msg.sender];
        require(schedule.active, "No active vesting schedule");
        require(schedule.totalAmount > 0, "No tokens to vest");
        
        uint256 vestedAmount = _calculateVestedAmount(schedule);
        uint256 releasable = vestedAmount - schedule.released;
        
        require(releasable > 0, "No tokens available for release");
        
        schedule.released += releasable;
        _transfer(address(this), msg.sender, releasable);
        
        emit TokensReleased(msg.sender, releasable);
    }
    
    /**
     * @dev Calculate vested amount for a schedule
     */
    function _calculateVestedAmount(VestingSchedule storage schedule) 
        internal 
        view 
        returns (uint256) 
    {
        if (block.timestamp >= schedule.startTime + schedule.duration) {
            return schedule.totalAmount;
        }
        
        if (block.timestamp <= schedule.startTime) {
            return 0;
        }
        
        uint256 timeElapsed = block.timestamp - schedule.startTime;
        return (schedule.totalAmount * timeElapsed) / schedule.duration;
    }
    
    /**
     * @dev Get vested amount for an address
     */
    function getVestedAmount(address account) external view returns (uint256) {
        VestingSchedule storage schedule = vestingSchedules[account];
        return _calculateVestedAmount(schedule);
    }
    
    /**
     * @dev Get releasable amount for an address
     */
    function getReleasableAmount(address account) external view returns (uint256) {
        VestingSchedule storage schedule = vestingSchedules[account];
        uint256 vested = _calculateVestedAmount(schedule);
        return vested - schedule.released;
    }
    
    /**
     * @dev Distribute rewards to users
     */
    function distributeRewards(address[] calldata recipients, uint256[] calldata amounts) 
        external 
        onlyOwner 
    {
        require(recipients.length == amounts.length, "Arrays length mismatch");
        
        uint256 totalAmount = 0;
        for (uint256 i = 0; i < amounts.length; i++) {
            totalAmount += amounts[i];
        }
        
        require(balanceOf(address(this)) >= totalAmount, "Insufficient balance");
        
        for (uint256 i = 0; i < recipients.length; i++) {
            _transfer(address(this), recipients[i], amounts[i]);
        }
        
        emit RewardsDistributed(totalAmount);
    }
    
    /**
     * @dev Pause token transfers
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause token transfers
     */
    function unpause() external onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Update team multisig address
     */
    function setTeamMultisig(address _teamMultisig) external onlyOwner {
        teamMultisig = _teamMultisig;
    }
    
    /**
     * @dev Update investor multisig address
     */
    function setInvestorMultisig(address _investorMultisig) external onlyOwner {
        investorMultisig = _investorMultisig;
    }
    
    /**
     * @dev Update ecosystem fund address
     */
    function setEcosystemFund(address _ecosystemFund) external onlyOwner {
        ecosystemFund = _ecosystemFund;
    }
    
    /**
     * @dev Override transfer to check pause status
     */
    function _update(address from, address to, uint256 amount) internal override(ERC20, ERC20Votes) whenNotPaused {
        super._update(from, to, amount);
    }
    
    /**
     * @dev Override nonces for ERC20Votes
     */
    function nonces(address owner) public view override(ERC20Permit, Nonces) returns (uint256) {
        return super.nonces(owner);
    }
}
