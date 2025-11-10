from flask import Blueprint, request, jsonify, current_app
from src.models.emergency import db, Device, Message, NetworkNode, EmergencyEvent
from datetime import datetime
import json
import uuid
import random

emergency_bp = Blueprint('emergency', __name__)

# Device management endpoints
@emergency_bp.route('/device/register', methods=['POST'])
def register_device():
    """Register a new device in the network"""
    try:
        data = request.get_json()
        
        # Generate unique device name if not provided
        if 'name' not in data or not data['name']:
            animal_names = ['octopus', 'dolphin', 'eagle', 'mountain', 'river', 'forest', 
                          'storm', 'thunder', 'lightning', 'phoenix', 'dragon', 'tiger',
                          'wolf', 'bear', 'hawk', 'falcon', 'shark', 'whale', 'lion']
            
            # Find available name
            used_names = [d.name for d in Device.query.all()]
            available_names = [name for name in animal_names if name not in used_names]
            
            if not available_names:
                # Generate numbered name if all predefined names are used
                base_name = random.choice(animal_names)
                counter = 1
                while f"{base_name}{counter}" in used_names:
                    counter += 1
                data['name'] = f"{base_name}{counter}"
            else:
                data['name'] = random.choice(available_names)
        
        # Check if device already exists
        existing_device = Device.query.filter_by(mac_address=data['mac_address']).first()
        if existing_device:
            return jsonify({
                'success': True,
                'message': 'Device already registered',
                'device': existing_device.to_dict()
            }), 200
        
        # Create new device
        device = Device(
            name=data['name'],
            device_type=data.get('device_type', 'pi_zero_2w'),
            mac_address=data['mac_address'],
            ip_address=data.get('ip_address'),
            lora_frequency=data.get('lora_frequency', 868.0)
        )
        
        db.session.add(device)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Device registered successfully',
            'device': device.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@emergency_bp.route('/device/<device_id>/status', methods=['PUT'])
def update_device_status(device_id):
    """Update device status and sensor data"""
    try:
        device = Device.query.get_or_404(device_id)
        data = request.get_json()
        
        # Update location if provided
        if 'latitude' in data and 'longitude' in data:
            device.latitude = data['latitude']
            device.longitude = data['longitude']
            device.altitude = data.get('altitude')
            device.location_updated = datetime.utcnow()
        
        # Update sensor data
        if 'temperature' in data or 'humidity' in data:
            device.temperature = data.get('temperature')
            device.humidity = data.get('humidity')
            device.sensor_updated = datetime.utcnow()
        
        # Update other status fields
        device.battery_level = data.get('battery_level', device.battery_level)
        device.signal_strength = data.get('signal_strength', device.signal_strength)
        device.emergency_mode = data.get('emergency_mode', device.emergency_mode)
        device.sos_active = data.get('sos_active', device.sos_active)
        device.is_online = True
        device.last_seen = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Device status updated',
            'device': device.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@emergency_bp.route('/devices', methods=['GET'])
def get_devices():
    """Get all devices in the network"""
    try:
        devices = Device.query.all()
        return jsonify({
            'success': True,
            'devices': [device.to_dict() for device in devices],
            'count': len(devices)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@emergency_bp.route('/devices/online', methods=['GET'])
def get_online_devices():
    """Get only online devices"""
    try:
        devices = Device.query.filter_by(is_online=True).all()
        return jsonify({
            'success': True,
            'devices': [device.to_dict() for device in devices],
            'count': len(devices)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Messaging endpoints
@emergency_bp.route('/message/send', methods=['POST'])
def send_message():
    """Send a message through the network"""
    try:
        data = request.get_json()
        
        message = Message(
            sender_id=data['sender_id'],
            recipient_id=data.get('recipient_id'),  # None for broadcast
            message_type=data.get('message_type', 'text'),
            priority=data.get('priority', 1),
            content=data['content'],
            encrypted=data.get('encrypted', True),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        
        db.session.add(message)
        db.session.commit()
        
        # TODO: Implement actual message routing through LoRa/2.4GHz
        
        return jsonify({
            'success': True,
            'message': 'Message queued for delivery',
            'message_id': message.id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@emergency_bp.route('/messages/<device_id>', methods=['GET'])
def get_messages(device_id):
    """Get messages for a specific device"""
    try:
        # Get messages sent to this device or broadcast messages
        messages = Message.query.filter(
            (Message.recipient_id == device_id) | (Message.recipient_id.is_(None))
        ).order_by(Message.created_at.desc()).limit(100).all()
        
        return jsonify({
            'success': True,
            'messages': [message.to_dict() for message in messages],
            'count': len(messages)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@emergency_bp.route('/message/<message_id>/acknowledge', methods=['PUT'])
def acknowledge_message(message_id):
    """Acknowledge message receipt"""
    try:
        message = Message.query.get_or_404(message_id)
        message.acknowledged_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Message acknowledged'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Emergency event endpoints
@emergency_bp.route('/emergency/sos', methods=['POST'])
def send_sos():
    """Send SOS emergency signal"""
    try:
        data = request.get_json()
        
        # Create emergency event
        event = EmergencyEvent(
            event_type='sos',
            severity=5,  # Maximum severity for SOS
            title='SOS Emergency Signal',
            description=data.get('description', 'Emergency assistance needed'),
            latitude=data['latitude'],
            longitude=data['longitude'],
            reported_by=data['device_id']
        )
        
        db.session.add(event)
        
        # Create broadcast message
        sos_message = Message(
            sender_id=data['device_id'],
            recipient_id=None,  # Broadcast
            message_type='sos',
            priority=4,  # Emergency priority
            content=json.dumps({
                'event_id': event.id,
                'type': 'sos',
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'description': data.get('description', 'Emergency assistance needed')
            }),
            latitude=data['latitude'],
            longitude=data['longitude']
        )
        
        db.session.add(sos_message)
        
        # Update device SOS status
        device = Device.query.get(data['device_id'])
        if device:
            device.sos_active = True
            device.emergency_mode = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'SOS signal sent',
            'event_id': event.id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@emergency_bp.route('/emergency/events', methods=['GET'])
def get_emergency_events():
    """Get active emergency events"""
    try:
        events = EmergencyEvent.query.filter_by(status='active').order_by(
            EmergencyEvent.severity.desc(), EmergencyEvent.created_at.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'events': [event.to_dict() for event in events],
            'count': len(events)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@emergency_bp.route('/emergency/event/<event_id>/resolve', methods=['PUT'])
def resolve_emergency(event_id):
    """Mark emergency event as resolved"""
    try:
        event = EmergencyEvent.query.get_or_404(event_id)
        event.status = 'resolved'
        event.resolved_at = datetime.utcnow()
        
        # Turn off SOS for the reporting device if this was an SOS event
        if event.event_type == 'sos':
            device = Device.query.get(event.reported_by)
            if device:
                device.sos_active = False
                # Keep emergency_mode on until manually turned off
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Emergency event resolved'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Network topology endpoints
@emergency_bp.route('/network/topology', methods=['GET'])
def get_network_topology():
    """Get current network topology"""
    try:
        nodes = NetworkNode.query.all()
        devices = Device.query.filter_by(is_online=True).all()
        
        topology = {
            'devices': [device.to_dict() for device in devices],
            'connections': [node.to_dict() for node in nodes]
        }
        
        return jsonify({
            'success': True,
            'topology': topology
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@emergency_bp.route('/network/neighbor', methods=['POST'])
def add_neighbor():
    """Add or update neighbor connection"""
    try:
        data = request.get_json()
        
        # Check if connection already exists
        existing = NetworkNode.query.filter_by(
            device_id=data['device_id'],
            neighbor_id=data['neighbor_id']
        ).first()
        
        if existing:
            # Update existing connection
            existing.signal_strength = data['signal_strength']
            existing.packet_loss = data.get('packet_loss', 0.0)
            existing.latency = data.get('latency')
            existing.connection_type = data['connection_type']
            existing.last_seen = datetime.utcnow()
        else:
            # Create new connection
            node = NetworkNode(
                device_id=data['device_id'],
                neighbor_id=data['neighbor_id'],
                signal_strength=data['signal_strength'],
                packet_loss=data.get('packet_loss', 0.0),
                latency=data.get('latency'),
                connection_type=data['connection_type']
            )
            db.session.add(node)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Neighbor connection updated'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# System status endpoints
@emergency_bp.route('/system/status', methods=['GET'])
def get_system_status():
    """Get overall system status"""
    try:
        total_devices = Device.query.count()
        online_devices = Device.query.filter_by(is_online=True).count()
        active_emergencies = EmergencyEvent.query.filter_by(status='active').count()
        recent_messages = Message.query.filter(
            Message.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
        ).count()
        
        return jsonify({
            'success': True,
            'status': {
                'total_devices': total_devices,
                'online_devices': online_devices,
                'offline_devices': total_devices - online_devices,
                'active_emergencies': active_emergencies,
                'messages_today': recent_messages,
                'system_uptime': 'TODO: Implement uptime tracking',
                'network_health': 'good' if online_devices > 0 else 'poor'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@emergency_bp.route('/system/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0-alpha'
    }), 200

