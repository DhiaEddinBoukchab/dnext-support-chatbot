"""
Generate docs_md/doxument.md from email_conversations (2)/knowledge_base.json
"""
import json
from pathlib import Path

project_root = Path(__file__).parent.parent
kb_path = project_root / "email_conversations (2)" / "knowledge_base.json"
out_path = project_root / "docs_md" / "emails.md"

if not kb_path.exists():
    print(f"knowledge_base.json not found at: {kb_path}")
    raise SystemExit(1)

with open(kb_path, "r", encoding="utf-8") as f:
    data = json.load(f)

kb = data.get("knowledge_base") or data.get("knowledgeBase") or []

out_path.parent.mkdir(parents=True, exist_ok=True)

lines = []
for i, entry in enumerate(kb):
    # Problem
    prob = entry.get("problem", "")
    sol = entry.get("solution", "")
    keywords = entry.get("keywords", [])
    cat = entry.get("category", "")

    lines.append('"problem": "' + prob.replace('"', '\\"') + '",')
    lines.append('      "solution": "' + sol.replace('"', '\\"') + '",')
    lines.append('      "keywords": [')
    for kw in keywords:
        lines.append('        "' + kw.replace('"', '\\"') + '",')
    if keywords:
        # remove trailing comma of last keyword
        lines[-1] = lines[-1].rstrip(',')
    lines.append('      ],')
    lines.append('      "category": "' + cat.replace('"', '\\"') + '"')
    # Separator
    lines.append('\n*******\n')

with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Wrote: {out_path}")
