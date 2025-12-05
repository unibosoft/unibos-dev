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
def start(worker_type, queues, concurrency):
    """Start Celery workers"""
    click.echo(f"🚀 Starting {worker_type} worker(s)...")

    if queues:
        queue_list = queues.split(',')
        click.echo(f"   Queues: {', '.join(queue_list)}")
    else:
        queue_map = {
            'all': ['default', 'ocr', 'media'],
            'core': ['default'],
            'ocr': ['ocr'],
            'media': ['media'],
        }
        queue_list = queue_map.get(worker_type, ['default'])
        click.echo(f"   Queues: {', '.join(queue_list)}")

    if concurrency:
        click.echo(f"   Concurrency: {concurrency}")

    click.echo("\nTo start manually:")
    click.echo(f"   celery -A core.profiles.worker.celery_app worker -Q {','.join(queue_list)} -l INFO")


@cli.command()
def stop():
    """Stop all workers"""
    click.echo("⏹️  Stopping all workers...")
    click.echo("\nTo stop workers:")
    click.echo("   pkill -f 'celery.*worker'")
    click.echo("   # or")
    click.echo("   celery -A core.profiles.worker.celery_app control shutdown")


@cli.command()
def status():
    """Show worker status"""
    click.echo("👷 Worker Status")
    click.echo("\nActive Workers:")
    click.echo("   celery -A core.profiles.worker.celery_app inspect active")
    click.echo("\nQueues:")
    click.echo("   • default - core tasks")
    click.echo("   • ocr - document processing")
    click.echo("   • media - image/video processing")
    click.echo("\nTo check status:")
    click.echo("   celery -A core.profiles.worker.celery_app inspect stats")


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
