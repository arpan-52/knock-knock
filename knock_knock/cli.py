#!/usr/bin/env python3
"""
Command-line interface for knock-knock

Developed by Arpan Pal, to help himself, if it helps you, bonus!
All in for the love of GMRT
"""

import click
import sys
from .scraper import GMRTScraper
from .sender import SheetSender
from .utils import get_system_info

# Hardcoded endpoint
DEFAULT_ENDPOINT = "https://script.google.com/macros/s/AKfycbx-Y2hgrIG0crPJvWn8POb95Ni4vMRAKEwUOZQVokNybKZd7w6BixmFYweku6v1lAkrYQ/exec"


@click.group()
@click.version_option()
def cli():
    """Knock-Knock: GMRT Observation Reminder System

    Developed by Arpan Pal, to help himself, if it helps you, bonus!
    All in for the love of GMRT
    """
    pass


@cli.command()
@click.argument('url')
@click.option('--email', '-e', prompt='Your email', help='Your email address for reminders')
@click.option('--name', '-n', prompt='Your name', help='Your name')
def create(url, email, name):
    """Create reminders for GMRT observations from URL"""

    endpoint = DEFAULT_ENDPOINT

    try:
        # Step 1: Scrape GMRT URL
        click.echo(f"Scraping GMRT observation details from: {url}")
        scraper = GMRTScraper()
        observations = scraper.scrape(url)

        if not observations:
            click.echo("ERROR: Failed to extract observation details from URL", err=True)
            sys.exit(1)

        # Step 2: Get timestamp
        system_info = get_system_info()

        # Display all found observations
        click.echo(f"\n{'='*80}")
        click.echo(f"Found {len(observations)} observation slot(s)")
        click.echo(f"{'='*80}\n")

        for idx, obs in enumerate(observations, 1):
            click.echo(f"  [{idx}] {obs['observation_date']} | {obs['observation_time']} | Band: {obs['band']}")
            if obs.get('description'):
                click.echo(f"      {obs['description']}")

        click.echo(f"\n{'='*80}")
        click.echo(f"Creating reminders for all {len(observations)} observations...")
        click.echo(f"{'='*80}\n")

        # Step 3: Send each observation to Google Sheet
        sender = SheetSender(endpoint)
        success_count = 0
        failed_count = 0

        for idx, obs in enumerate(observations, 1):
            payload = {
                'email': email,
                'name': name,
                'observation_date': obs.get('observation_date', 'N/A'),
                'observation_time': obs.get('observation_time', 'N/A'),
                'proposal_code': obs.get('proposal_code', 'N/A'),
                'band': obs.get('band', 'Unknown'),
                'description': obs.get('description', ''),
                'telescope': 'GMRT',
                'source_url': url,
                'created_at': system_info['timestamp'],
            }

            click.echo(f"  [{idx}/{len(observations)}] Sending: {obs['observation_date']} {obs['observation_time']}... ", nl=False)

            result = sender.send(payload)

            if result['success']:
                click.echo("OK")
                success_count += 1
            else:
                click.echo(f"FAILED ({result.get('error', 'Unknown error')})")
                failed_count += 1

        # Summary
        click.echo(f"\n{'='*80}")
        if success_count == len(observations):
            click.echo(f"All {success_count} reminders created successfully!")
            click.echo(f"You will receive email reminders at: {email}")
        elif success_count > 0:
            click.echo(f"WARNING: {success_count} reminders created, {failed_count} failed")
            click.echo(f"You will receive reminders for successful entries at: {email}")
        else:
            click.echo(f"ERROR: All reminders failed to create")
            sys.exit(1)
        click.echo(f"{'='*80}")

    except Exception as e:
        click.echo(f"ERROR: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def config():
    """Show current configuration"""
    click.echo("Current Configuration:")
    click.echo(f"  Endpoint: {DEFAULT_ENDPOINT}")
    click.echo("\nDeveloped by Arpan Pal, to help himself, if it helps you, bonus!")
    click.echo("All in for the love of GMRT")


def main():
    """Entry point for the CLI"""
    cli()


if __name__ == '__main__':
    main()
