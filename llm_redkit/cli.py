import sys, json, yaml, argparse
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from .client import LLMClient
from .scorer import score
from .report import render
from .report_pdf import render_pdf
from .attacks import ALL_ATTACKS

console = Console()

def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)

def main():
    p = argparse.ArgumentParser("redkit")
    p.add_argument("--config", required=True)
    p.add_argument("--out", default="report.html")
    p.add_argument("--json", default=None)
    p.add_argument("--pdf", default=None)
    args = p.parse_args()

    cfg = load_config(args.config)
    client = LLMClient(cfg["base_url"], cfg.get("api_key"),
                       cfg.get("model", "gpt-4o-mini"),
                       headers=cfg.get("headers"))
    system = cfg.get("system_prompt")
    cats = cfg.get("categories", list(ALL_ATTACKS.keys()))

    verdicts = []
    table = Table(title="LLM-RedKit", show_lines=False)
    table.add_column("Attack")
    table.add_column("Category")
    table.add_column("Result")

    for cat in cats:
        for i, prompt in enumerate(ALL_ATTACKS.get(cat, [])):
            name = cat + "[" + str(i) + "]"
            try:
                resp = client.chat(prompt, system=system)
            except Exception as e:
                console.log("[red]error[/red] " + name + ": " + str(e))
                continue
            v = score(name, resp, cat)
            verdicts.append(v)
            tag = "[" + v.severity + "]" if v.success else "[ok]"
            color = "red" if v.success else "green"
            table.add_row(name, cat, "[" + color + "]" + tag + "[/" + color + "]")

    console.print(table)

    html = render(cfg["base_url"], verdicts)
    Path(args.out).write_text(html, encoding="utf-8")
    console.print("[green]report → " + args.out + "[/green]")

    if args.json:
        Path(args.json).write_text(
            json.dumps([vars(v) for v in verdicts], indent=2),
            encoding="utf-8")
        console.print("[green]json   → " + args.json + "[/green]")

    if args.pdf:
        render_pdf(
            args.pdf,
            cfg["base_url"],
            [vars(v) for v in verdicts],
            {
                "report_id": datetime.utcnow().strftime("%Y%m%d-%H%M%S"),
                "date": datetime.utcnow().isoformat(),
                "version": "1.0.0",
            },
        )
        console.print("[green]pdf    → " + args.pdf + "[/green]")

    successes = sum(1 for v in verdicts if v.success)
    sys.exit(0 if successes == 0 else 1)

if __name__ == "__main__":
    main()
