"""
Utility functions for knock-knock
"""

from datetime import datetime


def get_system_info():
    """Get timestamp for reminder creation"""
    return {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
    }
