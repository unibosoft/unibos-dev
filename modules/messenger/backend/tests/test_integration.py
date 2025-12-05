"""
Messenger Integration Tests

Tests for end-to-end messaging flows:
- Conversation creation and management
- Message sending and receiving
- Encryption key generation and usage
- Read receipts and reactions
- Participant management
"""

import pytest
import uuid
from datetime import timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    Conversation,
    Participant,
    Message,
    MessageReaction,
    MessageReadReceipt,
    UserEncryptionKey,
    P2PSession,
    MessageDeliveryQueue,
)
from encryption import EncryptionService, get_encryption_service

User = get_user_model()


class TestConversationCreation(APITestCase):
    """Tests for conversation creation flows"""

    def setUp(self):
        """Setup test users"""
        self.alice = User.objects.create_user(
            username='alice',
            email='alice@test.com',
            password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob',
            email='bob@test.com',
            password='testpass123'
        )
        self.charlie = User.objects.create_user(
            username='charlie',
            email='charlie@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.alice)

    def test_create_direct_conversation(self):
        """Test creating a direct message conversation"""
        response = self.client.post('/api/v1/messenger/conversations/', {
            'conversation_type': 'direct',
            'participant_ids': [str(self.bob.id)]
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['conversation_type'], 'direct')

        # Check participants
        conv = Conversation.objects.get(id=response.data['id'])
        self.assertEqual(conv.participants.count(), 2)
        self.assertTrue(conv.participants.filter(user=self.alice).exists())
        self.assertTrue(conv.participants.filter(user=self.bob).exists())

    def test_create_group_conversation(self):
        """Test creating a group conversation"""
        response = self.client.post('/api/v1/messenger/conversations/', {
            'conversation_type': 'group',
            'name': 'Test Group',
            'description': 'A test group chat',
            'participant_ids': [str(self.bob.id), str(self.charlie.id)]
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['conversation_type'], 'group')
        self.assertEqual(response.data['name'], 'Test Group')

        conv = Conversation.objects.get(id=response.data['id'])
        self.assertEqual(conv.participants.count(), 3)  # Alice + Bob + Charlie

    def test_direct_conversation_deduplication(self):
        """Test that duplicate direct conversations are not created"""
        # Create first conversation
        response1 = self.client.post('/api/v1/messenger/conversations/', {
            'conversation_type': 'direct',
            'participant_ids': [str(self.bob.id)]
        })
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        conv_id = response1.data['id']

        # Try to create same conversation again
        response2 = self.client.post('/api/v1/messenger/conversations/', {
            'conversation_type': 'direct',
            'participant_ids': [str(self.bob.id)]
        })
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['id'], conv_id)

        # Should still only have one conversation
        self.assertEqual(Conversation.objects.filter(conversation_type='direct').count(), 1)

    def test_create_encrypted_conversation(self):
        """Test creating an encrypted conversation"""
        response = self.client.post('/api/v1/messenger/conversations/', {
            'conversation_type': 'direct',
            'participant_ids': [str(self.bob.id)],
            'is_encrypted': True
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conv = Conversation.objects.get(id=response.data['id'])
        self.assertTrue(conv.is_encrypted)

    def test_create_p2p_enabled_conversation(self):
        """Test creating a P2P-enabled conversation"""
        response = self.client.post('/api/v1/messenger/conversations/', {
            'conversation_type': 'direct',
            'participant_ids': [str(self.bob.id)],
            'transport_mode': 'hybrid',
            'p2p_enabled': True
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conv = Conversation.objects.get(id=response.data['id'])
        self.assertTrue(conv.p2p_enabled)
        self.assertEqual(conv.transport_mode, 'hybrid')


class TestMessageFlow(APITestCase):
    """Tests for message sending and receiving flows"""

    def setUp(self):
        """Setup test users and conversation"""
        self.alice = User.objects.create_user(
            username='alice',
            email='alice@test.com',
            password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob',
            email='bob@test.com',
            password='testpass123'
        )

        # Create conversation
        self.conversation = Conversation.objects.create(
            conversation_type='direct',
            created_by=self.alice,
            is_encrypted=True
        )
        Participant.objects.create(conversation=self.conversation, user=self.alice, role='owner')
        Participant.objects.create(conversation=self.conversation, user=self.bob, role='member')

        # Generate encryption keys
        self.encryption_service = EncryptionService()
        self.alice_key = UserEncryptionKey.objects.create(
            user=self.alice,
            device_id='alice-device-1',
            device_name='Alice Phone',
            public_key='base64_public_key',
            encrypted_private_key='encrypted',
            signing_public_key='base64_signing_key',
            encrypted_signing_private_key='encrypted',
            is_primary=True
        )

        self.client.force_authenticate(user=self.alice)

    @patch('views.MessageViewSet._notify_new_message')
    def test_send_encrypted_message(self, mock_notify):
        """Test sending an encrypted message"""
        response = self.client.post(
            f'/api/v1/messenger/conversations/{self.conversation.id}/messages/',
            {
                'message_type': 'text',
                'encrypted_content': 'base64_encrypted_content_here',
                'content_nonce': 'base64_nonce',
                'signature': 'base64_signature',
                'sender_key_id': str(self.alice_key.id),
                'client_message_id': str(uuid.uuid4())
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message_type'], 'text')
        self.assertTrue(mock_notify.called)

        # Check message was created
        msg = Message.objects.get(id=response.data['id'])
        self.assertEqual(msg.sender, self.alice)
        self.assertTrue(msg.is_delivered)

    @patch('views.MessageViewSet._notify_new_message')
    def test_message_deduplication(self, mock_notify):
        """Test that duplicate messages are not created"""
        client_msg_id = str(uuid.uuid4())

        # Send first message
        response1 = self.client.post(
            f'/api/v1/messenger/conversations/{self.conversation.id}/messages/',
            {
                'message_type': 'text',
                'encrypted_content': 'content1',
                'content_nonce': 'nonce1',
                'signature': 'sig1',
                'sender_key_id': str(self.alice_key.id),
                'client_message_id': client_msg_id
            }
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        msg_id = response1.data['id']

        # Try to send same message again (same client_message_id)
        response2 = self.client.post(
            f'/api/v1/messenger/conversations/{self.conversation.id}/messages/',
            {
                'message_type': 'text',
                'encrypted_content': 'content2',  # Different content
                'content_nonce': 'nonce2',
                'signature': 'sig2',
                'sender_key_id': str(self.alice_key.id),
                'client_message_id': client_msg_id  # Same ID
            }
        )

        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['id'], msg_id)

        # Should still only have one message
        self.assertEqual(self.conversation.messages.count(), 1)

    @patch('views.MessageViewSet._notify_new_message')
    def test_reply_to_message(self, mock_notify):
        """Test replying to a message"""
        # Create original message
        original = Message.objects.create(
            conversation=self.conversation,
            sender=self.bob,
            message_type='text',
            encrypted_content='original',
            content_nonce='nonce',
            signature='sig',
            sender_key_id=uuid.uuid4()
        )

        # Reply to it
        response = self.client.post(
            f'/api/v1/messenger/conversations/{self.conversation.id}/messages/',
            {
                'message_type': 'text',
                'encrypted_content': 'reply_content',
                'content_nonce': 'reply_nonce',
                'signature': 'reply_sig',
                'sender_key_id': str(self.alice_key.id),
                'reply_to': str(original.id)
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        reply = Message.objects.get(id=response.data['id'])
        self.assertEqual(reply.reply_to, original)

    @patch('views.MessageViewSet._notify_new_message')
    def test_message_updates_conversation_timestamp(self, mock_notify):
        """Test that sending message updates conversation last_message_at"""
        old_time = self.conversation.last_message_at

        response = self.client.post(
            f'/api/v1/messenger/conversations/{self.conversation.id}/messages/',
            {
                'message_type': 'text',
                'encrypted_content': 'content',
                'content_nonce': 'nonce',
                'signature': 'sig',
                'sender_key_id': str(self.alice_key.id)
            }
        )

        self.conversation.refresh_from_db()
        self.assertIsNotNone(self.conversation.last_message_at)
        if old_time:
            self.assertGreater(self.conversation.last_message_at, old_time)

    @patch('views.MessageViewSet._notify_new_message')
    def test_message_increments_unread_count(self, mock_notify):
        """Test that sending message increments unread count for others"""
        bob_participant = self.conversation.participants.get(user=self.bob)
        initial_count = bob_participant.unread_count

        response = self.client.post(
            f'/api/v1/messenger/conversations/{self.conversation.id}/messages/',
            {
                'message_type': 'text',
                'encrypted_content': 'content',
                'content_nonce': 'nonce',
                'signature': 'sig',
                'sender_key_id': str(self.alice_key.id)
            }
        )

        bob_participant.refresh_from_db()
        self.assertEqual(bob_participant.unread_count, initial_count + 1)


class TestReadReceipts(APITestCase):
    """Tests for read receipts"""

    def setUp(self):
        """Setup test users, conversation, and message"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )

        self.conversation = Conversation.objects.create(
            conversation_type='direct', created_by=self.alice
        )
        Participant.objects.create(conversation=self.conversation, user=self.alice, role='owner')
        self.bob_participant = Participant.objects.create(
            conversation=self.conversation, user=self.bob, role='member'
        )

        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.alice,
            message_type='text',
            encrypted_content='content',
            content_nonce='nonce',
            signature='sig',
            sender_key_id=uuid.uuid4()
        )

    def test_mark_message_as_read(self):
        """Test marking a message as read"""
        self.client.force_authenticate(user=self.bob)

        response = self.client.post(
            f'/api/v1/messenger/conversations/{self.conversation.id}/messages/{self.message.id}/read/',
            {'device_id': 'bob-phone'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('read_at', response.data)

        # Check receipt was created
        self.assertTrue(MessageReadReceipt.objects.filter(
            message=self.message, user=self.bob
        ).exists())

    def test_mark_all_messages_as_read(self):
        """Test marking all messages in conversation as read"""
        # Create multiple messages
        for i in range(5):
            Message.objects.create(
                conversation=self.conversation,
                sender=self.alice,
                message_type='text',
                encrypted_content=f'content{i}',
                content_nonce='nonce',
                signature='sig',
                sender_key_id=uuid.uuid4()
            )

        self.bob_participant.unread_count = 5
        self.bob_participant.save()

        self.client.force_authenticate(user=self.bob)
        response = self.client.post(
            f'/api/v1/messenger/conversations/{self.conversation.id}/read-all/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.bob_participant.refresh_from_db()
        self.assertEqual(self.bob_participant.unread_count, 0)


class TestReactions(APITestCase):
    """Tests for message reactions"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )

        self.conversation = Conversation.objects.create(
            conversation_type='direct', created_by=self.alice
        )
        Participant.objects.create(conversation=self.conversation, user=self.alice, role='owner')
        Participant.objects.create(conversation=self.conversation, user=self.bob, role='member')

        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.alice,
            message_type='text',
            encrypted_content='content',
            content_nonce='nonce',
            signature='sig',
            sender_key_id=uuid.uuid4()
        )

    def test_add_reaction(self):
        """Test adding a reaction to a message"""
        self.client.force_authenticate(user=self.bob)

        response = self.client.post(
            f'/api/v1/messenger/conversations/{self.conversation.id}/messages/{self.message.id}/reactions/',
            {'emoji': 'thumbs_up'}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(MessageReaction.objects.filter(
            message=self.message, user=self.bob, emoji='thumbs_up'
        ).exists())

    def test_remove_reaction(self):
        """Test removing a reaction from a message"""
        # Add reaction first
        MessageReaction.objects.create(
            message=self.message, user=self.bob, emoji='heart'
        )

        self.client.force_authenticate(user=self.bob)
        response = self.client.delete(
            f'/api/v1/messenger/conversations/{self.conversation.id}/messages/{self.message.id}/reactions/?emoji=heart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(MessageReaction.objects.filter(
            message=self.message, user=self.bob, emoji='heart'
        ).exists())

    def test_reaction_idempotency(self):
        """Test that adding same reaction twice doesn't create duplicate"""
        self.client.force_authenticate(user=self.bob)

        # Add reaction twice
        response1 = self.client.post(
            f'/api/v1/messenger/conversations/{self.conversation.id}/messages/{self.message.id}/reactions/',
            {'emoji': 'thumbs_up'}
        )
        response2 = self.client.post(
            f'/api/v1/messenger/conversations/{self.conversation.id}/messages/{self.message.id}/reactions/',
            {'emoji': 'thumbs_up'}
        )

        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # Should only have one reaction
        self.assertEqual(
            MessageReaction.objects.filter(
                message=self.message, user=self.bob, emoji='thumbs_up'
            ).count(),
            1
        )


class TestParticipantManagement(APITestCase):
    """Tests for participant management"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )
        self.charlie = User.objects.create_user(
            username='charlie', email='charlie@test.com', password='testpass123'
        )
        self.dave = User.objects.create_user(
            username='dave', email='dave@test.com', password='testpass123'
        )

        self.conversation = Conversation.objects.create(
            conversation_type='group',
            name='Test Group',
            created_by=self.alice
        )
        Participant.objects.create(conversation=self.conversation, user=self.alice, role='owner')
        Participant.objects.create(conversation=self.conversation, user=self.bob, role='member')

    def test_add_participant_as_owner(self):
        """Test adding a participant as conversation owner"""
        self.client.force_authenticate(user=self.alice)

        response = self.client.post(
            f'/api/v1/messenger/conversations/{self.conversation.id}/participants/',
            {'user_id': str(self.charlie.id)}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.conversation.participants.filter(user=self.charlie).exists())

    def test_add_participant_as_member_fails(self):
        """Test that regular member cannot add participants"""
        self.client.force_authenticate(user=self.bob)

        response = self.client.post(
            f'/api/v1/messenger/conversations/{self.conversation.id}/participants/',
            {'user_id': str(self.charlie.id)}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_participant(self):
        """Test removing a participant"""
        # Add charlie first
        Participant.objects.create(conversation=self.conversation, user=self.charlie, role='member')

        self.client.force_authenticate(user=self.alice)
        response = self.client.delete(
            f'/api/v1/messenger/conversations/{self.conversation.id}/participants/{self.charlie.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        participant = self.conversation.participants.get(user=self.charlie)
        self.assertFalse(participant.is_active)

    def test_cannot_remove_owner(self):
        """Test that owner cannot be removed"""
        self.client.force_authenticate(user=self.alice)

        response = self.client.delete(
            f'/api/v1/messenger/conversations/{self.conversation.id}/participants/{self.alice.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_leave_conversation(self):
        """Test leaving a conversation"""
        self.client.force_authenticate(user=self.bob)

        response = self.client.delete(
            f'/api/v1/messenger/conversations/{self.conversation.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        participant = self.conversation.participants.get(user=self.bob)
        self.assertFalse(participant.is_active)
        self.assertIsNotNone(participant.left_at)


class TestEncryptionKeyManagement(APITestCase):
    """Tests for encryption key management"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )
        self.client.force_authenticate(user=self.alice)

    def test_generate_key_pair(self):
        """Test generating new encryption key pair"""
        response = self.client.post('/api/v1/messenger/keys/generate/', {
            'device_id': 'alice-phone-1',
            'device_name': 'Alice iPhone',
            'set_as_primary': True
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('key_id', response.data)
        self.assertIn('public_key', response.data)
        self.assertIn('private_key', response.data)
        self.assertIn('signing_public_key', response.data)
        self.assertIn('signing_private_key', response.data)

        # Verify key was stored
        self.assertTrue(UserEncryptionKey.objects.filter(
            user=self.alice,
            device_id='alice-phone-1',
            is_primary=True
        ).exists())

    def test_generate_key_pair_duplicate_device_fails(self):
        """Test that generating key for same device twice fails"""
        # Create first key
        UserEncryptionKey.objects.create(
            user=self.alice,
            device_id='device-1',
            public_key='key',
            encrypted_private_key='encrypted',
            signing_public_key='key',
            encrypted_signing_private_key='encrypted'
        )

        # Try to create again
        response = self.client.post('/api/v1/messenger/keys/generate/', {
            'device_id': 'device-1'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_keys(self):
        """Test listing user's encryption keys"""
        UserEncryptionKey.objects.create(
            user=self.alice,
            device_id='device-1',
            device_name='Phone',
            public_key='key1',
            encrypted_private_key='encrypted',
            signing_public_key='key',
            encrypted_signing_private_key='encrypted'
        )
        UserEncryptionKey.objects.create(
            user=self.alice,
            device_id='device-2',
            device_name='Tablet',
            public_key='key2',
            encrypted_private_key='encrypted',
            signing_public_key='key',
            encrypted_signing_private_key='encrypted'
        )

        response = self.client.get('/api/v1/messenger/keys/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_revoke_key(self):
        """Test revoking an encryption key"""
        key = UserEncryptionKey.objects.create(
            user=self.alice,
            device_id='device-1',
            public_key='key',
            encrypted_private_key='encrypted',
            signing_public_key='key',
            encrypted_signing_private_key='encrypted'
        )

        response = self.client.post(f'/api/v1/messenger/keys/{key.id}/revoke/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        key.refresh_from_db()
        self.assertFalse(key.is_active)
        self.assertIsNotNone(key.revoked_at)

    def test_get_other_user_public_keys(self):
        """Test getting another user's public keys"""
        # Create Bob's keys
        UserEncryptionKey.objects.create(
            user=self.bob,
            device_id='bob-device',
            public_key='bob_public_key',
            encrypted_private_key='encrypted',
            signing_public_key='bob_signing_key',
            encrypted_signing_private_key='encrypted',
            is_primary=True
        )

        response = self.client.get(f'/api/v1/messenger/keys/public/{self.bob.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['public_key'], 'bob_public_key')


class TestMessageDeliveryQueue(TestCase):
    """Tests for offline message delivery queue"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )

        self.conversation = Conversation.objects.create(
            conversation_type='direct', created_by=self.alice
        )
        Participant.objects.create(conversation=self.conversation, user=self.alice, role='owner')
        Participant.objects.create(conversation=self.conversation, user=self.bob, role='member')

        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.alice,
            message_type='text',
            encrypted_content='content',
            content_nonce='nonce',
            signature='sig',
            sender_key_id=uuid.uuid4()
        )

    def test_queue_message_for_delivery(self):
        """Test queuing a message for offline delivery"""
        queue_entry = MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.bob,
            expires_at=timezone.now() + timedelta(days=30)
        )

        self.assertEqual(queue_entry.status, 'pending')
        self.assertEqual(queue_entry.retry_count, 0)

    def test_mark_as_delivered(self):
        """Test marking queued message as delivered"""
        queue_entry = MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.bob,
            expires_at=timezone.now() + timedelta(days=30)
        )

        queue_entry.mark_delivered()

        self.assertEqual(queue_entry.status, 'delivered')
        self.assertIsNotNone(queue_entry.delivered_at)

    def test_mark_as_failed(self):
        """Test marking queued message as failed"""
        queue_entry = MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.bob,
            expires_at=timezone.now() + timedelta(days=30)
        )

        queue_entry.mark_failed('Connection timeout')

        self.assertEqual(queue_entry.status, 'failed')
        self.assertEqual(queue_entry.failure_reason, 'Connection timeout')


class TestP2PSession(TestCase):
    """Tests for P2P session management"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )

    def test_create_p2p_session(self):
        """Test creating a P2P session"""
        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob,
            status='initiating'
        )

        self.assertEqual(session.status, 'initiating')
        self.assertEqual(session.messages_sent, 0)

    def test_connect_p2p_session(self):
        """Test connecting a P2P session"""
        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob,
            status='initiating'
        )

        session.connect()

        self.assertEqual(session.status, 'connected')
        self.assertIsNotNone(session.connected_at)

    def test_disconnect_p2p_session(self):
        """Test disconnecting a P2P session"""
        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob,
            status='connected'
        )

        session.disconnect()

        self.assertEqual(session.status, 'disconnected')
        self.assertIsNotNone(session.disconnected_at)


class TestEndToEndEncryptionFlow(TestCase):
    """Tests for complete E2E encryption flow"""

    def setUp(self):
        """Setup test fixtures"""
        self.encryption_service = EncryptionService()

    def test_full_message_flow(self):
        """Test complete encrypted message flow between two users"""
        # Alice generates keys
        alice_keys = self.encryption_service.generate_user_keypairs()

        # Bob generates keys
        bob_keys = self.encryption_service.generate_user_keypairs()

        # Alice sends message to Bob
        plaintext = "Hello Bob! This is a secret message."

        encrypted = self.encryption_service.encrypt_message(
            plaintext=plaintext,
            sender_private_key=alice_keys['encryption'].private_key,
            recipient_public_key=bob_keys['encryption'].public_key,
            sender_signing_key=alice_keys['signing'].private_key
        )

        # Simulate serialization (what would be stored in DB/sent over network)
        serialized = self.encryption_service.serialize_encrypted_message(encrypted)

        # Bob receives and deserializes
        deserialized = self.encryption_service.deserialize_encrypted_message(serialized)

        # Bob decrypts
        decrypted = self.encryption_service.decrypt_message(
            encrypted_message=deserialized,
            recipient_private_key=bob_keys['encryption'].private_key,
            sender_public_key=alice_keys['encryption'].public_key,
            sender_signing_public_key=alice_keys['signing'].public_key
        )

        self.assertEqual(decrypted, plaintext)

    def test_group_encryption_flow(self):
        """Test complete group encryption flow"""
        # Group members generate keys
        alice_keys = self.encryption_service.generate_user_keypairs()
        bob_keys = self.encryption_service.generate_user_keypairs()
        charlie_keys = self.encryption_service.generate_user_keypairs()

        # Alice creates group key
        group_key = self.encryption_service.generate_group_key()

        # Alice encrypts group key for each member
        bob_encrypted_key = self.encryption_service.encrypt_group_key(
            group_key=group_key,
            recipient_public_key=bob_keys['encryption'].public_key,
            sender_private_key=alice_keys['encryption'].private_key
        )

        charlie_encrypted_key = self.encryption_service.encrypt_group_key(
            group_key=group_key,
            recipient_public_key=charlie_keys['encryption'].public_key,
            sender_private_key=alice_keys['encryption'].private_key
        )

        # Bob decrypts group key
        bob_group_key = self.encryption_service.decrypt_group_key(
            encrypted_group_key=bob_encrypted_key,
            sender_public_key=alice_keys['encryption'].public_key,
            recipient_private_key=bob_keys['encryption'].private_key
        )

        # Alice sends message to group
        plaintext = "Hello group!"

        encrypted = self.encryption_service.encrypt_with_group_key(
            plaintext=plaintext,
            group_key=group_key,
            sender_signing_key=alice_keys['signing'].private_key
        )

        # Bob decrypts with his copy of group key
        decrypted = self.encryption_service.decrypt_with_group_key(
            encrypted_message=encrypted,
            group_key=bob_group_key,
            sender_signing_public_key=alice_keys['signing'].public_key
        )

        self.assertEqual(decrypted, plaintext)
        self.assertEqual(bob_group_key, group_key)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
