# SPDX-License-Identifier: MIT
"""Security utility functions for encryption, decryption, signing, and verification."""

import base64
import hashlib
import hmac
import os
from typing import Optional, Union

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False


class SymmetricEncryption:
    """Symmetric encryption/decryption using Fernet (AES 128)."""
    
    def __init__(self, key: Optional[bytes] = None) -> None:
        """
        Initialize symmetric encryption with a key.
        
        Args:
            key: Encryption key. If None, generates a new key.
            
        Raises:
            ImportError: If cryptography package is not available
        """
        if not HAS_CRYPTOGRAPHY:
            raise ImportError(
                "cryptography package is required for SymmetricEncryption. "
                "Install it with: uv add cryptography"
            )
        
        if key is None:
            self._key = Fernet.generate_key()
        else:
            self._key = key
        self._fernet = Fernet(self._key)
    
    @classmethod
    def from_password(cls, password: str, salt: Optional[bytes] = None) -> "SymmetricEncryption":
        """
        Create encryption instance from password using PBKDF2.
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation. If None, generates random salt.
            
        Returns:
            SymmetricEncryption instance
            
        Raises:
            ImportError: If cryptography package is not available
        """
        if not HAS_CRYPTOGRAPHY:
            raise ImportError(
                "cryptography package is required for SymmetricEncryption. "
                "Install it with: uv add cryptography"
            )
        
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return cls(key)
    
    def get_key(self) -> bytes:
        """Get the encryption key."""
        return self._key
    
    def encrypt(self, plaintext: Union[str, bytes]) -> bytes:
        """
        Encrypt plaintext data.
        
        Args:
            plaintext: Data to encrypt
            
        Returns:
            Encrypted data
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        return self._fernet.encrypt(plaintext)
    
    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypt ciphertext data.
        
        Args:
            ciphertext: Encrypted data to decrypt
            
        Returns:
            Decrypted data
            
        Raises:
            InvalidToken: If decryption fails
        """
        return self._fernet.decrypt(ciphertext)
    
    def encrypt_string(self, plaintext: str) -> str:
        """
        Encrypt string and return base64 encoded result.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Base64 encoded encrypted string
        """
        encrypted = self.encrypt(plaintext)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_string(self, ciphertext: str) -> str:
        """
        Decrypt base64 encoded string.
        
        Args:
            ciphertext: Base64 encoded encrypted string
            
        Returns:
            Decrypted string
        """
        encrypted_bytes = base64.b64decode(ciphertext.encode('utf-8'))
        decrypted = self.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')


class SimpleSymmetricEncryption:
    """Simple symmetric encryption using XOR and HMAC (when cryptography is not available)."""
    
    def __init__(self, key: Optional[bytes] = None) -> None:
        """
        Initialize simple symmetric encryption with a key.
        
        Args:
            key: Encryption key. If None, generates a new key.
        """
        if key is None:
            self._key = os.urandom(32)
        else:
            self._key = key[:32] if len(key) > 32 else key.ljust(32, b'\x00')
    
    def get_key(self) -> bytes:
        """Get the encryption key."""
        return self._key
    
    def _xor_encrypt_decrypt(self, data: bytes) -> bytes:
        """XOR encryption/decryption."""
        key_len = len(self._key)
        return bytes(data[i] ^ self._key[i % key_len] for i in range(len(data)))
    
    def encrypt(self, plaintext: Union[str, bytes]) -> bytes:
        """
        Encrypt plaintext data using XOR + HMAC.
        
        Args:
            plaintext: Data to encrypt
            
        Returns:
            Encrypted data with HMAC
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        # Add random IV
        iv = os.urandom(16)
        
        # XOR encrypt
        encrypted = self._xor_encrypt_decrypt(plaintext)
        
        # Create HMAC for integrity
        mac = hmac.new(self._key, iv + encrypted, hashlib.sha256).digest()
        
        return iv + mac + encrypted
    
    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypt ciphertext data.
        
        Args:
            ciphertext: Encrypted data to decrypt
            
        Returns:
            Decrypted data
            
        Raises:
            ValueError: If decryption fails or HMAC verification fails
        """
        if len(ciphertext) < 48:  # 16 (IV) + 32 (HMAC) = 48 minimum
            raise ValueError("Invalid ciphertext length")
        
        iv = ciphertext[:16]
        mac = ciphertext[16:48]
        encrypted = ciphertext[48:]
        
        # Verify HMAC
        expected_mac = hmac.new(self._key, iv + encrypted, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, expected_mac):
            raise ValueError("HMAC verification failed")
        
        # XOR decrypt
        return self._xor_encrypt_decrypt(encrypted)
    
    def encrypt_string(self, plaintext: str) -> str:
        """
        Encrypt string and return base64 encoded result.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Base64 encoded encrypted string
        """
        encrypted = self.encrypt(plaintext)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_string(self, ciphertext: str) -> str:
        """
        Decrypt base64 encoded string.
        
        Args:
            ciphertext: Base64 encoded encrypted string
            
        Returns:
            Decrypted string
        """
        encrypted_bytes = base64.b64decode(ciphertext.encode('utf-8'))
        decrypted = self.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')


class HMACSigner:
    """HMAC-based message signing and verification."""
    
    def __init__(self, secret_key: Union[str, bytes], algorithm: str = "sha256") -> None:
        """
        Initialize HMAC signer.
        
        Args:
            secret_key: Secret key for signing
            algorithm: Hash algorithm (sha256, sha384, sha512)
        """
        if isinstance(secret_key, str):
            secret_key = secret_key.encode('utf-8')
        self._secret_key = secret_key
        
        algorithm_map = {
            "sha256": hashlib.sha256,
            "sha384": hashlib.sha384,
            "sha512": hashlib.sha512,
        }
        
        if algorithm not in algorithm_map:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        self._hash_func = algorithm_map[algorithm]
    
    def sign(self, message: Union[str, bytes]) -> str:
        """
        Create HMAC signature for message.
        
        Args:
            message: Message to sign
            
        Returns:
            Base64 encoded signature
        """
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        signature = hmac.new(
            self._secret_key,
            message,
            self._hash_func
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
    
    def verify(self, message: Union[str, bytes], signature: str) -> bool:
        """
        Verify HMAC signature.
        
        Args:
            message: Original message
            signature: Base64 encoded signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            expected_signature = self.sign(message)
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False
    
    def sign_data(self, data: dict) -> str:
        """
        Sign dictionary data by converting to sorted string representation.
        
        Args:
            data: Dictionary to sign
            
        Returns:
            Base64 encoded signature
        """
        # Sort keys for consistent signing
        sorted_items = sorted(data.items())
        message = '&'.join([f"{k}={v}" for k, v in sorted_items])
        return self.sign(message)
    
    def verify_data(self, data: dict, signature: str) -> bool:
        """
        Verify signature of dictionary data.
        
        Args:
            data: Dictionary data
            signature: Signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        return self.verify(
            '&'.join([f"{k}={v}" for k, v in sorted(data.items())]),
            signature
        )


class RSASigner:
    """RSA-based digital signing and verification."""
    
    def __init__(self, private_key: Optional[bytes] = None, public_key: Optional[bytes] = None) -> None:
        """
        Initialize RSA signer.
        
        Args:
            private_key: PEM encoded private key for signing
            public_key: PEM encoded public key for verification
            
        Raises:
            ImportError: If cryptography package is not available
        """
        if not HAS_CRYPTOGRAPHY:
            raise ImportError(
                "cryptography package is required for RSASigner. "
                "Install it with: uv add cryptography"
            )
        
        self._private_key = None
        self._public_key = None
        
        if private_key:
            self._private_key = serialization.load_pem_private_key(
                private_key, password=None
            )
        
        if public_key:
            self._public_key = serialization.load_pem_public_key(public_key)
    
    @classmethod
    def generate_keypair(cls, key_size: int = 2048) -> tuple[bytes, bytes]:
        """
        Generate RSA key pair.
        
        Args:
            key_size: Size of the key in bits
            
        Returns:
            Tuple of (private_key_pem, public_key_pem)
            
        Raises:
            ImportError: If cryptography package is not available
        """
        if not HAS_CRYPTOGRAPHY:
            raise ImportError(
                "cryptography package is required for RSASigner. "
                "Install it with: uv add cryptography"
            )
        
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    def sign(self, message: Union[str, bytes]) -> str:
        """
        Create RSA signature for message.
        
        Args:
            message: Message to sign
            
        Returns:
            Base64 encoded signature
            
        Raises:
            ValueError: If private key is not available
        """
        if not self._private_key:
            raise ValueError("Private key required for signing")
        
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        signature = self._private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode('utf-8')
    
    def verify(self, message: Union[str, bytes], signature: str) -> bool:
        """
        Verify RSA signature.
        
        Args:
            message: Original message
            signature: Base64 encoded signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self._public_key:
            return False
        
        try:
            if isinstance(message, str):
                message = message.encode('utf-8')
            
            signature_bytes = base64.b64decode(signature.encode('utf-8'))
            
            self._public_key.verify(
                signature_bytes,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False


def generate_random_key(length: int = 32) -> str:
    """
    Generate a random key for symmetric encryption.
    
    Args:
        length: Length of the key in bytes
        
    Returns:
        Base64 encoded random key
    """
    return base64.b64encode(os.urandom(length)).decode('utf-8')


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    Hash password using PBKDF2 with SHA256.
    
    Args:
        password: Password to hash
        salt: Salt for hashing. If None, generates random salt.
        
    Returns:
        Tuple of (hashed_password, salt)
    """
    if salt is None:
        salt = base64.b64encode(os.urandom(16)).decode('utf-8')
    else:
        # Ensure salt is properly encoded as string
        if isinstance(salt, bytes):
            salt = base64.b64encode(salt).decode('utf-8')
    
    salt_bytes = base64.b64decode(salt.encode('utf-8'))
    
    if HAS_CRYPTOGRAPHY:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=100000,
        )
        hashed = kdf.derive(password.encode('utf-8'))
    else:
        # Fallback to standard library hashlib.pbkdf2_hmac
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt_bytes,
            100000
        )
    
    hashed_b64 = base64.b64encode(hashed).decode('utf-8')
    
    return hashed_b64, salt


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        password: Password to verify
        hashed_password: Base64 encoded hashed password
        salt: Base64 encoded salt
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        hashed, _ = hash_password(password, salt)
        return hmac.compare_digest(hashed, hashed_password)
    except Exception:
        return False


def create_symmetric_encryption(key: Optional[bytes] = None) -> Union[SymmetricEncryption, SimpleSymmetricEncryption]:
    """
    Create a symmetric encryption instance using the best available method.
    
    Args:
        key: Encryption key. If None, generates a new key.
        
    Returns:
        SymmetricEncryption if cryptography is available, SimpleSymmetricEncryption otherwise
    """
    if HAS_CRYPTOGRAPHY:
        return SymmetricEncryption(key)
    else:
        return SimpleSymmetricEncryption(key)


def encrypt_data(data: Union[str, bytes], key: Optional[bytes] = None) -> tuple[bytes, bytes]:
    """
    Encrypt data using the best available symmetric encryption.
    
    Args:
        data: Data to encrypt
        key: Encryption key. If None, generates a new key.
        
    Returns:
        Tuple of (encrypted_data, key_used)
    """
    encryptor = create_symmetric_encryption(key)
    encrypted = encryptor.encrypt(data)
    return encrypted, encryptor.get_key()


def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """
    Decrypt data using the best available symmetric encryption.
    
    Args:
        encrypted_data: Encrypted data
        key: Decryption key
        
    Returns:
        Decrypted data
    """
    encryptor = create_symmetric_encryption(key)
    return encryptor.decrypt(encrypted_data)