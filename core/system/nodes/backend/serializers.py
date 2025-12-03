"""
Serializers for Node Registry API
"""

from rest_framework import serializers
from .models import Node, NodeCapability, NodeMetric, NodeEvent


class NodeCapabilitySerializer(serializers.ModelSerializer):
    """Serializer for node capabilities"""

    class Meta:
        model = NodeCapability
        fields = [
            'has_gpu', 'has_camera', 'has_gpio', 'has_lora',
            'can_run_django', 'can_run_celery', 'can_run_websocket',
            'storage_gb', 'ram_gb', 'cpu_cores',
            'available_modules', 'enabled_modules',
        ]


class NodeMetricSerializer(serializers.ModelSerializer):
    """Serializer for node metrics"""

    class Meta:
        model = NodeMetric
        fields = [
            'id', 'recorded_at',
            'cpu_percent', 'memory_percent', 'memory_used_mb',
            'disk_percent', 'disk_used_gb',
            'network_bytes_sent', 'network_bytes_recv',
            'requests_per_minute', 'avg_response_time_ms',
        ]
        read_only_fields = ['id', 'recorded_at']


class NodeEventSerializer(serializers.ModelSerializer):
    """Serializer for node events"""
    event_type_display = serializers.CharField(
        source='get_event_type_display',
        read_only=True
    )

    class Meta:
        model = NodeEvent
        fields = [
            'id', 'event_type', 'event_type_display',
            'message', 'created_at', 'extra_data',
        ]
        read_only_fields = ['id', 'created_at']


class NodeSerializer(serializers.ModelSerializer):
    """Serializer for node listing"""
    capabilities = NodeCapabilitySerializer(read_only=True)
    node_type_display = serializers.CharField(
        source='get_node_type_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    is_online = serializers.BooleanField(read_only=True)

    class Meta:
        model = Node
        fields = [
            'id', 'hostname', 'node_type', 'node_type_display',
            'platform', 'ip_address', 'port', 'public_url',
            'status', 'status_display', 'is_active', 'is_online',
            'registered_at', 'last_seen', 'last_heartbeat',
            'version', 'build',
            'capabilities',
        ]
        read_only_fields = ['id', 'registered_at', 'last_seen', 'last_heartbeat']


class NodeDetailSerializer(NodeSerializer):
    """Detailed node serializer with events and metrics"""
    recent_events = serializers.SerializerMethodField()
    recent_metrics = serializers.SerializerMethodField()
    child_nodes = serializers.SerializerMethodField()

    class Meta(NodeSerializer.Meta):
        fields = NodeSerializer.Meta.fields + [
            'parent_node', 'registration_token',
            'recent_events', 'recent_metrics', 'child_nodes',
        ]

    def get_recent_events(self, obj):
        events = obj.events.all()[:10]
        return NodeEventSerializer(events, many=True).data

    def get_recent_metrics(self, obj):
        metrics = obj.metrics.all()[:24]  # Last 24 snapshots
        return NodeMetricSerializer(metrics, many=True).data

    def get_child_nodes(self, obj):
        children = obj.child_nodes.filter(is_active=True)
        return [{'id': str(c.id), 'hostname': c.hostname} for c in children]


class NodeRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for node registration"""
    capabilities = NodeCapabilitySerializer(required=False)

    class Meta:
        model = Node
        fields = [
            'id', 'hostname', 'node_type', 'platform',
            'ip_address', 'port', 'public_url',
            'version', 'build', 'capabilities',
        ]

    def create(self, validated_data):
        capabilities_data = validated_data.pop('capabilities', {})
        node = Node.objects.create(**validated_data)
        NodeCapability.objects.create(node=node, **capabilities_data)
        return node

    def update(self, instance, validated_data):
        capabilities_data = validated_data.pop('capabilities', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if capabilities_data:
            capability, _ = NodeCapability.objects.get_or_create(node=instance)
            for attr, value in capabilities_data.items():
                setattr(capability, attr, value)
            capability.save()

        return instance


class NodeHeartbeatSerializer(serializers.Serializer):
    """Serializer for heartbeat requests"""
    cpu_percent = serializers.FloatField(required=False, default=0)
    memory_percent = serializers.FloatField(required=False, default=0)
    memory_used_mb = serializers.IntegerField(required=False, default=0)
    disk_percent = serializers.FloatField(required=False, default=0)
    disk_used_gb = serializers.FloatField(required=False, default=0)
    requests_per_minute = serializers.IntegerField(required=False, default=0)
    avg_response_time_ms = serializers.FloatField(required=False, default=0)


class NodeSummarySerializer(serializers.Serializer):
    """Serializer for network summary"""
    total_nodes = serializers.IntegerField()
    online_nodes = serializers.IntegerField()
    offline_nodes = serializers.IntegerField()
    nodes_by_type = serializers.DictField()
    nodes_by_status = serializers.DictField()
