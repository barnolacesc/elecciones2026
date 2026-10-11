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

# Compile deterministic Spanish static site into /app/dist
RUN PYTHONPATH=/app/src python3 -m elecciones2026.generator build \
    --root-dir /app \
    --content-dir /app/content \
    --output-dir /app/dist \
    --build-date 2026-10-09 \
    --canonical-base "$CANONICAL_BASE"

# Preserve generated home metadata; client-side assets are copied by the generator.

# Stage 2: Minimal non-privileged runtime server
FROM nginxinc/nginx-unprivileged:stable-alpine@sha256:15c994d10d6d78658721c3bcafff14cb281fba2a4bdf9d5ba92c416a472516e3 AS runtime

# Upgrade security-sensitive packages to address known upstream advisories
USER root
RUN apk --no-cache upgrade tiff zlib
USER 101

# Copy custom Nginx configuration implementing ADR-0001 headers and cache rules
COPY --chown=101:101 nginx/default.conf /etc/nginx/conf.d/default.conf

# Copy verified static artifact from builder (no Python runtime, no build tools, no credentials)
COPY --from=builder --chown=101:101 /app/dist/ /usr/share/nginx/html/

EXPOSE 8080
STOPSIGNAL SIGQUIT

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1
