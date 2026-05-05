"""
Exporter: filtered conversation CSV export with image attachments bundled in ZIP.
"""

import json
import logging
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from admin_dashboard.dataframes import build_export_rows, parse_date

logger = logging.getLogger(__name__)


class ConversationExporter:
    """Exports filtered conversations to a ZIP file containing CSV + images."""

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
        Export filtered conversations to a ZIP file containing:
        - conversations.csv  (all conversation data)
        - images/            (all referenced image attachments)

        Returns the path to the ZIP file, or None if no data matched.
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

        # ── Prepare export directory ─────────────────────────────────────────
        exports_dir = Path("data/exports")
        exports_dir.mkdir(parents=True, exist_ok=True)

        # ── Collect all unique image paths ───────────────────────────────────
        image_paths: dict[str, str] = {}  # original_path → zip_internal_name
        for row in rows:
            if not row.get('Image Paths'):
                continue
            for path_str in row['Image Paths'].split(';'):
                path_str = path_str.strip()
                if path_str and path_str not in image_paths:
                    filename = f"{len(image_paths)+1:04d}_{Path(path_str).name}"
                    image_paths[path_str] = filename

        # ── Rewrite image paths in rows to ZIP-internal names ────────────────
        for row in rows:
            if not row.get('Image Paths'):
                continue
            new_paths = []
            for path_str in row['Image Paths'].split(';'):
                path_str = path_str.strip()
                if path_str in image_paths:
                    new_paths.append(f"images/{image_paths[path_str]}")
                else:
                    new_paths.append(path_str)
            row['Image Paths'] = ';'.join(new_paths)

        # ── Build CSV in memory ──────────────────────────────────────────────
        df = pd.DataFrame(rows)
        safe_email = (user_email or "all").replace("@", "_").replace(".", "_")
        timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_name   = f"conversations_{safe_email}_{timestamp}.csv"
        csv_bytes  = df.to_csv(index=False, encoding="utf-8").encode("utf-8")

        # ── Bundle everything into a ZIP ─────────────────────────────────────
        zip_path = exports_dir / f"export_{safe_email}_{timestamp}.zip"
        missing_images = 0

        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            # Add CSV
            zf.writestr(csv_name, csv_bytes)

            # Add images
            for original_path, zip_name in image_paths.items():
                src = Path(original_path)
                if src.exists():
                    zf.write(src, f"images/{zip_name}")
                else:
                    missing_images += 1
                    logger.warning(f"Image not found, skipping: {original_path}")

            # Add a README
            readme = self._build_readme(
                csv_name=csv_name,
                total_conversations=len(rows),
                total_images=len(image_paths),
                missing_images=missing_images,
                filters={
                    "email": user_email or "all",
                    "date_from": date_from or "—",
                    "date_to": date_to or "—",
                    "type": conversation_type or "all",
                },
            )
            zf.writestr("README.txt", readme)

        logger.info(
            f"Exported {len(df)} conversations + "
            f"{len(image_paths) - missing_images} images → {zip_path}"
        )
        return str(zip_path)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _build_readme(
        self,
        csv_name: str,
        total_conversations: int,
        total_images: int,
        missing_images: int,
        filters: dict,
    ) -> str:
        lines = [
            "=" * 50,
            "  DNEXT SUPPORT CHATBOT — CONVERSATION EXPORT",
            "=" * 50,
            "",
            f"Export date   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "FILTERS APPLIED:",
            f"  Email        : {filters['email']}",
            f"  From date    : {filters['date_from']}",
            f"  To date      : {filters['date_to']}",
            f"  Type         : {filters['type']}",
            "",
            "CONTENTS:",
            f"  {csv_name}",
            f"    → {total_conversations} conversation(s)",
            f"  images/",
            f"    → {total_images - missing_images} image(s) included",
        ]
        if missing_images:
            lines.append(f"    ⚠ {missing_images} image(s) not found (may have been deleted)")
        lines += [
            "",
            "HOW TO USE:",
            "  1. Open the CSV file in Excel or any spreadsheet app.",
            "  2. The 'Image Paths' column references files in the images/ folder.",
            "  3. Keep the CSV and images/ folder in the same directory.",
            "",
            "=" * 50,
        ]
        return "\n".join(lines)