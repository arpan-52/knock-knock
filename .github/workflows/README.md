# GitHub Actions Setup for Reminders

This workflow automatically sends email reminders twice daily for upcoming GMRT observations.

## Schedule
- **6:00 AM UTC** (11:30 AM IST)
- **6:00 PM UTC** (11:30 PM IST)

## Required Secrets

Add these secrets to your GitHub repository:
**Settings → Secrets and variables → Actions → New repository secret**

### 1. SHEET_CSV_URL
The CSV export URL of your Google Sheet:
```
https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0
```

To get this:
1. Open your Google Sheet
2. Get the Sheet ID from the URL
3. Make sure sheet is shared as "Anyone with link can view"

### 2. SMTP Configuration

#### Option A: Gmail SMTP
```
SMTP_HOST: smtp.gmail.com
SMTP_PORT: 587
SMTP_USER: your-email@gmail.com
SMTP_PASSWORD: your-app-password (not regular password!)
FROM_EMAIL: your-email@gmail.com
```

**Getting Gmail App Password:**
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Go to App Passwords
4. Generate new app password for "Mail"
5. Use that 16-character password

#### Option B: Other SMTP Services

**SendGrid:**
```
SMTP_HOST: smtp.sendgrid.net
SMTP_PORT: 587
SMTP_USER: apikey
SMTP_PASSWORD: your-sendgrid-api-key
FROM_EMAIL: verified-sender@yourdomain.com
```

**Mailgun:**
```
SMTP_HOST: smtp.mailgun.org
SMTP_PORT: 587
SMTP_USER: postmaster@your-domain.mailgun.org
SMTP_PASSWORD: your-mailgun-password
FROM_EMAIL: noreply@your-domain.mailgun.org
```

**AWS SES:**
```
SMTP_HOST: email-smtp.us-east-1.amazonaws.com
SMTP_PORT: 587
SMTP_USER: your-ses-smtp-username
SMTP_PASSWORD: your-ses-smtp-password
FROM_EMAIL: verified@yourdomain.com
```

### 3. GOOGLE_SHEET_ID (Optional)
Your Google Sheet ID - used for status updates
```
1a2b3c4d5e6f7g8h9i0j
```

### 4. GOOGLE_CREDENTIALS (Optional)
Service account JSON for updating sheet status - advanced feature

## Manual Testing

Test the workflow manually:
1. Go to **Actions** tab in GitHub
2. Select "Send GMRT Observation Reminders"
3. Click **Run workflow**
4. Choose branch and click **Run workflow**

## Reminder Logic

Reminders are sent at these intervals before observation:
- **7 days before**
- **3 days before**
- **1 day before**
- **On the day of observation**

## Troubleshooting

### No emails being sent
1. Check GitHub Actions logs
2. Verify SMTP credentials
3. Check spam folder
4. Verify sheet CSV URL is accessible

### Emails going to spam
1. Use a verified domain
2. Consider using SendGrid/Mailgun
3. Add SPF/DKIM records to your domain

### Sheet not accessible
1. Ensure sheet is shared publicly (view-only)
2. Verify CSV export URL is correct
3. Check sheet has correct column names

## Email Preview

Reminder emails include:
- Countdown to observation
- Observation date and time
- Proposal code
- Telescope name (GMRT)
- Link to original scheduling page
- Beautiful HTML formatting

## Cost

All components are **FREE**:
- ✅ Google Sheets - Free
- ✅ Google Apps Script - Free
- ✅ GitHub Actions - 2000 minutes/month free
- ✅ Gmail SMTP - Free (with limits)

For production use, consider:
- SendGrid: 100 emails/day free
- Mailgun: 5000 emails/month free (first 3 months)
