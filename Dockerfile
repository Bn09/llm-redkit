# syntax=docker/dockerfile:1.6

# ---------- Stage 1: builder ----------
FROM python:3.11-slim AS builder

WORKDIR /build

COPY pyproject.toml ./
COPY llm_redkit ./llm_redkit
COPY README.md ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --target=/install .

# ---------- Stage 2: runtime ----------
FROM python:3.11-slim

LABEL org.opencontainers.image.title="LLM-RedKit" \
      org.opencontainers.image.description="Agentic red-team harness for LLM applications" \
      org.opencontainers.image.source="https://github.com/Bn09/llm-redkit" \
      org.opencontainers.image.licenses="Commercial"

WORKDIR /work

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local/lib/python3.11/site-packages/
COPY --from=builder /build/README.md /work/README.md

RUN ln -sf /usr/local/lib/python3.11/site-packages/bin/redkit \
           /usr/local/bin/redkit 2>/dev/null || \
    printf '#!/usr/bin/env python3\nfrom llm_redkit.cli import main\nmain()\n' \
      > /usr/local/bin/redkit && chmod +x /usr/local/bin/redkit

# non-root user
RUN useradd -m -u 1000 redkit && \
    mkdir -p /work/output && \
    chown -R redkit:redkit /work
USER redkit

ENTRYPOINT ["redkit"]
CMD ["--help"]
