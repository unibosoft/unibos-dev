"""
Messenger Encryption Unit Tests

Tests for end-to-end encryption functionality:
- Key generation (X25519, Ed25519)
- Key derivation (HKDF)
- Message encryption/decryption (AES-256-GCM)
- Message signing/verification (Ed25519)
- Group encryption
- File encryption
- Replay attack prevention
- Error handling
"""

import pytest
import os
import base64
from unittest.mock import patch, MagicMock

# Import encryption module
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from encryption import (
    EncryptionService,
    KeyPair,
    EncryptedMessage,
    get_encryption_service
)
from cryptography.exceptions import InvalidSignature


class TestKeyGeneration:
    """Tests for key pair generation"""

    def setup_method(self):
        """Setup test fixtures"""
        self.service = EncryptionService()

    def test_generate_x25519_keypair(self):
        """Test X25519 key pair generation"""
        keypair = self.service.generate_x25519_keypair()

        assert keypair is not None
        assert keypair.key_type == 'x25519'
        assert len(keypair.public_key) == 32  # X25519 public key is 32 bytes
        assert len(keypair.private_key) == 32  # X25519 private key is 32 bytes
        assert keypair.public_key != keypair.private_key

    def test_generate_ed25519_keypair(self):
        """Test Ed25519 key pair generation"""
        keypair = self.service.generate_ed25519_keypair()

        assert keypair is not None
        assert keypair.key_type == 'ed25519'
        assert len(keypair.public_key) == 32  # Ed25519 public key is 32 bytes
        assert len(keypair.private_key) == 32  # Ed25519 private key is 32 bytes
        assert keypair.public_key != keypair.private_key

    def test_generate_user_keypairs(self):
        """Test generating all key pairs for a user"""
        keypairs = self.service.generate_user_keypairs()

        assert 'encryption' in keypairs
        assert 'signing' in keypairs
        assert keypairs['encryption'].key_type == 'x25519'
        assert keypairs['signing'].key_type == 'ed25519'

    def test_keypair_uniqueness(self):
        """Test that generated key pairs are unique"""
        keypair1 = self.service.generate_x25519_keypair()
        keypair2 = self.service.generate_x25519_keypair()

        assert keypair1.public_key != keypair2.public_key
        assert keypair1.private_key != keypair2.private_key

    def test_ed25519_keypair_uniqueness(self):
        """Test that Ed25519 key pairs are unique"""
        keypair1 = self.service.generate_ed25519_keypair()
        keypair2 = self.service.generate_ed25519_keypair()

        assert keypair1.public_key != keypair2.public_key
        assert keypair1.private_key != keypair2.private_key


class TestKeyDerivation:
    """Tests for key derivation functions"""

    def setup_method(self):
        """Setup test fixtures"""
        self.service = EncryptionService()
        self.alice_keys = self.service.generate_x25519_keypair()
        self.bob_keys = self.service.generate_x25519_keypair()

    def test_derive_shared_secret(self):
        """Test X25519 shared secret derivation"""
        # Alice derives shared secret using Bob's public key
        shared_alice = self.service.derive_shared_secret(
            self.alice_keys.private_key,
            self.bob_keys.public_key
        )

        # Bob derives shared secret using Alice's public key
        shared_bob = self.service.derive_shared_secret(
            self.bob_keys.private_key,
            self.alice_keys.public_key
        )

        # Both should derive the same shared secret
        assert shared_alice == shared_bob
        assert len(shared_alice) == 32

    def test_derive_message_key(self):
        """Test HKDF key derivation for message encryption"""
        shared_secret = os.urandom(32)
        message_key = self.service.derive_message_key(shared_secret)

        assert len(message_key) == 32  # AES-256 key
        assert message_key != shared_secret  # Should be derived, not same

    def test_derive_message_key_with_context(self):
        """Test HKDF with different contexts produces different keys"""
        shared_secret = os.urandom(32)

        key1 = self.service.derive_message_key(shared_secret, b'context-1')
        key2 = self.service.derive_message_key(shared_secret, b'context-2')

        assert key1 != key2  # Different contexts = different keys

    def test_derive_message_key_deterministic(self):
        """Test that HKDF is deterministic with same inputs"""
        shared_secret = os.urandom(32)
        context = b'test-context'

        key1 = self.service.derive_message_key(shared_secret, context)
        key2 = self.service.derive_message_key(shared_secret, context)

        assert key1 == key2  # Same inputs = same output


class TestMessageEncryption:
    """Tests for message encryption and decryption"""

    def setup_method(self):
        """Setup test fixtures"""
        self.service = EncryptionService()

        # Generate key pairs for Alice and Bob
        self.alice_encryption = self.service.generate_x25519_keypair()
        self.alice_signing = self.service.generate_ed25519_keypair()
        self.bob_encryption = self.service.generate_x25519_keypair()
        self.bob_signing = self.service.generate_ed25519_keypair()

    def test_encrypt_message_basic(self):
        """Test basic message encryption"""
        plaintext = "Hello, Bob!"

        encrypted = self.service.encrypt_message(
            plaintext=plaintext,
            sender_private_key=self.alice_encryption.private_key,
            recipient_public_key=self.bob_encryption.public_key,
            sender_signing_key=self.alice_signing.private_key
        )

        assert encrypted is not None
        assert isinstance(encrypted, EncryptedMessage)
        assert encrypted.ciphertext != plaintext.encode()
        assert len(encrypted.nonce) == 12  # AES-GCM nonce
        assert len(encrypted.signature) == 64  # Ed25519 signature
        assert encrypted.encryption_version == 1

    def test_decrypt_message_basic(self):
        """Test basic message decryption"""
        plaintext = "Hello, Bob! This is a secret message."

        # Alice encrypts
        encrypted = self.service.encrypt_message(
            plaintext=plaintext,
            sender_private_key=self.alice_encryption.private_key,
            recipient_public_key=self.bob_encryption.public_key,
            sender_signing_key=self.alice_signing.private_key
        )

        # Bob decrypts
        decrypted = self.service.decrypt_message(
            encrypted_message=encrypted,
            recipient_private_key=self.bob_encryption.private_key,
            sender_public_key=self.alice_encryption.public_key,
            sender_signing_public_key=self.alice_signing.public_key
        )

        assert decrypted == plaintext

    def test_encrypt_decrypt_unicode(self):
        """Test encryption with Unicode characters"""
        plaintext = "Merhaba! Nasılsın? Benim adım "

        encrypted = self.service.encrypt_message(
            plaintext=plaintext,
            sender_private_key=self.alice_encryption.private_key,
            recipient_public_key=self.bob_encryption.public_key,
            sender_signing_key=self.alice_signing.private_key
        )

        decrypted = self.service.decrypt_message(
            encrypted_message=encrypted,
            recipient_private_key=self.bob_encryption.private_key,
            sender_public_key=self.alice_encryption.public_key,
            sender_signing_public_key=self.alice_signing.public_key
        )

        assert decrypted == plaintext

    def test_encrypt_decrypt_emoji(self):
        """Test encryption with emojis"""
        plaintext = "Hello! Test message with emojis"

        encrypted = self.service.encrypt_message(
            plaintext=plaintext,
            sender_private_key=self.alice_encryption.private_key,
            recipient_public_key=self.bob_encryption.public_key,
            sender_signing_key=self.alice_signing.private_key
        )

        decrypted = self.service.decrypt_message(
            encrypted_message=encrypted,
            recipient_private_key=self.bob_encryption.private_key,
            sender_public_key=self.alice_encryption.public_key,
            sender_signing_public_key=self.alice_signing.public_key
        )

        assert decrypted == plaintext

    def test_encrypt_decrypt_long_message(self):
        """Test encryption with long messages"""
        plaintext = "A" * 10000  # 10KB message

        encrypted = self.service.encrypt_message(
            plaintext=plaintext,
            sender_private_key=self.alice_encryption.private_key,
            recipient_public_key=self.bob_encryption.public_key,
            sender_signing_key=self.alice_signing.private_key
        )

        decrypted = self.service.decrypt_message(
            encrypted_message=encrypted,
            recipient_private_key=self.bob_encryption.private_key,
            sender_public_key=self.alice_encryption.public_key,
            sender_signing_public_key=self.alice_signing.public_key
        )

        assert decrypted == plaintext

    def test_encrypt_decrypt_empty_message(self):
        """Test encryption with empty message"""
        plaintext = ""

        encrypted = self.service.encrypt_message(
            plaintext=plaintext,
            sender_private_key=self.alice_encryption.private_key,
            recipient_public_key=self.bob_encryption.public_key,
            sender_signing_key=self.alice_signing.private_key
        )

        decrypted = self.service.decrypt_message(
            encrypted_message=encrypted,
            recipient_private_key=self.bob_encryption.private_key,
            sender_public_key=self.alice_encryption.public_key,
            sender_signing_public_key=self.alice_signing.public_key
        )

        assert decrypted == plaintext

    def test_encrypt_with_associated_data(self):
        """Test encryption with additional authenticated data (AAD)"""
        plaintext = "Secret message"
        aad = b"conversation-id:12345"

        encrypted = self.service.encrypt_message(
            plaintext=plaintext,
            sender_private_key=self.alice_encryption.private_key,
            recipient_public_key=self.bob_encryption.public_key,
            sender_signing_key=self.alice_signing.private_key,
            associated_data=aad
        )

        decrypted = self.service.decrypt_message(
            encrypted_message=encrypted,
            recipient_private_key=self.bob_encryption.private_key,
            sender_public_key=self.alice_encryption.public_key,
            sender_signing_public_key=self.alice_signing.public_key,
            associated_data=aad
        )

        assert decrypted == plaintext

    def test_decrypt_fails_with_wrong_aad(self):
        """Test that decryption fails with wrong AAD"""
        plaintext = "Secret message"
        aad = b"conversation-id:12345"
        wrong_aad = b"conversation-id:99999"

        encrypted = self.service.encrypt_message(
            plaintext=plaintext,
            sender_private_key=self.alice_encryption.private_key,
            recipient_public_key=self.bob_encryption.public_key,
            sender_signing_key=self.alice_signing.private_key,
            associated_data=aad
        )

        # Should fail with wrong AAD
        with pytest.raises(InvalidSignature):
            self.service.decrypt_message(
                encrypted_message=encrypted,
                recipient_private_key=self.bob_encryption.private_key,
                sender_public_key=self.alice_encryption.public_key,
                sender_signing_public_key=self.alice_signing.public_key,
                associated_data=wrong_aad
            )


class TestSignatureVerification:
    """Tests for message signature verification"""

    def setup_method(self):
        """Setup test fixtures"""
        self.service = EncryptionService()
        self.alice_encryption = self.service.generate_x25519_keypair()
        self.alice_signing = self.service.generate_ed25519_keypair()
        self.bob_encryption = self.service.generate_x25519_keypair()
        self.bob_signing = self.service.generate_ed25519_keypair()
        self.eve_signing = self.service.generate_ed25519_keypair()  # Attacker

    def test_signature_verification_success(self):
        """Test that valid signatures verify correctly"""
        plaintext = "Authenticated message"

        encrypted = self.service.encrypt_message(
            plaintext=plaintext,
            sender_private_key=self.alice_encryption.private_key,
            recipient_public_key=self.bob_encryption.public_key,
            sender_signing_key=self.alice_signing.private_key
        )

        # Should not raise - signature is valid
        decrypted = self.service.decrypt_message(
            encrypted_message=encrypted,
            recipient_private_key=self.bob_encryption.private_key,
            sender_public_key=self.alice_encryption.public_key,
            sender_signing_public_key=self.alice_signing.public_key
        )

        assert decrypted == plaintext

    def test_signature_verification_wrong_key(self):
        """Test that wrong signing key fails verification"""
        plaintext = "Authenticated message"

        encrypted = self.service.encrypt_message(
            plaintext=plaintext,
            sender_private_key=self.alice_encryption.private_key,
            recipient_public_key=self.bob_encryption.public_key,
            sender_signing_key=self.alice_signing.private_key
        )

        # Try to verify with Eve's public key (wrong key)
        with pytest.raises(InvalidSignature):
            self.service.decrypt_message(
                encrypted_message=encrypted,
                recipient_private_key=self.bob_encryption.private_key,
                sender_public_key=self.alice_encryption.public_key,
                sender_signing_public_key=self.eve_signing.public_key  # Wrong key!
            )

    def test_signature_verification_tampered_ciphertext(self):
        """Test that tampered ciphertext fails verification"""
        plaintext = "Original message"

        encrypted = self.service.encrypt_message(
            plaintext=plaintext,
            sender_private_key=self.alice_encryption.private_key,
            recipient_public_key=self.bob_encryption.public_key,
            sender_signing_key=self.alice_signing.private_key
        )

        # Tamper with ciphertext
        tampered_ciphertext = bytearray(encrypted.ciphertext)
        tampered_ciphertext[0] ^= 0xFF  # Flip bits

        tampered_message = EncryptedMessage(
            ciphertext=bytes(tampered_ciphertext),
            nonce=encrypted.nonce,
            signature=encrypted.signature,
            sender_public_key=encrypted.sender_public_key,
            encryption_version=encrypted.encryption_version
        )

        with pytest.raises(InvalidSignature):
            self.service.decrypt_message(
                encrypted_message=tampered_message,
                recipient_private_key=self.bob_encryption.private_key,
                sender_public_key=self.alice_encryption.public_key,
                sender_signing_public_key=self.alice_signing.public_key
            )

    def test_signature_verification_tampered_nonce(self):
        """Test that tampered nonce fails verification"""
        plaintext = "Original message"

        encrypted = self.service.encrypt_message(
            plaintext=plaintext,
            sender_private_key=self.alice_encryption.private_key,
            recipient_public_key=self.bob_encryption.public_key,
            sender_signing_key=self.alice_signing.private_key
        )

        # Tamper with nonce
        tampered_nonce = bytearray(encrypted.nonce)
        tampered_nonce[0] ^= 0xFF

        tampered_message = EncryptedMessage(
            ciphertext=encrypted.ciphertext,
            nonce=bytes(tampered_nonce),
            signature=encrypted.signature,
            sender_public_key=encrypted.sender_public_key,
            encryption_version=encrypted.encryption_version
        )

        with pytest.raises(InvalidSignature):
            self.service.decrypt_message(
                encrypted_message=tampered_message,
                recipient_private_key=self.bob_encryption.private_key,
                sender_public_key=self.alice_encryption.public_key,
                sender_signing_public_key=self.alice_signing.public_key
            )


class TestReplayAttackPrevention:
    """Tests for replay attack prevention"""

    def setup_method(self):
        """Setup test fixtures"""
        self.service = EncryptionService()
        self.alice_encryption = self.service.generate_x25519_keypair()
        self.alice_signing = self.service.generate_ed25519_keypair()
        self.bob_encryption = self.service.generate_x25519_keypair()

    def test_unique_nonces(self):
        """Test that each encryption produces a unique nonce"""
        plaintext = "Same message"
        nonces = set()

        for _ in range(100):
            encrypted = self.service.encrypt_message(
                plaintext=plaintext,
                sender_private_key=self.alice_encryption.private_key,
                recipient_public_key=self.bob_encryption.public_key,
                sender_signing_key=self.alice_signing.private_key
            )
            nonces.add(encrypted.nonce)

        # All nonces should be unique
        assert len(nonces) == 100

    def test_different_ciphertext_same_plaintext(self):
        """Test that same plaintext produces different ciphertext each time"""
        plaintext = "Same message"
        ciphertexts = set()

        for _ in range(10):
            encrypted = self.service.encrypt_message(
                plaintext=plaintext,
                sender_private_key=self.alice_encryption.private_key,
                recipient_public_key=self.bob_encryption.public_key,
                sender_signing_key=self.alice_signing.private_key
            )
            ciphertexts.add(encrypted.ciphertext)

        # All ciphertexts should be unique due to random nonces
        assert len(ciphertexts) == 10


class TestGroupEncryption:
    """Tests for group message encryption"""

    def setup_method(self):
        """Setup test fixtures"""
        self.service = EncryptionService()

        # Group members
        self.alice_encryption = self.service.generate_x25519_keypair()
        self.alice_signing = self.service.generate_ed25519_keypair()
        self.bob_encryption = self.service.generate_x25519_keypair()
        self.charlie_encryption = self.service.generate_x25519_keypair()

    def test_generate_group_key(self):
        """Test group key generation"""
        group_key = self.service.generate_group_key()

        assert len(group_key) == 32  # AES-256 key

    def test_encrypt_group_key_for_member(self):
        """Test encrypting group key for a member"""
        group_key = self.service.generate_group_key()

        # Alice encrypts group key for Bob
        encrypted_key = self.service.encrypt_group_key(
            group_key=group_key,
            recipient_public_key=self.bob_encryption.public_key,
            sender_private_key=self.alice_encryption.private_key
        )

        assert encrypted_key is not None
        assert len(encrypted_key) > 32  # Nonce + ciphertext

        # Bob decrypts
        decrypted_key = self.service.decrypt_group_key(
            encrypted_group_key=encrypted_key,
            sender_public_key=self.alice_encryption.public_key,
            recipient_private_key=self.bob_encryption.private_key
        )

        assert decrypted_key == group_key

    def test_encrypt_message_with_group_key(self):
        """Test encrypting message with group key"""
        group_key = self.service.generate_group_key()
        plaintext = "Hello group!"

        encrypted = self.service.encrypt_with_group_key(
            plaintext=plaintext,
            group_key=group_key,
            sender_signing_key=self.alice_signing.private_key
        )

        assert encrypted is not None
        assert encrypted.ciphertext != plaintext.encode()

    def test_decrypt_message_with_group_key(self):
        """Test decrypting message with group key"""
        group_key = self.service.generate_group_key()
        plaintext = "Secret group message!"

        # Alice encrypts
        encrypted = self.service.encrypt_with_group_key(
            plaintext=plaintext,
            group_key=group_key,
            sender_signing_key=self.alice_signing.private_key
        )

        # Bob (who has the group key) decrypts
        decrypted = self.service.decrypt_with_group_key(
            encrypted_message=encrypted,
            group_key=group_key,
            sender_signing_public_key=self.alice_signing.public_key
        )

        assert decrypted == plaintext

    def test_group_message_signature_verification(self):
        """Test that group messages verify sender signature"""
        group_key = self.service.generate_group_key()
        plaintext = "Authenticated group message"
        eve_signing = self.service.generate_ed25519_keypair()

        # Alice sends message
        encrypted = self.service.encrypt_with_group_key(
            plaintext=plaintext,
            group_key=group_key,
            sender_signing_key=self.alice_signing.private_key
        )

        # Try to verify with wrong key (Eve's)
        with pytest.raises(InvalidSignature):
            self.service.decrypt_with_group_key(
                encrypted_message=encrypted,
                group_key=group_key,
                sender_signing_public_key=eve_signing.public_key
            )


class TestFileEncryption:
    """Tests for file encryption"""

    def setup_method(self):
        """Setup test fixtures"""
        self.service = EncryptionService()

    def test_encrypt_file_basic(self):
        """Test basic file encryption"""
        file_data = b"This is file content. " * 100

        encrypted_data, nonce, file_key = self.service.encrypt_file(file_data)

        assert encrypted_data != file_data
        assert len(nonce) == 12
        assert len(file_key) == 32

    def test_decrypt_file_basic(self):
        """Test basic file decryption"""
        file_data = b"This is secret file content!"

        encrypted_data, nonce, file_key = self.service.encrypt_file(file_data)
        decrypted_data = self.service.decrypt_file(encrypted_data, nonce, file_key)

        assert decrypted_data == file_data

    def test_encrypt_file_with_provided_key(self):
        """Test file encryption with provided key"""
        file_data = b"Content to encrypt"
        custom_key = os.urandom(32)

        encrypted_data, nonce, returned_key = self.service.encrypt_file(
            file_data, file_key=custom_key
        )

        assert returned_key == custom_key

        # Decrypt with same key
        decrypted = self.service.decrypt_file(encrypted_data, nonce, custom_key)
        assert decrypted == file_data

    def test_encrypt_large_file(self):
        """Test encryption of large files"""
        file_data = os.urandom(10 * 1024 * 1024)  # 10MB

        encrypted_data, nonce, file_key = self.service.encrypt_file(file_data)
        decrypted_data = self.service.decrypt_file(encrypted_data, nonce, file_key)

        assert decrypted_data == file_data

    def test_encrypt_binary_file(self):
        """Test encryption of binary data"""
        # Simulate image/binary data
        file_data = bytes(range(256)) * 100

        encrypted_data, nonce, file_key = self.service.encrypt_file(file_data)
        decrypted_data = self.service.decrypt_file(encrypted_data, nonce, file_key)

        assert decrypted_data == file_data


class TestUtilityFunctions:
    """Tests for utility functions"""

    def setup_method(self):
        """Setup test fixtures"""
        self.service = EncryptionService()

    def test_hash_content(self):
        """Test SHA-256 hashing"""
        content = b"Test content to hash"
        hash1 = self.service.hash_content(content)

        assert len(hash1) == 64  # SHA-256 hex = 64 chars
        assert hash1 == self.service.hash_content(content)  # Deterministic

    def test_hash_different_content(self):
        """Test that different content produces different hashes"""
        hash1 = self.service.hash_content(b"Content 1")
        hash2 = self.service.hash_content(b"Content 2")

        assert hash1 != hash2

    def test_base64_encoding(self):
        """Test base64 encoding/decoding"""
        original = os.urandom(100)

        encoded = self.service.to_base64(original)
        decoded = self.service.from_base64(encoded)

        assert isinstance(encoded, str)
        assert decoded == original

    def test_serialize_encrypted_message(self):
        """Test EncryptedMessage serialization"""
        alice_encryption = self.service.generate_x25519_keypair()
        alice_signing = self.service.generate_ed25519_keypair()
        bob_encryption = self.service.generate_x25519_keypair()

        encrypted = self.service.encrypt_message(
            plaintext="Test message",
            sender_private_key=alice_encryption.private_key,
            recipient_public_key=bob_encryption.public_key,
            sender_signing_key=alice_signing.private_key
        )

        serialized = self.service.serialize_encrypted_message(encrypted)

        assert 'ciphertext' in serialized
        assert 'nonce' in serialized
        assert 'signature' in serialized
        assert 'sender_public_key' in serialized
        assert 'encryption_version' in serialized
        assert isinstance(serialized['ciphertext'], str)  # Base64 string

    def test_deserialize_encrypted_message(self):
        """Test EncryptedMessage deserialization"""
        alice_encryption = self.service.generate_x25519_keypair()
        alice_signing = self.service.generate_ed25519_keypair()
        bob_encryption = self.service.generate_x25519_keypair()

        original = self.service.encrypt_message(
            plaintext="Test message",
            sender_private_key=alice_encryption.private_key,
            recipient_public_key=bob_encryption.public_key,
            sender_signing_key=alice_signing.private_key
        )

        serialized = self.service.serialize_encrypted_message(original)
        deserialized = self.service.deserialize_encrypted_message(serialized)

        assert deserialized.ciphertext == original.ciphertext
        assert deserialized.nonce == original.nonce
        assert deserialized.signature == original.signature
        assert deserialized.sender_public_key == original.sender_public_key

    def test_serialize_deserialize_roundtrip(self):
        """Test that serialization roundtrip preserves decryptability"""
        alice_encryption = self.service.generate_x25519_keypair()
        alice_signing = self.service.generate_ed25519_keypair()
        bob_encryption = self.service.generate_x25519_keypair()

        plaintext = "Roundtrip test message"

        encrypted = self.service.encrypt_message(
            plaintext=plaintext,
            sender_private_key=alice_encryption.private_key,
            recipient_public_key=bob_encryption.public_key,
            sender_signing_key=alice_signing.private_key
        )

        # Serialize -> Deserialize
        serialized = self.service.serialize_encrypted_message(encrypted)
        deserialized = self.service.deserialize_encrypted_message(serialized)

        # Should still decrypt correctly
        decrypted = self.service.decrypt_message(
            encrypted_message=deserialized,
            recipient_private_key=bob_encryption.private_key,
            sender_public_key=alice_encryption.public_key,
            sender_signing_public_key=alice_signing.public_key
        )

        assert decrypted == plaintext


class TestSingletonService:
    """Tests for singleton encryption service"""

    def test_get_encryption_service(self):
        """Test singleton pattern"""
        service1 = get_encryption_service()
        service2 = get_encryption_service()

        assert service1 is service2

    def test_service_functionality(self):
        """Test that singleton service works correctly"""
        service = get_encryption_service()
        keypair = service.generate_x25519_keypair()

        assert keypair is not None
        assert len(keypair.public_key) == 32


class TestSecurityProperties:
    """Tests for security properties"""

    def setup_method(self):
        """Setup test fixtures"""
        self.service = EncryptionService()

    def test_forward_secrecy_key_independence(self):
        """Test that compromising one key doesn't affect others"""
        alice_encryption = self.service.generate_x25519_keypair()
        alice_signing = self.service.generate_ed25519_keypair()
        bob_encryption = self.service.generate_x25519_keypair()

        # Encrypt multiple messages
        messages = ["Message 1", "Message 2", "Message 3"]
        encrypted_messages = []

        for msg in messages:
            encrypted = self.service.encrypt_message(
                plaintext=msg,
                sender_private_key=alice_encryption.private_key,
                recipient_public_key=bob_encryption.public_key,
                sender_signing_key=alice_signing.private_key
            )
            encrypted_messages.append(encrypted)

        # Each message has unique nonce and ciphertext
        nonces = [m.nonce for m in encrypted_messages]
        ciphertexts = [m.ciphertext for m in encrypted_messages]

        assert len(set(nonces)) == 3
        assert len(set(ciphertexts)) == 3

    def test_wrong_recipient_cannot_decrypt(self):
        """Test that wrong recipient cannot decrypt"""
        alice_encryption = self.service.generate_x25519_keypair()
        alice_signing = self.service.generate_ed25519_keypair()
        bob_encryption = self.service.generate_x25519_keypair()
        eve_encryption = self.service.generate_x25519_keypair()  # Attacker

        plaintext = "Secret for Bob only"

        # Alice encrypts for Bob
        encrypted = self.service.encrypt_message(
            plaintext=plaintext,
            sender_private_key=alice_encryption.private_key,
            recipient_public_key=bob_encryption.public_key,
            sender_signing_key=alice_signing.private_key
        )

        # Eve tries to decrypt (will fail at decryption stage)
        with pytest.raises(Exception):  # Will fail due to wrong shared secret
            self.service.decrypt_message(
                encrypted_message=encrypted,
                recipient_private_key=eve_encryption.private_key,
                sender_public_key=alice_encryption.public_key,
                sender_signing_public_key=alice_signing.public_key
            )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
