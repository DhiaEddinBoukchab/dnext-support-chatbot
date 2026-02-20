"""
Exporter: filtered conversation CSV export with image attachment copying.
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from admin_dashboard.dataframes import build_export_rows, parse_date

logger = logging.getLogger(__name__)


class ConversationExporter:
    """Exports filtered conversations to CSV and copies image attachments."""

    def __init__(self, db):
        self.db = db

    def export_to_csv(
        self,
        user_email: str,
        date_from: str,
        date_to: str,
        conversation_type: str,
    ) -> Optional[str]:
        """
        Export filtered conversations to a CSV file.
        Returns the path to the CSV file, or None if no data matched.
        """
        conversations = self.db.get_conversations_filtered(
            user_email=user_email or None,
            date_from=parse_date(date_from),
            date_to=parse_date(date_to, end_of_day=True),
            conversation_type=conversation_type or None,
            limit=500,
        )

        rows = build_export_rows(conversations)
        if not rows:
            return None

        # Copy images into exports/images/ and rewrite paths in rows
        exports_dir = Path("exports")
        images_dir  = exports_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        path_map: dict = {}
        for row in rows:
            if not row['Image Paths']:
                continue
            new_paths = []
            for path in row['Image Paths'].split(';'):
                if path not in path_map:
                    path_map[path] = self._copy_image(path, images_dir, exports_dir)
                new_paths.append(path_map[path])
            row['Image Paths'] = ';'.join(new_paths)

        df = pd.DataFrame(rows)
        safe_email = (user_email or "all").replace("@", "_").replace(".", "_")
        timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path   = exports_dir / f"conversations_{safe_email}_{timestamp}.csv"
        df.to_csv(out_path, index=False, encoding="utf-8")
        logger.info(f"Exported {len(df)} conversations to {out_path}")
        return str(out_path)

    def _copy_image(self, src_str: str, images_dir: Path, exports_dir: Path) -> str:
        """Copy a single image to images_dir and return its relative path."""
        src = Path(src_str)
        if not src.exists():
            logger.warning(f"Image not found: {src_str}")
            return src_str
        try:
            ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = images_dir / f"{src.stem}_{ts}{src.suffix}"
            shutil.copy2(src, dest)
            return str(dest.relative_to(exports_dir))
        except Exception as e:
            logger.error(f"Failed to copy image {src_str}: {e}")
            return src_str