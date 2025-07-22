"""
Klondike Archiver - Encryption Module
Provides password-based encryption for .kcl files
"""

import hashlib
import secrets
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CryptoManager:
    """
    Manages encryption and decryption for Klondike archives
    Uses Fernet (AES-128) with PBKDF2 key derivation
    """
    
    def __init__(self):
        self.salt_size = 32  # 256-bit salt
        self.iterations = 100000  # PBKDF2 iterations
    
    def derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: User-provided password
            salt: Random salt for key derivation
            
        Returns:
            32-byte encryption key
        """
        password_bytes = password.encode('utf-8')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.iterations,
        )
        return base64.urlsafe_b64encode(kdf.derive(password_bytes))
    
    def generate_salt(self) -> bytes:
        """Generate a random salt for key derivation"""
        return secrets.token_bytes(self.salt_size)
    
    def encrypt_data(self, data: bytes, password: str) -> bytes:
        """
        Encrypt data with password
        
        Args:
            data: Raw data to encrypt
            password: Encryption password
            
        Returns:
            Encrypted data with salt prepended
        """
        # Generate random salt
        salt = self.generate_salt()
        
        # Derive key from password
        key = self.derive_key(password, salt)
        
        # Create Fernet cipher
        fernet = Fernet(key)
        
        # Encrypt data
        encrypted_data = fernet.encrypt(data)
        
        # Prepend salt to encrypted data
        return salt + encrypted_data
    
    def decrypt_data(self, encrypted_data: bytes, password: str) -> bytes:
        """
        Decrypt data with password
        
        Args:
            encrypted_data: Encrypted data with salt prepended
            password: Decryption password
            
        Returns:
            Decrypted raw data
            
        Raises:
            ValueError: If decryption fails (wrong password or corrupted data)
        """
        if len(encrypted_data) < self.salt_size:
            raise ValueError("Invalid encrypted data: too short")
        
        # Extract salt and encrypted content
        salt = encrypted_data[:self.salt_size]
        ciphertext = encrypted_data[self.salt_size:]
        
        # Derive key from password and salt
        key = self.derive_key(password, salt)
        
        # Create Fernet cipher
        fernet = Fernet(key)
        
        try:
            # Decrypt data
            return fernet.decrypt(ciphertext)
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def verify_password(self, encrypted_data: bytes, password: str) -> bool:
        """
        Verify if password is correct without fully decrypting
        
        Args:
            encrypted_data: Encrypted data with salt prepended
            password: Password to verify
            
        Returns:
            True if password is correct, False otherwise
        """
        try:
            # Try to decrypt a small portion
            self.decrypt_data(encrypted_data, password)
            return True
        except ValueError:
            return False
    
    def get_encryption_info(self, encrypted_data: bytes) -> dict:
        """
        Get information about encrypted data
        
        Args:
            encrypted_data: Encrypted data with salt prepended
            
        Returns:
            Dictionary with encryption information
        """
        if len(encrypted_data) < self.salt_size:
            return {'valid': False, 'error': 'Data too short'}
        
        salt = encrypted_data[:self.salt_size]
        ciphertext = encrypted_data[self.salt_size:]
        
        return {
            'valid': True,
            'salt_size': len(salt),
            'ciphertext_size': len(ciphertext),
            'total_size': len(encrypted_data),
            'algorithm': 'Fernet (AES-128)',
            'kdf': 'PBKDF2-SHA256',
            'iterations': self.iterations
        }

class SecureArchiveHeader:
    """
    Manages secure headers for encrypted archives
    Includes metadata about encryption and integrity checks
    """
    
    def __init__(self):
        self.magic = b'KLONDIKE'
        self.version = b'SECURE01'
        self.header_size = 64  # Fixed header size
    
    def create_header(self, file_count: int, table_size: int, encryption_info: dict) -> bytes:
        """
        Create secure archive header
        
        Args:
            file_count: Number of files in archive
            table_size: Size of file table
            encryption_info: Information about encryption
            
        Returns:
            Binary header data
        """
        import struct
        
        header = bytearray(self.header_size)
        offset = 0
        
        # Magic signature
        header[offset:offset+8] = self.magic
        offset += 8
        
        # Version
        header[offset:offset+8] = self.version
        offset += 8
        
        # File count (4 bytes)
        struct.pack_into('<I', header, offset, file_count)
        offset += 4
        
        # Table size (4 bytes)
        struct.pack_into('<I', header, offset, table_size)
        offset += 4
        
        # Encryption flags (4 bytes)
        flags = 0
        if encryption_info.get('enabled', False):
            flags |= 0x01  # Encryption enabled
        if encryption_info.get('compressed', False):
            flags |= 0x02  # Data is compressed before encryption
        
        struct.pack_into('<I', header, offset, flags)
        offset += 4
        
        # Salt size (4 bytes)
        struct.pack_into('<I', header, offset, encryption_info.get('salt_size', 0))
        offset += 4
        
        # KDF iterations (4 bytes)
        struct.pack_into('<I', header, offset, encryption_info.get('iterations', 0))
        offset += 4
        
        # Reserved space for future use (remaining bytes)
        # This allows for header evolution while maintaining compatibility
        
        return bytes(header)
    
    def parse_header(self, header_data: bytes) -> dict:
        """
        Parse secure archive header
        
        Args:
            header_data: Binary header data
            
        Returns:
            Dictionary with header information
            
        Raises:
            ValueError: If header is invalid
        """
        import struct
        
        if len(header_data) < self.header_size:
            raise ValueError("Header too short")
        
        offset = 0
        
        # Check magic
        magic = header_data[offset:offset+8]
        if magic != self.magic:
            raise ValueError("Invalid magic signature")
        offset += 8
        
        # Check version
        version = header_data[offset:offset+8]
        if version != self.version:
            raise ValueError(f"Unsupported version: {version}")
        offset += 8
        
        # Parse fields
        file_count = struct.unpack('<I', header_data[offset:offset+4])[0]
        offset += 4
        
        table_size = struct.unpack('<I', header_data[offset:offset+4])[0]
        offset += 4
        
        flags = struct.unpack('<I', header_data[offset:offset+4])[0]
        offset += 4
        
        salt_size = struct.unpack('<I', header_data[offset:offset+4])[0]
        offset += 4
        
        iterations = struct.unpack('<I', header_data[offset:offset+4])[0]
        offset += 4
        
        return {
            'file_count': file_count,
            'table_size': table_size,
            'encrypted': bool(flags & 0x01),
            'compressed': bool(flags & 0x02),
            'salt_size': salt_size,
            'iterations': iterations,
            'version': version.decode('ascii', errors='ignore')
        }

class PasswordStrengthChecker:
    """
    Utility class to check password strength and provide recommendations
    """
    
    @staticmethod
    def check_strength(password: str) -> dict:
        """
        Check password strength and return analysis
        
        Args:
            password: Password to analyze
            
        Returns:
            Dictionary with strength analysis
        """
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1
        else:
            feedback.append("Use at least 8 characters (12+ recommended)")
        
        # Character variety
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        variety_score = sum([has_lower, has_upper, has_digit, has_special])
        score += variety_score
        
        if not has_lower:
            feedback.append("Add lowercase letters")
        if not has_upper:
            feedback.append("Add uppercase letters")
        if not has_digit:
            feedback.append("Add numbers")
        if not has_special:
            feedback.append("Add special characters (!@#$%^&*)")
        
        # Common patterns (basic check)
        common_patterns = ['123', 'abc', 'password', 'qwerty', '111']
        if any(pattern in password.lower() for pattern in common_patterns):
            score -= 2
            feedback.append("Avoid common patterns")
        
        # Determine strength level
        if score >= 6:
            strength = "Strong"
        elif score >= 4:
            strength = "Good"
        elif score >= 2:
            strength = "Weak"
        else:
            strength = "Very Weak"
        
        return {
            'score': max(0, score),
            'strength': strength,
            'feedback': feedback,
            'character_variety': variety_score
        }
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """
        Generate a cryptographically secure password
        
        Args:
            length: Desired password length (minimum 12)
            
        Returns:
            Generated password
        """
        import string
        
        if length < 12:
            length = 12
        
        # Character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Ensure at least one character from each set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]
        
        # Fill remaining length with random characters from all sets
        all_chars = lowercase + uppercase + digits + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)