"""
Send data to Google Apps Script endpoint
"""

import requests
import json


class SheetSender:
    """Send observation data to Google Sheets via Apps Script"""

    def __init__(self, endpoint_url):
        """
        Initialize sender with Apps Script endpoint

        Args:
            endpoint_url: Google Apps Script web app URL
        """
        self.endpoint = endpoint_url

    def send(self, data):
        """
        Send data to Google Sheet

        Args:
            data: Dictionary containing observation and user details

        Returns:
            dict with 'success' boolean and optional 'error' message
        """
        try:
            response = requests.post(
                self.endpoint,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            response.raise_for_status()

            # Parse response
            result = response.json()
            return {
                'success': result.get('status') == 'success',
                'message': result.get('message', ''),
                'error': result.get('error', None)
            }

        except requests.RequestException as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
        except json.JSONDecodeError:
            return {
                'success': False,
                'error': 'Invalid response from server'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
