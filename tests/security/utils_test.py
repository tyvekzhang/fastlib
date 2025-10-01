import base64
import json
import time

import pytest

# Import the module under test
from fastlib.config.manager import ConfigManager
ConfigManager.initialize_global_config()
from fastlib.security.utils import (
    SymmetricEncryption,
    Ed25519Signer,
    HMACSigner,
    RSASigner,
    hash_password,
    verify_password,
    generate_random_key,
    encrypt_data,
    decrypt_data,
)


class TestSymmetricEncryption:
    """Test symmetric encryption functionality"""
    
    def test_encrypt_decrypt_with_generated_key(self):
        """Test encryption and decryption with auto-generated key"""
        encryptor = SymmetricEncryption()
        secret_message = "This is highly confidential information"

        encrypted = encryptor.encrypt_string(secret_message)
        decrypted = encryptor.decrypt_string(encrypted)

        assert decrypted == secret_message

    def test_encrypt_decrypt_with_password(self):
        """Test encryption and decryption with password-derived key"""
        password = "my_secure_password"
        encryptor = SymmetricEncryption.from_password(password)

        user_data = "User sensitive data: ID number, bank card, etc."
        encrypted_data = encryptor.encrypt_string(user_data)
        decrypted_data = encryptor.decrypt_string(encrypted_data)

        assert decrypted_data == user_data

    def test_encrypt_decrypt_with_existing_key(self):
        """Test encryption and decryption with existing key"""
        encryptor1 = SymmetricEncryption()
        existing_key = encryptor1.get_key()
        encryptor2 = SymmetricEncryption(existing_key)

        test_message = "Test message"
        encrypted_test = encryptor2.encrypt_string(test_message)
        decrypted_test = encryptor2.decrypt_string(encrypted_test)

        assert decrypted_test == test_message

    def test_different_keys_produce_different_results(self):
        """Test that different keys produce different encryption results"""
        encryptor1 = SymmetricEncryption()
        encryptor2 = SymmetricEncryption()

        message = "Same message"
        encrypted1 = encryptor1.encrypt_string(message)
        encrypted2 = encryptor2.encrypt_string(message)

        assert encrypted1 != encrypted2


class TestEd25519Signing:
    """Test Ed25519 signing functionality"""
    
    def setup_method(self):
        """Setup before each test method"""
        self.private_key, self.public_key = Ed25519Signer.generate_keypair()
        self.signer = Ed25519Signer(private_key=self.private_key)
        self.verifier = Ed25519Signer(public_key=self.public_key)
        self.message = "Important transaction data: Transfer 1000 yuan"

    def test_sign_verify(self):
        """Test basic signing and verification"""
        signature = self.signer.sign(self.message)
        is_valid = self.verifier.verify(self.message, signature)

        assert is_valid is True

    def test_tamper_detection(self):
        """Test tamper detection"""
        signature = self.signer.sign(self.message)
        tampered_message = "Important transaction data: Transfer 10000 yuan"
        is_tampered_valid = self.verifier.verify(tampered_message, signature)

        assert is_tampered_valid is False

    def test_key_bytes_serialization(self):
        """Test key byte serialization"""
        private_key_bytes = self.signer.get_private_key_bytes()

        # Rebuild signer from bytes
        signer_from_bytes = Ed25519Signer.from_private_key_bytes(private_key_bytes)
        same_signature = signer_from_bytes.sign(self.message)
        original_signature = self.signer.sign(self.message)

        assert same_signature == original_signature


class TestHMACSigning:
    """Test HMAC signing functionality"""
    
    def setup_method(self):
        """Setup before each test method"""
        self.api_secret = "my_api_secret_key"
        self.hmac_signer = HMACSigner(self.api_secret)
        self.api_data = {
            "user_id": 12345,
            "action": "transfer",
            "amount": 100.0,
            "timestamp": "2024-01-01T10:00:00Z",
        }

    def test_sign_verify_data(self):
        """Test data signing and verification"""
        signature = self.hmac_signer.sign_data(self.api_data)
        is_valid = self.hmac_signer.verify_data(self.api_data, signature)

        assert is_valid is True

    def test_tamper_detection(self):
        """Test data tamper detection"""
        signature = self.hmac_signer.sign_data(self.api_data)
        tampered_data = self.api_data.copy()
        tampered_data["amount"] = 1000.0
        is_tampered_valid = self.hmac_signer.verify_data(tampered_data, signature)

        assert is_tampered_valid is False

    def test_different_algorithms(self):
        """Test different hash algorithms"""
        hmac_sha512 = HMACSigner(self.api_secret, algorithm="sha512")
        sha512_signature = hmac_sha512.sign_data(self.api_data)
        
        # Verify SHA512 signature can also be correctly verified
        assert hmac_sha512.verify_data(self.api_data, sha512_signature) is True


class TestRSASigning:
    """Test RSA signing functionality"""
    
    def test_sign_verify(self):
        """Test RSA signing and verification"""
        private_key, public_key = RSASigner.generate_keypair(key_size=2048)
        rsa_signer = RSASigner(private_key=private_key)
        rsa_verifier = RSASigner(public_key=public_key)

        document = "Important document: Cooperation agreement"
        signature = rsa_signer.sign(document)
        is_valid = rsa_verifier.verify(document, signature)

        assert is_valid is True


class TestPasswordHashing:
    """Test password hashing functionality"""
    
    def test_hash_verify_password(self):
        """Test password hashing and verification"""
        user_password = "my_secure_password_123"
        hashed_password, salt = hash_password(user_password)

        # Correct password verification
        is_correct = verify_password("my_secure_password_123", hashed_password, salt)
        assert is_correct is True

        # Wrong password verification
        is_wrong = verify_password("wrong_password", hashed_password, salt)
        assert is_wrong is False


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_generate_random_key(self):
        """Test generating random key"""
        random_key = generate_random_key(44)
        
        # Ensure two generated keys are different
        another_key = generate_random_key(44)
        assert random_key != another_key

    def test_encrypt_decrypt_data(self):
        """Test quick encryption and decryption of data"""
        sensitive_data = "Sensitive data that needs quick encryption"
        encrypted, key_used = encrypt_data(sensitive_data)
        decrypted = decrypt_data(encrypted, key_used)

        assert decrypted == sensitive_data.encode('utf-8')


class TestPerformance:
    """Performance testing"""
    
    def test_ed25519_performance(self):
        """Test Ed25519 performance"""
        message = "This is a test message for performance comparison" * 10
        
        ed_private, ed_public = Ed25519Signer.generate_keypair()
        ed_signer = Ed25519Signer(private_key=ed_private)
        ed_verifier = Ed25519Signer(public_key=ed_public)

        start_time = time.time()
        ed_signature = ed_signer.sign(message)
        ed_sign_time = time.time() - start_time

        start_time = time.time()
        ed_valid = ed_verifier.verify(message, ed_signature)
        ed_verify_time = time.time() - start_time

        # Performance assertions - signing and verification should complete in reasonable time
        assert ed_sign_time < 1.0  # Complete signing within 1 second
        assert ed_verify_time < 1.0  # Complete verification within 1 second
        assert ed_valid is True

    def test_hmac_performance(self):
        """Test HMAC performance"""
        message = "This is a test message for performance comparison" * 10
        hmac_signer = HMACSigner("test_secret_key")

        start_time = time.time()
        hmac_signature = hmac_signer.sign(message)
        hmac_sign_time = time.time() - start_time

        start_time = time.time()
        hmac_valid = hmac_signer.verify(message, hmac_signature)
        hmac_verify_time = time.time() - start_time

        assert hmac_sign_time < 1.0
        assert hmac_verify_time < 1.0
        assert hmac_valid is True


# Parameterized test examples
class TestParameterized:
    """Parameterized testing"""
    
    @pytest.mark.parametrize("password,expected_length", [
        ("short", 44),
        ("very_long_password_that_exceeds_normal_length", 44),
        ("123456", 44),
        ("special_chars!@#$%^&*()", 44),
    ])
    def test_password_based_encryption_various_passwords(self, password, expected_length):
        """Test encryption with different passwords"""
        encryptor = SymmetricEncryption.from_password(password)
        key = encryptor.get_key()
        assert len(key) == expected_length

    @pytest.mark.parametrize("message", [
        "",
        "a",
        "hello world",
        "Chinese message",
        "a" * 1000,  # Long message
        "🍎🐍",  # Special characters
    ])
    def test_encrypt_decrypt_various_messages(self, message):
        """Test encryption and decryption of various messages"""
        encryptor = SymmetricEncryption()
        encrypted = encryptor.encrypt_string(message)
        decrypted = encryptor.decrypt_string(encrypted)
        assert decrypted == message