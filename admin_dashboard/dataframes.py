"""
DataFrame builders: convert DB models into pandas DataFrames for Gradio tables.
"""

import json
import logging
from datetime import datetime
from typing import List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

# ── Column definitions ────────────────────────────────────────────────────────
USER_COLS         = ['ID', 'Email', 'Name', 'Status', 'Total Queries', 'Created', 'Last Login']
CONV_COLS         = ['ID', 'User', 'Message', 'Response', 'Type', 'Time', 'Response Time (ms)']
CONV_COLS_NO_USER = ['ID', 'User ID', 'Message', 'Response', 'Type', 'Time', 'Response Time (ms)']
CONV_COLS_EXPORT  = CONV_COLS + ['Image Paths']


def build_users_df(users) -> pd.DataFrame:
    if not users:
        return pd.DataFrame(columns=USER_COLS)
    rows = [
        {
            'ID': u.user_id,
            'Email': u.email,
            'Name': u.full_name,
            'Status': u.status.value,
            'Total Queries': u.total_queries,
            'Created': u.created_at.strftime('%Y-%m-%d %H:%M'),
            'Last Login': u.last_login.strftime('%Y-%m-%d %H:%M') if u.last_login else 'Never',
        }
        for u in users
    ]
    return pd.DataFrame(rows)


def _conv_row(conv, user_label, truncate: bool = True) -> dict:
    """Build a single conversation row dict."""

    def _t(text):
        return (text[:100] + '...') if truncate and len(text) > 100 else text

    return {
        'ID': conv.conversation_id,
        'User': user_label,
        'Message': _t(conv.message),
        'Response': _t(conv.response),
        'Type': conv.conversation_type,
        'Time': conv.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'Response Time (ms)': conv.response_time_ms or 'N/A',
    }


def build_recent_convs_df(recent_pairs, truncate: bool = True) -> pd.DataFrame:
    """recent_pairs is List[Tuple[Conversation, User]]."""
    rows = [_conv_row(conv, user.email, truncate) for conv, user in recent_pairs]
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=CONV_COLS)


def build_user_convs_df(conversations) -> pd.DataFrame:
    """Single-user conversation list (no email column)."""
    if not conversations:
        return pd.DataFrame(columns=CONV_COLS_NO_USER)
    rows = [
        {
            'ID': c.conversation_id,
            'User ID': c.user_id,
            'Message': (c.message[:100] + '...') if len(c.message) > 100 else c.message,
            'Response': (c.response[:100] + '...') if len(c.response) > 100 else c.response,
            'Type': c.conversation_type,
            'Time': c.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Response Time (ms)': c.response_time_ms or 'N/A',
        }
        for c in conversations
    ]
    return pd.DataFrame(rows)


def build_export_rows(conv_pairs) -> List[dict]:
    """Full-content rows including image attachment paths (for CSV export)."""
    rows = []
    for conv, user in conv_pairs:
        image_paths = []
        if getattr(conv, 'attachments', None):
            try:
                for item in json.loads(conv.attachments):
                    if item.get('type') == 'image' and item.get('path'):
                        image_paths.append(item['path'])
            except Exception as e:
                logger.warning(f"Failed to parse attachments for conv {conv.conversation_id}: {e}")

        rows.append({
            'ID': conv.conversation_id,
            'User': user.email,
            'Message': conv.message,
            'Response': conv.response,
            'Type': conv.conversation_type,
            'Time': conv.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Response Time (ms)': conv.response_time_ms or 'N/A',
            'Image Paths': ';'.join(image_paths),
        })
    return rows


def parse_date(date_str: str, end_of_day: bool = False) -> Optional[datetime]:
    """Parse YYYY-MM-DD string, optionally setting time to 23:59:59."""
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.replace(hour=23, minute=59, second=59) if end_of_day else dt
    except ValueError:
        logger.warning(f"Invalid date format: {date_str}")
        return None