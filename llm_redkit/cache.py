import hashlib
import json
from pathlib import Path
from .platform_utils import get_cache_dir


class ResponseCache:
    def __init__(self, enabled=True, path=None):
        self.enabled = enabled
        self.dir = Path(path) if path else get_cache_dir()
        if self.enabled:
            self.dir.mkdir(parents=True, exist_ok=True)

    def _key(self, base_url, model, prompt, system):
        h = hashlib.sha256()
        for x in (base_url, model, prompt, system or ""):
            h.update(x.encode("utf-8"))
            h.update(b"|")
        return h.hexdigest()

    def get(self, base_url, model, prompt, system):
        if not self.enabled:
            return None
        p = self.dir / (self._key(base_url, model, prompt, system) + ".json")
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))["response"]
        except Exception:
            return None

    def set(self, base_url, model, prompt, system, response):
        if not self.enabled:
            return
        p = self.dir / (self._key(base_url, model, prompt, system) + ".json")
        p.write_text(json.dumps({
            "response": response,
            "meta": {
                "base_url": base_url,
                "model": model,
                "system": system,
                "prompt": prompt,
            },
        }, ensure_ascii=False), encoding="utf-8")

    def clear(self):
        if not self.dir.exists():
            return 0
        n = 0
        for f in self.dir.glob("*.json"):
            f.unlink()
            n += 1
        return n

    def stats(self):
        if not self.dir.exists():
            return {"entries": 0, "size_bytes": 0}
        files = list(self.dir.glob("*.json"))
        return {
            "entries": len(files),
            "size_bytes": sum(f.stat().st_size for f in files),
        }
