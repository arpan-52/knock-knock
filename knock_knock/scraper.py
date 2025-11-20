"""
GMRT URL scraper to extract observation details
"""

import requests
import re
from urllib.parse import urlparse, parse_qs


class GMRTScraper:
    """Scraper for GMRT observation scheduling pages"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape(self, url):
        """
        Scrape observation details from GMRT URL

        Args:
            url: GMRT observation URL (e.g., gtac.php?code=...)

        Returns:
            list of dicts with observation details (multiple time slots possible)
        """
        try:
            # Extract proposal code from URL
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            proposal_code = params.get('code', ['Unknown'])[0]

            # Fetch the page
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            html = response.text

            # Parse observations using the working logic
            observations = self._parse_schedule(html, proposal_code, url)

            if not observations:
                raise Exception("No observations found in the schedule")

            return observations

        except requests.RequestException as e:
            raise Exception(f"Failed to fetch GMRT page: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to parse observation details: {str(e)}")

    def _parse_schedule(self, html, proposal_code, source_url):
        """Parse the schedule from tooltips - group consecutive yellow cells"""
        # Find all cells with yellow background
        pattern = r'background-color:yellow[^>]*onmouseover="Tip\(\'([^\']+)\'\)'
        matches = re.findall(pattern, html)

        if not matches:
            return []

        # Store raw data before grouping
        raw_obs = []

        for tooltip in matches:
            # Clean HTML tags for text content
            cleaned = re.sub(r'<[^>]+>', '', tooltip)

            # Skip if no IST time found
            if 'IST' not in cleaned:
                continue

            # Skip maintenance and other non-observation blocks
            if 'Maintenance' in cleaned or 'Backlash' in cleaned or 'SSC' in cleaned:
                continue

            # Parse IST time: IST Day-DDMmmYYYY(HH-HH)
            ist_match = re.search(r'IST\s+(\w+-\d{2}\w{3}\d{4})\((\d{1,2})-(\d{1,2})\)', cleaned)
            if not ist_match:
                continue

            date = ist_match.group(1)
            start_hour = int(ist_match.group(2))
            end_hour = int(ist_match.group(3))

            # Extract band info
            band_match = re.search(r'<strong>B(\d+)</strong>', tooltip)
            band = 'B' + band_match.group(1) if band_match else 'Unknown'

            # Extract observation ID and project info
            obs_match = re.search(r'(\d{2,3}_\d{3,4}\([^)]+\))', cleaned)
            obs_code = obs_match.group(1) if obs_match else ''

            # Get PI name
            pi_match = re.search(r'\(NCRA[^)]*\).*?([A-Za-z\s]+)\(', cleaned)
            pi_info = pi_match.group(1).strip() if pi_match else ''

            # Create description from observation code and PI
            if obs_code:
                description = f"{obs_code} - {pi_info}" if pi_info else obs_code
            else:
                description = ''

            raw_obs.append({
                'date': date,
                'start_hour': start_hour,
                'end_hour': end_hour,
                'band': band,
                'description': description[:80],
                'obs_code': obs_code
            })

        # Group consecutive yellow cells with same observation code
        observations = []
        if raw_obs:
            current_group = raw_obs[0]

            for i in range(1, len(raw_obs)):
                next_obs = raw_obs[i]

                # Check if consecutive: same date, same obs code, and end_hour of current matches start_hour of next
                if (current_group['date'] == next_obs['date'] and
                    current_group['obs_code'] == next_obs['obs_code'] and
                    current_group['end_hour'] == next_obs['start_hour']):
                    # Extend current group
                    current_group['end_hour'] = next_obs['end_hour']
                else:
                    # Save current group and start new one
                    observations.append({
                        'proposal_code': proposal_code,
                        'observation_date': current_group['date'],
                        'observation_time': f"{current_group['start_hour']:02d}:00 - {current_group['end_hour']:02d}:00",
                        'band': current_group['band'],
                        'description': current_group['description'],
                        'source_url': source_url
                    })
                    current_group = next_obs

            # Don't forget the last group
            observations.append({
                'proposal_code': proposal_code,
                'observation_date': current_group['date'],
                'observation_time': f"{current_group['start_hour']:02d}:00 - {current_group['end_hour']:02d}:00",
                'band': current_group['band'],
                'description': current_group['description'],
                'source_url': source_url
            })

        return observations
