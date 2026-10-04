import os
from collections import Counter


class ConsistencyRunner:
    """Runs the same prompt N times without cache and reports variance."""

    def __init__(self, client, runs=3):
        self.client = client
        self.runs = max(1, runs)

    def run(self, prompt, system=None):
        old = os.environ.get("REDKIT_NO_CACHE")
        os.environ["REDKIT_NO_CACHE"] = "1"
        try:
            replies = [self.client.chat(prompt, system=system)
                       for _ in range(self.runs)]
        finally:
            if old is None:
                os.environ.pop("REDKIT_NO_CACHE", None)
            else:
                os.environ["REDKIT_NO_CACHE"] = old

        unique = len(set(replies))
        consistent = (unique == 1)
        majority, count = Counter(replies).most_common(1)[0]
        return {
            "runs": self.runs,
            "unique_replies": unique,
            "consistency": round(count / self.runs, 2),
            "consistent": consistent,
            "majority_reply": majority,
            "all_replies": replies,
        }
