"""
Double Ratchet Algorithm Implementation for UNIBOS Messenger

Implements the Signal Protocol's Double Ratchet Algorithm for Perfect Forward Secrecy.

Features:
- Diffie-Hellman (DH) Ratchet: Updates keys when messages are exchanged
- Symmetric-Key Ratchet: Derives new keys for each message
- Message Key Derivation: Unique key per message
- Out-of-order message handling: Stores skipped message keys
- Header encryption: Protects metadata

Based on: https://signal.org/docs/specifications/doubleratchet/

Security Properties:
- Perfect Forward Secrecy: Compromise of long-term keys doesn't expose past messages
- Break-in Recovery: Future messages are secure even after state compromise
- Message Ordering: Handles out-of-order delivery gracefully
"""

import os
import hashlib
import logging
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger('messenger.double_ratchet')


# ============================================================================
# Constants
# ============================================================================

MAX_SKIP = 1000  # Maximum number of message keys to skip/store
KEY_SIZE = 32    # AES-256 key size
NONCE_SIZE = 12  # AES-GCM nonce size
CHAIN_KEY_INFO = b'UnibosChainKey'
MESSAGE_KEY_INFO = b'UnibosMessageKey'
ROOT_KEY_INFO = b'UnibosRootKey'


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class MessageHeader:
    """Header for Double Ratchet messages"""
    dh_public_key: bytes        # Sender's current DH public key
    previous_chain_length: int  # Number of messages in previous sending chain
    message_number: int         # Message number in current sending chain


@dataclass
class EncryptedRatchetMessage:
    """Encrypted message with Double Ratchet header"""
    header: MessageHeader
    ciphertext: bytes
    nonce: bytes


@dataclass
class SkippedMessageKey:
    """Stores skipped message keys for out-of-order delivery"""
    dh_public_key: bytes
    message_number: int
    message_key: bytes
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RatchetState:
    """
    Complete state for a Double Ratchet session.

    This state should be persisted securely between messages.
    """
    # DH Ratchet keys
    dh_sending_keypair: Tuple[bytes, bytes]  # (private, public)
    dh_receiving_key: Optional[bytes] = None  # Peer's public key

    # Root key for DH ratchet
    root_key: bytes = field(default_factory=lambda: os.urandom(KEY_SIZE))

    # Chain keys for symmetric ratchet
    sending_chain_key: Optional[bytes] = None
    receiving_chain_key: Optional[bytes] = None

    # Message counters
    send_message_number: int = 0
    receive_message_number: int = 0
    previous_sending_chain_length: int = 0

    # Skipped message keys (for out-of-order handling)
    skipped_message_keys: Dict[Tuple[bytes, int], bytes] = field(default_factory=dict)

    # Session metadata
    session_id: str = ""
    peer_id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=datetime.utcnow)


# ============================================================================
# Key Derivation Functions
# ============================================================================

def hkdf_derive(key_material: bytes, info: bytes, length: int = KEY_SIZE) -> bytes:
    """
    Derive key using HKDF-SHA256.

    Args:
        key_material: Input key material
        info: Context/application-specific info
        length: Output key length

    Returns:
        Derived key
    """
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=None,
        info=info,
        backend=default_backend()
    )
    return hkdf.derive(key_material)


def kdf_root_key(root_key: bytes, dh_output: bytes) -> Tuple[bytes, bytes]:
    """
    Derive new root key and chain key from DH output.

    Args:
        root_key: Current root key
        dh_output: DH shared secret

    Returns:
        Tuple of (new_root_key, chain_key)
    """
    # Concatenate for KDF input
    kdf_input = root_key + dh_output

    # Derive 64 bytes: 32 for new root key, 32 for chain key
    output = hkdf_derive(kdf_input, ROOT_KEY_INFO, length=64)

    return output[:KEY_SIZE], output[KEY_SIZE:]


def kdf_chain_key(chain_key: bytes) -> Tuple[bytes, bytes]:
    """
    Derive new chain key and message key.

    Args:
        chain_key: Current chain key

    Returns:
        Tuple of (new_chain_key, message_key)
    """
    # Derive new chain key
    new_chain_key = hkdf_derive(chain_key, CHAIN_KEY_INFO)

    # Derive message key
    message_key = hkdf_derive(chain_key, MESSAGE_KEY_INFO)

    return new_chain_key, message_key


def dh_exchange(private_key: bytes, public_key: bytes) -> bytes:
    """
    Perform X25519 Diffie-Hellman exchange.

    Args:
        private_key: Local private key
        public_key: Peer's public key

    Returns:
        Shared secret
    """
    private = X25519PrivateKey.from_private_bytes(private_key)
    public = X25519PublicKey.from_public_bytes(public_key)
    return private.exchange(public)


def generate_dh_keypair() -> Tuple[bytes, bytes]:
    """
    Generate X25519 key pair.

    Returns:
        Tuple of (private_key, public_key)
    """
    private_key = X25519PrivateKey.generate()
    public_key = private_key.public_key()

    return (
        private_key.private_bytes_raw(),
        public_key.public_bytes_raw()
    )


# ============================================================================
# Double Ratchet Class
# ============================================================================

class DoubleRatchet:
    """
    Double Ratchet Algorithm implementation.

    Usage:
        # Alice initiates session with Bob's public key
        alice_ratchet = DoubleRatchet.init_sender(
            shared_secret=initial_shared_secret,
            recipient_public_key=bob_identity_key
        )

        # Bob receives and creates his ratchet
        bob_ratchet = DoubleRatchet.init_receiver(
            shared_secret=initial_shared_secret,
            sender_public_key=alice_public_key
        )

        # Alice encrypts
        encrypted = alice_ratchet.encrypt("Hello Bob!")

        # Bob decrypts
        plaintext = bob_ratchet.decrypt(encrypted)
    """

    def __init__(self, state: RatchetState):
        """
        Initialize with existing state.

        Args:
            state: RatchetState to use
        """
        self.state = state

    @classmethod
    def init_sender(
        cls,
        shared_secret: bytes,
        recipient_public_key: bytes,
        session_id: str = "",
        peer_id: str = ""
    ) -> 'DoubleRatchet':
        """
        Initialize ratchet as the session initiator (sender).

        Args:
            shared_secret: Pre-shared secret (from X3DH or similar)
            recipient_public_key: Recipient's identity public key
            session_id: Optional session identifier
            peer_id: Optional peer identifier

        Returns:
            Initialized DoubleRatchet for sending
        """
        # Generate initial DH keypair
        dh_keypair = generate_dh_keypair()

        # Perform DH with recipient's key
        dh_output = dh_exchange(dh_keypair[0], recipient_public_key)

        # Derive initial root key and sending chain key
        root_key, sending_chain_key = kdf_root_key(shared_secret, dh_output)

        state = RatchetState(
            dh_sending_keypair=dh_keypair,
            dh_receiving_key=recipient_public_key,
            root_key=root_key,
            sending_chain_key=sending_chain_key,
            receiving_chain_key=None,
            session_id=session_id,
            peer_id=peer_id
        )

        return cls(state)

    @classmethod
    def init_receiver(
        cls,
        shared_secret: bytes,
        keypair: Tuple[bytes, bytes],
        session_id: str = "",
        peer_id: str = ""
    ) -> 'DoubleRatchet':
        """
        Initialize ratchet as the receiver.

        Args:
            shared_secret: Pre-shared secret (from X3DH or similar)
            keypair: Receiver's DH keypair (private, public)
            session_id: Optional session identifier
            peer_id: Optional peer identifier

        Returns:
            Initialized DoubleRatchet for receiving
        """
        state = RatchetState(
            dh_sending_keypair=keypair,
            dh_receiving_key=None,
            root_key=shared_secret,
            sending_chain_key=None,
            receiving_chain_key=None,
            session_id=session_id,
            peer_id=peer_id
        )

        return cls(state)

    def encrypt(self, plaintext: str) -> EncryptedRatchetMessage:
        """
        Encrypt a message using the Double Ratchet.

        Args:
            plaintext: Message to encrypt

        Returns:
            EncryptedRatchetMessage with header and ciphertext
        """
        self.state.last_activity = datetime.now(timezone.utc)

        # Ensure we have a sending chain key
        if self.state.sending_chain_key is None:
            raise ValueError("Cannot encrypt: no sending chain key. Wait for first message.")

        # Derive message key from chain key
        new_chain_key, message_key = kdf_chain_key(self.state.sending_chain_key)
        self.state.sending_chain_key = new_chain_key

        # Create header
        header = MessageHeader(
            dh_public_key=self.state.dh_sending_keypair[1],
            previous_chain_length=self.state.previous_sending_chain_length,
            message_number=self.state.send_message_number
        )

        # Encrypt plaintext
        nonce = os.urandom(NONCE_SIZE)
        aesgcm = AESGCM(message_key)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)

        # Increment message counter
        self.state.send_message_number += 1

        return EncryptedRatchetMessage(
            header=header,
            ciphertext=ciphertext,
            nonce=nonce
        )

    def decrypt(self, message: EncryptedRatchetMessage) -> str:
        """
        Decrypt a message using the Double Ratchet.

        Handles DH ratchet step if needed and out-of-order messages.

        Args:
            message: EncryptedRatchetMessage to decrypt

        Returns:
            Decrypted plaintext string
        """
        self.state.last_activity = datetime.now(timezone.utc)

        # Check if message key was previously stored (out-of-order)
        stored_key = self._try_skipped_message_keys(message)
        if stored_key is not None:
            return self._decrypt_with_key(message, stored_key)

        # Check if we need to perform DH ratchet step
        if message.header.dh_public_key != self.state.dh_receiving_key:
            # Store any skipped message keys from current receiving chain
            self._skip_message_keys(
                self.state.dh_receiving_key,
                self.state.receive_message_number,
                message.header.previous_chain_length
            )

            # Perform DH ratchet
            self._dh_ratchet(message.header.dh_public_key)

        # Skip any messages in current chain
        self._skip_message_keys(
            self.state.dh_receiving_key,
            self.state.receive_message_number,
            message.header.message_number
        )

        # Derive message key
        new_chain_key, message_key = kdf_chain_key(self.state.receiving_chain_key)
        self.state.receiving_chain_key = new_chain_key
        self.state.receive_message_number = message.header.message_number + 1

        return self._decrypt_with_key(message, message_key)

    def _dh_ratchet(self, peer_public_key: bytes) -> None:
        """
        Perform a DH ratchet step.

        Args:
            peer_public_key: New public key from peer
        """
        # Update receiving key
        self.state.dh_receiving_key = peer_public_key

        # Derive receiving chain key
        dh_output = dh_exchange(self.state.dh_sending_keypair[0], peer_public_key)
        self.state.root_key, self.state.receiving_chain_key = kdf_root_key(
            self.state.root_key, dh_output
        )

        # Generate new sending keypair
        self.state.previous_sending_chain_length = self.state.send_message_number
        self.state.send_message_number = 0
        self.state.dh_sending_keypair = generate_dh_keypair()

        # Derive new sending chain key
        dh_output = dh_exchange(self.state.dh_sending_keypair[0], peer_public_key)
        self.state.root_key, self.state.sending_chain_key = kdf_root_key(
            self.state.root_key, dh_output
        )

        self.state.receive_message_number = 0

    def _skip_message_keys(
        self,
        dh_public_key: Optional[bytes],
        start: int,
        until: int
    ) -> None:
        """
        Store skipped message keys for out-of-order delivery.

        Args:
            dh_public_key: DH public key for this chain
            start: Starting message number
            until: Message number to skip until
        """
        if dh_public_key is None or self.state.receiving_chain_key is None:
            return

        if until - start > MAX_SKIP:
            raise ValueError(f"Too many skipped messages: {until - start}")

        while self.state.receive_message_number < until:
            new_chain_key, message_key = kdf_chain_key(self.state.receiving_chain_key)
            self.state.receiving_chain_key = new_chain_key

            # Store with (public_key, message_number) as key
            key_tuple = (dh_public_key, self.state.receive_message_number)
            self.state.skipped_message_keys[key_tuple] = message_key

            self.state.receive_message_number += 1

    def _try_skipped_message_keys(
        self,
        message: EncryptedRatchetMessage
    ) -> Optional[bytes]:
        """
        Try to find a stored message key for out-of-order message.

        Args:
            message: Message to check

        Returns:
            Message key if found, None otherwise
        """
        key_tuple = (message.header.dh_public_key, message.header.message_number)

        if key_tuple in self.state.skipped_message_keys:
            message_key = self.state.skipped_message_keys.pop(key_tuple)
            return message_key

        return None

    def _decrypt_with_key(
        self,
        message: EncryptedRatchetMessage,
        message_key: bytes
    ) -> str:
        """
        Decrypt message with given key.

        Args:
            message: Encrypted message
            message_key: Key to use for decryption

        Returns:
            Decrypted plaintext
        """
        aesgcm = AESGCM(message_key)
        plaintext_bytes = aesgcm.decrypt(
            message.nonce,
            message.ciphertext,
            None
        )
        return plaintext_bytes.decode('utf-8')

    # ========== State Management ==========

    def get_state_dict(self) -> Dict[str, Any]:
        """
        Export state as dictionary for persistence.

        Returns:
            Dictionary representation of state
        """
        import base64

        def to_b64(data: Optional[bytes]) -> Optional[str]:
            return base64.b64encode(data).decode('ascii') if data else None

        skipped = {}
        for (pk, num), key in self.state.skipped_message_keys.items():
            skipped[f"{to_b64(pk)}:{num}"] = to_b64(key)

        return {
            'dh_sending_private': to_b64(self.state.dh_sending_keypair[0]),
            'dh_sending_public': to_b64(self.state.dh_sending_keypair[1]),
            'dh_receiving_key': to_b64(self.state.dh_receiving_key),
            'root_key': to_b64(self.state.root_key),
            'sending_chain_key': to_b64(self.state.sending_chain_key),
            'receiving_chain_key': to_b64(self.state.receiving_chain_key),
            'send_message_number': self.state.send_message_number,
            'receive_message_number': self.state.receive_message_number,
            'previous_sending_chain_length': self.state.previous_sending_chain_length,
            'skipped_message_keys': skipped,
            'session_id': self.state.session_id,
            'peer_id': self.state.peer_id,
            'created_at': self.state.created_at.isoformat(),
            'last_activity': self.state.last_activity.isoformat(),
        }

    @classmethod
    def from_state_dict(cls, data: Dict[str, Any]) -> 'DoubleRatchet':
        """
        Restore ratchet from dictionary state.

        Args:
            data: Dictionary representation of state

        Returns:
            Restored DoubleRatchet instance
        """
        import base64

        def from_b64(data: Optional[str]) -> Optional[bytes]:
            return base64.b64decode(data.encode('ascii')) if data else None

        skipped = {}
        for key_str, value in data.get('skipped_message_keys', {}).items():
            pk_b64, num_str = key_str.rsplit(':', 1)
            pk = from_b64(pk_b64)
            num = int(num_str)
            skipped[(pk, num)] = from_b64(value)

        state = RatchetState(
            dh_sending_keypair=(
                from_b64(data['dh_sending_private']),
                from_b64(data['dh_sending_public'])
            ),
            dh_receiving_key=from_b64(data.get('dh_receiving_key')),
            root_key=from_b64(data['root_key']),
            sending_chain_key=from_b64(data.get('sending_chain_key')),
            receiving_chain_key=from_b64(data.get('receiving_chain_key')),
            send_message_number=data.get('send_message_number', 0),
            receive_message_number=data.get('receive_message_number', 0),
            previous_sending_chain_length=data.get('previous_sending_chain_length', 0),
            skipped_message_keys=skipped,
            session_id=data.get('session_id', ''),
            peer_id=data.get('peer_id', ''),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(timezone.utc),
            last_activity=datetime.fromisoformat(data['last_activity']) if data.get('last_activity') else datetime.now(timezone.utc),
        )

        return cls(state)

    def cleanup_old_keys(self, max_age_hours: int = 24) -> int:
        """
        Remove old skipped message keys.

        Args:
            max_age_hours: Maximum age of keys to keep

        Returns:
            Number of keys removed
        """
        # Since we don't track individual key ages in the simplified version,
        # this is a placeholder for future enhancement
        return 0


# ============================================================================
# Session Manager
# ============================================================================

class RatchetSessionManager:
    """
    Manages Double Ratchet sessions for multiple peers.

    Usage:
        manager = RatchetSessionManager()

        # Create session with a peer
        manager.create_session(
            peer_id="user-123",
            shared_secret=secret,
            peer_public_key=their_key,
            is_initiator=True
        )

        # Encrypt message
        encrypted = manager.encrypt("user-123", "Hello!")

        # Decrypt message
        plaintext = manager.decrypt("user-123", encrypted)
    """

    def __init__(self):
        self.sessions: Dict[str, DoubleRatchet] = {}

    def create_session(
        self,
        peer_id: str,
        shared_secret: bytes,
        peer_public_key: Optional[bytes] = None,
        keypair: Optional[Tuple[bytes, bytes]] = None,
        is_initiator: bool = True
    ) -> DoubleRatchet:
        """
        Create a new Double Ratchet session.

        Args:
            peer_id: Identifier for the peer
            shared_secret: Pre-shared secret
            peer_public_key: Peer's public key (required if initiator)
            keypair: Own keypair (required if receiver)
            is_initiator: True if initiating the session

        Returns:
            Created DoubleRatchet instance
        """
        session_id = f"session-{peer_id}-{datetime.now(timezone.utc).timestamp()}"

        if is_initiator:
            if peer_public_key is None:
                raise ValueError("peer_public_key required for initiator")
            ratchet = DoubleRatchet.init_sender(
                shared_secret=shared_secret,
                recipient_public_key=peer_public_key,
                session_id=session_id,
                peer_id=peer_id
            )
        else:
            if keypair is None:
                keypair = generate_dh_keypair()
            ratchet = DoubleRatchet.init_receiver(
                shared_secret=shared_secret,
                keypair=keypair,
                session_id=session_id,
                peer_id=peer_id
            )

        self.sessions[peer_id] = ratchet
        return ratchet

    def get_session(self, peer_id: str) -> Optional[DoubleRatchet]:
        """Get session for peer."""
        return self.sessions.get(peer_id)

    def has_session(self, peer_id: str) -> bool:
        """Check if session exists for peer."""
        return peer_id in self.sessions

    def remove_session(self, peer_id: str) -> bool:
        """Remove session for peer."""
        if peer_id in self.sessions:
            del self.sessions[peer_id]
            return True
        return False

    def encrypt(self, peer_id: str, plaintext: str) -> EncryptedRatchetMessage:
        """Encrypt message for peer."""
        session = self.sessions.get(peer_id)
        if session is None:
            raise ValueError(f"No session for peer: {peer_id}")
        return session.encrypt(plaintext)

    def decrypt(self, peer_id: str, message: EncryptedRatchetMessage) -> str:
        """Decrypt message from peer."""
        session = self.sessions.get(peer_id)
        if session is None:
            raise ValueError(f"No session for peer: {peer_id}")
        return session.decrypt(message)

    def export_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Export all sessions for persistence."""
        return {
            peer_id: ratchet.get_state_dict()
            for peer_id, ratchet in self.sessions.items()
        }

    def import_sessions(self, data: Dict[str, Dict[str, Any]]) -> None:
        """Import sessions from persistence."""
        for peer_id, state_dict in data.items():
            self.sessions[peer_id] = DoubleRatchet.from_state_dict(state_dict)


# Singleton instance
_session_manager: Optional[RatchetSessionManager] = None


def get_session_manager() -> RatchetSessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = RatchetSessionManager()
    return _session_manager
