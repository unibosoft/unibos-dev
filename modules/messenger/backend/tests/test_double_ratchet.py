"""
Tests for Double Ratchet Algorithm implementation.

Tests:
- Basic encryption/decryption
- DH Ratchet stepping
- Out-of-order message handling
- State persistence
- Session management
"""

import pytest
import os
from datetime import datetime

# Add module path for imports
import sys
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos-dev/modules/messenger/backend')

from double_ratchet import (
    DoubleRatchet,
    RatchetState,
    RatchetSessionManager,
    EncryptedRatchetMessage,
    MessageHeader,
    generate_dh_keypair,
    dh_exchange,
    kdf_root_key,
    kdf_chain_key,
    hkdf_derive,
    KEY_SIZE,
)


class TestKeyDerivation:
    """Test key derivation functions"""

    def test_hkdf_derive_produces_correct_length(self):
        """HKDF should produce key of requested length"""
        key_material = os.urandom(32)
        derived = hkdf_derive(key_material, b'test-info', length=32)
        assert len(derived) == 32

    def test_hkdf_derive_deterministic(self):
        """Same inputs should produce same output"""
        key_material = os.urandom(32)
        info = b'test-info'
        derived1 = hkdf_derive(key_material, info)
        derived2 = hkdf_derive(key_material, info)
        assert derived1 == derived2

    def test_hkdf_different_info_different_output(self):
        """Different info should produce different output"""
        key_material = os.urandom(32)
        derived1 = hkdf_derive(key_material, b'info-1')
        derived2 = hkdf_derive(key_material, b'info-2')
        assert derived1 != derived2

    def test_kdf_root_key_produces_two_keys(self):
        """Root KDF should produce new root key and chain key"""
        root_key = os.urandom(32)
        dh_output = os.urandom(32)
        new_root, chain_key = kdf_root_key(root_key, dh_output)

        assert len(new_root) == KEY_SIZE
        assert len(chain_key) == KEY_SIZE
        assert new_root != chain_key
        assert new_root != root_key

    def test_kdf_chain_key_produces_two_keys(self):
        """Chain KDF should produce new chain key and message key"""
        chain_key = os.urandom(32)
        new_chain, message_key = kdf_chain_key(chain_key)

        assert len(new_chain) == KEY_SIZE
        assert len(message_key) == KEY_SIZE
        assert new_chain != message_key
        assert new_chain != chain_key


class TestDHExchange:
    """Test Diffie-Hellman operations"""

    def test_generate_dh_keypair(self):
        """Should generate valid keypair"""
        private, public = generate_dh_keypair()
        assert len(private) == 32
        assert len(public) == 32

    def test_dh_exchange_shared_secret(self):
        """DH exchange should produce same shared secret for both parties"""
        alice_private, alice_public = generate_dh_keypair()
        bob_private, bob_public = generate_dh_keypair()

        alice_shared = dh_exchange(alice_private, bob_public)
        bob_shared = dh_exchange(bob_private, alice_public)

        assert alice_shared == bob_shared
        assert len(alice_shared) == 32

    def test_different_keys_different_secrets(self):
        """Different key pairs should produce different shared secrets"""
        alice_private, alice_public = generate_dh_keypair()
        bob_private, bob_public = generate_dh_keypair()
        eve_private, eve_public = generate_dh_keypair()

        alice_bob = dh_exchange(alice_private, bob_public)
        alice_eve = dh_exchange(alice_private, eve_public)

        assert alice_bob != alice_eve


class TestDoubleRatchetBasic:
    """Test basic Double Ratchet operations"""

    def setup_method(self):
        """Setup test fixtures"""
        # Generate initial shared secret (simulating X3DH)
        self.shared_secret = os.urandom(32)

        # Generate Bob's identity keypair
        self.bob_private, self.bob_public = generate_dh_keypair()

    def test_init_sender(self):
        """Sender initialization should work"""
        alice = DoubleRatchet.init_sender(
            shared_secret=self.shared_secret,
            recipient_public_key=self.bob_public
        )

        assert alice.state.sending_chain_key is not None
        assert alice.state.dh_receiving_key == self.bob_public
        assert alice.state.send_message_number == 0

    def test_init_receiver(self):
        """Receiver initialization should work"""
        bob = DoubleRatchet.init_receiver(
            shared_secret=self.shared_secret,
            keypair=(self.bob_private, self.bob_public)
        )

        assert bob.state.receiving_chain_key is None  # Not set until first message
        assert bob.state.sending_chain_key is None

    def test_encrypt_decrypt_single_message(self):
        """Should encrypt and decrypt a single message"""
        # Alice initiates
        alice = DoubleRatchet.init_sender(
            shared_secret=self.shared_secret,
            recipient_public_key=self.bob_public
        )

        # Bob receives
        bob = DoubleRatchet.init_receiver(
            shared_secret=self.shared_secret,
            keypair=(self.bob_private, self.bob_public)
        )

        # Alice encrypts
        plaintext = "Hello Bob!"
        encrypted = alice.encrypt(plaintext)

        # Bob decrypts
        decrypted = bob.decrypt(encrypted)

        assert decrypted == plaintext

    def test_encrypt_multiple_messages(self):
        """Should handle multiple messages in sequence"""
        alice = DoubleRatchet.init_sender(
            shared_secret=self.shared_secret,
            recipient_public_key=self.bob_public
        )
        bob = DoubleRatchet.init_receiver(
            shared_secret=self.shared_secret,
            keypair=(self.bob_private, self.bob_public)
        )

        messages = [
            "Message 1",
            "Message 2",
            "Message 3"
        ]

        for msg in messages:
            encrypted = alice.encrypt(msg)
            decrypted = bob.decrypt(encrypted)
            assert decrypted == msg

    def test_bidirectional_communication(self):
        """Should handle messages in both directions"""
        alice = DoubleRatchet.init_sender(
            shared_secret=self.shared_secret,
            recipient_public_key=self.bob_public
        )
        bob = DoubleRatchet.init_receiver(
            shared_secret=self.shared_secret,
            keypair=(self.bob_private, self.bob_public)
        )

        # Alice -> Bob
        enc1 = alice.encrypt("Hello Bob")
        dec1 = bob.decrypt(enc1)
        assert dec1 == "Hello Bob"

        # Bob -> Alice
        enc2 = bob.encrypt("Hello Alice")
        dec2 = alice.decrypt(enc2)
        assert dec2 == "Hello Alice"

        # Alice -> Bob again
        enc3 = alice.encrypt("How are you?")
        dec3 = bob.decrypt(enc3)
        assert dec3 == "How are you?"

    def test_message_counter_increments(self):
        """Message counter should increment with each message"""
        alice = DoubleRatchet.init_sender(
            shared_secret=self.shared_secret,
            recipient_public_key=self.bob_public
        )

        assert alice.state.send_message_number == 0

        alice.encrypt("Message 1")
        assert alice.state.send_message_number == 1

        alice.encrypt("Message 2")
        assert alice.state.send_message_number == 2


class TestDHRatchetStep:
    """Test DH Ratchet stepping"""

    def setup_method(self):
        """Setup test fixtures"""
        self.shared_secret = os.urandom(32)
        self.bob_private, self.bob_public = generate_dh_keypair()

        self.alice = DoubleRatchet.init_sender(
            shared_secret=self.shared_secret,
            recipient_public_key=self.bob_public
        )
        self.bob = DoubleRatchet.init_receiver(
            shared_secret=self.shared_secret,
            keypair=(self.bob_private, self.bob_public)
        )

    def test_dh_ratchet_on_reply(self):
        """DH ratchet should step when direction changes"""
        initial_alice_public = self.alice.state.dh_sending_keypair[1]

        # Alice -> Bob
        enc1 = self.alice.encrypt("From Alice")
        self.bob.decrypt(enc1)

        # Bob -> Alice (should trigger DH ratchet)
        enc2 = self.bob.encrypt("From Bob")
        self.alice.decrypt(enc2)

        # Bob should have new sending keys
        assert self.bob.state.dh_sending_keypair[1] != self.bob_public

    def test_key_rotation_per_direction(self):
        """Keys should rotate when communication direction changes"""
        # Collect Alice's public keys over time
        alice_keys = []

        # Alice -> Bob (multiple messages)
        for i in range(3):
            enc = self.alice.encrypt(f"Alice message {i}")
            self.bob.decrypt(enc)

        alice_keys.append(self.alice.state.dh_sending_keypair[1])

        # Bob -> Alice
        enc = self.bob.encrypt("Bob reply")
        self.alice.decrypt(enc)

        # Alice -> Bob again (should have new keys)
        enc = self.alice.encrypt("Alice again")
        alice_keys.append(self.alice.state.dh_sending_keypair[1])

        # Keys should be different after ratchet step
        assert alice_keys[0] != alice_keys[1]


class TestOutOfOrderMessages:
    """Test out-of-order message handling"""

    def setup_method(self):
        """Setup test fixtures"""
        self.shared_secret = os.urandom(32)
        self.bob_private, self.bob_public = generate_dh_keypair()

        self.alice = DoubleRatchet.init_sender(
            shared_secret=self.shared_secret,
            recipient_public_key=self.bob_public
        )
        self.bob = DoubleRatchet.init_receiver(
            shared_secret=self.shared_secret,
            keypair=(self.bob_private, self.bob_public)
        )

    def test_out_of_order_delivery(self):
        """Should handle messages delivered out of order"""
        # Alice sends 3 messages
        enc1 = self.alice.encrypt("Message 1")
        enc2 = self.alice.encrypt("Message 2")
        enc3 = self.alice.encrypt("Message 3")

        # Bob receives out of order: 1, 3, 2
        dec1 = self.bob.decrypt(enc1)
        assert dec1 == "Message 1"

        dec3 = self.bob.decrypt(enc3)
        assert dec3 == "Message 3"

        dec2 = self.bob.decrypt(enc2)
        assert dec2 == "Message 2"

    def test_skipped_keys_stored(self):
        """Skipped message keys should be stored"""
        # Alice sends 3 messages
        enc1 = self.alice.encrypt("Message 1")
        enc2 = self.alice.encrypt("Message 2")
        enc3 = self.alice.encrypt("Message 3")

        # Bob receives only message 3 first
        self.bob.decrypt(enc3)

        # Skipped keys for messages 1 and 2 should be stored
        assert len(self.bob.state.skipped_message_keys) == 2

    def test_skipped_keys_used_once(self):
        """Skipped keys should be removed after use"""
        enc1 = self.alice.encrypt("Message 1")
        enc2 = self.alice.encrypt("Message 2")

        # Bob receives message 2 first (stores key for 1)
        self.bob.decrypt(enc2)
        assert len(self.bob.state.skipped_message_keys) == 1

        # Bob receives message 1 (uses stored key)
        self.bob.decrypt(enc1)
        assert len(self.bob.state.skipped_message_keys) == 0


class TestStatePersistence:
    """Test state serialization and restoration"""

    def setup_method(self):
        """Setup test fixtures"""
        self.shared_secret = os.urandom(32)
        self.bob_private, self.bob_public = generate_dh_keypair()

    def test_export_import_state(self):
        """Should export and import state correctly"""
        alice = DoubleRatchet.init_sender(
            shared_secret=self.shared_secret,
            recipient_public_key=self.bob_public,
            session_id="test-session",
            peer_id="bob"
        )

        # Exchange some messages to advance state
        bob = DoubleRatchet.init_receiver(
            shared_secret=self.shared_secret,
            keypair=(self.bob_private, self.bob_public)
        )

        enc = alice.encrypt("Test message")
        bob.decrypt(enc)

        # Export state
        state_dict = alice.get_state_dict()

        # Restore from state
        restored = DoubleRatchet.from_state_dict(state_dict)

        # Verify state matches
        assert restored.state.send_message_number == alice.state.send_message_number
        assert restored.state.session_id == alice.state.session_id
        assert restored.state.peer_id == alice.state.peer_id

    def test_restored_session_continues_working(self):
        """Restored session should continue working"""
        alice = DoubleRatchet.init_sender(
            shared_secret=self.shared_secret,
            recipient_public_key=self.bob_public
        )
        bob = DoubleRatchet.init_receiver(
            shared_secret=self.shared_secret,
            keypair=(self.bob_private, self.bob_public)
        )

        # Initial message
        enc1 = alice.encrypt("Before save")
        bob.decrypt(enc1)

        # Save and restore Alice
        state_dict = alice.get_state_dict()
        alice_restored = DoubleRatchet.from_state_dict(state_dict)

        # Continue communication
        enc2 = alice_restored.encrypt("After restore")
        decrypted = bob.decrypt(enc2)

        assert decrypted == "After restore"


class TestSessionManager:
    """Test session manager"""

    def setup_method(self):
        """Setup test fixtures"""
        self.manager = RatchetSessionManager()
        self.shared_secret = os.urandom(32)
        self.peer_private, self.peer_public = generate_dh_keypair()

    def test_create_session_initiator(self):
        """Should create session as initiator"""
        session = self.manager.create_session(
            peer_id="peer-1",
            shared_secret=self.shared_secret,
            peer_public_key=self.peer_public,
            is_initiator=True
        )

        assert self.manager.has_session("peer-1")
        assert session.state.sending_chain_key is not None

    def test_create_session_receiver(self):
        """Should create session as receiver"""
        keypair = generate_dh_keypair()
        session = self.manager.create_session(
            peer_id="peer-1",
            shared_secret=self.shared_secret,
            keypair=keypair,
            is_initiator=False
        )

        assert self.manager.has_session("peer-1")

    def test_encrypt_decrypt_via_manager(self):
        """Should encrypt/decrypt via manager"""
        # Create two managers (Alice and Bob)
        alice_manager = RatchetSessionManager()
        bob_manager = RatchetSessionManager()

        bob_keypair = generate_dh_keypair()

        alice_manager.create_session(
            peer_id="bob",
            shared_secret=self.shared_secret,
            peer_public_key=bob_keypair[1],
            is_initiator=True
        )

        bob_manager.create_session(
            peer_id="alice",
            shared_secret=self.shared_secret,
            keypair=bob_keypair,
            is_initiator=False
        )

        # Alice -> Bob
        encrypted = alice_manager.encrypt("bob", "Hello from manager!")
        decrypted = bob_manager.decrypt("alice", encrypted)

        assert decrypted == "Hello from manager!"

    def test_remove_session(self):
        """Should remove session"""
        self.manager.create_session(
            peer_id="peer-1",
            shared_secret=self.shared_secret,
            peer_public_key=self.peer_public,
            is_initiator=True
        )

        assert self.manager.has_session("peer-1")

        result = self.manager.remove_session("peer-1")
        assert result is True
        assert not self.manager.has_session("peer-1")

    def test_export_import_sessions(self):
        """Should export and import all sessions"""
        self.manager.create_session(
            peer_id="peer-1",
            shared_secret=self.shared_secret,
            peer_public_key=self.peer_public,
            is_initiator=True
        )

        # Export
        exported = self.manager.export_sessions()

        # Import into new manager
        new_manager = RatchetSessionManager()
        new_manager.import_sessions(exported)

        assert new_manager.has_session("peer-1")


class TestSecurityProperties:
    """Test security properties of the implementation"""

    def setup_method(self):
        """Setup test fixtures"""
        self.shared_secret = os.urandom(32)
        self.bob_private, self.bob_public = generate_dh_keypair()

    def test_different_shared_secrets_fail(self):
        """Messages encrypted with different shared secret should fail"""
        alice = DoubleRatchet.init_sender(
            shared_secret=self.shared_secret,
            recipient_public_key=self.bob_public
        )

        # Bob with different secret
        wrong_secret = os.urandom(32)
        bob = DoubleRatchet.init_receiver(
            shared_secret=wrong_secret,
            keypair=(self.bob_private, self.bob_public)
        )

        encrypted = alice.encrypt("Secret message")

        with pytest.raises(Exception):
            bob.decrypt(encrypted)

    def test_unique_ciphertext_per_message(self):
        """Same plaintext should produce different ciphertext"""
        alice = DoubleRatchet.init_sender(
            shared_secret=self.shared_secret,
            recipient_public_key=self.bob_public
        )

        plaintext = "Identical message"
        enc1 = alice.encrypt(plaintext)
        enc2 = alice.encrypt(plaintext)

        assert enc1.ciphertext != enc2.ciphertext
        assert enc1.nonce != enc2.nonce

    def test_forward_secrecy(self):
        """Compromising current keys should not expose past messages"""
        alice = DoubleRatchet.init_sender(
            shared_secret=self.shared_secret,
            recipient_public_key=self.bob_public
        )
        bob = DoubleRatchet.init_receiver(
            shared_secret=self.shared_secret,
            keypair=(self.bob_private, self.bob_public)
        )

        # Exchange messages
        enc1 = alice.encrypt("First message")
        bob.decrypt(enc1)

        enc2 = bob.encrypt("Reply")
        alice.decrypt(enc2)

        enc3 = alice.encrypt("Second message")

        # Save Alice's current keys
        current_keys = alice.state.dh_sending_keypair

        # Continue conversation (ratchet advances)
        bob.decrypt(enc3)
        enc4 = bob.encrypt("Another reply")
        alice.decrypt(enc4)

        # Keys have changed (forward secrecy)
        assert alice.state.dh_sending_keypair != current_keys

    def test_replay_protection(self):
        """Same encrypted message should not decrypt twice in normal flow"""
        alice = DoubleRatchet.init_sender(
            shared_secret=self.shared_secret,
            recipient_public_key=self.bob_public
        )
        bob = DoubleRatchet.init_receiver(
            shared_secret=self.shared_secret,
            keypair=(self.bob_private, self.bob_public)
        )

        encrypted = alice.encrypt("One-time message")

        # First decrypt works
        bob.decrypt(encrypted)

        # Second decrypt should fail (key already used)
        with pytest.raises(Exception):
            bob.decrypt(encrypted)


class TestUnicodeAndEdgeCases:
    """Test edge cases and unicode handling"""

    def setup_method(self):
        """Setup test fixtures"""
        self.shared_secret = os.urandom(32)
        self.bob_private, self.bob_public = generate_dh_keypair()

        self.alice = DoubleRatchet.init_sender(
            shared_secret=self.shared_secret,
            recipient_public_key=self.bob_public
        )
        self.bob = DoubleRatchet.init_receiver(
            shared_secret=self.shared_secret,
            keypair=(self.bob_private, self.bob_public)
        )

    def test_unicode_messages(self):
        """Should handle unicode messages"""
        messages = [
            "Hello 世界",
            "Привет мир",
            "مرحبا بالعالم",
            "🔐 Encrypted! 🎉",
            "Türkçe: öğretmen, çalışmak",
        ]

        for msg in messages:
            encrypted = self.alice.encrypt(msg)
            decrypted = self.bob.decrypt(encrypted)
            assert decrypted == msg

    def test_empty_message(self):
        """Should handle empty messages"""
        encrypted = self.alice.encrypt("")
        decrypted = self.bob.decrypt(encrypted)
        assert decrypted == ""

    def test_large_message(self):
        """Should handle large messages"""
        large_msg = "X" * 100000  # 100KB
        encrypted = self.alice.encrypt(large_msg)
        decrypted = self.bob.decrypt(encrypted)
        assert decrypted == large_msg

    def test_special_characters(self):
        """Should handle special characters"""
        msg = "Line1\nLine2\tTabbed\r\nCRLF\x00NullByte"
        encrypted = self.alice.encrypt(msg)
        decrypted = self.bob.decrypt(encrypted)
        assert decrypted == msg


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
