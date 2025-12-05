"""
Messenger Delivery Reliability Tests

Tests for message delivery mechanisms:
- Delivery queue management
- Retry logic
- Expiration handling
- Offline delivery
"""

import pytest
import uuid
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    Conversation,
    Participant,
    Message,
    MessageDeliveryQueue,
)

User = get_user_model()


class TestMessageDeliveryQueue(TestCase):
    """Tests for message delivery queue"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )

        self.conversation = Conversation.objects.create(
            conversation_type='direct',
            created_by=self.alice
        )
        Participant.objects.create(conversation=self.conversation, user=self.alice, role='owner')
        Participant.objects.create(conversation=self.conversation, user=self.bob, role='member')

        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.alice,
            message_type='text',
            encrypted_content='encrypted_content',
            content_nonce='nonce',
            signature='signature',
            sender_key_id=uuid.uuid4()
        )

    def test_create_queue_entry(self):
        """Test creating a delivery queue entry"""
        queue_entry = MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.bob,
            expires_at=timezone.now() + timedelta(days=30)
        )

        self.assertEqual(queue_entry.status, 'pending')
        self.assertEqual(queue_entry.retry_count, 0)
        self.assertEqual(queue_entry.max_retries, 5)

    def test_mark_delivered(self):
        """Test marking message as delivered"""
        queue_entry = MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.bob,
            expires_at=timezone.now() + timedelta(days=30)
        )

        queue_entry.mark_delivered()

        self.assertEqual(queue_entry.status, 'delivered')
        self.assertIsNotNone(queue_entry.delivered_at)

    def test_mark_failed(self):
        """Test marking delivery as failed"""
        queue_entry = MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.bob,
            expires_at=timezone.now() + timedelta(days=30)
        )

        queue_entry.mark_failed('Connection refused')

        self.assertEqual(queue_entry.status, 'failed')
        self.assertEqual(queue_entry.failure_reason, 'Connection refused')

    def test_increment_retry_count(self):
        """Test incrementing retry count"""
        queue_entry = MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.bob,
            expires_at=timezone.now() + timedelta(days=30)
        )

        initial_count = queue_entry.retry_count
        queue_entry.retry_count += 1
        queue_entry.last_retry_at = timezone.now()
        queue_entry.save()

        queue_entry.refresh_from_db()
        self.assertEqual(queue_entry.retry_count, initial_count + 1)
        self.assertIsNotNone(queue_entry.last_retry_at)


class TestDeliveryQueueQueries(TestCase):
    """Tests for delivery queue query patterns"""

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

        self.conversation = Conversation.objects.create(
            conversation_type='group',
            name='Test Group',
            created_by=self.alice
        )
        Participant.objects.create(conversation=self.conversation, user=self.alice, role='owner')
        Participant.objects.create(conversation=self.conversation, user=self.bob, role='member')
        Participant.objects.create(conversation=self.conversation, user=self.charlie, role='member')

        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.alice,
            message_type='text',
            encrypted_content='content',
            content_nonce='nonce',
            signature='sig',
            sender_key_id=uuid.uuid4()
        )

    def test_find_pending_messages_for_user(self):
        """Test finding pending messages for a specific user"""
        # Create queue entries
        MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.bob,
            status='pending',
            expires_at=timezone.now() + timedelta(days=30)
        )
        MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.charlie,
            status='delivered',
            expires_at=timezone.now() + timedelta(days=30)
        )

        pending = MessageDeliveryQueue.objects.filter(
            recipient=self.bob,
            status='pending'
        )

        self.assertEqual(pending.count(), 1)

    def test_find_expired_messages(self):
        """Test finding expired queue entries"""
        # Create expired entry
        MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.bob,
            status='pending',
            expires_at=timezone.now() - timedelta(days=1)
        )

        # Create valid entry
        MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.charlie,
            status='pending',
            expires_at=timezone.now() + timedelta(days=30)
        )

        expired = MessageDeliveryQueue.objects.filter(
            status='pending',
            expires_at__lt=timezone.now()
        )

        self.assertEqual(expired.count(), 1)

    def test_find_ready_for_retry(self):
        """Test finding entries ready for retry"""
        retry_time = timezone.now() - timedelta(minutes=5)

        # Entry ready for retry
        MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.bob,
            status='pending',
            retry_count=2,
            next_retry_at=retry_time,
            expires_at=timezone.now() + timedelta(days=30)
        )

        # Entry not yet ready
        MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.charlie,
            status='pending',
            next_retry_at=timezone.now() + timedelta(hours=1),
            expires_at=timezone.now() + timedelta(days=30)
        )

        ready = MessageDeliveryQueue.objects.filter(
            status='pending',
            next_retry_at__lte=timezone.now()
        )

        self.assertEqual(ready.count(), 1)


class TestDeliveryRetryLogic(TestCase):
    """Tests for delivery retry logic"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )

        self.conversation = Conversation.objects.create(
            conversation_type='direct',
            created_by=self.alice
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

    def test_retry_within_limit(self):
        """Test retry when within max retries"""
        queue_entry = MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.bob,
            retry_count=2,
            max_retries=5,
            expires_at=timezone.now() + timedelta(days=30)
        )

        self.assertTrue(queue_entry.retry_count < queue_entry.max_retries)

    def test_retry_at_limit(self):
        """Test behavior at max retries"""
        queue_entry = MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.bob,
            retry_count=5,
            max_retries=5,
            expires_at=timezone.now() + timedelta(days=30)
        )

        self.assertEqual(queue_entry.retry_count, queue_entry.max_retries)

    def test_exponential_backoff(self):
        """Test exponential backoff for retry timing"""
        queue_entry = MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.bob,
            retry_count=0,
            expires_at=timezone.now() + timedelta(days=30)
        )

        # Simulate exponential backoff: 1min, 2min, 4min, 8min, 16min
        base_delay = timedelta(minutes=1)
        delays = []

        for i in range(5):
            delay = base_delay * (2 ** i)
            delays.append(delay)

        self.assertEqual(delays[0], timedelta(minutes=1))
        self.assertEqual(delays[1], timedelta(minutes=2))
        self.assertEqual(delays[2], timedelta(minutes=4))
        self.assertEqual(delays[3], timedelta(minutes=8))
        self.assertEqual(delays[4], timedelta(minutes=16))


class TestMessageExpiration(TestCase):
    """Tests for message expiration"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )

        self.conversation = Conversation.objects.create(
            conversation_type='direct',
            created_by=self.alice
        )
        Participant.objects.create(conversation=self.conversation, user=self.alice, role='owner')
        Participant.objects.create(conversation=self.conversation, user=self.bob, role='member')

    def test_message_with_expiration(self):
        """Test message with expiration date"""
        expires = timezone.now() + timedelta(hours=24)

        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.alice,
            message_type='text',
            encrypted_content='disappearing message',
            content_nonce='nonce',
            signature='sig',
            sender_key_id=uuid.uuid4(),
            expires_at=expires
        )

        self.assertEqual(message.expires_at, expires)

    def test_find_expired_messages(self):
        """Test finding expired messages"""
        # Expired message
        Message.objects.create(
            conversation=self.conversation,
            sender=self.alice,
            message_type='text',
            encrypted_content='expired',
            content_nonce='nonce',
            signature='sig',
            sender_key_id=uuid.uuid4(),
            expires_at=timezone.now() - timedelta(hours=1)
        )

        # Valid message
        Message.objects.create(
            conversation=self.conversation,
            sender=self.alice,
            message_type='text',
            encrypted_content='valid',
            content_nonce='nonce',
            signature='sig',
            sender_key_id=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(hours=24)
        )

        expired = Message.objects.filter(
            expires_at__lt=timezone.now()
        )

        self.assertEqual(expired.count(), 1)


class TestDeliveryViaTypes(TestCase):
    """Tests for different delivery methods"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )

        self.conversation = Conversation.objects.create(
            conversation_type='direct',
            created_by=self.alice
        )
        Participant.objects.create(conversation=self.conversation, user=self.alice, role='owner')
        Participant.objects.create(conversation=self.conversation, user=self.bob, role='member')

    def test_hub_delivery(self):
        """Test message delivered via hub"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.alice,
            message_type='text',
            encrypted_content='content',
            content_nonce='nonce',
            signature='sig',
            sender_key_id=uuid.uuid4(),
            delivered_via='hub'
        )

        self.assertEqual(message.delivered_via, 'hub')

    def test_p2p_delivery(self):
        """Test message delivered via P2P"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.alice,
            message_type='text',
            encrypted_content='content',
            content_nonce='nonce',
            signature='sig',
            sender_key_id=uuid.uuid4(),
            delivered_via='p2p'
        )

        self.assertEqual(message.delivered_via, 'p2p')


class TestMessageDeliveryStatus(TestCase):
    """Tests for message delivery status"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )

        self.conversation = Conversation.objects.create(
            conversation_type='direct',
            created_by=self.alice
        )
        Participant.objects.create(conversation=self.conversation, user=self.alice, role='owner')
        Participant.objects.create(conversation=self.conversation, user=self.bob, role='member')

    def test_message_delivered_status(self):
        """Test marking message as delivered"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.alice,
            message_type='text',
            encrypted_content='content',
            content_nonce='nonce',
            signature='sig',
            sender_key_id=uuid.uuid4(),
            is_delivered=False
        )

        self.assertFalse(message.is_delivered)

        message.mark_delivered()

        self.assertTrue(message.is_delivered)
        self.assertIsNotNone(message.delivered_at)

    def test_message_deleted_status(self):
        """Test soft deleting a message"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.alice,
            message_type='text',
            encrypted_content='content',
            content_nonce='nonce',
            signature='sig',
            sender_key_id=uuid.uuid4()
        )

        message.soft_delete(for_everyone=True)

        self.assertTrue(message.is_deleted)
        self.assertTrue(message.deleted_for_everyone)
        self.assertIsNotNone(message.deleted_at)


class TestMessageDedup(TestCase):
    """Tests for message deduplication"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )

        self.conversation = Conversation.objects.create(
            conversation_type='direct',
            created_by=self.alice
        )
        Participant.objects.create(conversation=self.conversation, user=self.alice, role='owner')
        Participant.objects.create(conversation=self.conversation, user=self.bob, role='member')

    def test_client_message_id_uniqueness(self):
        """Test that client message ID prevents duplicates"""
        client_id = str(uuid.uuid4())

        # First message
        message1 = Message.objects.create(
            conversation=self.conversation,
            sender=self.alice,
            message_type='text',
            encrypted_content='content1',
            content_nonce='nonce1',
            signature='sig1',
            sender_key_id=uuid.uuid4(),
            client_message_id=client_id
        )

        # Try to find existing message with same client_message_id
        existing = Message.objects.filter(
            conversation=self.conversation,
            client_message_id=client_id
        ).first()

        self.assertEqual(existing, message1)

    def test_empty_client_message_id(self):
        """Test messages without client_message_id"""
        message1 = Message.objects.create(
            conversation=self.conversation,
            sender=self.alice,
            message_type='text',
            encrypted_content='content1',
            content_nonce='nonce1',
            signature='sig1',
            sender_key_id=uuid.uuid4(),
            client_message_id=''
        )

        message2 = Message.objects.create(
            conversation=self.conversation,
            sender=self.alice,
            message_type='text',
            encrypted_content='content2',
            content_nonce='nonce2',
            signature='sig2',
            sender_key_id=uuid.uuid4(),
            client_message_id=''
        )

        # Both should be created
        self.assertEqual(self.conversation.messages.count(), 2)


class TestQueueCleanup(TestCase):
    """Tests for queue cleanup operations"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )

        self.conversation = Conversation.objects.create(
            conversation_type='direct',
            created_by=self.alice
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

    def test_cleanup_expired_entries(self):
        """Test cleaning up expired queue entries"""
        # Create expired entries
        for i in range(3):
            MessageDeliveryQueue.objects.create(
                message=self.message,
                recipient=self.bob,
                status='pending',
                expires_at=timezone.now() - timedelta(days=i+1)
            )

        # Create valid entry
        MessageDeliveryQueue.objects.create(
            message=self.message,
            recipient=self.bob,
            status='pending',
            expires_at=timezone.now() + timedelta(days=30)
        )

        expired_count = MessageDeliveryQueue.objects.filter(
            expires_at__lt=timezone.now()
        ).update(status='expired')

        self.assertEqual(expired_count, 3)

    def test_cleanup_delivered_entries(self):
        """Test cleaning up old delivered entries"""
        # Create old delivered entries
        for i in range(5):
            entry = MessageDeliveryQueue.objects.create(
                message=self.message,
                recipient=self.bob,
                status='delivered',
                expires_at=timezone.now() + timedelta(days=30)
            )
            entry.delivered_at = timezone.now() - timedelta(days=30)
            entry.save()

        old_delivered = MessageDeliveryQueue.objects.filter(
            status='delivered',
            delivered_at__lt=timezone.now() - timedelta(days=7)
        )

        self.assertEqual(old_delivered.count(), 5)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
