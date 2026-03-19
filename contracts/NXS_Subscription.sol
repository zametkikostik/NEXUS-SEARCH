// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title NEXUS Search Subscription NFT
 * @dev NFT-based subscription for premium features
 */
contract NXSSubscription is ERC721, ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    
    Counters.Counter private _tokenIdCounter;
    
    // Subscription tiers
    enum Tier {
        BASIC,
        PREMIUM,
        ENTERPRISE
    }
    
    struct Subscription {
        Tier tier;
        uint256 startTime;
        uint256 endTime;
        bool active;
    }
    
    mapping(uint256 => Subscription) public subscriptions;
    mapping(address => uint256[]) public userSubscriptions;
    
    // Pricing (in wei)
    uint256 public basicPrice = 0.01 ether;
    uint256 public premiumPrice = 0.05 ether;
    uint256 public enterprisePrice = 0.1 ether;
    
    // Durations
    uint256 public constant BASIC_DURATION = 30 days;
    uint256 public constant PREMIUM_DURATION = 90 days;
    uint256 public constant ENTERPRISE_DURATION = 365 days;
    
    // Payment token (optional, defaults to ETH)
    address public paymentToken;
    
    // Events
    event SubscriptionCreated(
        address indexed user,
        uint256 indexed tokenId,
        Tier tier,
        uint256 endTime
    );
    event SubscriptionRenewed(
        address indexed user,
        uint256 indexed tokenId,
        uint256 newEndTime
    );
    event PriceUpdated(Tier tier, uint256 newPrice);
    
    constructor() ERC721("NEXUS Subscription", "NXSS") Ownable(msg.sender) {}
    
    /**
     * @dev Create basic subscription
     */
    function createBasicSubscription() external payable returns (uint256) {
        require(msg.value >= basicPrice, "Insufficient payment");
        return _createSubscription(Tier.BASIC, BASIC_DURATION);
    }
    
    /**
     * @dev Create premium subscription
     */
    function createPremiumSubscription() external payable returns (uint256) {
        require(msg.value >= premiumPrice, "Insufficient payment");
        return _createSubscription(Tier.PREMIUM, PREMIUM_DURATION);
    }
    
    /**
     * @dev Create enterprise subscription
     */
    function createEnterpriseSubscription() external payable returns (uint256) {
        require(msg.value >= enterprisePrice, "Insufficient payment");
        return _createSubscription(Tier.ENTERPRISE, ENTERPRISE_DURATION);
    }
    
    /**
     * @dev Internal function to create subscription
     */
    function _createSubscription(Tier tier, uint256 duration) internal returns (uint256) {
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        
        _safeMint(msg.sender, tokenId);
        
        subscriptions[tokenId] = Subscription({
            tier: tier,
            startTime: block.timestamp,
            endTime: block.timestamp + duration,
            active: true
        });
        
        userSubscriptions[msg.sender].push(tokenId);
        
        emit SubscriptionCreated(msg.sender, tokenId, tier, block.timestamp + duration);
        
        return tokenId;
    }
    
    /**
     * @dev Renew existing subscription
     */
    function renewSubscription(uint256 tokenId) external payable {
        require(ownerOf(tokenId) == msg.sender, "Not token owner");
        
        Subscription storage sub = subscriptions[tokenId];
        require(sub.active, "Subscription not active");
        
        uint256 price;
        uint256 duration;
        
        if (sub.tier == Tier.BASIC) {
            price = basicPrice;
            duration = BASIC_DURATION;
        } else if (sub.tier == Tier.PREMIUM) {
            price = premiumPrice;
            duration = PREMIUM_DURATION;
        } else {
            price = enterprisePrice;
            duration = ENTERPRISE_DURATION;
        }
        
        require(msg.value >= price, "Insufficient payment");
        
        // Extend subscription
        if (sub.endTime < block.timestamp) {
            sub.startTime = block.timestamp;
            sub.endTime = block.timestamp + duration;
        } else {
            sub.endTime += duration;
        }
        
        emit SubscriptionRenewed(msg.sender, tokenId, sub.endTime);
    }
    
    /**
     * @dev Check if user has active subscription
     */
    function hasActiveSubscription(address user) external view returns (bool) {
        uint256[] memory subs = userSubscriptions[user];
        
        for (uint256 i = 0; i < subs.length; i++) {
            Subscription storage sub = subscriptions[subs[i]];
            if (sub.active && sub.endTime > block.timestamp) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * @dev Get active subscription tier for user
     */
    function getActiveTier(address user) external view returns (Tier) {
        uint256[] memory subs = userSubscriptions[user];
        Tier highestTier = Tier.BASIC;
        
        for (uint256 i = 0; i < subs.length; i++) {
            Subscription storage sub = subscriptions[subs[i]];
            if (sub.active && sub.endTime > block.timestamp) {
                if (uint256(sub.tier) > uint256(highestTier)) {
                    highestTier = sub.tier;
                }
            }
        }
        
        return highestTier;
    }
    
    /**
     * @dev Get subscription details
     */
    function getSubscription(uint256 tokenId) external view returns (
        Tier tier,
        uint256 startTime,
        uint256 endTime,
        bool active
    ) {
        Subscription storage sub = subscriptions[tokenId];
        return (sub.tier, sub.startTime, sub.endTime, sub.active);
    }
    
    /**
     * @dev Update pricing (owner only)
     */
    function setPrice(Tier tier, uint256 newPrice) external onlyOwner {
        if (tier == Tier.BASIC) {
            basicPrice = newPrice;
        } else if (tier == Tier.PREMIUM) {
            premiumPrice = newPrice;
        } else {
            enterprisePrice = newPrice;
        }
        
        emit PriceUpdated(tier, newPrice);
    }
    
    /**
     * @dev Withdraw collected payments (owner only)
     */
    function withdraw() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
    
    /**
     * @dev Set payment token address (for ERC20 payments)
     */
    function setPaymentToken(address _token) external onlyOwner {
        paymentToken = _token;
    }
    
    /**
     * @dev Override token URI
     */
    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }
    
    /**
     * @dev Override supportsInterface
     */
    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721URIStorage) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
