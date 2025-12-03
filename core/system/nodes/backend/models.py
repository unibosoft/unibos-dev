"""
Node Registry Models for UNIBOS

Stores node information in the database for central registry management.
Mirrors the dataclasses from core.base.identity.identity for database persistence.
"""

import uuid
from django.db import models
from django.utils import timezone


class NodeType(models.TextChoices):
    """Node type classification"""
    CENTRAL = 'central', 'Central Server'
    LOCAL = 'local', 'Local Development'
    EDGE = 'edge', 'Edge Device'
    DESKTOP = 'desktop', 'Desktop/Laptop'
    UNKNOWN = 'unknown', 'Unknown'


class NodeStatus(models.TextChoices):
    """Node online status"""
    ONLINE = 'online', 'Online'
    OFFLINE = 'offline', 'Offline'
    MAINTENANCE = 'maintenance', 'Maintenance'
    UNREACHABLE = 'unreachable', 'Unreachable'


class Node(models.Model):
    """
    Registered UNIBOS Node

    Each node in the network registers here with its UUID and capabilities.
    The central server maintains this registry for node discovery and management.
    """
    # Primary identifier - matches the file-based UUID from identity.py
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Node identification
    hostname = models.CharField(max_length=255)
    node_type = models.CharField(
        max_length=20,
        choices=NodeType.choices,
        default=NodeType.UNKNOWN
    )
    platform = models.CharField(max_length=50)  # macos, linux, raspberry-pi, windows

    # Network information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    port = models.PositiveIntegerField(default=8000)
    public_url = models.URLField(blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=NodeStatus.choices,
        default=NodeStatus.OFFLINE
    )
    is_active = models.BooleanField(default=True)

    # Registration
    registered_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(default=timezone.now)
    last_heartbeat = models.DateTimeField(null=True, blank=True)

    # Registration token for secure communication
    registration_token = models.CharField(max_length=255, blank=True)

    # Parent node (for hierarchical networks)
    parent_node = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_nodes'
    )

    # Metadata
    version = models.CharField(max_length=50, blank=True)  # UNIBOS version
    build = models.CharField(max_length=50, blank=True)    # Build number

    class Meta:
        db_table = 'nodes'
        verbose_name = 'Node'
        verbose_name_plural = 'Nodes'
        ordering = ['-last_seen']
        indexes = [
            models.Index(fields=['node_type']),
            models.Index(fields=['status']),
            models.Index(fields=['hostname']),
            models.Index(fields=['last_seen']),
        ]

    def __str__(self):
        return f"{self.hostname} ({self.get_node_type_display()})"

    def update_heartbeat(self):
        """Update heartbeat timestamp"""
        self.last_heartbeat = timezone.now()
        self.last_seen = timezone.now()
        self.status = NodeStatus.ONLINE
        self.save(update_fields=['last_heartbeat', 'last_seen', 'status'])

    def mark_offline(self):
        """Mark node as offline"""
        self.status = NodeStatus.OFFLINE
        self.save(update_fields=['status'])

    @property
    def is_online(self):
        """Check if node is online based on last heartbeat"""
        if not self.last_heartbeat:
            return False
        # Consider online if heartbeat within last 5 minutes
        delta = timezone.now() - self.last_heartbeat
        return delta.total_seconds() < 300


class NodeCapability(models.Model):
    """
    Node capabilities - what the node can do

    Stores hardware and software capabilities for each node.
    """
    node = models.OneToOneField(
        Node,
        on_delete=models.CASCADE,
        related_name='capabilities'
    )

    # Hardware capabilities
    has_gpu = models.BooleanField(default=False)
    has_camera = models.BooleanField(default=False)
    has_gpio = models.BooleanField(default=False)
    has_lora = models.BooleanField(default=False)

    # Service capabilities
    can_run_django = models.BooleanField(default=True)
    can_run_celery = models.BooleanField(default=True)
    can_run_websocket = models.BooleanField(default=True)

    # Storage
    storage_gb = models.PositiveIntegerField(default=0)
    ram_gb = models.PositiveIntegerField(default=0)
    cpu_cores = models.PositiveIntegerField(default=1)

    # Available modules on this node
    available_modules = models.JSONField(default=list)

    # Enabled modules on this node
    enabled_modules = models.JSONField(default=list)

    class Meta:
        db_table = 'node_capabilities'
        verbose_name = 'Node Capability'
        verbose_name_plural = 'Node Capabilities'

    def __str__(self):
        return f"Capabilities for {self.node.hostname}"


class NodeMetric(models.Model):
    """
    Node performance metrics over time

    Stores periodic snapshots of node performance for monitoring.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='metrics'
    )

    # Timestamp
    recorded_at = models.DateTimeField(auto_now_add=True)

    # CPU metrics
    cpu_percent = models.FloatField(default=0)

    # Memory metrics
    memory_percent = models.FloatField(default=0)
    memory_used_mb = models.PositiveIntegerField(default=0)

    # Disk metrics
    disk_percent = models.FloatField(default=0)
    disk_used_gb = models.FloatField(default=0)

    # Network metrics
    network_bytes_sent = models.BigIntegerField(default=0)
    network_bytes_recv = models.BigIntegerField(default=0)

    # Request metrics
    requests_per_minute = models.PositiveIntegerField(default=0)
    avg_response_time_ms = models.FloatField(default=0)

    class Meta:
        db_table = 'node_metrics'
        verbose_name = 'Node Metric'
        verbose_name_plural = 'Node Metrics'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['node', 'recorded_at']),
        ]

    def __str__(self):
        return f"{self.node.hostname} @ {self.recorded_at}"


class NodeEvent(models.Model):
    """
    Node events for audit logging

    Records significant events on each node.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='events'
    )

    # Event info
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('registered', 'Node Registered'),
            ('online', 'Node Online'),
            ('offline', 'Node Offline'),
            ('maintenance', 'Maintenance Started'),
            ('updated', 'Node Updated'),
            ('capability_changed', 'Capability Changed'),
            ('module_enabled', 'Module Enabled'),
            ('module_disabled', 'Module Disabled'),
            ('error', 'Error'),
            ('warning', 'Warning'),
        ]
    )
    message = models.TextField()

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    extra_data = models.JSONField(default=dict)

    class Meta:
        db_table = 'node_events'
        verbose_name = 'Node Event'
        verbose_name_plural = 'Node Events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['node', 'event_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.node.hostname}: {self.get_event_type_display()}"
