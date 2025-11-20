/**
 * Google Apps Script for Knock-Knock GMRT Reminder System
 *
 * This script:
 * 1. Receives POST requests from the knock-knock CLI
 * 2. Validates and parses the data
 * 3. Appends a new row to the Google Sheet
 *
 * Deploy as: Web App
 * Execute as: Me
 * Who has access: Anyone
 */

// Configuration
const SHEET_NAME = 'Reminders'; // Name of the sheet tab

/**
 * Handle POST requests from knock-knock CLI
 */
function doPost(e) {
  try {
    // Parse incoming JSON
    const data = JSON.parse(e.postData.contents);

    // Validate required fields
    const requiredFields = ['email', 'name', 'proposal_code', 'observation_date'];
    for (const field of requiredFields) {
      if (!data[field]) {
        return createResponse(false, `Missing required field: ${field}`);
      }
    }

    // Get the active spreadsheet
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let sheet = ss.getSheetByName(SHEET_NAME);

    // Create sheet if it doesn't exist
    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
      // Add headers
      sheet.appendRow([
        'Email',
        'Name',
        'Observation Date',
        'Observation Time',
        'Proposal Code',
        'Band',
        'Description',
        'Telescope',
        'Source URL',
        'IP Address',
        'MAC Address',
        'Created At',
        'Reminder Sent'
      ]);

      // Format header row
      const headerRange = sheet.getRange(1, 1, 1, 13);
      headerRange.setFontWeight('bold');
      headerRange.setBackground('#4285f4');
      headerRange.setFontColor('#ffffff');
    }

    // Append new row with data
    sheet.appendRow([
      data.email || '',
      data.name || '',
      data.observation_date || '',
      data.observation_time || '',
      data.proposal_code || '',
      data.band || '',
      data.description || '',
      data.telescope || 'GMRT',
      data.source_url || '',
      data.ip_address || '',
      data.mac_address || '',
      data.created_at || new Date().toISOString(),
      'No' // Reminder sent status
    ]);

    // Log the entry
    Logger.log(`New reminder added for ${data.email} - ${data.proposal_code} on ${data.observation_date}`);

    return createResponse(true, 'Reminder created successfully');

  } catch (error) {
    Logger.log('Error in doPost: ' + error.toString());
    return createResponse(false, 'Server error: ' + error.toString());
  }
}

/**
 * Handle GET requests (for testing)
 */
function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    status: 'success',
    message: 'Knock-Knock GMRT Reminder System API is running',
    timestamp: new Date().toISOString()
  })).setMimeType(ContentService.MimeType.JSON);
}

/**
 * Create standardized JSON response
 */
function createResponse(success, message, data = {}) {
  const response = {
    status: success ? 'success' : 'error',
    message: message,
    timestamp: new Date().toISOString(),
    ...data
  };

  return ContentService
    .createTextOutput(JSON.stringify(response))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Test function - Run this to create sample data
 */
function testAddReminder() {
  const testData = {
    postData: {
      contents: JSON.stringify({
        email: 'test@example.com',
        name: 'Test User',
        observation_date: 'Mon-01Dec2025',
        observation_time: '07:00 - 13:00',
        proposal_code: '49_098',
        band: 'B4',
        description: '49_098(S2.2)',
        telescope: 'GMRT',
        source_url: 'http://www.ncra.tifr.res.in/~secr-ops/sch/webfiles/gtac.php?code=49_098',
        ip_address: '192.168.1.1',
        mac_address: '00:11:22:33:44:55',
        created_at: new Date().toISOString()
      })
    }
  };

  const result = doPost(testData);
  Logger.log(result.getContent());
}

/**
 * Get all pending reminders (for GitHub Actions)
 * This can be called via URL with proper authentication
 */
function getPendingReminders() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(SHEET_NAME);

  if (!sheet) {
    return createResponse(false, 'No reminders found');
  }

  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const rows = data.slice(1);

  // Convert to JSON array
  const reminders = rows.map(row => {
    const reminder = {};
    headers.forEach((header, index) => {
      reminder[header] = row[index];
    });
    return reminder;
  }).filter(r => r['Reminder Sent'] !== 'Yes'); // Only pending reminders

  return createResponse(true, 'Reminders retrieved', { reminders: reminders });
}
