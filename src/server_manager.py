#!/usr/bin/env python3
"""
UNIBOS Server Manager - Manages backend and frontend servers
"""

import os
import sys
import time
import subprocess
import signal
import psutil
import json
from pathlib import Path
from datetime import datetime

class ServerManager:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.backend_path = self.base_path / 'backend'
        self.frontend_path = self.base_path / 'frontend'
        self.backend_pid_file = self.base_path / '.backend.pid'
        self.frontend_pid_file = self.base_path / '.frontend.pid'
        self.backend_process = None
        self.frontend_process = None
        
    def check_port(self, port):
        """Check if a port is in use"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return False
        return True
    
    def kill_process_on_port(self, port):
        """Kill process using a specific port"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        print(f"Killing process {proc.pid} on port {port}")
                        proc.kill()
                        time.sleep(1)
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False
    
    def start_backend(self):
        """Start the backend server"""
        print("Starting Backend Server...")
        
        # Check if already running
        if not self.check_port(8000):
            print("Port 8000 is already in use!")
            if input("Kill the existing process? (y/n): ").lower() == 'y':
                self.kill_process_on_port(8000)
                time.sleep(2)
            else:
                return False
        
        # Start backend
        os.chdir(self.backend_path)
        
        # Create a simple startup script inline
        startup_cmd = [
            sys.executable, '-c', '''
import os
import sys
import django

# Add backend to path
sys.path.insert(0, os.getcwd())

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.emergency')

# Setup Django
django.setup()

# Run migrations silently
from django.core.management import call_command
call_command('migrate', verbosity=0)

# Create superuser if needed
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@unibos.com', 'unibos123')
    print('Created default superuser')

# Start server
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
'''
        ]
        
        # Start process
        self.backend_process = subprocess.Popen(
            startup_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Save PID
        with open(self.backend_pid_file, 'w') as f:
            f.write(str(self.backend_process.pid))
        
        # Wait for startup
        time.sleep(3)
        
        # Check if running
        if self.backend_process.poll() is None:
            print("✅ Backend server started on http://localhost:8000")
            return True
        else:
            stderr = self.backend_process.stderr.read()
            print(f"❌ Backend server failed to start: {stderr}")
            return False
    
    def start_frontend(self):
        """Start the frontend server"""
        print("Starting Frontend Server...")
        
        # Check if already running
        if not self.check_port(3000):
            print("Port 3000 is already in use!")
            if input("Kill the existing process? (y/n): ").lower() == 'y':
                self.kill_process_on_port(3000)
                time.sleep(2)
            else:
                return False
        
        # Start frontend
        os.chdir(self.frontend_path)
        
        # Check if node_modules exists
        if not (self.frontend_path / 'node_modules').exists():
            print("Installing frontend dependencies...")
            subprocess.run(['npm', 'install', '--legacy-peer-deps'], check=False)
        
        # Start process
        env = os.environ.copy()
        env['BROWSER'] = 'none'  # Don't open browser automatically
        self.frontend_process = subprocess.Popen(
            ['npm', 'start'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=env
        )
        
        # Save PID
        with open(self.frontend_pid_file, 'w') as f:
            f.write(str(self.frontend_process.pid))
        
        # Wait for startup
        time.sleep(5)
        
        # Check if running
        if self.frontend_process.poll() is None:
            print("✅ Frontend server started on http://localhost:3000")
            return True
        else:
            stderr = self.frontend_process.stderr.read()
            print(f"❌ Frontend server failed to start: {stderr}")
            return False
    
    def stop_backend(self):
        """Stop the backend server"""
        if self.backend_pid_file.exists():
            try:
                pid = int(self.backend_pid_file.read_text())
                os.kill(pid, signal.SIGTERM)
                self.backend_pid_file.unlink()
                print("✅ Backend server stopped")
                return True
            except:
                pass
        
        # Try to kill by port
        if self.kill_process_on_port(8000):
            print("✅ Backend server stopped")
            return True
        
        print("Backend server not running")
        return False
    
    def stop_frontend(self):
        """Stop the frontend server"""
        if self.frontend_pid_file.exists():
            try:
                pid = int(self.frontend_pid_file.read_text())
                os.kill(pid, signal.SIGTERM)
                self.frontend_pid_file.unlink()
                print("✅ Frontend server stopped")
                return True
            except:
                pass
        
        # Try to kill by port
        if self.kill_process_on_port(3000):
            print("✅ Frontend server stopped")
            return True
        
        print("Frontend server not running")
        return False
    
    def status(self):
        """Check status of both servers"""
        backend_running = not self.check_port(8000)
        frontend_running = not self.check_port(3000)
        
        print("\n=== UNIBOS Server Status ===")
        print(f"Backend:  {'🟢 Running' if backend_running else '🔴 Stopped'} (port 8000)")
        print(f"Frontend: {'🟢 Running' if frontend_running else '🔴 Stopped'} (port 3000)")
        
        if backend_running:
            print("\nBackend URLs:")
            print("  - API: http://localhost:8000/api/")
            print("  - Admin: http://localhost:8000/admin/")
        
        if frontend_running:
            print("\nFrontend URL:")
            print("  - App: http://localhost:3000")
        
        return {'backend': backend_running, 'frontend': frontend_running}
    
    def start_all(self):
        """Start both servers"""
        print("Starting UNIBOS servers...")
        
        backend_ok = self.start_backend()
        time.sleep(2)
        frontend_ok = self.start_frontend()
        
        if backend_ok and frontend_ok:
            print("\n✅ All servers started successfully!")
            self.status()
            return True
        else:
            print("\n❌ Some servers failed to start")
            self.status()
            return False
    
    def stop_all(self):
        """Stop both servers"""
        print("Stopping UNIBOS servers...")
        self.stop_backend()
        self.stop_frontend()
        print("\n✅ All servers stopped")
        return True
    
    def restart_all(self):
        """Restart both servers"""
        print("Restarting UNIBOS servers...")
        self.stop_all()
        time.sleep(2)
        return self.start_all()

def main():
    if len(sys.argv) < 2:
        print("Usage: python server_manager.py [start|stop|restart|status|start-backend|start-frontend|stop-backend|stop-frontend]")
        return
    
    manager = ServerManager()
    command = sys.argv[1]
    
    commands = {
        'start': manager.start_all,
        'stop': manager.stop_all,
        'restart': manager.restart_all,
        'status': manager.status,
        'start-backend': manager.start_backend,
        'start-frontend': manager.start_frontend,
        'stop-backend': manager.stop_backend,
        'stop-frontend': manager.stop_frontend,
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: " + ", ".join(commands.keys()))

if __name__ == "__main__":
    main()