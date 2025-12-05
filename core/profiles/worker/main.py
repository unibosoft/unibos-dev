#!/usr/bin/env python3
"""
UNIBOS Worker CLI - Main Entry Point
Background task processing with Celery workers
"""

import click
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.version import __version__


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name='unibos-worker')
@click.pass_context
def cli(ctx):
    """
    👷 unibos-worker - background task processing

    manages celery workers for background tasks:
    - task queue processing
    - ocr document processing
    - media transcoding
    - scheduled jobs

    examples:
        unibos-worker                  # interactive tui mode
        unibos-worker start            # start all workers
        unibos-worker start --type ocr # start ocr worker only
        unibos-worker stop             # stop all workers
        unibos-worker status           # worker status
        unibos-worker tasks            # view task queue
    """
    ctx.ensure_object(dict)

    # If no subcommand, run TUI
    if ctx.invoked_subcommand is None:
        try:
            from core.profiles.worker.tui import run_interactive
            run_interactive()
        except KeyboardInterrupt:
            click.echo("\n\n👋 goodbye!")
            sys.exit(0)
        except Exception as e:
            click.echo(f"\n❌ error: {e}", err=True)
            sys.exit(1)


@cli.command()
@click.option('--type', 'worker_type', default='all',
              type=click.Choice(['all', 'core', 'ocr', 'media']),
              help='Worker type to start')
@click.option('--queues', default=None, help='Comma-separated list of queues')
@click.option('--concurrency', '-c', default=None, type=int, help='Number of worker processes')
@click.option('--loglevel', '-l', default='INFO',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              help='Log level')
@click.option('--detach', '-d', is_flag=True, help='Run worker in background')
def start(worker_type, queues, concurrency, loglevel, detach):
    """Start Celery workers"""
    import subprocess
    import os

    click.echo(f"🚀 Starting {worker_type} worker(s)...")

    if queues:
        queue_list = queues.split(',')
    else:
        queue_map = {
            'all': ['default', 'ocr', 'media'],
            'core': ['default'],
            'ocr': ['ocr'],
            'media': ['media'],
        }
        queue_list = queue_map.get(worker_type, ['default'])

    click.echo(f"   Queues: {', '.join(queue_list)}")
    click.echo(f"   Log level: {loglevel}")

    # Build celery command
    cmd = [
        'celery',
        '-A', 'core.profiles.worker.celery_app',
        'worker',
        '-Q', ','.join(queue_list),
        '-l', loglevel,
        '-n', f'{worker_type}@%h',
    ]

    if concurrency:
        cmd.extend(['-c', str(concurrency)])
        click.echo(f"   Concurrency: {concurrency}")

    if detach:
        cmd.append('--detach')
        click.echo("   Mode: Background (detached)")
    else:
        click.echo("   Mode: Foreground (Ctrl+C to stop)")

    click.echo()

    # Set environment
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_root.parent)

    try:
        if detach:
            subprocess.run(cmd, env=env, check=True)
            click.echo("✅ Worker started in background")
        else:
            # Run in foreground - this will block
            subprocess.run(cmd, env=env)
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Failed to start worker: {e}", err=True)
        sys.exit(1)
    except FileNotFoundError:
        click.echo("❌ Celery not found. Install with: pip install celery[redis]", err=True)
        sys.exit(1)


@cli.command()
@click.option('--force', '-f', is_flag=True, help='Force kill workers')
def stop(force):
    """Stop all workers"""
    import subprocess

    click.echo("⏹️  Stopping all workers...")

    if force:
        # Force kill
        result = subprocess.run(['pkill', '-9', '-f', 'celery.*worker'], capture_output=True)
        if result.returncode == 0:
            click.echo("✅ Workers force killed")
        else:
            click.echo("ℹ️  No workers running")
    else:
        # Graceful shutdown
        try:
            subprocess.run([
                'celery', '-A', 'core.profiles.worker.celery_app',
                'control', 'shutdown'
            ], check=True, capture_output=True)
            click.echo("✅ Shutdown signal sent to workers")
        except subprocess.CalledProcessError:
            click.echo("ℹ️  No workers running or shutdown failed")
        except FileNotFoundError:
            # Fallback to pkill
            subprocess.run(['pkill', '-f', 'celery.*worker'], capture_output=True)
            click.echo("✅ Workers stopped")


@cli.command()
def status():
    """Show worker status"""
    import subprocess
    import json

    click.echo("👷 Worker Status\n")

    # Check if Redis is available
    try:
        import redis
        r = redis.Redis()
        r.ping()
        click.echo("✅ Redis: Connected")
    except Exception:
        click.echo("❌ Redis: Not available")
        click.echo("   Start with: redis-server")
        return

    # Try to get worker stats
    try:
        result = subprocess.run(
            ['celery', '-A', 'core.profiles.worker.celery_app', 'inspect', 'stats', '--json'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            stats = json.loads(result.stdout)
            if stats:
                click.echo(f"✅ Workers: {len(stats)} active\n")
                for worker_name, worker_stats in stats.items():
                    pool = worker_stats.get('pool', {})
                    click.echo(f"   {worker_name}")
                    click.echo(f"      Processes: {pool.get('max-concurrency', 'N/A')}")
                    click.echo(f"      Tasks completed: {worker_stats.get('total', {}).get('tasks.core.health_check', 0)}")
            else:
                click.echo("⚠️  No workers running")
        else:
            click.echo("⚠️  No workers running")
    except subprocess.TimeoutExpired:
        click.echo("⚠️  No workers responding")
    except FileNotFoundError:
        click.echo("❌ Celery not installed")
    except json.JSONDecodeError:
        click.echo("⚠️  No workers running")

    click.echo("\nQueues:")
    click.echo("   • default - core tasks (health, cleanup, notifications)")
    click.echo("   • ocr - document processing")
    click.echo("   • media - image/video processing")


@cli.command()
def tasks():
    """View task queue"""
    click.echo("📋 Task Queue")
    click.echo("\nTo view tasks:")
    click.echo("   celery -A core.profiles.worker.celery_app inspect active")
    click.echo("   celery -A core.profiles.worker.celery_app inspect reserved")
    click.echo("   celery -A core.profiles.worker.celery_app inspect scheduled")


@cli.command()
def purge():
    """Purge all tasks from queue"""
    click.echo("🗑️  Purging task queue...")
    click.echo("\nTo purge tasks:")
    click.echo("   celery -A core.profiles.worker.celery_app purge")


def main():
    """
    Main entry point for the CLI

    Hybrid mode:
    - With arguments → Click commands
    - Without arguments → Interactive TUI mode
    """
    try:
        cli(obj={})
    except KeyboardInterrupt:
        click.echo("\n\n👋 interrupted by user")
        sys.exit(130)
    except Exception as e:
        click.echo(f"\n❌ error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
