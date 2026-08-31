#!/usr/bin/env python3
"""Fetch Raffie Grasshopper CSV from Gmail RAW MIME (read-only).

Writes Detail_*.csv to .local/phone-call-forensic/ then runs analyzer.
Expects GMAIL_RAW_B64_PATH pointing at a file with urlsafe base64 MIME from
get_message(messageFormat=RAW), or pass path as argv[1].
"""
from __future__ import annotations

import base64
import subprocess
import sys
from email import message_from_bytes
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PRIV = REPO / ".local" / "phone-call-forensic"
ANALYZER = REPO / "ads-launch" / "analyze_grasshopper_export_readonly.py"


def extract_csv(raw_b64: str, out_dir: Path) -> Path:
    pad = "=" * (-len(raw_b64.strip()) % 4)
    mime = base64.urlsafe_b64decode(raw_b64.strip() + pad)
    msg = message_from_bytes(mime)
    for part in msg.walk():
        fn = part.get_filename()
        if fn and fn.lower().endswith(".csv"):
            payload = part.get_payload(decode=True)
            if not payload:
                raise SystemExit("empty csv payload")
            dest = out_dir / fn
            dest.write_bytes(payload)
            dest.chmod(0o600)
            return dest
    raise SystemExit("no csv attachment in mime")


def main() -> int:
    raw_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        os.environ.get("GMAIL_RAW_B64_PATH", PRIV / "_gmail_raw.b64")
    )
    if not raw_path.is_file():
        print(f"missing raw b64: {raw_path}", file=sys.stderr)
        return 2
    PRIV.mkdir(parents=True, exist_ok=True)
    csv_path = extract_csv(raw_path.read_text(), PRIV)
    print("WROTE", csv_path)
    return subprocess.call([sys.executable, str(ANALYZER)])


if __name__ == "__main__":
    import os

    raise SystemExit(main())
