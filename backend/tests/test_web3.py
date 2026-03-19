"""
Tests for Web3 authentication
"""
import pytest
from web3 import Web3
from eth_account.messages import encode_defunct
from web3.signature import SignatureVerifier
from web3.jwt_manager import TokenManager


@pytest.fixture
def verifier():
    """Create signature verifier"""
    return SignatureVerifier()


@pytest.fixture
def token_manager():
    """Create token manager"""
    return TokenManager()


def test_generate_message(verifier):
    """Test auth message generation"""
    address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    message = verifier.generate_message(address)
    
    assert address in message
    assert "NEXUS Search" in message
    assert "Timestamp:" in message


def test_generate_message_with_nonce(verifier):
    """Test auth message with nonce"""
    address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    nonce = "test-nonce-123"
    message = verifier.generate_message(address, nonce)
    
    assert nonce in message


def test_parse_message(verifier):
    """Test message parsing"""
    address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    message = verifier.generate_message(address)
    
    parsed = verifier.parse_message(message)
    
    assert parsed["address"] == address
    assert parsed["timestamp"] is not None


def test_create_token(token_manager):
    """Test JWT token creation"""
    address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    
    access_token = token_manager.create_token(address, token_type="access")
    refresh_token = token_manager.create_token(address, token_type="refresh")
    
    assert access_token is not None
    assert refresh_token is not None
    assert access_token != refresh_token


def test_decode_token(token_manager):
    """Test JWT token decoding"""
    address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    token = token_manager.create_token(address)
    
    payload = token_manager.decode_token(token)
    
    assert payload["sub"] == address.lower()
    assert payload["address"] == address
    assert payload["type"] == "access"


def test_get_token_info(token_manager):
    """Test token info retrieval"""
    address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    token = token_manager.create_token(address)
    
    info = token_manager.get_token_info(token)
    
    assert info["address"] == address
    assert info["type"] == "access"
    assert "expires" in info
