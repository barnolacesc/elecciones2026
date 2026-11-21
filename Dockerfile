# Pinned deterministic multi-stage build for local preview and production release.
# Conforms to Roadmap package E3.2, Task 4.5, and ADR-0001.

# Stage 1: Deterministic static site builder
FROM python:3.12-alpine@sha256:1b668429b3511ab407d8e00648891631b0b1a4d7e15e3ca70f38ab5b91ad4ab4 AS builder

ARG CANONICAL_BASE=https://xn--eleccionesespaa2026-83b.es
WORKDIR /app

# Copy application sources, content records, schemas, and assets
COPY pyproject.toml /app/
COPY src/ /app/src/
COPY content/ /app/content/
COPY site/ /app/site/

ARG ELECTION_ID=es-gen-2026
ARG QUIZ_MODE=unavailable
ARG PILOT_PROVISIONAL=0
# Empty selects the deterministic source-register update date for production.
ARG BUILD_DATE

# Compile deterministic Spanish static site into /app/dist
RUN PYTHONPATH=/app/src python3 -m elecciones2026.generator build \
    --root-dir /app \
    --content-dir /app/content \
    --output-dir /app/dist \
    --election-id "$ELECTION_ID" \
    --quiz-mode "$QUIZ_MODE" \
    $(test "$PILOT_PROVISIONAL" = 1 && echo --pilot-provisional) \
    --build-date "$BUILD_DATE" \
    --canonical-base "$CANONICAL_BASE"

# Precompute the large immutable comparison script once for the serving image.
RUN python3 - <<'PYTHON'
from gzip import compress
from pathlib import Path

for bundle in Path("/app/dist").glob("comparison-data.*.js"):
    compressed = bundle.with_suffix(".js.gz")
    compressed.write_bytes(compress(bundle.read_bytes(), compresslevel=6, mtime=0))
PYTHON

# Preserve generated home metadata; client-side assets are copied by the generator.

# Stage 2: Minimal non-privileged runtime server
FROM nginx/nginx-unprivileged:1.30.7-alpine3.24@sha256:0c53a1f2890c3526bfd201440f0fd3970e5b78f80630f58284aad0d34b5ec7bd AS runtime

# Upgrade security-sensitive packages to address known upstream advisories
USER root
RUN apk --no-cache upgrade
USER 101

# Copy custom Nginx configuration implementing ADR-0001 headers and cache rules
COPY --chown=101:101 nginx/default.conf /etc/nginx/conf.d/default.conf

# Copy verified static artifact from builder (no Python runtime, no build tools, no credentials)
COPY --from=builder --chown=101:101 /app/dist/ /usr/share/nginx/html/

EXPOSE 8080
STOPSIGNAL SIGQUIT

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1
