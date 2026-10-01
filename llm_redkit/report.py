from jinja2 import Template
from datetime import datetime

HTML = """
<!doctype html><html><head><meta charset="utf-8"><title>LLM-RedKit Report</title>
<style>
body{font-family:monospace;background:#0b0b0b;color:#ddd;padding:24px}
h1{color:#f55}.crit{color:#ff3333}.high{color:#ff7700}
.med{color:#ffcc00}.low{color:#88cc88}.info{color:#666}
table{border-collapse:collapse;width:100%;margin-top:12px}
th,td{border:1px solid #333;padding:6px 10px;text-align:left;font-size:13px}
th{background:#1a1a1a}
pre{background:#111;padding:10px;overflow:auto;font-size:12px}
</style></head><body>
<h1>LLM-RedKit Report</h1>
<p>Target: {{ target }}</p>
<p>Date: {{ date }}</p>
<p>Total: {{ total }} | Successes: {{ successes }}</p>
<h2>Summary</h2>
<table><tr><th>Severity</th><th>Count</th></tr>
{% for k,v in sev_counts.items() %}<tr><td class="{{ k }}">{{ k }}</td><td>{{ v }}</td></tr>{% endfor %}
</table>
<h2>Findings</h2>
{% for v in verdicts %}
<h3 class="{{ v.severity }}">{{ v.attack }} — {{ v.severity.upper() }}</h3>
<pre>{{ v.evidence }}</pre>
{% endfor %}
</body></html>
"""

def render(target: str, verdicts: list) -> str:
    total = len(verdicts)
    successes = sum(1 for v in verdicts if v.success)
    sev = {"critical":0,"high":0,"medium":0,"low":0,"info":0}
    for v in verdicts:
        sev[v.severity] = sev.get(v.severity, 0) + 1
    return Template(HTML).render(
        target=target, date=datetime.utcnow().isoformat(),
        total=total, successes=successes, sev_counts=sev,
        verdicts=[v for v in verdicts if v.success])
