"""
NEXUS Search - Core Configuration
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    APP_NAME: str = Field(default="NEXUS Search", description="Application name")
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    API_PREFIX: str = Field(default="/api/v1", description="API prefix")
    
    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    
    # Redis
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_DB: int = Field(default=0, description="Redis database")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    DATABASE_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    
    # Redis TTL
    CACHE_TTL_DEFAULT: int = Field(default=3600, description="Default cache TTL in seconds")
    CACHE_TTL_NEWS: int = Field(default=300, description="News cache TTL")
    CACHE_TTL_STATIC: int = Field(default=86400, description="Static content cache TTL")
    
    # IPFS
    IPFS_HOST: str = Field(default="localhost", description="IPFS host")
    IPFS_PORT: int = Field(default=5001, description="IPFS port")
    IPFS_GATEWAY: str = Field(default="https://ipfs.io/ipfs/", description="IPFS gateway URL")
    
    # Web3
    WEB3_PROVIDER_URI: str = Field(default="http://localhost:8545", description="Web3 provider URI")
    WEB3_CHAIN_ID: int = Field(default=1, description="Chain ID")
    WEB3_NETWORK: str = Field(default="mainnet", description="Network name")
    
    # Smart Contract
    CONTRACT_ADDRESS: str = Field(default="0x0000000000000000000000000000000000000000", description="Main contract address")
    
    # JWT
    JWT_SECRET: str = Field(default="change-me-in-production", description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_EXPIRATION_MINUTES: int = Field(default=60, description="JWT expiration in minutes")
    JWT_REFRESH_EXPIRATION_DAYS: int = Field(default=7, description="JWT refresh expiration in days")
    
    # Wallet Signature
    SIGNATURE_EXPIRATION_MINUTES: int = Field(default=10, description="Signature expiration in minutes")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit per minute")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, description="Rate limit per hour")
    RATE_LIMIT_PER_DAY: int = Field(default=10000, description="Rate limit per day")
    
    # Query Limits
    SEARCH_LIMIT_DEFAULT: int = Field(default=10, description="Default search limit")
    SEARCH_LIMIT_MAX: int = Field(default=50, description="Maximum search limit")
    
    # Proxy Configuration
    PROXY_ROTATION_ENABLED: bool = Field(default=True, description="Enable proxy rotation")
    PROXY_LIST_FILE: str = Field(default="proxies.txt", description="Proxy list file")
    PROXY_TIMEOUT: int = Field(default=10, description="Proxy timeout in seconds")
    PROXY_MAX_RETRIES: int = Field(default=3, description="Proxy max retries")
    
    # Proxy Providers
    PROXY_PROVIDER_URL: Optional[str] = Field(default=None, description="Proxy provider URL")
    PROXY_PROVIDER_API_KEY: Optional[str] = Field(default=None, description="Proxy provider API key")
    DATACENTER_PROXIES: Optional[str] = Field(default=None, description="Datacenter proxies (comma-separated)")
    
    # Tor
    TOR_PROXY_ENABLED: bool = Field(default=False, description="Enable Tor proxy")
    TOR_PROXY_HOST: str = Field(default="127.0.0.1", description="Tor proxy host")
    TOR_PROXY_PORT: int = Field(default=9050, description="Tor proxy port")
    
    # Request Settings
    REQUEST_TIMEOUT: int = Field(default=30, description="Request timeout in seconds")
    REQUEST_MAX_RETRIES: int = Field(default=3, description="Request max retries")
    REQUEST_BACKOFF_FACTOR: float = Field(default=1.5, description="Request backoff factor")
    REQUEST_USER_AGENT_ROTATION: bool = Field(default=True, description="Enable User-Agent rotation")
    
    # Circuit Breaker
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = Field(default=5, description="Circuit breaker failure threshold")
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = Field(default=60, description="Circuit breaker recovery timeout")
    CIRCUIT_BREAKER_TIMEOUT: int = Field(default=30, description="Circuit breaker timeout")
    
    # Content Filtering
    FILTER_ENABLED: bool = Field(default=True, description="Enable content filtering")
    FILTER_BLACKLIST_FILE: str = Field(default="blacklist.txt", description="Blacklist file")
    FILTER_ML_MODEL_PATH: str = Field(default="models/content_filter_model.pkl", description="ML model path")
    FILTER_CONFIDENCE_THRESHOLD: float = Field(default=0.7, description="ML confidence threshold")
    
    # Blacklist Categories
    BLOCK_EXTREMISM: bool = Field(default=True, description="Block extremism")
    BLOCK_TERRORISM: bool = Field(default=True, description="Block terrorism")
    BLOCK_PROPAGANDA: bool = Field(default=True, description="Block propaganda")
    BLOCK_ADULT_CONTENT: bool = Field(default=False, description="Block adult content")
    
    # Providers
    GOOGLE_ENABLED: bool = Field(default=True, description="Enable Google provider")
    GOOGLE_API_KEY: Optional[str] = Field(default=None, description="Google API key")
    GOOGLE_CX: Optional[str] = Field(default=None, description="Google Custom Search CX")
    
    DUCKDUCKGO_ENABLED: bool = Field(default=True, description="Enable DuckDuckGo provider")
    BRAVE_ENABLED: bool = Field(default=True, description="Enable Brave provider")
    BRAVE_API_KEY: Optional[str] = Field(default=None, description="Brave API key")
    
    YANDEX_ENABLED: bool = Field(default=True, description="Enable Yandex provider")
    YANDEX_API_KEY: Optional[str] = Field(default=None, description="Yandex API key")
    
    DZEN_ENABLED: bool = Field(default=True, description="Enable Dzen provider")
    REDDIT_ENABLED: bool = Field(default=True, description="Enable Reddit provider")
    
    # Provider Timeouts
    PROVIDER_TIMEOUT_DEFAULT: int = Field(default=10, description="Default provider timeout")
    PROVIDER_TIMEOUT_GOOGLE: int = Field(default=15, description="Google provider timeout")
    PROVIDER_TIMEOUT_DUCKDUCKGO: int = Field(default=10, description="DuckDuckGo provider timeout")
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = Field(default=True, description="Enable Prometheus")
    PROMETHEUS_PORT: int = Field(default=9090, description="Prometheus port")
    
    # Sentry
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=0.1, description="Sentry traces sample rate")
    
    # Security
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:8080", description="Allowed CORS origins")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow CORS credentials")
    
    # P2P Node
    P2P_NODE_ENABLED: bool = Field(default=False, description="Enable P2P node")
    P2P_NODE_PORT: int = Field(default=8081, description="P2P node port")
    P2P_BOOTSTRAP_NODES: Optional[str] = Field(default=None, description="P2P bootstrap nodes")
    
    # Tokenomics
    TOKEN_CONTRACT_ADDRESS: str = Field(default="0x0000000000000000000000000000000000000000", description="Token contract address")
    TOKEN_DECIMALS: int = Field(default=18, description="Token decimals")
    MINIMUM_TOKEN_BALANCE: float = Field(default=1, description="Minimum token balance")
    
    # Payment
    PAY_PER_SEARCH_AMOUNT: float = Field(default=0.01, description="Pay per search amount")
    SUBSCRIPTION_NFT_ADDRESS: str = Field(default="0x0000000000000000000000000000000000000000", description="Subscription NFT address")
    
    # Staking
    STAKING_CONTRACT_ADDRESS: str = Field(default="0x0000000000000000000000000000000000000000", description="Staking contract address")
    STAKING_REWARD_RATE: float = Field(default=0.05, description="Staking reward rate")
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins as list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def datacenter_proxies_list(self) -> List[str]:
        """Parse datacenter proxies as list"""
        if not self.DATACENTER_PROXIES:
            return []
        return [proxy.strip() for proxy in self.DATACENTER_PROXIES.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
