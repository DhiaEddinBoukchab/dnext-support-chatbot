"""
Analytics: statistics display, timeseries, and recent image attachments.
"""

import json
import logging
from typing import List

import pandas as pd

logger = logging.getLogger(__name__)


class Analytics:
    """Read-only analytics queries on top of the database."""

    def __init__(self, db):
        self.db = db

    def get_statistics_md(self) -> str:
        """Return a formatted Markdown string of system-wide statistics."""
        stats = self.db.get_statistics()
        if not stats:
            return "No statistics available."
        return f"""
## 📊 System Overview

**Users**
- Total Users: {stats.get('total_users', 0)}
- Active Users (7 days): {stats.get('active_users_7d', 0)}

**Conversations**
- Total Conversations: {stats.get('total_conversations', 0)}
- Today's Conversations: {stats.get('conversations_today', 0)}
- Avg Response Time: {stats.get('avg_response_time_ms', 0):.0f} ms
"""

    def get_timeseries_df(self, days: int = 14) -> pd.DataFrame:
        """Conversations-per-day DataFrame for the last `days` days."""
        series = self.db.get_conversations_timeseries(days=days)
        if not series:
            return pd.DataFrame({"date": [], "conversations": []})
        return pd.DataFrame({
            "date":          [str(day) for day, _ in series],
            "conversations": [count     for _, count in series],
        })

    def get_recent_image_paths(self, limit: int = 20) -> List[str]:
        """Return file paths for the most recent image attachments."""
        recent = self.db.get_recent_conversations(limit=200)
        image_paths: List[str] = []

        for conv, _ in recent:
            if not getattr(conv, 'attachments', None):
                continue
            try:
                items = json.loads(conv.attachments)
            except Exception as e:
                logger.warning(f"Failed to parse attachments JSON: {e}")
                continue
            for item in items:
                if item.get('type') == 'image' and item.get('path'):
                    image_paths.append(item['path'])
                    if len(image_paths) >= limit:
                        return image_paths
        return image_paths