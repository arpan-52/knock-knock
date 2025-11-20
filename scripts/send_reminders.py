#!/usr/bin/env python3
"""
GitHub Actions script to send GMRT observation reminders
Reads from Google Sheet CSV and sends email reminders
"""

import os
import sys
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dateutil import parser
import requests


def fetch_sheet_data(csv_url):
    """Fetch data from Google Sheets CSV export"""
    try:
        response = requests.get(csv_url, timeout=10)
        response.raise_for_status()

        # Parse CSV
        lines = response.text.strip().split('\n')
        reader = csv.DictReader(lines)
        return list(reader)

    except Exception as e:
        print(f"Error fetching sheet data: {e}")
        sys.exit(1)


def parse_observation_date(date_str):
    """Parse observation date from GMRT format (e.g., Sun-23Nov2025)"""
    try:
        # GMRT format: Day-DDMmmYYYY (e.g., "Sun-23Nov2025")
        # Remove day-of-week prefix and parse the date
        if '-' in date_str:
            # Split on first hyphen to remove "Sun-", "Mon-", etc.
            parts = date_str.split('-', 1)
            if len(parts) == 2:
                date_str = parts[1]  # "23Nov2025"

        # Parse the date (DDMmmYYYY format)
        parsed = parser.parse(date_str, dayfirst=True)
        return parsed
    except Exception as e:
        return None


def should_send_reminder(observation_date_str, reminder_sent):
    """
    Determine if reminder should be sent
    Send reminders:
    - 3 days before observation
    - 1 day before observation
    """
    if reminder_sent and reminder_sent.upper() == 'YES':
        return False, None

    obs_date = parse_observation_date(observation_date_str)
    if not obs_date:
        return False, None

    # Calculate days until observation
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    days_until = (obs_date.replace(hour=0, minute=0, second=0, microsecond=0) - today).days

    # Send reminder at 3 days and 1 day before
    if days_until == 3 or days_until == 1:
        return True, days_until

    return False, None


def send_email(to_email, name, observation_data, days_until):
    """Send reminder email"""
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('FROM_EMAIL', smtp_user)

    if not smtp_user or not smtp_password:
        print("SMTP credentials not configured. Skipping email send.")
        return False

    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'GMRT Observation Reminder: {observation_data["proposal_code"]}'
    msg['From'] = from_email
    msg['To'] = to_email

    # Create email body
    if days_until == 0:
        urgency = "TODAY"
        greeting = f"Your GMRT observation is scheduled for TODAY!"
    elif days_until == 1:
        urgency = "TOMORROW"
        greeting = f"Your GMRT observation is scheduled for TOMORROW!"
    else:
        urgency = f"{days_until} days"
        greeting = f"Your GMRT observation is coming up in {days_until} days."

    text_body = f"""
Hello {name},

{greeting}

Observation Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date: {observation_data['observation_date']}
Time: {observation_data['observation_time']}
Telescope: {observation_data['telescope']}
Proposal Code: {observation_data['proposal_code']}
Source: {observation_data.get('source_url', 'N/A')}

Time until observation: {urgency}

Please ensure you are prepared for your observation session.

Good luck with your observations!

Best regards,
knock-knock (Arpan Pal)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Copyright (c) 2025 Arpan Pal

Developed by Arpan Pal — after forgetting an observation slot and getting
thoroughly scolded by my operator friends Arun, Tanuja, and Manthan. So,
to avoid that happening again, I built this tool.
If it helps you too, that's a bonus.
"""

    html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
        .details {{ background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #667eea; }}
        .detail-row {{ padding: 8px 0; border-bottom: 1px solid #eee; }}
        .urgency {{ font-size: 24px; font-weight: bold; color: #d32f2f; text-align: center; padding: 15px;
                    background: #ffebee; border-radius: 5px; margin: 15px 0; }}
        .footer {{ background: #333; color: #fff; padding: 15px; text-align: center;
                   border-radius: 0 0 10px 10px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">GMRT Observation Reminder</h1>
        </div>
        <div class="content">
            <p>Hello <strong>{name}</strong>,</p>
            <p>{greeting}</p>

            <div class="urgency">
                Time until observation: {urgency}
            </div>

            <div class="details">
                <h3 style="margin-top: 0; color: #667eea;">Observation Details</h3>
                <div class="detail-row"><strong>Date:</strong> {observation_data['observation_date']}</div>
                <div class="detail-row"><strong>Time:</strong> {observation_data['observation_time']}</div>
                <div class="detail-row"><strong>Telescope:</strong> {observation_data['telescope']}</div>
                <div class="detail-row"><strong>Proposal Code:</strong> {observation_data['proposal_code']}</div>
                <div class="detail-row"><strong>Source:</strong> <a href="{observation_data.get('source_url', '#')}">{observation_data.get('source_url', 'N/A')}</a></div>
            </div>

            <p>Please ensure you are prepared for your observation session.</p>
            <p><strong>Good luck with your observations!</strong></p>
        </div>
        <div class="footer">
            <p style="margin: 5px 0;"><strong>knock-knock (Arpan Pal)</strong></p>
            <p style="margin: 5px 0; font-size: 10px;">Copyright (c) 2025 Arpan Pal</p>
            <p style="margin: 10px 0; font-size: 11px;">Developed by Arpan Pal — after forgetting an observation slot and getting thoroughly scolded by my operator friends Arun, Tanuja, and Manthan. So, to avoid that happening again, I built this tool. If it helps you too, that's a bonus.</p>
        </div>
    </div>
</body>
</html>
"""

    # Attach both plain text and HTML versions
    part1 = MIMEText(text_body, 'plain')
    part2 = MIMEText(html_body, 'html')
    msg.attach(part1)
    msg.attach(part2)

    # Send email
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        print(f"✅ Sent reminder to {to_email} for observation on {observation_data['observation_date']}")
        return True

    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False


def main():
    """Main function"""
    csv_url = os.getenv('SHEET_CSV_URL')

    if not csv_url:
        print("Error: SHEET_CSV_URL environment variable not set")
        sys.exit(1)

    print("📊 Fetching reminder data from Google Sheet...")
    reminders = fetch_sheet_data(csv_url)

    print(f"Found {len(reminders)} total reminders")

    sent_count = 0

    for idx, reminder in enumerate(reminders, 1):
        email = reminder.get('Email', '').strip()
        name = reminder.get('Name', '').strip()
        obs_date = reminder.get('Observation Date', '').strip()
        reminder_sent = reminder.get('Reminder Sent', '').strip()

        if not email or not obs_date:
            continue

        should_send, days_until = should_send_reminder(obs_date, reminder_sent)

        if should_send:
            observation_data = {
                'observation_date': obs_date,
                'observation_time': reminder.get('Observation Time', 'Not specified'),
                'proposal_code': reminder.get('Proposal Code', 'N/A'),
                'telescope': reminder.get('Telescope', 'GMRT'),
                'source_url': reminder.get('Source URL', ''),
            }

            if send_email(email, name, observation_data, days_until):
                sent_count += 1

    print(f"\n✅ Reminder job complete. Sent {sent_count} reminders.")


if __name__ == '__main__':
    main()
