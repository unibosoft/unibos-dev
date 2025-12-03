"""
UNIBOS-DEV TUI - Simplified Structure
Development TUI with single dev-tools section
"""

import subprocess
from pathlib import Path
from typing import List

from core.clients.tui import BaseTUI
from core.clients.tui.components import MenuSection
from core.clients.cli.framework.ui import MenuItem, Colors
from core.clients.tui.common_items import CommonItems


class UnibosDevTUI(BaseTUI):
    """Development TUI with v527 structure"""

    def __init__(self):
        """Initialize dev TUI with proper config"""
        from core.clients.tui.base import TUIConfig
        from core.version import __version__, __build__, get_short_version_string

        config = TUIConfig(
            title="unibos-dev",
            version=get_short_version_string(),  # Dynamic: "v1.0.0 22:25"
            location="dev environment",
            sidebar_width=25,  # V527 spec: exactly 25 characters
            show_splash=True,
            quick_splash=False,
            lowercase_ui=True,  # v527 style
            show_breadcrumbs=True,
            show_time=True,  # Time in footer, not header
            show_hostname=True,
            show_status_led=True
        )

        super().__init__(config)

        # Register dev-specific handlers
        self.register_dev_handlers()

    def get_profile_name(self) -> str:
        """Get profile name"""
        return "development"

    def get_menu_sections(self) -> List[MenuSection]:
        """Get development menu sections - simplified single section"""
        return [
            # Single unified dev-tools section
            MenuSection(
                id='dev_tools',
                label='dev-tools',
                icon='🛠️',
                items=[
                    # System & Status
                    MenuItem(
                        id='system_status',
                        label=self.i18n.translate('menu.system_status'),
                        icon='📊',
                        description='system status & info\n\n'
                                   '→ system information\n'
                                   '→ version details\n'
                                   '→ service status\n'
                                   '→ resource usage\n\n'
                                   'complete system overview',
                        enabled=True
                    ),
                    CommonItems.web_ui(self.i18n),
                    CommonItems.database_setup(self.i18n, profile_type='dev'),
                    MenuItem(
                        id='code_forge',
                        label=self.i18n.translate('menu.git'),
                        icon='⚙️',
                        description='git operations\n\n'
                                   '→ git status\n'
                                   '→ commit history\n'
                                   '→ branch management\n\n'
                                   'source code management',
                        enabled=True
                    ),
                    MenuItem(
                        id='version_manager',
                        label=self.i18n.translate('menu.versions'),
                        icon='📋',
                        description='version archives\n\n'
                                   '→ create archives\n'
                                   '→ browse history\n'
                                   '→ release pipeline\n\n'
                                   'version control and archiving',
                        enabled=True
                    ),
                    MenuItem(
                        id='deploy_servers',
                        label=self.i18n.translate('menu.deploy'),
                        icon='🌍',
                        description='server deployment\n\n'
                                   '→ rocksteady (production)\n'
                                   '→ bebop (staging)\n'
                                   '→ deploy & manage\n\n'
                                   'multi-server deploy',
                        enabled=True
                    ),
                    MenuItem(
                        id='ai_builder',
                        label=self.i18n.translate('menu.ai_builder'),
                        icon='🤖',
                        description='ai development\n\n'
                                   '→ code generation\n'
                                   '→ ai assistance\n'
                                   '→ smart refactoring\n\n'
                                   'ai-powered tools',
                        enabled=True
                    ),
                    CommonItems.administration(self.i18n),
                ]
            ),
        ]

    def register_dev_handlers(self):
        """Register all development action handlers"""
        # Dev tools handlers
        self.register_action('system_status', self.handle_system_status)
        self.register_action('web_ui', self.handle_web_ui)
        self.register_action('database_setup', self.handle_database_setup)
        self.register_action('code_forge', self.handle_code_forge)
        self.register_action('version_manager', self.handle_version_manager)
        self.register_action('deploy_servers', self.handle_deploy_servers)
        self.register_action('ai_builder', self.handle_ai_builder)
        self.register_action('administration', self.handle_administration)

    # ===== DEV TOOLS HANDLERS =====

    def handle_system_status(self, item: MenuItem) -> bool:
        """system status submenu - local dev environment info"""
        options = [
            ("overview", "📊 overview", "quick system health check"),
            ("services", "⚡ services", "check running services"),
            ("ports", "🔌 ports", "view active port bindings"),
            ("python", "🐍 python", "python environment info"),
            ("disk", "💾 disk", "disk usage and data directories"),
            ("network", "🌐 network", "network connectivity status"),
            ("back", "← back", "return to dev tools"),
        ]

        handlers = {
            "overview": self._status_overview,
            "services": self._status_services,
            "ports": self._status_ports,
            "python": self._status_python,
            "disk": self._status_disk,
            "network": self._status_network,
        }

        return self.show_submenu(
            title="system status",
            subtitle="local development environment",
            options=options,
            handlers=handlers
        )

    def _status_overview(self):
        """Quick system health overview"""
        import socket
        import os
        from pathlib import Path
        from core.version import __version__, __build__

        lines = []
        root_dir = Path(__file__).parent.parent.parent.parent

        # Version
        lines.append(f"version: v{__version__}+build.{__build__}")
        lines.append(f"profile: development")
        lines.append(f"hostname: {socket.gethostname().lower()}")
        lines.append(f"user: {os.environ.get('USER', 'unknown')}")
        lines.append("")

        # Key directories
        lines.append("directories:")
        dirs = [
            ("core", root_dir / "core"),
            ("modules", root_dir / "modules"),
            ("data", root_dir / "data"),
        ]
        for name, path in dirs:
            status = "✓" if path.exists() else "✗"
            lines.append(f"  {status} {name}")

        # Django
        lines.append("")
        django_path = root_dir / "core" / "clients" / "web"
        if (django_path / "manage.py").exists():
            lines.append("✓ django project found")
        else:
            lines.append("✗ django project not found")

        # PostgreSQL
        try:
            result = subprocess.run(['psql', '--version'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                pg_version = result.stdout.strip().split()[-1] if result.stdout else "unknown"
                lines.append(f"✓ postgresql {pg_version}")
        except:
            lines.append("· postgresql not found")

        # Redis
        try:
            result = subprocess.run(['redis-cli', 'ping'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and 'PONG' in result.stdout:
                lines.append("✓ redis running")
            else:
                lines.append("· redis not running")
        except:
            lines.append("· redis not available")

        self.show_info_panel("overview", lines)

    def _status_services(self):
        """Check running development services"""
        lines = []

        # Check uvicorn/gunicorn
        try:
            result = subprocess.run(['pgrep', '-f', 'uvicorn'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                lines.append(f"✓ uvicorn running ({len(pids)} process{'es' if len(pids) > 1 else ''})")
            else:
                lines.append("· uvicorn not running")
        except:
            lines.append("· uvicorn: check failed")

        # Check celery
        try:
            result = subprocess.run(['pgrep', '-f', 'celery'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                lines.append(f"✓ celery running ({len(pids)} workers)")
            else:
                lines.append("· celery not running")
        except:
            lines.append("· celery: check failed")

        # Check redis
        try:
            result = subprocess.run(['pgrep', '-f', 'redis-server'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                lines.append("✓ redis-server running")
            else:
                lines.append("· redis-server not running")
        except:
            lines.append("· redis: check failed")

        # Check postgresql
        try:
            result = subprocess.run(['pgrep', '-f', 'postgres'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                lines.append("✓ postgresql running")
            else:
                lines.append("· postgresql not running")
        except:
            lines.append("· postgresql: check failed")

        lines.append("")
        lines.append("use web ui menu to start/stop dev server")

        self.show_info_panel("services", lines)

    def _status_ports(self):
        """Show active port bindings"""
        lines = []

        # Common dev ports to check
        ports_to_check = [
            (8000, "django/uvicorn"),
            (8001, "prometheus"),
            (5432, "postgresql"),
            (6379, "redis"),
            (5555, "celery flower"),
        ]

        lines.append("port bindings:")
        lines.append("")

        for port, service in ports_to_check:
            try:
                result = subprocess.run(
                    ['lsof', '-i', f':{port}', '-P', '-n'],
                    capture_output=True, text=True, timeout=2
                )
                if result.returncode == 0 and result.stdout.strip():
                    # Parse first process from output
                    output_lines = result.stdout.strip().split('\n')
                    if len(output_lines) > 1:
                        parts = output_lines[1].split()
                        process = parts[0] if parts else "unknown"
                        lines.append(f"  :{port}  ✓ {service} ({process})")
                    else:
                        lines.append(f"  :{port}  ✓ {service}")
                else:
                    lines.append(f"  :{port}  · {service} (free)")
            except:
                lines.append(f"  :{port}  ? {service}")

        self.show_info_panel("ports", lines)

    def _status_python(self):
        """Python environment information"""
        import sys
        import os
        from pathlib import Path

        lines = []
        root_dir = Path(__file__).parent.parent.parent.parent

        # Python version
        lines.append(f"python: {sys.version.split()[0]}")
        lines.append(f"executable: {sys.executable}")
        lines.append("")

        # Virtual environment
        venv_path = root_dir / "core" / "clients" / "web" / "venv"
        if venv_path.exists():
            lines.append(f"✓ venv exists: core/clients/web/venv")
            # Check if we're in venv
            if os.environ.get('VIRTUAL_ENV'):
                lines.append(f"✓ venv active")
            else:
                lines.append(f"· venv not activated")
        else:
            lines.append("· venv not found")

        lines.append("")

        # Key packages
        lines.append("key packages:")
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', 'django', 'uvicorn', 'celery'],
                capture_output=True, text=True
            )
            packages = {}
            current_pkg = None
            for line in result.stdout.split('\n'):
                if line.startswith('Name:'):
                    current_pkg = line.split(':')[1].strip().lower()
                elif line.startswith('Version:') and current_pkg:
                    packages[current_pkg] = line.split(':')[1].strip()

            for pkg in ['django', 'uvicorn', 'celery']:
                if pkg in packages:
                    lines.append(f"  ✓ {pkg} {packages[pkg]}")
                else:
                    lines.append(f"  · {pkg} not installed")
        except:
            lines.append("  could not check packages")

        self.show_info_panel("python", lines)

    def _status_disk(self):
        """Disk usage and data directories"""
        import os
        from pathlib import Path

        def format_size(size):
            if size >= 1024 * 1024 * 1024:
                return f"{size / (1024*1024*1024):.1f}gb"
            elif size >= 1024 * 1024:
                return f"{size / (1024*1024):.1f}mb"
            elif size >= 1024:
                return f"{size / 1024:.1f}kb"
            return f"{size}b"

        def dir_size(path):
            total = 0
            try:
                for f in Path(path).rglob('*'):
                    if f.is_file():
                        total += f.stat().st_size
            except:
                pass
            return total

        lines = []
        root_dir = Path(__file__).parent.parent.parent.parent

        # Project size
        lines.append("project directories:")
        dirs = [
            ("core", root_dir / "core"),
            ("modules", root_dir / "modules"),
            ("data", root_dir / "data"),
            ("archive", root_dir / "archive"),
        ]

        for name, path in dirs:
            if path.exists():
                size = dir_size(path)
                lines.append(f"  {format_size(size):>10}  {name}/")
            else:
                lines.append(f"  {'---':>10}  {name}/ (not found)")

        lines.append("")

        # Data subdirectories
        data_dir = root_dir / "data"
        if data_dir.exists():
            lines.append("data subdirectories:")
            subdirs = ['logs', 'media', 'cache', 'backups', 'deploy_logs']
            for subdir in subdirs:
                subpath = data_dir / subdir
                if subpath.exists():
                    size = dir_size(subpath)
                    lines.append(f"  {format_size(size):>10}  data/{subdir}/")

        self.show_info_panel("disk", lines)

    def _status_network(self):
        """Network connectivity status"""
        import socket

        lines = []

        # Local hostname
        lines.append(f"hostname: {socket.gethostname().lower()}")

        # Get local IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            lines.append(f"local ip: {local_ip}")
        except:
            lines.append("local ip: unknown")

        lines.append("")

        # Internet connectivity
        lines.append("connectivity:")
        tests = [
            ("1.1.1.1", 53, "cloudflare dns"),
            ("8.8.8.8", 53, "google dns"),
            ("github.com", 443, "github"),
        ]

        for host, port, name in tests:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                sock.close()
                if result == 0:
                    lines.append(f"  ✓ {name}")
                else:
                    lines.append(f"  ✗ {name}")
            except:
                lines.append(f"  ✗ {name}")

        lines.append("")

        # SSH to servers
        lines.append("ssh targets:")
        for server in ['rocksteady', 'bebop']:
            try:
                result = subprocess.run(
                    ['ssh', '-o', 'ConnectTimeout=2', '-o', 'BatchMode=yes', server, 'echo ok'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    lines.append(f"  ✓ {server}")
                else:
                    lines.append(f"  · {server} (not configured)")
            except:
                lines.append(f"  · {server} (timeout)")

        self.show_info_panel("network", lines)

    def handle_code_forge(self, item: MenuItem) -> bool:
        """Git and version control"""
        options = [
            ("status", "📊 git status", "show dev/prod repository status"),
            ("push_dev", "⬆️  push dev", "push to development (origin)"),
            ("push_all", "🔄 push all", "push to dev, server, manager, prod"),
            ("push_prod", "📦 push prod", "push filtered to production"),
            ("pull", "⬇️  pull", "pull latest changes"),
            ("branch", "🌿 branches", "show branch information"),
            ("log", "📜 log", "show recent commits"),
            ("setup", "⚙️  setup", "configure git remotes"),
            ("back", "← back", "return to dev tools"),
        ]

        handlers = {
            "status": self._git_show_status,
            "push_dev": self._git_push_dev,
            "push_all": self._git_push_all,
            "push_prod": self._git_push_prod,
            "pull": self._git_pull,
            "branch": self._git_branch_info,
            "log": self._git_show_log,
            "setup": self._git_setup,
        }

        return self.show_submenu(
            title="git",
            subtitle="source code management",
            options=options,
            handlers=handlers
        )

    def _git_show_status(self):
        """Show git status for dev and prod"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'git', 'status'],
            title="git status"
        )
        self.show_command_output(result)

    def _git_push_dev(self):
        """Push to development repository (origin)"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'git', 'push-dev'],
            title="pushing to dev"
        )
        self.show_command_output(result)

    def _git_push_all(self):
        """Push to all repositories"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'git', 'push-all'],
            title="pushing to all repos"
        )
        self.show_command_output(result)

    def _git_push_prod(self):
        """Push filtered to production"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'git', 'push-prod'],
            title="pushing to prod"
        )
        self.show_command_output(result)

    def _git_pull(self):
        """Pull from remote"""
        result = self.execute_command_streaming(
            ['git', 'pull'],
            title="pulling changes"
        )
        self.show_command_output(result)

    def _git_branch_info(self):
        """Show branch info"""
        self.update_content(title="branches", lines=["⏳ loading..."], color=Colors.CYAN)
        self.render()
        result = self.execute_command(['git', 'branch', '-vv'])
        self.show_command_output(result)

    def _git_show_log(self):
        """Show commit log"""
        self.update_content(title="commit log", lines=["⏳ loading..."], color=Colors.CYAN)
        self.render()
        result = self.execute_command(['git', 'log', '--oneline', '-20'])
        self.show_command_output(result)

    def _git_setup(self):
        """Setup git remotes"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'git', 'setup'],
            title="git setup"
        )
        self.show_command_output(result)

    def handle_web_ui(self, item: MenuItem) -> bool:
        """Local development web interface management"""
        # Check current server status for dynamic subtitle
        server_status = self._check_dev_server_status()

        options = [
            ("status", "📊 status", "check development server status"),
            ("start", "🚀 start", "start uvicorn development server"),
            ("stop", "⏹️  stop", "stop the development server"),
            ("restart", "🔄 restart", "restart development server"),
            ("open", "🌐 open browser", "open http://localhost:8000"),
            ("logs", "📝 logs", "view server output logs"),
            ("shell", "🐚 django shell", "open django interactive shell"),
            ("migrate", "🔃 migrate", "apply database migrations"),
            ("static", "📦 collectstatic", "collect static files"),
            ("back", "← back", "return to dev tools"),
        ]

        handlers = {
            "status": self._web_ui_show_status,
            "start": self._web_ui_start_server,
            "stop": self._web_ui_stop_server,
            "restart": self._web_ui_restart_server,
            "open": self._web_ui_open_browser,
            "logs": self._web_ui_show_logs,
            "shell": self._web_ui_django_shell,
            "migrate": self._web_ui_run_migrations,
            "static": self._web_ui_collectstatic,
        }

        return self.show_submenu(
            title="web ui",
            subtitle=f"local dev server · {server_status}",
            options=options,
            handlers=handlers
        )

    def _check_dev_server_status(self) -> str:
        """Quick check if dev server is running"""
        try:
            result = subprocess.run(['pgrep', '-f', 'uvicorn'], capture_output=True, text=True, timeout=1)
            if result.returncode == 0 and result.stdout.strip():
                return "running on :8000"
            return "stopped"
        except:
            return "unknown"

    def _web_ui_start_server(self):
        """start uvicorn development server in background"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'dev', 'run', '-b'],
            title="starting server"
        )
        self.show_command_output(result)

    def _web_ui_stop_server(self):
        """stop development server"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'dev', 'stop'],
            title="stopping server"
        )
        self.show_command_output(result)

    def _web_ui_restart_server(self):
        """restart development server"""
        import time

        # Stop first
        self.update_content(title="restarting", lines=["stopping server..."], color=Colors.CYAN)
        self.render()
        subprocess.run(['unibos-dev', 'dev', 'stop'], capture_output=True)
        time.sleep(1.0)

        # Start
        result = self.execute_command_streaming(
            ['unibos-dev', 'dev', 'run', '-b'],
            title="restarting server"
        )
        self.show_command_output(result)

    def _web_ui_show_status(self):
        """Show detailed server status"""
        lines = []

        # Check uvicorn process
        try:
            result = subprocess.run(['pgrep', '-f', 'uvicorn'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                lines.append(f"✓ uvicorn running (pid: {pids[0]})")
            else:
                lines.append("· uvicorn not running")
        except:
            lines.append("· uvicorn: check failed")

        # Check port 8000
        try:
            result = subprocess.run(
                ['lsof', '-i', ':8000', '-P', '-n'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                lines.append("✓ port 8000 in use")
            else:
                lines.append("· port 8000 free")
        except:
            pass

        lines.append("")

        # HTTP check
        try:
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:8000/'],
                capture_output=True, text=True, timeout=3
            )
            status_code = result.stdout.strip()
            if status_code.startswith('2') or status_code.startswith('3'):
                lines.append(f"✓ http://localhost:8000/ responding ({status_code})")
            else:
                lines.append(f"⚠ http://localhost:8000/ returned {status_code}")
        except:
            lines.append("· http check failed (server may be down)")

        lines.append("")
        lines.append("quick actions:")
        lines.append("  start: unibos-dev dev run -b")
        lines.append("  stop:  unibos-dev dev stop")

        self.show_info_panel("server status", lines)

    def _web_ui_open_browser(self):
        """Open browser to local development server"""
        import webbrowser
        url = "http://localhost:8000"

        lines = [
            f"opening {url}",
            "",
            "if browser doesn't open, visit manually:",
            f"  {url}",
            "",
            f"admin panel: {url}/admin/",
        ]

        try:
            webbrowser.open(url)
            lines.append("")
            lines.append("✓ browser opened")
        except Exception as e:
            lines.append("")
            lines.append(f"✗ could not open browser: {e}")

        self.show_info_panel("open browser", lines)

    def _web_ui_show_logs(self):
        """show server logs"""
        result = self.execute_command(['unibos-dev', 'dev', 'logs'])
        self.show_command_output(result)

    def _web_ui_django_shell(self):
        """Show django shell instructions"""
        lines = [
            "django interactive shell",
            "",
            "run this command in terminal:",
            "",
            "  cd core/clients/web",
            "  ./venv/bin/python manage.py shell",
            "",
            "or use:",
            "  unibos-dev dev shell",
            "",
            "common commands:",
            "  from django.contrib.auth.models import User",
            "  User.objects.all()",
        ]

        self.show_info_panel("django shell", lines)

    def _web_ui_run_migrations(self):
        """run django migrations"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'dev', 'migrate'],
            title="running migrations"
        )
        self.show_command_output(result)

    def _web_ui_collectstatic(self):
        """collect static files"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'dev', 'collectstatic'],
            title="collecting static files"
        )
        self.show_command_output(result)

    def handle_administration(self, item: MenuItem) -> bool:
        """System administration"""
        options = [
            ("users", "👤 user management", "manage users and permissions"),
            ("settings", "⚙️  system settings", "configure system settings"),
            ("modules", "📦 module management", "enable/disable modules"),
            ("logs", "📝 system logs", "view system logs"),
            ("django_admin", "🌐 django admin", "open django admin interface"),
            ("back", "← back", "return to dev tools"),
        ]

        handlers = {
            "users": self._admin_users,
            "settings": self._admin_settings,
            "modules": self._admin_modules,
            "logs": self._admin_logs,
            "django_admin": self._admin_django,
        }

        return self.show_submenu(
            title="admin",
            subtitle="system administration",
            options=options,
            handlers=handlers
        )

    def _admin_users(self):
        """User management placeholder"""
        self.show_info_panel("user management", [
            "coming soon",
            "",
            "for now, use django admin:",
            "  http://localhost:8000/admin/auth/user/"
        ], Colors.YELLOW)

    def _admin_settings(self):
        """System settings placeholder"""
        self.show_info_panel("system settings", [
            "coming soon",
            "",
            "for now, edit settings files directly:",
            "  core/clients/web/unibos_backend/settings/"
        ], Colors.YELLOW)

    def _admin_modules(self):
        """Module management placeholder"""
        self.show_info_panel("module management", [
            "coming soon",
            "",
            "modules are managed via .enabled files:",
            "  modules/<module_name>/.enabled"
        ], Colors.YELLOW)

    def _admin_logs(self):
        """View system logs"""
        from pathlib import Path
        log_path = Path(__file__).parent.parent.parent.parent / "core" / "clients" / "web" / "logs" / "django.log"
        result = self.execute_command(['tail', '-50', str(log_path)])
        self.show_command_output(result)

    def _admin_django(self):
        """Open Django admin info"""
        self.show_info_panel("django admin", [
            "django admin interface",
            "",
            "1. start server: unibos-dev dev run",
            "2. visit: http://localhost:8000/admin",
            "",
            "default credentials:",
            "  username: admin",
            "  password: (set during setup)"
        ])

    def handle_ai_builder(self, item: MenuItem) -> bool:
        """AI-powered development tools"""
        options = [
            ("claude", "🤖 claude code", "ai-powered coding assistant"),
            ("generate", "✨ generate code", "generate boilerplate code"),
            ("review", "🔍 code review", "ai code review suggestions"),
            ("docs", "📝 generate docs", "auto-generate documentation"),
            ("back", "← back", "return to dev tools"),
        ]

        handlers = {
            "claude": self._ai_claude,
            "generate": self._ai_generate,
            "review": self._ai_review,
            "docs": self._ai_docs,
        }

        return self.show_submenu(
            title="ai builder",
            subtitle="ai-powered development",
            options=options,
            handlers=handlers
        )

    def _ai_claude(self):
        """Claude Code info"""
        self.show_info_panel("claude code", [
            "claude code - ai coding assistant",
            "",
            "currently active: you're using claude code right now!",
            "",
            "features:",
            "  • code generation",
            "  • debugging assistance",
            "  • code review",
            "  • documentation",
            "",
            "just ask me anything about your code."
        ], Colors.MAGENTA)

    def _ai_generate(self):
        """Code generation placeholder"""
        self.show_info_panel("generate code", [
            "coming soon",
            "",
            "for now, use claude code to generate code:",
            "  just describe what you need!"
        ], Colors.YELLOW)

    def _ai_review(self):
        """Code review placeholder"""
        self.show_info_panel("code review", [
            "coming soon",
            "",
            "for now, ask claude code to review your code:",
            "  share your code and ask for review"
        ], Colors.YELLOW)

    def _ai_docs(self):
        """Documentation generation placeholder"""
        self.show_info_panel("generate docs", [
            "coming soon",
            "",
            "for now, ask claude code to generate docs:",
            "  share your code and ask for documentation"
        ], Colors.YELLOW)

    def handle_database_setup(self, item: MenuItem) -> bool:
        """PostgreSQL installation wizard"""
        options = [
            ("check", "🔍 check status", "check if postgresql is installed and running"),
            ("install", "📥 install postgresql", "install using homebrew (macos)"),
            ("create", "🗄️  create database", "create unibos database"),
            ("migrate", "🔄 run migrations", "apply django migrations"),
            ("backup", "💾 backup database", "create database backup"),
            ("restore", "♻️  restore database", "restore from backup"),
            ("back", "← back", "return to dev tools"),
        ]

        handlers = {
            "check": self._db_check_status,
            "install": self._db_install_postgresql,
            "create": self._db_create_database,
            "migrate": self._db_run_migrations,
            "backup": self._db_backup,
            "restore": self._db_restore,
        }

        return self.show_submenu(
            title="database",
            subtitle="postgresql database management",
            options=options,
            handlers=handlers
        )

    def _db_check_status(self):
        """Check database status"""
        result = self.execute_command(['unibos-dev', 'db', 'status'])
        self.show_command_output(result)

    def _db_install_postgresql(self):
        """install postgresql"""
        self.show_info_panel("postgresql installation", [
            "postgresql installation",
            "",
            "this will install postgresql using homebrew.",
            "",
            "run these commands in terminal:",
            "",
            "  brew install postgresql@14",
            "  brew services start postgresql@14",
            "",
            "then create database:",
            "",
            "  createdb unibos_dev",
        ], Colors.YELLOW)

    def _db_create_database(self):
        """create database"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'db', 'create'],
            title="creating database"
        )
        self.show_command_output(result)

    def _db_run_migrations(self):
        """Run migrations"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'db', 'migrate'],
            title="running migrations"
        )
        self.show_command_output(result)

    def _db_backup(self):
        """Backup database"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'db', 'backup'],
            title="database backup"
        )
        self.show_command_output(result)

    def _db_restore(self):
        """Restore database"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'db', 'restore'],
            title="database restore"
        )
        self.show_command_output(result)

    # ===== DEPLOY SERVERS =====

    # Server configurations
    SERVERS = {
        'rocksteady': {
            'name': 'rocksteady',
            'label': '🖥️  rocksteady',
            'description': 'production server',
            'env': 'production',
            'icon': '🖥️',
        },
        'bebop': {
            'name': 'bebop',
            'label': '🧪 bebop',
            'description': 'staging server',
            'env': 'staging',
            'icon': '🧪',
        },
    }

    def handle_deploy_servers(self, item: MenuItem) -> bool:
        """Server selection menu"""
        options = [
            ("rocksteady", "🖥️  rocksteady", "production server"),
            ("bebop", "🧪 bebop", "staging server"),
            ("history", "📜 deploy history", "view recent deployments"),
            ("back", "← back", "return to dev tools"),
        ]

        handlers = {
            "rocksteady": lambda: self._show_server_menu('rocksteady'),
            "bebop": lambda: self._show_server_menu('bebop'),
            "history": self._deploy_show_history,
        }

        return self.show_submenu(
            title="deploy",
            subtitle="select target server",
            options=options,
            handlers=handlers
        )

    def _deploy_show_history(self):
        """Show deployment history"""
        result = self.execute_command(['unibos-dev', 'deploy', 'history', '-n', '20'])
        self.show_command_output(result)

    def _show_server_menu(self, server_name: str):
        """Show operations menu for a specific server"""
        server = self.SERVERS.get(server_name, {})
        server_label = server.get('label', server_name)
        server_env = server.get('env', 'unknown')

        options = [
            ("status", "📊 status", f"check {server_name} service status"),
            ("deploy", "🚀 deploy", f"deploy to {server_name}"),
            ("deploy_log", "📜 last deploy log", f"view last deployment log"),
            ("start", "▶️  start", f"start service on {server_name}"),
            ("stop", "⏹️  stop", f"stop service on {server_name}"),
            ("restart", "🔄 restart", f"restart service on {server_name}"),
            ("logs", "📝 service logs", f"view {server_name} service logs"),
            ("backup", "💾 backup", f"backup {server_name} database"),
            ("backups", "📋 backups", f"list {server_name} backups"),
            ("ssh", "🔐 ssh", f"ssh info for {server_name}"),
            ("back", "← back", "return to server selection"),
        ]

        handlers = {
            "status": lambda: self._server_status(server_name),
            "deploy": lambda: self._server_deploy(server_name),
            "deploy_log": lambda: self._server_deploy_log(server_name),
            "start": lambda: self._server_start(server_name),
            "stop": lambda: self._server_stop(server_name),
            "restart": lambda: self._server_restart(server_name),
            "logs": lambda: self._server_logs(server_name),
            "backup": lambda: self._server_backup(server_name),
            "backups": lambda: self._server_list_backups(server_name),
            "ssh": lambda: self._server_ssh(server_name),
        }

        return self.show_submenu(
            title=f"{server_label}",
            subtitle=f"{server_env} environment",
            options=options,
            handlers=handlers
        )

    def _server_status(self, server: str):
        """Check server status"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'deploy', 'status', server],
            title=f"checking {server} status"
        )
        self.show_command_output(result)

    def _server_deploy(self, server: str):
        """Deploy to server with live streaming output"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'deploy', 'run', server],
            title=f"deploying to {server}"
        )
        self.show_command_output(result)

    def _server_deploy_log(self, server: str):
        """View last deployment log"""
        result = self.execute_command(
            ['unibos-dev', 'deploy', 'log', server, '--last']
        )
        self.show_command_output(result)

    def _server_start(self, server: str):
        """Start server service"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'deploy', 'start', server],
            title=f"starting {server}"
        )
        self.show_command_output(result)

    def _server_stop(self, server: str):
        """Stop server service"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'deploy', 'stop', server],
            title=f"stopping {server}"
        )
        self.show_command_output(result)

    def _server_restart(self, server: str):
        """Restart server service"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'deploy', 'restart', server],
            title=f"restarting {server}"
        )
        self.show_command_output(result)

    def _server_logs(self, server: str):
        """View server logs"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'deploy', 'logs', server],
            title=f"{server} logs"
        )
        self.show_command_output(result)

    def _server_backup(self, server: str):
        """Create database backup"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'deploy', 'backup', server],
            title=f"backing up {server}"
        )
        self.show_command_output(result)

    def _server_list_backups(self, server: str):
        """List available backups"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'deploy', 'backups', server],
            title=f"{server} backups"
        )
        self.show_command_output(result)

    def _server_ssh(self, server: str):
        """SSH connection info"""
        self.show_info_panel(f"ssh to {server}", [
            f"ssh connection to {server}",
            "",
            "run this command in your terminal:",
            "",
            f"  ssh {server}",
            "",
            f"or use: unibos-dev deploy ssh {server}",
        ], Colors.YELLOW)

    def handle_version_manager(self, item: MenuItem) -> bool:
        """Version control and archiving"""
        from core.version import __version__, __build__, VERSION_CODENAME

        options = [
            ("info", "📊 version info", "show detailed version information"),
            ("browse", "📋 browse archives", "view version archive history"),
            ("create", "📦 quick release", "create new version archive"),
            ("increment", "🔼 increment version", "bump version number"),
            ("analyze", "📈 archive analyzer", "analyze archive statistics"),
            ("git_status", "🔀 git status", "show git repository status"),
            ("git_tag", "🏷️  create git tag", "create and push git tag"),
            ("back", "← back", "return to dev tools"),
        ]

        handlers = {
            "info": self._version_show_info,
            "browse": self._version_browse_archives,
            "create": self._version_quick_release,
            "increment": self._version_increment,
            "analyze": self._version_analyze,
            "git_status": self._version_git_status,
            "git_tag": self._version_create_tag,
        }

        return self.show_submenu(
            title="versions",
            subtitle=f"v{__version__}+{__build__} · {VERSION_CODENAME.lower()}",
            options=options,
            handlers=handlers
        )

    def _version_show_info(self):
        """Show detailed version information - clean format"""
        from core.version import (
            __version__, __build__, parse_build_timestamp, get_archive_name,
            FEATURES, VERSION_CODENAME, RELEASE_DATE, RELEASE_TYPE
        )

        build_info = parse_build_timestamp(__build__)

        lines = [
            f"v{__version__}+build.{__build__}",
            f"{VERSION_CODENAME.lower()} · {RELEASE_TYPE.lower()} · {RELEASE_DATE}",
            "",
        ]

        if build_info:
            lines.append(f"built: {build_info['date']} {build_info['time']}")
            lines.append("")

        lines.extend([
            f"archive: {get_archive_name()}",
            "",
            "features:",
        ])

        for feature, enabled in FEATURES.items():
            status = "✓" if enabled else "·"
            lines.append(f"  {status} {feature}")

        self.show_info_panel("version info", lines)

    def _version_quick_release(self):
        """Quick release wizard - simplified"""
        from core.version import __version__, get_new_build

        parts = [int(x) for x in __version__.split('.')]
        options = [
            ("build", "📦 build", f"v{__version__} (new timestamp)"),
            ("patch", "🔧 patch", f"v{parts[0]}.{parts[1]}.{parts[2]+1}"),
            ("minor", "✨ minor", f"v{parts[0]}.{parts[1]+1}.0"),
            ("major", "🚀 major", f"v{parts[0]+1}.0.0"),
        ]

        selected = 0

        while True:
            lines = [
                f"current: v{__version__}",
                "",
            ]

            for i, (key, label, preview) in enumerate(options):
                if i == selected:
                    lines.append(f" → {label}  ·  {preview}")
                else:
                    lines.append(f"   {label}")

            self.update_content(title="quick release", lines=lines, color=Colors.CYAN)
            self.render()

            key = self.get_key()

            if key == 'UP':
                selected = (selected - 1) % len(options)
            elif key == 'DOWN':
                selected = (selected + 1) % len(options)
            elif key == 'ENTER' or key == 'RIGHT':
                self._execute_release(options[selected][0])
                return
            elif key == 'ESC' or key == 'LEFT':
                return

    def _execute_release(self, release_type: str):
        """Execute the release process using ReleasePipeline"""
        from core.profiles.dev.release_pipeline import ReleasePipeline, PipelineStep

        # Map 'build' to 'daily' for pipeline
        pipeline_type = 'daily' if release_type == 'build' else release_type

        pipeline = ReleasePipeline()
        new_version = pipeline.calculate_new_version(pipeline_type)
        new_build = pipeline.get_new_build()

        # Progress tracking
        progress_lines = []
        current_step_name = ""

        def on_step_start(step: PipelineStep):
            nonlocal current_step_name
            current_step_name = step.name

        def on_step_complete(step: PipelineStep):
            if step.status == "success":
                progress_lines.append(f"  ✓ {step.name}")
            elif step.status == "failed":
                progress_lines.append(f"  ✗ {step.name}: {step.message}")
            elif step.status == "skipped":
                progress_lines.append(f"  ○ {step.name} (skipped)")

        def on_progress(msg: str):
            nonlocal progress_lines
            # Update display
            lines = [
                f"releasing v{new_version}+build.{new_build}",
                "",
                f"  ◦ {current_step_name}..." if current_step_name else "",
            ] + progress_lines[-8:]  # Show last 8 completed steps

            self.update_content(title="release pipeline", lines=lines, color=Colors.CYAN)
            self.render()

        # Set callbacks
        pipeline.on_step_start = on_step_start
        pipeline.on_step_complete = on_step_complete
        pipeline.on_progress = on_progress

        # Show initial state
        lines = [
            f"releasing v{new_version}+build.{new_build}",
            "",
            "  preparing pipeline...",
        ]
        self.update_content(title="release pipeline", lines=lines, color=Colors.CYAN)
        self.render()

        # Run pipeline
        result = pipeline.run(
            release_type=pipeline_type,
            message=f"chore: release v{new_version}",
            repos=['dev', 'server', 'manager', 'prod'],
            dry_run=False
        )

        # Show result
        if result.success:
            lines = [
                f"✓ v{result.version}+build.{result.build}",
                "",
            ] + progress_lines + [
                "",
                f"completed in {result.duration:.1f}s",
            ]
            if result.archive_path:
                lines.append(f"archive: {result.archive_path.split('/')[-1]}")
            color = Colors.GREEN
        else:
            lines = [
                f"✗ release failed",
                "",
            ] + progress_lines + [
                "",
                f"error: {result.error}",
            ]
            color = Colors.RED

        self.update_content(title="release complete" if result.success else "release failed", lines=lines, color=color)
        self.render()

        while True:
            key = self.get_key()
            if key == 'ESC':
                if result.success:
                    # Restart TUI to reflect new version
                    self._restart_tui()
                break

    def _restart_tui(self):
        """Restart TUI to reflect updated version"""
        import os
        import sys

        # Show restart message
        self.update_content(
            title="restarting",
            lines=["", "  tui yeniden başlatılıyor...", ""],
            color=Colors.CYAN
        )
        self.render()

        # Clean up terminal
        self.cleanup()

        # Re-execute the TUI
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def _version_increment(self):
        """Version increment wizard - simplified"""
        from core.version import __version__

        parts = [int(x) for x in __version__.split('.')]
        options = [
            ("patch", "🔧 patch", f"v{parts[0]}.{parts[1]}.{parts[2]+1} (bugfix)"),
            ("minor", "✨ minor", f"v{parts[0]}.{parts[1]+1}.0 (feature)"),
            ("major", "🚀 major", f"v{parts[0]+1}.0.0 (breaking)"),
        ]

        selected = 0

        while True:
            lines = [f"current: v{__version__}", ""]

            for i, (key, label, preview) in enumerate(options):
                if i == selected:
                    lines.append(f" → {label}  ·  {preview}")
                else:
                    lines.append(f"   {label}")

            self.update_content(title="increment", lines=lines, color=Colors.CYAN)
            self.render()

            key = self.get_key()

            if key == 'UP':
                selected = (selected - 1) % len(options)
            elif key == 'DOWN':
                selected = (selected + 1) % len(options)
            elif key == 'ENTER' or key == 'RIGHT':
                self._execute_release(options[selected][0])
                return
            elif key == 'ESC' or key == 'LEFT':
                return

    def _version_create_tag(self):
        """Create git tag - simplified"""
        from core.version import __version__

        self.show_info_panel("git tag", [
            f"tag: v{__version__}",
            "",
            "commands:",
            f"  git tag -a v{__version__} -m \"v{__version__}\"",
            f"  git push --tags",
            "",
            "or: unibos-dev git push-dev --tags"
        ])

    def _version_browse_archives(self):
        """Browse version archives with new format support"""
        from pathlib import Path
        import json
        import re

        archive_dir = Path(__file__).parent.parent.parent.parent / "archive" / "versions"

        if not archive_dir.exists():
            self.show_info_panel("browse archives", [
                "archive directory not found",
                "",
                f"expected: {archive_dir}",
            ], Colors.YELLOW)
            return

        # Find all archives - both old and new format
        archives = []

        # Scan archive directory
        for item in sorted(archive_dir.iterdir(), reverse=True):
            if item.is_dir():
                archive_info = {
                    'path': item,
                    'name': item.name,
                    'version': 'unknown',
                    'build': None,
                    'date': None,
                    'format': 'unknown'
                }

                # Try to read VERSION.json
                version_file = item / 'VERSION.json'
                if version_file.exists():
                    try:
                        with open(version_file) as f:
                            data = json.load(f)

                            # New format (v1.0.0+)
                            if 'version' in data and isinstance(data['version'], dict):
                                v = data['version']
                                archive_info['version'] = f"{v.get('major', 0)}.{v.get('minor', 0)}.{v.get('patch', 0)}"
                                archive_info['build'] = v.get('build')
                                archive_info['format'] = 'new'
                                if 'build_info' in data:
                                    archive_info['date'] = data['build_info'].get('date')
                            # Old format
                            else:
                                archive_info['version'] = data.get('version', 'unknown')
                                archive_info['build'] = data.get('build_number') or data.get('build')
                                archive_info['date'] = data.get('release_date', '')[:10] if data.get('release_date') else None
                                archive_info['format'] = 'old'
                    except:
                        pass

                # Parse version from directory name if not found in VERSION.json
                if archive_info['version'] == 'unknown':
                    # New format: unibos_v1.0.0_b20251201222554
                    new_match = re.match(r'unibos_v(\d+\.\d+\.\d+)_b(\d{14})', item.name)
                    if new_match:
                        archive_info['version'] = new_match.group(1)
                        archive_info['build'] = new_match.group(2)
                        archive_info['format'] = 'new'
                    else:
                        # Old format: unibos_v534_20251116_...
                        old_match = re.match(r'unibos_v(\d+)_(\d{8})', item.name)
                        if old_match:
                            archive_info['version'] = f"0.{old_match.group(1)}.0"
                            archive_info['date'] = f"{old_match.group(2)[:4]}-{old_match.group(2)[4:6]}-{old_match.group(2)[6:8]}"
                            archive_info['format'] = 'old'

                archives.append(archive_info)

        # Build display - simplified
        lines = [f"{len(archives)} archives", ""]

        if archives:
            for i, archive in enumerate(archives[:15]):  # Show last 15
                if archive['format'] == 'new' and archive['build']:
                    b = archive['build']
                    if len(b) == 14:
                        lines.append(f"  v{archive['version']} · {b[0:4]}-{b[4:6]}-{b[6:8]} {b[8:10]}:{b[10:12]}")
                    else:
                        lines.append(f"  v{archive['version']} · b{archive['build']}")
                else:
                    date_str = archive['date'] or ''
                    lines.append(f"  v{archive['version']} · {date_str}")

            if len(archives) > 15:
                lines.extend(["", f"  +{len(archives) - 15} more"])
        else:
            lines.append("  no archives found")

        self.show_info_panel("archives", lines)

    def _version_analyze(self):
        """Analyze archives with statistics - simplified"""
        from pathlib import Path

        archive_dir = Path(__file__).parent.parent.parent.parent / "archive" / "versions"

        def format_size(size):
            if size >= 1024 * 1024 * 1024:
                return f"{size / (1024*1024*1024):.1f}gb"
            elif size >= 1024 * 1024:
                return f"{size / (1024*1024):.1f}mb"
            elif size >= 1024:
                return f"{size / 1024:.1f}kb"
            return f"{size}b"

        if not archive_dir.exists():
            lines = ["archive directory not found"]
        else:
            total_size = 0
            sizes = []

            for item in archive_dir.iterdir():
                if item.is_dir():
                    dir_size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                    total_size += dir_size
                    sizes.append((item.name, dir_size))

            lines = [
                f"{len(sizes)} archives · {format_size(total_size)} total",
                "",
            ]

            if sizes:
                avg_size = total_size / len(sizes)
                lines.append(f"avg: {format_size(int(avg_size))}")
                lines.append("")

                sizes.sort(key=lambda x: x[1], reverse=True)
                lines.append("largest:")
                for name, size in sizes[:5]:
                    short_name = name[:35] + "..." if len(name) > 38 else name
                    lines.append(f"  {format_size(size):>8} {short_name}")

                anomalies = [s for s in sizes if s[1] > avg_size * 2]
                if anomalies:
                    lines.extend(["", f"⚠ {len(anomalies)} anomalies (>2x avg)"])

        self.show_info_panel("analyzer", lines)

    def _version_git_status(self):
        """show git status - simplified"""
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent.parent
        lines = []

        try:
            # Get git status
            result = subprocess.run(
                ['git', 'status', '--short', '--branch'],
                capture_output=True, text=True, cwd=project_root
            )

            # Parse branch info
            status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []

            if status_lines:
                branch_line = status_lines[0]
                lines.append(f"branch: {branch_line.replace('## ', '')}")
                lines.append("")

                # File changes
                changes = status_lines[1:] if len(status_lines) > 1 else []
                if changes:
                    lines.append(f"changes ({len(changes)}):")
                    for change in changes[:15]:
                        lines.append(f"  {change}")
                    if len(changes) > 15:
                        lines.append(f"  ... and {len(changes) - 15} more")
                else:
                    lines.append("✓ working tree clean")

            # Get recent commits
            commits_result = subprocess.run(
                ['git', 'log', '--oneline', '-5'],
                capture_output=True, text=True, cwd=project_root
            )

            if commits_result.stdout.strip():
                lines.append("")
                lines.append("recent commits:")
                for commit in commits_result.stdout.strip().split('\n'):
                    lines.append(f"  {commit}")

        except Exception as e:
            lines = [f"error: {e}"]

        self.show_info_panel("git status", lines)

def run_interactive():
    """Run the dev TUI"""
    tui = UnibosDevTUI()
    tui.run()


if __name__ == "__main__":
    run_interactive()
