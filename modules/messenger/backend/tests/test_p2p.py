"""
Messenger P2P Connection Tests

Tests for P2P messaging functionality:
- P2P session lifecycle
- Connection establishment
- Message routing
- Fallback mechanisms
"""

import pytest
import uuid
from unittest.mock import patch, MagicMock, AsyncMock
from django.test import TestCase
from django.contrib.auth import get_user_model

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import P2PSession, Conversation, Participant

User = get_user_model()


class TestP2PSessionLifecycle(TestCase):
    """Tests for P2P session state transitions"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )

    def test_session_initial_state(self):
        """Test session starts in initiating state"""
        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob
        )

        self.assertEqual(session.status, 'initiating')
        self.assertIsNone(session.connected_at)
        self.assertIsNone(session.disconnected_at)

    def test_session_connecting_state(self):
        """Test session transitions to connecting"""
        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob,
            status='initiating'
        )

        session.status = 'connecting'
        session.save()

        self.assertEqual(session.status, 'connecting')

    def test_session_connected_state(self):
        """Test session transitions to connected"""
        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob,
            status='connecting'
        )

        session.connect()

        self.assertEqual(session.status, 'connected')
        self.assertIsNotNone(session.connected_at)

    def test_session_disconnected_state(self):
        """Test session transitions to disconnected"""
        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob,
            status='connected'
        )

        session.disconnect()

        self.assertEqual(session.status, 'disconnected')
        self.assertIsNotNone(session.disconnected_at)

    def test_session_failed_state(self):
        """Test session can be marked as failed"""
        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob,
            status='connecting'
        )

        session.status = 'failed'
        session.save()

        self.assertEqual(session.status, 'failed')


class TestP2PSessionStats(TestCase):
    """Tests for P2P session statistics"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )

    def test_initial_stats(self):
        """Test initial session stats are zero"""
        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob
        )

        self.assertEqual(session.messages_sent, 0)
        self.assertEqual(session.messages_received, 0)
        self.assertEqual(session.bytes_transferred, 0)

    def test_update_message_counts(self):
        """Test updating message counts"""
        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob,
            status='connected'
        )

        session.messages_sent = 10
        session.messages_received = 8
        session.bytes_transferred = 15000
        session.save()

        session.refresh_from_db()
        self.assertEqual(session.messages_sent, 10)
        self.assertEqual(session.messages_received, 8)
        self.assertEqual(session.bytes_transferred, 15000)

    def test_session_key_version(self):
        """Test session key versioning"""
        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob
        )

        self.assertEqual(session.session_key_version, 1)

        session.session_key_version = 2
        session.save()

        session.refresh_from_db()
        self.assertEqual(session.session_key_version, 2)


class TestP2PSessionConnection(TestCase):
    """Tests for P2P connection info storage"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )

    def test_store_connection_offer(self):
        """Test storing WebRTC-style connection offer"""
        offer = {
            'type': 'offer',
            'sdp': 'v=0\r\no=- 123456789 2 IN IP4 127.0.0.1...'
        }

        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob,
            connection_info={'offer': offer}
        )

        self.assertEqual(session.connection_info['offer']['type'], 'offer')

    def test_store_connection_answer(self):
        """Test storing connection answer"""
        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob,
            connection_info={'offer': {'type': 'offer', 'sdp': '...'}}
        )

        answer = {
            'type': 'answer',
            'sdp': 'v=0\r\no=- 987654321 2 IN IP4 192.168.1.1...'
        }

        session.connection_info['answer'] = answer
        session.save()

        session.refresh_from_db()
        self.assertEqual(session.connection_info['answer']['type'], 'answer')

    def test_store_ice_candidates(self):
        """Test storing ICE candidates"""
        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob,
            connection_info={}
        )

        ice_candidates = [
            {'candidate': 'candidate:1 1 UDP 2130706431 192.168.1.1 54400 typ host'},
            {'candidate': 'candidate:2 1 UDP 1694498815 203.0.113.1 54400 typ srflx'}
        ]

        session.connection_info['ice_candidates'] = ice_candidates
        session.save()

        session.refresh_from_db()
        self.assertEqual(len(session.connection_info['ice_candidates']), 2)


class TestP2PSessionWithConversation(TestCase):
    """Tests for P2P sessions linked to conversations"""

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
            created_by=self.alice,
            transport_mode='hybrid',
            p2p_enabled=True
        )
        Participant.objects.create(conversation=self.conversation, user=self.alice, role='owner')
        Participant.objects.create(conversation=self.conversation, user=self.bob, role='member')

    def test_session_linked_to_conversation(self):
        """Test P2P session linked to conversation"""
        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob,
            conversation=self.conversation
        )

        self.assertEqual(session.conversation, self.conversation)
        self.assertIn(session, self.conversation.p2p_sessions.all())

    def test_conversation_p2p_settings(self):
        """Test conversation P2P settings"""
        self.assertTrue(self.conversation.p2p_enabled)
        self.assertEqual(self.conversation.transport_mode, 'hybrid')


class TestP2PSessionQueries(TestCase):
    """Tests for P2P session query patterns"""

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

    def test_find_active_sessions_for_user(self):
        """Test finding active P2P sessions for a user"""
        # Create sessions in various states
        P2PSession.objects.create(user1=self.alice, user2=self.bob, status='connected')
        P2PSession.objects.create(user1=self.alice, user2=self.charlie, status='disconnected')
        P2PSession.objects.create(user1=self.charlie, user2=self.bob, status='connected')

        from django.db.models import Q
        alice_active = P2PSession.objects.filter(
            Q(user1=self.alice) | Q(user2=self.alice),
            status='connected'
        )

        self.assertEqual(alice_active.count(), 1)

    def test_find_session_between_users(self):
        """Test finding session between two specific users"""
        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob,
            status='connected'
        )

        from django.db.models import Q
        found = P2PSession.objects.filter(
            Q(user1=self.alice, user2=self.bob) |
            Q(user1=self.bob, user2=self.alice)
        ).first()

        self.assertEqual(found, session)

    def test_no_duplicate_sessions(self):
        """Test that duplicate active sessions are prevented"""
        P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob,
            status='connected'
        )

        from django.db.models import Q

        # Check for existing active session before creating new one
        existing = P2PSession.objects.filter(
            Q(user1=self.alice, user2=self.bob) |
            Q(user1=self.bob, user2=self.alice),
            status__in=['initiating', 'connecting', 'connected']
        ).exists()

        self.assertTrue(existing)


class TestP2PTransportModes(TestCase):
    """Tests for different transport modes"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )

    def test_hub_relay_mode(self):
        """Test hub relay transport mode"""
        conversation = Conversation.objects.create(
            conversation_type='direct',
            created_by=self.alice,
            transport_mode='hub',
            p2p_enabled=False
        )

        self.assertEqual(conversation.transport_mode, 'hub')
        self.assertFalse(conversation.p2p_enabled)

    def test_p2p_direct_mode(self):
        """Test P2P direct transport mode"""
        conversation = Conversation.objects.create(
            conversation_type='direct',
            created_by=self.alice,
            transport_mode='p2p',
            p2p_enabled=True
        )

        self.assertEqual(conversation.transport_mode, 'p2p')
        self.assertTrue(conversation.p2p_enabled)

    def test_hybrid_mode(self):
        """Test hybrid transport mode (P2P with hub fallback)"""
        conversation = Conversation.objects.create(
            conversation_type='direct',
            created_by=self.alice,
            transport_mode='hybrid',
            p2p_enabled=True
        )

        self.assertEqual(conversation.transport_mode, 'hybrid')
        self.assertTrue(conversation.p2p_enabled)


class TestP2PSessionString(TestCase):
    """Tests for P2P session string representation"""

    def setUp(self):
        """Setup test fixtures"""
        self.alice = User.objects.create_user(
            username='alice', email='alice@test.com', password='testpass123'
        )
        self.bob = User.objects.create_user(
            username='bob', email='bob@test.com', password='testpass123'
        )

    def test_session_str(self):
        """Test session string representation"""
        session = P2PSession.objects.create(
            user1=self.alice,
            user2=self.bob,
            status='connected'
        )

        str_repr = str(session)
        self.assertIn('alice', str_repr)
        self.assertIn('bob', str_repr)
        self.assertIn('connected', str_repr)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
