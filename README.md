# LLM-RedKit

Automated red-team harness for LLM applications.

## Attack categories

- prompt_injection — Instruction override
- jailbreak — DAN / persona bypasses
- data_leak — Secret and PII extraction
- encoding — Base64 / hex / ROT13 payloads
- system_extract — System prompt theft

## Install

    git clone https://github.com/Bn09/llm-redkit.git
    cd llm-redkit
    python3 -m venv venv
    source venv/bin/activate
    pip install -e .
    pip install reportlab

## Usage

    redkit --config examples/config.yaml --out report.html --json findings.json --pdf report.pdf

## Works with

- Ollama (local, free)
- OpenAI
- Any OpenAI-compatible endpoint

## License

Commercial.


