from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Device(db.Model):
    """Device model for emergency communication nodes"""
    __tablename__ = 'devices'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), unique=True, nullable=False)  # e.g., "octopus", "dolphin"
    device_type = db.Column(db.String(20), nullable=False)  # "pi_zero_2w" or "pi_5"
    mac_address = db.Column(db.String(17), unique=True, nullable=False)
    ip_address = db.Column(db.String(15), nullable=True)
    
    # Location data
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    altitude = db.Column(db.Float, nullable=True)
    location_updated = db.Column(db.DateTime, nullable=True)
    
    # Device status
    is_online = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    battery_level = db.Column(db.Integer, nullable=True)  # 0-100
    
    # Environmental sensors
    temperature = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    sensor_updated = db.Column(db.DateTime, nullable=True)
    
    # Network info
    lora_frequency = db.Column(db.Float, default=868.0)  # MHz
    signal_strength = db.Column(db.Integer, nullable=True)  # dBm
    
    # Emergency status
    emergency_mode = db.Column(db.Boolean, default=False)
    sos_active = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'device_type': self.device_type,
            'mac_address': self.mac_address,
            'ip_address': self.ip_address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'location_updated': self.location_updated.isoformat() if self.location_updated else None,
            'is_online': self.is_online,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'battery_level': self.battery_level,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'sensor_updated': self.sensor_updated.isoformat() if self.sensor_updated else None,
            'lora_frequency': self.lora_frequency,
            'signal_strength': self.signal_strength,
            'emergency_mode': self.emergency_mode,
            'sos_active': self.sos_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Message(db.Model):
    """Message model for emergency communications"""
    __tablename__ = 'messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = db.Column(db.String(36), db.ForeignKey('devices.id'), nullable=False)
    recipient_id = db.Column(db.String(36), db.ForeignKey('devices.id'), nullable=True)  # None for broadcast
    
    message_type = db.Column(db.String(20), nullable=False)  # "text", "sos", "location", "status"
    priority = db.Column(db.Integer, default=1)  # 1=low, 2=normal, 3=high, 4=emergency
    
    content = db.Column(db.Text, nullable=False)
    encrypted = db.Column(db.Boolean, default=True)
    
    # Routing information
    hop_count = db.Column(db.Integer, default=0)
    route_path = db.Column(db.Text, nullable=True)  # JSON array of device IDs
    
    # Status tracking
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivered_at = db.Column(db.DateTime, nullable=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    
    # Location data (for location-based messages)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('Device', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('Device', foreign_keys=[recipient_id], backref='received_messages')
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'message_type': self.message_type,
            'priority': self.priority,
            'content': self.content,
            'encrypted': self.encrypted,
            'hop_count': self.hop_count,
            'route_path': self.route_path,
            'sent_at': self.sent_at.isoformat(),
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created_at': self.created_at.isoformat()
        }

class NetworkNode(db.Model):
    """Network topology and routing information"""
    __tablename__ = 'network_nodes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = db.Column(db.String(36), db.ForeignKey('devices.id'), nullable=False)
    neighbor_id = db.Column(db.String(36), db.ForeignKey('devices.id'), nullable=False)
    
    # Connection quality metrics
    signal_strength = db.Column(db.Integer, nullable=False)  # dBm
    packet_loss = db.Column(db.Float, default=0.0)  # 0.0-1.0
    latency = db.Column(db.Integer, nullable=True)  # milliseconds
    
    # Connection type
    connection_type = db.Column(db.String(10), nullable=False)  # "lora" or "24ghz"
    
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    device = db.relationship('Device', foreign_keys=[device_id])
    neighbor = db.relationship('Device', foreign_keys=[neighbor_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'neighbor_id': self.neighbor_id,
            'signal_strength': self.signal_strength,
            'packet_loss': self.packet_loss,
            'latency': self.latency,
            'connection_type': self.connection_type,
            'last_seen': self.last_seen.isoformat(),
            'created_at': self.created_at.isoformat()
        }

class EmergencyEvent(db.Model):
    """Emergency events and coordination"""
    __tablename__ = 'emergency_events'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = db.Column(db.String(30), nullable=False)  # "sos", "medical", "fire", "earthquake", etc.
    severity = db.Column(db.Integer, nullable=False)  # 1-5 scale
    
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Location
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    radius = db.Column(db.Float, default=1.0)  # km
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, resolved, closed
    reported_by = db.Column(db.String(36), db.ForeignKey('devices.id'), nullable=False)
    
    # Resources needed
    resources_needed = db.Column(db.Text, nullable=True)  # JSON
    resources_available = db.Column(db.Text, nullable=True)  # JSON
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    reporter = db.relationship('Device', backref='reported_events')
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'radius': self.radius,
            'status': self.status,
            'reported_by': self.reported_by,
            'resources_needed': self.resources_needed,
            'resources_available': self.resources_available,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

