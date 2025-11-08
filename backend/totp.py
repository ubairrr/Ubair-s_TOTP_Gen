import hmac
import hashlib
import struct
import base64
import time
from typing import Optional

class TOTP:
    """
    TOTP (Time-based One-Time Password) implementation based on RFC 6238
    """
    
    def __init__(
        self,
        secret: str,
        time_step: int = 30,
        t0: int = 0,
        digits: int = 6,
        algorithm: str = 'sha1'
    ):
        """
        Initialize TOTP generator
        
        Args:
            secret: Base32 encoded secret key
            time_step: Time step in seconds (default: 30)
            t0: Unix time to start counting time steps (default: 0)
            digits: Number of digits in OTP (default: 6)
            algorithm: Hash algorithm - 'sha1', 'sha256', or 'sha512' (default: 'sha1')
        """
        self.secret = secret
        self.time_step = time_step
        self.t0 = t0
        self.digits = digits
        self.algorithm = algorithm
        
        # Map algorithm names to hashlib functions
        self.algorithm_map = {
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512
        }
        
        if algorithm not in self.algorithm_map:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    def _decode_secret(self) -> bytes:
        """Decode base32 secret key"""
        try:
            # Add padding if necessary
            secret = self.secret
            missing_padding = len(secret) % 8
            if missing_padding:
                secret += '=' * (8 - missing_padding)
            return base64.b32decode(secret.upper())
        except Exception as e:
            raise ValueError(f"Invalid secret key: {e}")
    
    def _get_time_counter(self, timestamp: Optional[int] = None) -> int:
        """
        Calculate time counter (T) value
        
        Args:
            timestamp: Unix timestamp (default: current time)
        
        Returns:
            Time counter value
        """
        if timestamp is None:
            timestamp = int(time.time())
        
        return (timestamp - self.t0) // self.time_step
    
    def _generate_hotp(self, counter: int) -> str:
        """
        Generate HOTP value for given counter
        
        Args:
            counter: Counter value
        
        Returns:
            OTP string
        """
        # Decode secret
        key = self._decode_secret()
        
        # Convert counter to bytes (8 bytes, big-endian)
        counter_bytes = struct.pack('>Q', counter)
        
        # Generate HMAC
        hash_func = self.algorithm_map[self.algorithm]
        hmac_hash = hmac.new(key, counter_bytes, hash_func).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        truncated_hash = hmac_hash[offset:offset + 4]
        
        # Convert to integer
        code = struct.unpack('>I', truncated_hash)[0]
        code = code & 0x7FFFFFFF
        
        # Generate OTP
        otp = str(code % (10 ** self.digits))
        
        # Pad with zeros if necessary
        return otp.zfill(self.digits)
    
    def generate(self, timestamp: Optional[int] = None) -> dict:
        """
        Generate TOTP code
        
        Args:
            timestamp: Unix timestamp (default: current time)
        
        Returns:
            Dictionary with OTP and metadata
        """
        if timestamp is None:
            timestamp = int(time.time())
        
        counter = self._get_time_counter(timestamp)
        otp = self._generate_hotp(counter)
        
        # Calculate remaining time
        time_remaining = self.time_step - (timestamp - self.t0) % self.time_step
        
        return {
            'otp': otp,
            'counter': counter,
            'time_remaining': time_remaining,
            'timestamp': timestamp
        }
    
    def verify(self, otp: str, timestamp: Optional[int] = None, window: int = 1) -> bool:
        """
        Verify TOTP code
        
        Args:
            otp: OTP to verify
            timestamp: Unix timestamp (default: current time)
            window: Number of time steps to check before and after current time
        
        Returns:
            True if OTP is valid, False otherwise
        """
        if timestamp is None:
            timestamp = int(time.time())
        
        current_counter = self._get_time_counter(timestamp)
        
        # Check current and adjacent time windows
        for i in range(-window, window + 1):
            counter = current_counter + i
            if self._generate_hotp(counter) == otp:
                return True
        
        return False
    
    @staticmethod
    def generate_secret(length: int = 32) -> str:
        """
        Generate a random base32 secret
        
        Args:
            length: Length of secret in bytes (default: 32)
        
        Returns:
            Base32 encoded secret
        """
        import secrets
        random_bytes = secrets.token_bytes(length)
        return base64.b32encode(random_bytes).decode('utf-8')
