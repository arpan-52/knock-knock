# Google Apps Script Setup

## Step-by-Step Instructions

### 1. Create a Google Sheet
1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it "GMRT Observation Reminders" (or any name you prefer)
4. Note down the Spreadsheet ID from the URL:
   - URL format: `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit`

### 2. Open Apps Script Editor
1. In your Google Sheet, go to: **Extensions** → **Apps Script**
2. Delete any default code in the editor
3. Copy the entire content from `Code.gs` file
4. Paste it into the Apps Script editor
5. Save the project (Ctrl+S or Cmd+S)
6. Name it "Knock-Knock API"

### 3. Deploy as Web App
1. Click **Deploy** → **New deployment**
2. Click the gear icon ⚙️ next to "Select type"
3. Choose **Web app**
4. Configure:
   - **Description**: "Knock-Knock GMRT Reminder API"
   - **Execute as**: Me (your email)
   - **Who has access**: Anyone
5. Click **Deploy**
6. Review permissions:
   - Click **Authorize access**
   - Choose your Google account
   - Click **Advanced** → **Go to [Project Name] (unsafe)**
   - Click **Allow**
7. **Copy the Web App URL** - you'll need this!
   - Format: `https://script.google.com/macros/s/{SCRIPT_ID}/exec`

### 4. Test the Deployment
1. In Apps Script editor, select `testAddReminder` function
2. Click **Run**
3. Check your Google Sheet - it should have created a row with test data
4. Delete the test row

### 5. Configure CLI Tool
Set the endpoint URL as an environment variable:

```bash
# Linux/Mac
export KNOCK_KNOCK_ENDPOINT="https://script.google.com/macros/s/{YOUR_SCRIPT_ID}/exec"

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export KNOCK_KNOCK_ENDPOINT="https://script.google.com/macros/s/{YOUR_SCRIPT_ID}/exec"' >> ~/.bashrc

# Windows (PowerShell)
$env:KNOCK_KNOCK_ENDPOINT="https://script.google.com/macros/s/{YOUR_SCRIPT_ID}/exec"

# Windows (Command Prompt)
set KNOCK_KNOCK_ENDPOINT=https://script.google.com/macros/s/{YOUR_SCRIPT_ID}/exec
```

### 6. Sheet Structure
The script automatically creates a sheet with these columns:

| Column | Description |
|--------|-------------|
| Email | User's email for reminders |
| Name | User's name |
| Observation Date | Scheduled observation date |
| Observation Time | Scheduled observation time |
| Proposal Code | GMRT proposal code |
| Telescope | Always "GMRT" |
| Source URL | Original GMRT scheduling URL |
| IP Address | User's IP address |
| MAC Address | User's MAC address |
| Created At | Timestamp of reminder creation |
| Reminder Sent | Status (Yes/No) |

### 7. Make Sheet Accessible for GitHub Actions
1. Click **Share** button on your Google Sheet
2. Change to: **Anyone with the link** → **Viewer**
3. Copy the shareable link
4. Save this link - GitHub Actions will use it

### 8. Get CSV Export URL
For GitHub Actions to read the sheet:
```
https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0
```
Replace `{SPREADSHEET_ID}` with your actual ID.

## Troubleshooting

### "Authorization required" error
- Redeploy the web app
- Make sure "Who has access" is set to "Anyone"

### Data not appearing in sheet
- Check Apps Script logs: **Execution log** button
- Verify JSON format from CLI
- Run `testAddReminder()` to check permissions

### "Script has been disabled" error
- Go to Google Account settings
- Security → Less secure app access → Enable
- Or create a new deployment

## Security Notes
- The endpoint URL should be kept private (don't commit to public repos)
- Anyone with the URL can add reminders
- The Google Sheet itself can be private - only the script needs public access
- Consider adding API key validation in the script for production use
