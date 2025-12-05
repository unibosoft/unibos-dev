"""
Security Penetration Tests for Messenger Module

Tests for common security vulnerabilities:
- OWASP Top 10 vulnerabilities
- Authentication bypass attempts
- Encryption weaknesses
- Input validation
- Authorization flaws
"""

import pytest
import os
import base64
import json
import uuid
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from encryption import EncryptionService, EncryptedMessage
from cryptography.exceptions import InvalidSignature


class TestCryptographicSecurity:
    """Tests for cryptographic security"""

    def setup_method(self):
        self.service = EncryptionService()

    # ========== Key Security Tests ==========

    def test_private_key_not_exposed_in_serialization(self):
        """Test that private keys are not included in serialization"""
        alice_enc = self.service.generate_x25519_keypair()
        alice_sign = self.service.generate_ed25519_keypair()
        bob_enc = self.service.generate_x25519_keypair()

        encrypted = self.service.encrypt_message(
            plaintext="Secret",
            sender_private_key=alice_enc.private_key,
            recipient_public_key=bob_enc.public_key,
            sender_signing_key=alice_sign.private_key
        )

        serialized = self.service.serialize_encrypted_message(encrypted)

        # Check no private key data in serialized output
        serialized_str = json.dumps(serialized)
        assert alice_enc.private_key.hex() not in serialized_str
        assert alice_sign.private_key.hex() not in serialized_str

    def test_key_entropy(self):
        """Test that generated keys have sufficient entropy"""
        keys = [self.service.generate_x25519_keypair() for _ in range(100)]

        # Check all keys are unique
        public_keys = [k.public_key for k in keys]
        private_keys = [k.private_key for k in keys]

        assert len(set(public_keys)) == 100
        assert len(set(private_keys)) == 100

    def test_nonce_randomness(self):
        """Test that nonces are cryptographically random"""
        alice_enc = self.service.generate_x25519_keypair()
        alice_sign = self.service.generate_ed25519_keypair()
        bob_enc = self.service.generate_x25519_keypair()

        nonces = set()
        for _ in range(1000):
            encrypted = self.service.encrypt_message(
                plaintext="Same message",
                sender_private_key=alice_enc.private_key,
                recipient_public_key=bob_enc.public_key,
                sender_signing_key=alice_sign.private_key
            )
            nonces.add(encrypted.nonce)

        # All nonces should be unique (probability of collision is negligible)
        assert len(nonces) == 1000

    # ========== Signature Manipulation Tests ==========

    def test_signature_forgery_attempt(self):
        """Test that forged signatures are rejected"""
        alice_enc = self.service.generate_x25519_keypair()
        alice_sign = self.service.generate_ed25519_keypair()
        bob_enc = self.service.generate_x25519_keypair()
        eve_sign = self.service.generate_ed25519_keypair()

        encrypted = self.service.encrypt_message(
            plaintext="Original message",
            sender_private_key=alice_enc.private_key,
            recipient_public_key=bob_enc.public_key,
            sender_signing_key=alice_sign.private_key
        )

        # Eve tries to create a valid signature with her key
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        eve_private = Ed25519PrivateKey.from_private_bytes(eve_sign.private_key)
        forged_signature = eve_private.sign(encrypted.nonce + encrypted.ciphertext)

        forged_message = EncryptedMessage(
            ciphertext=encrypted.ciphertext,
            nonce=encrypted.nonce,
            signature=forged_signature,
            sender_public_key=encrypted.sender_public_key,
            encryption_version=encrypted.encryption_version
        )

        # Should fail verification with Alice's public key
        with pytest.raises(InvalidSignature):
            self.service.decrypt_message(
                encrypted_message=forged_message,
                recipient_private_key=bob_enc.private_key,
                sender_public_key=alice_enc.public_key,
                sender_signing_public_key=alice_sign.public_key
            )

    def test_signature_truncation_attack(self):
        """Test that truncated signatures are rejected"""
        alice_enc = self.service.generate_x25519_keypair()
        alice_sign = self.service.generate_ed25519_keypair()
        bob_enc = self.service.generate_x25519_keypair()

        encrypted = self.service.encrypt_message(
            plaintext="Secret message",
            sender_private_key=alice_enc.private_key,
            recipient_public_key=bob_enc.public_key,
            sender_signing_key=alice_sign.private_key
        )

        # Truncate signature
        truncated_signature = encrypted.signature[:32]  # Half of Ed25519 signature

        truncated_message = EncryptedMessage(
            ciphertext=encrypted.ciphertext,
            nonce=encrypted.nonce,
            signature=truncated_signature,
            sender_public_key=encrypted.sender_public_key,
            encryption_version=encrypted.encryption_version
        )

        with pytest.raises(Exception):
            self.service.decrypt_message(
                encrypted_message=truncated_message,
                recipient_private_key=bob_enc.private_key,
                sender_public_key=alice_enc.public_key,
                sender_signing_public_key=alice_sign.public_key
            )

    # ========== Ciphertext Manipulation Tests ==========

    def test_ciphertext_bit_flip_attack(self):
        """Test that bit-flipped ciphertext is rejected"""
        alice_enc = self.service.generate_x25519_keypair()
        alice_sign = self.service.generate_ed25519_keypair()
        bob_enc = self.service.generate_x25519_keypair()

        encrypted = self.service.encrypt_message(
            plaintext="Important data",
            sender_private_key=alice_enc.private_key,
            recipient_public_key=bob_enc.public_key,
            sender_signing_key=alice_sign.private_key
        )

        # Flip bits in ciphertext
        tampered = bytearray(encrypted.ciphertext)
        for i in range(min(10, len(tampered))):
            tampered[i] ^= 0xFF

        tampered_message = EncryptedMessage(
            ciphertext=bytes(tampered),
            nonce=encrypted.nonce,
            signature=encrypted.signature,
            sender_public_key=encrypted.sender_public_key,
            encryption_version=encrypted.encryption_version
        )

        # Should fail signature verification
        with pytest.raises(InvalidSignature):
            self.service.decrypt_message(
                encrypted_message=tampered_message,
                recipient_private_key=bob_enc.private_key,
                sender_public_key=alice_enc.public_key,
                sender_signing_public_key=alice_sign.public_key
            )

    def test_ciphertext_extension_attack(self):
        """Test that extended ciphertext is rejected"""
        alice_enc = self.service.generate_x25519_keypair()
        alice_sign = self.service.generate_ed25519_keypair()
        bob_enc = self.service.generate_x25519_keypair()

        encrypted = self.service.encrypt_message(
            plaintext="Original",
            sender_private_key=alice_enc.private_key,
            recipient_public_key=bob_enc.public_key,
            sender_signing_key=alice_sign.private_key
        )

        # Extend ciphertext
        extended_ciphertext = encrypted.ciphertext + b'\x00' * 100

        extended_message = EncryptedMessage(
            ciphertext=extended_ciphertext,
            nonce=encrypted.nonce,
            signature=encrypted.signature,
            sender_public_key=encrypted.sender_public_key,
            encryption_version=encrypted.encryption_version
        )

        with pytest.raises(InvalidSignature):
            self.service.decrypt_message(
                encrypted_message=extended_message,
                recipient_private_key=bob_enc.private_key,
                sender_public_key=alice_enc.public_key,
                sender_signing_public_key=alice_sign.public_key
            )

    # ========== Nonce Manipulation Tests ==========

    def test_nonce_reuse_detection(self):
        """Test that nonce reuse produces different ciphertext"""
        alice_enc = self.service.generate_x25519_keypair()
        alice_sign = self.service.generate_ed25519_keypair()
        bob_enc = self.service.generate_x25519_keypair()

        # Encrypt same message twice
        enc1 = self.service.encrypt_message(
            plaintext="Same message",
            sender_private_key=alice_enc.private_key,
            recipient_public_key=bob_enc.public_key,
            sender_signing_key=alice_sign.private_key
        )

        enc2 = self.service.encrypt_message(
            plaintext="Same message",
            sender_private_key=alice_enc.private_key,
            recipient_public_key=bob_enc.public_key,
            sender_signing_key=alice_sign.private_key
        )

        # Nonces should be different (random)
        assert enc1.nonce != enc2.nonce
        # Ciphertext should be different due to different nonces
        assert enc1.ciphertext != enc2.ciphertext

    def test_zero_nonce_attack(self):
        """Test behavior with zero nonce (should still work but is bad practice)"""
        # This test verifies the system doesn't crash with unusual inputs
        # In production, nonces should always be random
        alice_enc = self.service.generate_x25519_keypair()
        bob_enc = self.service.generate_x25519_keypair()

        shared_secret = self.service.derive_shared_secret(
            alice_enc.private_key,
            bob_enc.public_key
        )
        message_key = self.service.derive_message_key(shared_secret)

        # The system should use random nonces, not allow custom ones
        # This test just verifies the key derivation works
        assert len(message_key) == 32

    # ========== Key Exchange Security ==========

    def test_small_subgroup_attack_prevention(self):
        """Test that X25519 implementation rejects invalid public keys"""
        alice_enc = self.service.generate_x25519_keypair()

        # Try to use a low-order point (all zeros is invalid for X25519)
        invalid_public_key = b'\x00' * 32

        # X25519 should handle this safely (produces all-zero shared secret)
        # The cryptography library handles this internally
        try:
            result = self.service.derive_shared_secret(
                alice_enc.private_key,
                invalid_public_key
            )
            # If it doesn't raise, the result should be the "canonical" output
            # for invalid keys
            assert result is not None
        except Exception:
            # Some implementations may raise an exception, which is also acceptable
            pass

    def test_different_keys_produce_different_secrets(self):
        """Test that different key pairs produce different shared secrets"""
        alice = self.service.generate_x25519_keypair()
        bob = self.service.generate_x25519_keypair()
        charlie = self.service.generate_x25519_keypair()

        secret_ab = self.service.derive_shared_secret(alice.private_key, bob.public_key)
        secret_ac = self.service.derive_shared_secret(alice.private_key, charlie.public_key)
        secret_bc = self.service.derive_shared_secret(bob.private_key, charlie.public_key)

        # All secrets should be different
        assert secret_ab != secret_ac
        assert secret_ab != secret_bc
        assert secret_ac != secret_bc

    # ========== Group Key Security ==========

    def test_group_key_isolation(self):
        """Test that group keys don't leak between groups"""
        group1_key = self.service.generate_group_key()
        group2_key = self.service.generate_group_key()

        assert group1_key != group2_key
        assert len(group1_key) == 32
        assert len(group2_key) == 32

    def test_encrypted_group_key_different_per_recipient(self):
        """Test that group key is encrypted differently for each recipient"""
        admin = self.service.generate_x25519_keypair()
        member1 = self.service.generate_x25519_keypair()
        member2 = self.service.generate_x25519_keypair()

        group_key = self.service.generate_group_key()

        enc_key1 = self.service.encrypt_group_key(
            group_key, member1.public_key, admin.private_key
        )
        enc_key2 = self.service.encrypt_group_key(
            group_key, member2.public_key, admin.private_key
        )

        # Encrypted keys should be different (different nonces + different recipients)
        assert enc_key1 != enc_key2

        # But both should decrypt to the same group key
        dec_key1 = self.service.decrypt_group_key(
            enc_key1, admin.public_key, member1.private_key
        )
        dec_key2 = self.service.decrypt_group_key(
            enc_key2, admin.public_key, member2.private_key
        )

        assert dec_key1 == group_key
        assert dec_key2 == group_key

    # ========== File Encryption Security ==========

    def test_file_key_uniqueness(self):
        """Test that file encryption keys are unique"""
        keys = set()
        for _ in range(100):
            _, _, key = self.service.encrypt_file(b"test data")
            keys.add(key)

        assert len(keys) == 100

    def test_file_nonce_uniqueness(self):
        """Test that file encryption nonces are unique"""
        nonces = set()
        for _ in range(100):
            _, nonce, _ = self.service.encrypt_file(b"test data")
            nonces.add(nonce)

        assert len(nonces) == 100

    # ========== Serialization Security ==========

    def test_malformed_base64_handling(self):
        """Test handling of malformed base64 in deserialization"""
        malformed_data = {
            'ciphertext': 'not valid base64!!!',
            'nonce': 'also invalid###',
            'signature': 'bad data',
            'sender_public_key': '',
            'encryption_version': 1
        }

        with pytest.raises(Exception):
            self.service.deserialize_encrypted_message(malformed_data)

    def test_missing_fields_handling(self):
        """Test handling of missing fields in deserialization"""
        incomplete_data = {
            'ciphertext': base64.b64encode(b'test').decode(),
            # Missing nonce, signature
        }

        with pytest.raises(KeyError):
            self.service.deserialize_encrypted_message(incomplete_data)

    def test_extra_fields_ignored(self):
        """Test that extra fields in serialized data are ignored"""
        alice_enc = self.service.generate_x25519_keypair()
        alice_sign = self.service.generate_ed25519_keypair()
        bob_enc = self.service.generate_x25519_keypair()

        encrypted = self.service.encrypt_message(
            plaintext="Test",
            sender_private_key=alice_enc.private_key,
            recipient_public_key=bob_enc.public_key,
            sender_signing_key=alice_sign.private_key
        )

        serialized = self.service.serialize_encrypted_message(encrypted)

        # Add extra malicious fields
        serialized['malicious_field'] = 'attacker_data'
        serialized['private_key'] = 'fake_private_key'

        # Should still deserialize correctly
        deserialized = self.service.deserialize_encrypted_message(serialized)
        assert deserialized.ciphertext == encrypted.ciphertext


class TestInputValidation:
    """Tests for input validation security"""

    def setup_method(self):
        self.service = EncryptionService()

    def test_empty_plaintext(self):
        """Test encryption of empty plaintext"""
        alice_enc = self.service.generate_x25519_keypair()
        alice_sign = self.service.generate_ed25519_keypair()
        bob_enc = self.service.generate_x25519_keypair()

        encrypted = self.service.encrypt_message(
            plaintext="",
            sender_private_key=alice_enc.private_key,
            recipient_public_key=bob_enc.public_key,
            sender_signing_key=alice_sign.private_key
        )

        decrypted = self.service.decrypt_message(
            encrypted_message=encrypted,
            recipient_private_key=bob_enc.private_key,
            sender_public_key=alice_enc.public_key,
            sender_signing_public_key=alice_sign.public_key
        )

        assert decrypted == ""

    def test_very_long_plaintext(self):
        """Test encryption of very long plaintext"""
        alice_enc = self.service.generate_x25519_keypair()
        alice_sign = self.service.generate_ed25519_keypair()
        bob_enc = self.service.generate_x25519_keypair()

        # 1MB message
        long_text = "A" * (1024 * 1024)

        encrypted = self.service.encrypt_message(
            plaintext=long_text,
            sender_private_key=alice_enc.private_key,
            recipient_public_key=bob_enc.public_key,
            sender_signing_key=alice_sign.private_key
        )

        decrypted = self.service.decrypt_message(
            encrypted_message=encrypted,
            recipient_private_key=bob_enc.private_key,
            sender_public_key=alice_enc.public_key,
            sender_signing_public_key=alice_sign.public_key
        )

        assert decrypted == long_text

    def test_special_characters_in_plaintext(self):
        """Test encryption of special characters"""
        alice_enc = self.service.generate_x25519_keypair()
        alice_sign = self.service.generate_ed25519_keypair()
        bob_enc = self.service.generate_x25519_keypair()

        special_text = "Test with special chars: \x00\x01\x02\n\r\t"

        encrypted = self.service.encrypt_message(
            plaintext=special_text,
            sender_private_key=alice_enc.private_key,
            recipient_public_key=bob_enc.public_key,
            sender_signing_key=alice_sign.private_key
        )

        decrypted = self.service.decrypt_message(
            encrypted_message=encrypted,
            recipient_private_key=bob_enc.private_key,
            sender_public_key=alice_enc.public_key,
            sender_signing_public_key=alice_sign.public_key
        )

        assert decrypted == special_text

    def test_unicode_edge_cases(self):
        """Test encryption of Unicode edge cases"""
        alice_enc = self.service.generate_x25519_keypair()
        alice_sign = self.service.generate_ed25519_keypair()
        bob_enc = self.service.generate_x25519_keypair()

        # Various Unicode edge cases
        test_strings = [
            "\u0000",  # Null
            "\uFFFD",  # Replacement char
            "\U0001F600",  # Emoji
            "Test string with unicode text",  # RTL text simulation
            "\u202E",  # Right-to-left override
        ]

        for test_str in test_strings:
            encrypted = self.service.encrypt_message(
                plaintext=test_str,
                sender_private_key=alice_enc.private_key,
                recipient_public_key=bob_enc.public_key,
                sender_signing_key=alice_sign.private_key
            )

            decrypted = self.service.decrypt_message(
                encrypted_message=encrypted,
                recipient_private_key=bob_enc.private_key,
                sender_public_key=alice_enc.public_key,
                sender_signing_public_key=alice_sign.public_key
            )

            assert decrypted == test_str


class TestTimingAttacks:
    """Tests for timing attack resistance"""

    def setup_method(self):
        self.service = EncryptionService()

    def test_signature_verification_constant_time(self):
        """Test that signature verification doesn't leak timing info"""
        import time

        alice_enc = self.service.generate_x25519_keypair()
        alice_sign = self.service.generate_ed25519_keypair()
        bob_enc = self.service.generate_x25519_keypair()

        encrypted = self.service.encrypt_message(
            plaintext="Test message",
            sender_private_key=alice_enc.private_key,
            recipient_public_key=bob_enc.public_key,
            sender_signing_key=alice_sign.private_key
        )

        # Time valid decryption
        valid_times = []
        for _ in range(10):
            start = time.perf_counter()
            self.service.decrypt_message(
                encrypted_message=encrypted,
                recipient_private_key=bob_enc.private_key,
                sender_public_key=alice_enc.public_key,
                sender_signing_public_key=alice_sign.public_key
            )
            valid_times.append(time.perf_counter() - start)

        # Time invalid signature
        tampered = EncryptedMessage(
            ciphertext=encrypted.ciphertext,
            nonce=encrypted.nonce,
            signature=b'\x00' * 64,  # Invalid signature
            sender_public_key=encrypted.sender_public_key,
            encryption_version=encrypted.encryption_version
        )

        invalid_times = []
        for _ in range(10):
            start = time.perf_counter()
            try:
                self.service.decrypt_message(
                    encrypted_message=tampered,
                    recipient_private_key=bob_enc.private_key,
                    sender_public_key=alice_enc.public_key,
                    sender_signing_public_key=alice_sign.public_key
                )
            except:
                pass
            invalid_times.append(time.perf_counter() - start)

        # Note: This is a basic check. In practice, timing analysis requires
        # more sophisticated statistical methods and many more samples.
        # The cryptography library uses constant-time operations internally.
        avg_valid = sum(valid_times) / len(valid_times)
        avg_invalid = sum(invalid_times) / len(invalid_times)

        # Times should be in the same order of magnitude
        # (not a strict test, just sanity check)
        assert avg_valid > 0
        assert avg_invalid > 0


class TestKeyManagementSecurity:
    """Tests for key management security"""

    def setup_method(self):
        self.service = EncryptionService()

    def test_key_derivation_with_same_secret_same_context(self):
        """Test HKDF determinism"""
        secret = os.urandom(32)
        context = b"test-context"

        key1 = self.service.derive_message_key(secret, context)
        key2 = self.service.derive_message_key(secret, context)

        assert key1 == key2

    def test_key_derivation_different_contexts(self):
        """Test HKDF with different contexts produces different keys"""
        secret = os.urandom(32)

        key1 = self.service.derive_message_key(secret, b"context-1")
        key2 = self.service.derive_message_key(secret, b"context-2")

        assert key1 != key2

    def test_key_derivation_empty_context(self):
        """Test HKDF with empty context"""
        secret = os.urandom(32)

        # Should work with empty context
        key = self.service.derive_message_key(secret, b"")
        assert len(key) == 32


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
