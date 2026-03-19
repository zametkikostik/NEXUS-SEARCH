"""
Web3 Signature Verification
"""
import re
from typing import Optional, Tuple
from eth_account.messages import encode_defunct, recover_to_address
from eth_utils import is_address, to_checksum_address
from core.config import get_settings
from core.logging import get_logger
from core.exceptions import SignatureInvalidException, SignatureExpiredException

settings = get_settings()
logger = get_logger(__name__)


class SignatureVerifier:
    """Verify Ethereum wallet signatures"""
    
    def __init__(self):
        self.expiration_minutes = settings.SIGNATURE_EXPIRATION_MINUTES
    
    def generate_message(self, address: str, nonce: Optional[str] = None) -> str:
        """
        Generate message for wallet signature
        
        Args:
            address: Wallet address
            nonce: Optional nonce for replay protection
        
        Returns:
            Message string to sign
        """
        import time
        
        timestamp = int(time.time())
        
        message = (
            "Welcome to NEXUS Search!\n\n"
            "Click to sign in and accept the Terms of Service.\n\n"
            "This request will not trigger a blockchain transaction or cost any gas fees.\n\n"
            f"Wallet address:\n{address}\n\n"
            f"Timestamp:\n{timestamp}\n"
        )
        
        if nonce:
            message += f"\nNonce:\n{nonce}\n"
        
        return message
    
    def verify_signature(
        self,
        address: str,
        message: str,
        signature: str
    ) -> Tuple[bool, str]:
        """
        Verify wallet signature
        
        Args:
            address: Expected wallet address
            message: Original message that was signed
            signature: Signature to verify
        
        Returns:
            Tuple of (is_valid, recovered_address)
        """
        try:
            # Validate address format
            if not is_address(address):
                logger.warning("Invalid address format", address=address)
                raise SignatureInvalidException()
            
            # Normalize address
            address = to_checksum_address(address)
            
            # Validate signature format
            if not signature.startswith('0x'):
                signature = '0x' + signature
            
            if len(signature) != 132:  # 65 bytes = 130 hex chars + 0x
                logger.warning("Invalid signature length", length=len(signature))
                raise SignatureInvalidException()
            
            # Recover address from signature
            message_encoded = encode_defunct(text=message)
            recovered_address = recover_to_address(
                signable_message=message_encoded,
                signature=signature
            )
            
            if not recovered_address:
                logger.warning("Failed to recover address")
                raise SignatureInvalidException()
            
            recovered_address = to_checksum_address(recovered_address)
            
            # Compare addresses
            is_valid = recovered_address == address
            
            if not is_valid:
                logger.warning(
                    "Address mismatch",
                    expected=address,
                    recovered=recovered_address
                )
                raise SignatureInvalidException()
            
            logger.info("Signature verified", address=address)
            return True, recovered_address
            
        except (SignatureInvalidException, SignatureExpiredException):
            raise
        except Exception as e:
            logger.error("Signature verification failed", error=str(e))
            raise SignatureInvalidException()
    
    def parse_message(self, message: str) -> dict:
        """
        Parse signed message to extract data
        
        Returns:
            Dict with address, timestamp, nonce
        """
        data = {
            "address": None,
            "timestamp": None,
            "nonce": None
        }
        
        # Extract address
        address_match = re.search(
            r'Wallet address:\n(0x[a-fA-F0-9]{40})',
            message
        )
        if address_match:
            data["address"] = address_match.group(1)
        
        # Extract timestamp
        timestamp_match = re.search(
            r'Timestamp:\n(\d+)',
            message
        )
        if timestamp_match:
            data["timestamp"] = int(timestamp_match.group(1))
        
        # Extract nonce
        nonce_match = re.search(
            r'Nonce:\n(\S+)',
            message
        )
        if nonce_match:
            data["nonce"] = nonce_match.group(1)
        
        return data
    
    def is_message_expired(self, message: str) -> bool:
        """Check if message has expired"""
        import time
        
        data = self.parse_message(message)
        timestamp = data.get("timestamp")
        
        if not timestamp:
            return True
        
        elapsed_minutes = (time.time() - timestamp) / 60
        return elapsed_minutes > self.expiration_minutes


# Global verifier instance
signature_verifier = SignatureVerifier()


def get_signature_verifier() -> SignatureVerifier:
    """Get signature verifier dependency"""
    return signature_verifier
