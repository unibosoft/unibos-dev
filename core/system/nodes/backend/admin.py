"""
Django Admin Configuration for Node Registry
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Node, NodeCapability, NodeMetric, NodeEvent


class NodeCapabilityInline(admin.StackedInline):
    model = NodeCapability
    can_delete = False
    verbose_name = 'Capabilities'
    verbose_name_plural = 'Capabilities'


class NodeMetricInline(admin.TabularInline):
    model = NodeMetric
    extra = 0
    readonly_fields = [
        'recorded_at', 'cpu_percent', 'memory_percent',
        'disk_percent', 'requests_per_minute',
    ]
    ordering = ['-recorded_at']
    max_num = 10

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = [
        'hostname', 'node_type', 'platform', 'status_badge',
        'is_online', 'version', 'last_seen',
    ]
    list_filter = ['node_type', 'status', 'platform', 'is_active']
    search_fields = ['hostname', 'ip_address', 'id']
    readonly_fields = ['id', 'registered_at', 'last_seen', 'last_heartbeat']
    inlines = [NodeCapabilityInline, NodeMetricInline]
    ordering = ['-last_seen']

    fieldsets = (
        ('Identity', {
            'fields': ('id', 'hostname', 'node_type', 'platform')
        }),
        ('Network', {
            'fields': ('ip_address', 'port', 'public_url')
        }),
        ('Status', {
            'fields': ('status', 'is_active', 'registered_at', 'last_seen', 'last_heartbeat')
        }),
        ('Version', {
            'fields': ('version', 'build')
        }),
        ('Hierarchy', {
            'fields': ('parent_node', 'registration_token'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'online': 'green',
            'offline': 'red',
            'maintenance': 'orange',
            'unreachable': 'gray',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def is_online(self, obj):
        return obj.is_online
    is_online.boolean = True
    is_online.short_description = 'Online'


@admin.register(NodeEvent)
class NodeEventAdmin(admin.ModelAdmin):
    list_display = ['node', 'event_type', 'message', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['node__hostname', 'message']
    readonly_fields = ['id', 'node', 'event_type', 'message', 'created_at', 'extra_data']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False


@admin.register(NodeMetric)
class NodeMetricAdmin(admin.ModelAdmin):
    list_display = [
        'node', 'recorded_at', 'cpu_percent', 'memory_percent',
        'disk_percent', 'requests_per_minute',
    ]
    list_filter = ['node', 'recorded_at']
    search_fields = ['node__hostname']
    readonly_fields = [
        'id', 'node', 'recorded_at', 'cpu_percent', 'memory_percent',
        'memory_used_mb', 'disk_percent', 'disk_used_gb',
        'network_bytes_sent', 'network_bytes_recv',
        'requests_per_minute', 'avg_response_time_ms',
    ]
    ordering = ['-recorded_at']

    def has_add_permission(self, request):
        return False
