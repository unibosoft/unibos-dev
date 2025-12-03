"""
API Views for Node Registry

Provides endpoints for node registration, discovery, and management.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils import timezone
from django.db.models import Count

from .models import Node, NodeCapability, NodeMetric, NodeEvent, NodeStatus, NodeType
from .serializers import (
    NodeSerializer,
    NodeDetailSerializer,
    NodeRegistrationSerializer,
    NodeHeartbeatSerializer,
    NodeMetricSerializer,
    NodeEventSerializer,
    NodeSummarySerializer,
)


class NodeViewSet(viewsets.ModelViewSet):
    """
    Node Registry API

    Provides CRUD operations for nodes plus registration and heartbeat endpoints.
    """
    queryset = Node.objects.filter(is_active=True).select_related('capabilities')
    serializer_class = NodeSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NodeDetailSerializer
        if self.action in ['register', 'create', 'update', 'partial_update']:
            return NodeRegistrationSerializer
        return NodeSerializer

    def get_permissions(self):
        # Allow unauthenticated registration and heartbeat for nodes
        if self.action in ['register', 'heartbeat', 'discover']:
            return [AllowAny()]
        return super().get_permissions()

    def perform_destroy(self, instance):
        # Soft delete - just mark as inactive
        instance.is_active = False
        instance.save(update_fields=['is_active'])

        # Log the event
        NodeEvent.objects.create(
            node=instance,
            event_type='offline',
            message=f'Node {instance.hostname} was deactivated',
        )

    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Register a new node or update existing registration

        POST /api/v1/nodes/register/
        """
        node_id = request.data.get('id')

        if node_id:
            # Update existing registration
            try:
                node = Node.objects.get(id=node_id)
                serializer = NodeRegistrationSerializer(
                    node, data=request.data, partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    node.update_heartbeat()

                    NodeEvent.objects.create(
                        node=node,
                        event_type='updated',
                        message=f'Node {node.hostname} updated registration',
                        extra_data={'ip': request.META.get('REMOTE_ADDR')},
                    )

                    return Response(
                        NodeDetailSerializer(node).data,
                        status=status.HTTP_200_OK
                    )
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Node.DoesNotExist:
                pass  # Fall through to create

        # Create new registration
        serializer = NodeRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            node = serializer.save()
            node.update_heartbeat()

            NodeEvent.objects.create(
                node=node,
                event_type='registered',
                message=f'Node {node.hostname} registered',
                extra_data={
                    'ip': request.META.get('REMOTE_ADDR'),
                    'platform': node.platform,
                },
            )

            return Response(
                NodeDetailSerializer(node).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def heartbeat(self, request, id=None):
        """
        Receive heartbeat from a node

        POST /api/v1/nodes/{id}/heartbeat/
        """
        try:
            node = Node.objects.get(id=id)
        except Node.DoesNotExist:
            return Response(
                {'error': 'Node not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Update heartbeat
        was_offline = node.status != NodeStatus.ONLINE
        node.update_heartbeat()

        # Store metrics if provided
        serializer = NodeHeartbeatSerializer(data=request.data)
        if serializer.is_valid():
            NodeMetric.objects.create(node=node, **serializer.validated_data)

        # Log if node came back online
        if was_offline:
            NodeEvent.objects.create(
                node=node,
                event_type='online',
                message=f'Node {node.hostname} came online',
            )

        return Response({'status': 'ok', 'last_seen': node.last_seen})

    @action(detail=False, methods=['get'])
    def discover(self, request):
        """
        Discover available nodes in the network

        GET /api/v1/nodes/discover/?type=central
        """
        queryset = self.get_queryset().filter(status=NodeStatus.ONLINE)

        # Filter by type
        node_type = request.query_params.get('type')
        if node_type:
            queryset = queryset.filter(node_type=node_type)

        # Filter by capability
        if request.query_params.get('has_gpu'):
            queryset = queryset.filter(capabilities__has_gpu=True)
        if request.query_params.get('has_camera'):
            queryset = queryset.filter(capabilities__has_camera=True)
        if request.query_params.get('can_run_celery'):
            queryset = queryset.filter(capabilities__can_run_celery=True)

        serializer = NodeSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get network summary statistics

        GET /api/v1/nodes/summary/
        """
        queryset = self.get_queryset()

        # Count by type
        by_type = dict(queryset.values_list('node_type').annotate(count=Count('id')))

        # Count by status
        by_status = dict(queryset.values_list('status').annotate(count=Count('id')))

        summary = {
            'total_nodes': queryset.count(),
            'online_nodes': queryset.filter(status=NodeStatus.ONLINE).count(),
            'offline_nodes': queryset.filter(status=NodeStatus.OFFLINE).count(),
            'nodes_by_type': by_type,
            'nodes_by_status': by_status,
        }

        return Response(summary)

    @action(detail=True, methods=['get'])
    def metrics(self, request, id=None):
        """
        Get node metrics history

        GET /api/v1/nodes/{id}/metrics/?limit=24
        """
        try:
            node = Node.objects.get(id=id)
        except Node.DoesNotExist:
            return Response(
                {'error': 'Node not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        limit = int(request.query_params.get('limit', 24))
        metrics = node.metrics.all()[:limit]
        serializer = NodeMetricSerializer(metrics, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def events(self, request, id=None):
        """
        Get node events

        GET /api/v1/nodes/{id}/events/?limit=50
        """
        try:
            node = Node.objects.get(id=id)
        except Node.DoesNotExist:
            return Response(
                {'error': 'Node not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        limit = int(request.query_params.get('limit', 50))
        events = node.events.all()[:limit]
        serializer = NodeEventSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def maintenance(self, request, id=None):
        """
        Toggle node maintenance mode

        POST /api/v1/nodes/{id}/maintenance/
        """
        try:
            node = Node.objects.get(id=id)
        except Node.DoesNotExist:
            return Response(
                {'error': 'Node not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if node.status == NodeStatus.MAINTENANCE:
            node.status = NodeStatus.ONLINE
            event_type = 'online'
            message = f'Node {node.hostname} maintenance ended'
        else:
            node.status = NodeStatus.MAINTENANCE
            event_type = 'maintenance'
            message = f'Node {node.hostname} entered maintenance mode'

        node.save(update_fields=['status'])

        NodeEvent.objects.create(
            node=node,
            event_type=event_type,
            message=message,
        )

        return Response(NodeSerializer(node).data)
