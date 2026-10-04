import json
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path


class AuditLog:
    """Tamper-evident JSONL audit log.

    Every entry includes:
      - run_id: unique per session
      - ts: UTC timestamp
      - type: event type
      - hash: sha256 of this entry
      - prev_hash: sha256 of previous entry (chain)
    """

    def __init__(self, path, run_id=None):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id or str(uuid.uuid4())
        self._last_hash = self._load_last_hash()

    def _load_last_hash(self):
        if not self.path.exists():
            return "0" * 64
        last = "0" * 64
        try:
            with self.path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                        last = rec.get("hash", last)
                    except Exception:
                        continue
        except Exception:
            pass
        return last

    def _hash(self, obj):
        return hashlib.sha256(
            json.dumps(obj, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()

    def log(self, event_type, **fields):
        rec = {
            "run_id": self.run_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "prev_hash": self._last_hash,
            **fields,
        }
        rec["hash"] = self._hash(rec)
        self._last_hash = rec["hash"]
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, default=str, ensure_ascii=False) + "\n")
        return rec

    def verify(self):
        """Verify the hash chain. Returns (ok, count, first_bad_index)."""
        if not self.path.exists():
            return (True, 0, None)
        prev = "0" * 64
        count = 0
        with self.path.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    return (False, count, i)
                stored = rec.pop("hash", None)
                if rec.get("prev_hash") != prev:
                    return (False, count, i)
                calc = self._hash(rec)
                if calc != stored:
                    return (False, count, i)
                prev = stored
                count += 1
        return (True, count, None)
