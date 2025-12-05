"""
UNIBOS Worker TUI - Worker Management Interface
TUI for managing Celery background workers
"""

from typing import List
from core.clients.tui import BaseTUI
from core.clients.tui.components import MenuSection
from core.clients.cli.framework.ui import MenuItem, Colors


class WorkerTUI(BaseTUI):
    """Worker TUI for background task management"""

    def __init__(self):
        """Initialize worker TUI with proper config"""
        from core.clients.tui.base import TUIConfig

        config = TUIConfig(
            title="unibos-worker",
            version="v1.1.6",
            location="worker",
            sidebar_width=30,
            show_splash=True,
            quick_splash=True,
            lowercase_ui=True,
            show_breadcrumbs=True,
            show_time=True,
            show_hostname=True,
            show_status_led=True
        )

        super().__init__(config)

        # Register worker-specific handlers
        self.register_worker_handlers()

    def get_profile_name(self) -> str:
        """Get profile name"""
        return "worker"

    def get_menu_sections(self) -> List[MenuSection]:
        """Get worker menu sections"""
        return [
            # Section 1: Workers
            MenuSection(
                id='workers',
                label='workers',
                icon='👷',
                items=[
                    MenuItem(
                        id='start_all',
                        label='🚀 start all workers',
                        icon='',
                        description='start all worker processes\n\n'
                                   '→ Start core worker\n'
                                   '→ Start OCR worker\n'
                                   '→ Start media worker\n\n'
                                   'Start all background workers',
                        enabled=True
                    ),
                    MenuItem(
                        id='start_core',
                        label='⚙️ start core worker',
                        icon='',
                        description='core task processing\n\n'
                                   '→ Health checks\n'
                                   '→ Cleanup tasks\n'
                                   '→ Notifications\n\n'
                                   'Start core worker only',
                        enabled=True
                    ),
                    MenuItem(
                        id='start_ocr',
                        label='📄 start ocr worker',
                        icon='',
                        description='document processing\n\n'
                                   '→ OCR extraction\n'
                                   '→ Text processing\n'
                                   '→ Document indexing\n\n'
                                   'Start OCR worker only',
                        enabled=True
                    ),
                    MenuItem(
                        id='start_media',
                        label='🎬 start media worker',
                        icon='',
                        description='media processing\n\n'
                                   '→ Image resizing\n'
                                   '→ Video transcoding\n'
                                   '→ Thumbnail generation\n\n'
                                   'Start media worker only',
                        enabled=True
                    ),
                    MenuItem(
                        id='stop_all',
                        label='⏹️ stop all workers',
                        icon='',
                        description='stop all workers\n\n'
                                   '→ Graceful shutdown\n'
                                   '→ Complete pending tasks\n'
                                   '→ Release resources\n\n'
                                   'Stop all running workers',
                        enabled=True
                    ),
                ]
            ),

            # Section 2: Tasks
            MenuSection(
                id='tasks',
                label='tasks',
                icon='📋',
                items=[
                    MenuItem(
                        id='view_active',
                        label='📊 active tasks',
                        icon='',
                        description='currently running tasks\n\n'
                                   '→ Task list\n'
                                   '→ Progress info\n'
                                   '→ Worker assignment\n\n'
                                   'View active tasks',
                        enabled=True
                    ),
                    MenuItem(
                        id='view_pending',
                        label='⏳ pending tasks',
                        icon='',
                        description='queued tasks\n\n'
                                   '→ Queue length\n'
                                   '→ Task priority\n'
                                   '→ Estimated time\n\n'
                                   'View pending tasks',
                        enabled=True
                    ),
                    MenuItem(
                        id='view_scheduled',
                        label='📅 scheduled tasks',
                        icon='',
                        description='scheduled/periodic tasks\n\n'
                                   '→ Cron jobs\n'
                                   '→ Next run time\n'
                                   '→ Schedule info\n\n'
                                   'View scheduled tasks',
                        enabled=True
                    ),
                    MenuItem(
                        id='purge_queue',
                        label='🗑️ purge queue',
                        icon='',
                        description='clear all pending tasks\n\n'
                                   '→ Remove pending tasks\n'
                                   '→ Clear queue\n'
                                   '→ Reset state\n\n'
                                   'Purge task queue (caution!)',
                        enabled=True
                    ),
                ]
            ),

            # Section 3: Status
            MenuSection(
                id='status',
                label='status',
                icon='📈',
                items=[
                    MenuItem(
                        id='worker_status',
                        label='💚 worker status',
                        icon='',
                        description='worker health\n\n'
                                   '→ Active workers\n'
                                   '→ Queue status\n'
                                   '→ Connection info\n\n'
                                   'View worker status',
                        enabled=True
                    ),
                    MenuItem(
                        id='queue_stats',
                        label='📊 queue statistics',
                        icon='',
                        description='queue metrics\n\n'
                                   '→ Tasks processed\n'
                                   '→ Success rate\n'
                                   '→ Average time\n\n'
                                   'View queue statistics',
                        enabled=True
                    ),
                    MenuItem(
                        id='worker_logs',
                        label='📝 worker logs',
                        icon='',
                        description='worker log output\n\n'
                                   '→ Recent logs\n'
                                   '→ Error logs\n'
                                   '→ Task results\n\n'
                                   'View worker logs',
                        enabled=True
                    ),
                ]
            ),
        ]

    def register_worker_handlers(self):
        """Register all worker action handlers"""
        # Worker section
        self.register_action('start_all', self.handle_start_all)
        self.register_action('start_core', self.handle_start_core)
        self.register_action('start_ocr', self.handle_start_ocr)
        self.register_action('start_media', self.handle_start_media)
        self.register_action('stop_all', self.handle_stop_all)

        # Tasks section
        self.register_action('view_active', self.handle_view_active)
        self.register_action('view_pending', self.handle_view_pending)
        self.register_action('view_scheduled', self.handle_view_scheduled)
        self.register_action('purge_queue', self.handle_purge_queue)

        # Status section
        self.register_action('worker_status', self.handle_worker_status)
        self.register_action('queue_stats', self.handle_queue_stats)
        self.register_action('worker_logs', self.handle_worker_logs)

    # ===== WORKER HANDLERS =====

    def handle_start_all(self, item: MenuItem) -> bool:
        """Start all workers"""
        self.update_content(
            title="Start All Workers",
            lines=[
                "🚀 Starting All Workers",
                "",
                "Workers to start:",
                "",
                "→ Core Worker (default queue)",
                "→ OCR Worker (ocr queue)",
                "→ Media Worker (media queue)",
                "",
                "Command:",
                "  celery -A core.profiles.worker.celery_app worker \\",
                "    -Q default,ocr,media -l INFO",
                "",
                "Or start individually:",
                "  unibos-worker start --type core",
                "  unibos-worker start --type ocr",
                "  unibos-worker start --type media",
                "",
                "Press ESC to continue"
            ],
            color=Colors.GREEN
        )
        self.render()
        return True

    def handle_start_core(self, item: MenuItem) -> bool:
        """Start core worker"""
        self.update_content(
            title="Start Core Worker",
            lines=[
                "⚙️ Starting Core Worker",
                "",
                "Core worker handles:",
                "  • Health checks",
                "  • Cleanup tasks",
                "  • Notifications",
                "  • General background tasks",
                "",
                "Command:",
                "  celery -A core.profiles.worker.celery_app worker \\",
                "    -Q default -l INFO",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_start_ocr(self, item: MenuItem) -> bool:
        """Start OCR worker"""
        self.update_content(
            title="Start OCR Worker",
            lines=[
                "📄 Starting OCR Worker",
                "",
                "OCR worker handles:",
                "  • Document text extraction",
                "  • PDF processing",
                "  • Image OCR",
                "  • Text indexing",
                "",
                "Requirements:",
                "  • Tesseract OCR installed",
                "  • Sufficient RAM (512MB+)",
                "",
                "Command:",
                "  celery -A core.profiles.worker.celery_app worker \\",
                "    -Q ocr -l INFO",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_start_media(self, item: MenuItem) -> bool:
        """Start media worker"""
        self.update_content(
            title="Start Media Worker",
            lines=[
                "🎬 Starting Media Worker",
                "",
                "Media worker handles:",
                "  • Image resizing",
                "  • Video transcoding",
                "  • Thumbnail generation",
                "  • Format conversion",
                "",
                "Requirements:",
                "  • FFmpeg installed",
                "  • ImageMagick installed",
                "  • Sufficient RAM (1GB+)",
                "",
                "Command:",
                "  celery -A core.profiles.worker.celery_app worker \\",
                "    -Q media -l INFO",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_stop_all(self, item: MenuItem) -> bool:
        """Stop all workers"""
        self.update_content(
            title="Stop All Workers",
            lines=[
                "⏹️ Stopping All Workers",
                "",
                "This will:",
                "  • Send shutdown signal to all workers",
                "  • Wait for current tasks to complete",
                "  • Release resources",
                "",
                "Commands:",
                "",
                "→ Graceful shutdown:",
                "  celery -A core.profiles.worker.celery_app control shutdown",
                "",
                "→ Force stop:",
                "  pkill -f 'celery.*worker'",
                "",
                "Press ESC to continue"
            ],
            color=Colors.YELLOW
        )
        self.render()
        return True

    # ===== TASK HANDLERS =====

    def handle_view_active(self, item: MenuItem) -> bool:
        """View active tasks"""
        self.update_content(
            title="Active Tasks",
            lines=[
                "📊 Active Tasks",
                "",
                "To view active tasks:",
                "",
                "→ List active tasks:",
                "  celery -A core.profiles.worker.celery_app inspect active",
                "",
                "→ Watch task progress:",
                "  celery -A core.profiles.worker.celery_app events",
                "",
                "→ Using Flower (if installed):",
                "  celery -A core.profiles.worker.celery_app flower",
                "  Open: http://localhost:5555",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_view_pending(self, item: MenuItem) -> bool:
        """View pending tasks"""
        self.update_content(
            title="Pending Tasks",
            lines=[
                "⏳ Pending Tasks",
                "",
                "To view pending tasks:",
                "",
                "→ Reserved tasks (assigned to workers):",
                "  celery -A core.profiles.worker.celery_app inspect reserved",
                "",
                "→ Queue length (Redis):",
                "  redis-cli llen celery",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_view_scheduled(self, item: MenuItem) -> bool:
        """View scheduled tasks"""
        self.update_content(
            title="Scheduled Tasks",
            lines=[
                "📅 Scheduled Tasks",
                "",
                "To view scheduled tasks:",
                "",
                "→ Scheduled tasks:",
                "  celery -A core.profiles.worker.celery_app inspect scheduled",
                "",
                "→ Periodic tasks (celery beat):",
                "  Check celerybeat configuration",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_purge_queue(self, item: MenuItem) -> bool:
        """Purge task queue"""
        self.update_content(
            title="Purge Queue",
            lines=[
                "🗑️ Purge Task Queue",
                "",
                "⚠️  WARNING: This will delete all pending tasks!",
                "",
                "To purge queue:",
                "",
                "→ Purge all queues:",
                "  celery -A core.profiles.worker.celery_app purge",
                "",
                "→ Purge specific queue:",
                "  celery -A core.profiles.worker.celery_app purge -Q ocr",
                "",
                "Press ESC to continue"
            ],
            color=Colors.RED
        )
        self.render()
        return True

    # ===== STATUS HANDLERS =====

    def handle_worker_status(self, item: MenuItem) -> bool:
        """Show worker status"""
        self.update_content(
            title="Worker Status",
            lines=[
                "💚 Worker Status",
                "",
                "To check worker status:",
                "",
                "→ Active workers:",
                "  celery -A core.profiles.worker.celery_app inspect active_queues",
                "",
                "→ Worker stats:",
                "  celery -A core.profiles.worker.celery_app inspect stats",
                "",
                "→ Ping workers:",
                "  celery -A core.profiles.worker.celery_app inspect ping",
                "",
                "Press ESC to continue"
            ],
            color=Colors.GREEN
        )
        self.render()
        return True

    def handle_queue_stats(self, item: MenuItem) -> bool:
        """Show queue statistics"""
        self.update_content(
            title="Queue Statistics",
            lines=[
                "📊 Queue Statistics",
                "",
                "Available Queues:",
                "  • default - core tasks",
                "  • ocr - document processing",
                "  • media - media processing",
                "",
                "To view stats:",
                "",
                "→ Worker statistics:",
                "  celery -A core.profiles.worker.celery_app inspect stats",
                "",
                "→ Queue lengths:",
                "  redis-cli llen default",
                "  redis-cli llen ocr",
                "  redis-cli llen media",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_worker_logs(self, item: MenuItem) -> bool:
        """Show worker logs"""
        self.update_content(
            title="Worker Logs",
            lines=[
                "📝 Worker Logs",
                "",
                "Log locations:",
                "",
                "→ Celery worker logs:",
                "  tail -f /var/log/celery/worker.log",
                "",
                "→ System journal:",
                "  sudo journalctl -u celery -f",
                "",
                "→ Real-time events:",
                "  celery -A core.profiles.worker.celery_app events",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True


def run_interactive():
    """Run the worker TUI"""
    tui = WorkerTUI()
    tui.run()


if __name__ == "__main__":
    run_interactive()
