# Dependency and Security Advisory Audit

- **Package:** Roadmap Package `E3.2` (Issue #16)
- **Applicable OpenSpec Change:** `mvp-programme-comparison`
- **Related OpenSpec Tasks:** 4.1, 4.2, 4.5
- **Audit Date:** 2026-10-10
- **Auditor:** Release Engineering Lead / Automated CI Security Suite
- **Status:** Complete — Release Evidence Attached

---

## 1. Executive Summary

This document satisfies the release evidence requirements for OpenSpec tasks **4.1**, **4.2**, and **4.5** of the `mvp-programme-comparison` change. It provides an auditable inventory of all runtime, build, test, and container dependencies, analyzes known security advisories, documents the PDF-processing architecture, and verifies least-privilege CI and container isolation controls.

### Key Audit Findings
1. **Zero Runtime Dependencies:** The static site generator (`elecciones2026.generator`), schema validators (`elecciones2026.schemas`), editorial gatekeeper (`elecciones2026.editorial`), and source importer (`elecciones2026.importer`) use exclusively the Python standard library. No third-party Python packages are installed or required at runtime.
2. **Zero Native PDF Parsers:** Untrusted PDF programmes are analyzed through standard library byte scanning and constant-time SHA-256 verification in `src/elecciones2026/importer.py`. No native binary parsers (such as Poppler, Ghostscript, ImageMagick, or MuPDF) are executed, completely eliminating memory corruption and remote code execution vulnerabilities commonly associated with document-rendering engines.
3. **Digest-Pinned Containers:** Both the builder (`python:3.12-alpine`) and runtime (`nginxinc/nginx-unprivileged:stable-alpine`) images are pinned by immutable cryptographic SHA-256 digests.
4. **Vulnerability Remediation:** Container base scanning identified one upstream advisory in Alpine's base image (CVE-2026-4775 in `tiff 4.7.1-r0`). This is remediated at build time via `apk --no-cache upgrade tiff zlib` (upgrading to `4.7.2-r0`), leaving zero High or Critical vulnerabilities.
5. **Least-Privilege CI and Fork Isolation:** The CI workflow operates under top-level `permissions: contents: read`. Pull requests triggered from external forks run under read-only permissions with zero access to repository secrets or deployment credentials. Dangerous workflow triggers (`pull_request_target`) are strictly prohibited.

---

## 2. Dependency Inventory

### 2.1 Python Runtime Dependencies
- **Declared Dependencies (`pyproject.toml`):** None (`dependencies = []`).
- **Python Version Requirement:** Python `>=3.12` (supported up to `>=3.14`).
- **Core Standard Library Modules Used:**
  - `dataclasses`, `json`, `pathlib`, `re`, `typing`, `hashlib`, `hmac`
  - `urllib.parse`, `urllib.request`, `socket`, `ipaddress` (in isolated `importer.py` offline/SSRF module)
  - `xml.etree.ElementTree` (sitemap generation)
  - `html`, `shutil`, `argparse`

### 2.2 Python Build and Test Dependencies
| Package | Version Range | Purpose | Advisories / Risk |
|---|---|---|---|
| `setuptools` | `>=80.0.0` | PEP 517 build backend (`setuptools.build_meta`) | Clean; modern versions address historical tarfile/package extraction issues |
| `pytest` | `>=8.0.0` | Test discovery and test runner | Development/CI only; no runtime footprint |
| `ruff` | `>=0.17.0` | Fast linter and syntax validator | Development/CI only |
| `pip-audit` | `>=2.9.0` | Supply-chain CVE scanner | CI security scan |

### 2.3 Container Base Images
| Stage | Image Repository | Pinned Digest | Base OS / Version | Purpose |
|---|---|---|---|---|
| **Builder (Stage 1)** | `docker.io/library/python:3.12-alpine` | `sha256:1b668429b3511ab407d8e00648891631b0b1a4d7e15e3ca70f38ab5b91ad4ab4` | Alpine 3.24 | Compiles static site deterministically; discarded after build |
| **Runtime (Stage 2)** | `docker.io/nginxinc/nginx-unprivileged:stable-alpine` | `sha256:15c994d10d6d78658721c3bcafff14cb281fba2a4bdf9d5ba92c416a472516e3` | Alpine 3.24.2 / Nginx 1.30.5 | Serves static artifact on port 8080 under UID 101 |

---

## 3. PDF-Processing Tool Review and Architecture

### 3.1 Threat Model for Untrusted Document Ingestion
Political manifestos published by competing parties are untrusted binary inputs. Potential threats include:
- Buffer overflows, memory corruption, or heap exploits in native C/C++ PDF renderers (Ghostscript, Poppler, Xpdf).
- Embedded active content (`/JavaScript`, `/Launch`, `/SubmitForm`, `/EmbeddedFiles`).
- Polyglot files masking executables or archives as PDF files.
- SSRF and internal network scanning via remote document fetching.
- Denial of Service via unbounded memory allocation ("PDF bombs", recursive decompression).

### 3.2 Implemented Architectural Controls (`src/elecciones2026/importer.py`)
1. **Zero External Binary Execution:** The project **does not invoke** `pdftotext`, `poppler`, `ghostscript`, `pdfminer`, or `tesseract` in the build or serving paths.
2. **Lexical Inspection Only:** The PDF parser scans raw byte streams using regex and byte windowing strictly to:
   - Validate the `%PDF-` header magic bytes within the first 1,024 bytes.
   - Reject polyglot executable signatures (`MZ`, `ELF`, Mach-O, ZIP, shell shebangs).
   - Detect and reject prohibited dictionary names (`/JavaScript`, `/JS`, `/Launch`, `/EmbeddedFiles`, `/SubmitForm`, `/ImportData`, `/RichMedia`, `/Screen`, `/Sound`, `/XFA`), including `#xx` hex-encoded obfuscations.
3. **Streaming Resource Boundaries:**
   - 50 MB hard ceiling on file size (`DEFAULT_MAX_FILE_SIZE_BYTES`).
   - Incremental streaming in 64 KB chunks, aborting mid-stream if limits are exceeded.
   - 15-second socket timeout (`DEFAULT_TIMEOUT_SECONDS`).
   - Maximum 3 HTTP redirect hops with redirect cycle detection.
4. **Network and SSRF Boundaries:**
   - Strict scheme enforcement (HTTPS only).
   - Complete exclusion of IPv4 and IPv6 loopback, private (RFC 1918), link-local (cloud metadata `169.254.169.254`), and CGNAT ranges before socket connection.
   - Offline-only isolation mode for air-gapped verification.
5. **Constant-Time Verification:** Computed SHA-256 digests are compared against the versioned source register using `hmac.compare_digest`.

---

## 4. Container Security and Digest Verification (Task 4.5)

### 4.1 Base Image Vulnerability Scan
Trivy security scan of `nginxinc/nginx-unprivileged:stable-alpine@sha256:15c994d10d6d78658721c3bcafff14cb281fba2a4bdf9d5ba92c416a472516e3`:

```
┌─────────┬───────────────┬──────────┬────────┬───────────────────┬───────────────┬───────────────────────────────────┐
│ Library │ Vulnerability │ Severity │ Status │ Installed Version │ Fixed Version │ Title                             │
├─────────┼───────────────┼──────────┼────────┼───────────────────┼───────────────┼───────────────────────────────────┤
│ tiff    │ CVE-2026-4775 │ HIGH     │ fixed  │ 4.7.1-r0          │ 4.7.2-r0      │ libtiff integer overflow / DoS    │
└─────────┴───────────────┴──────────┴────────┴───────────────────┴───────────────┴───────────────────────────────────┘
```

**Remediation:**  
The `Dockerfile` runtime stage executes `apk --no-cache upgrade tiff zlib` before switching to `USER 101`. This upgrades `tiff` to `4.7.2-r0` and `zlib` to `1.3.2-r1`, eliminating the vulnerability in the final serving image.

### 4.2 Non-Privileged Execution and Filesystem Protection
- **User Segregation:** The runtime image runs as unprivileged user `nginx` (`UID 101`, `GID 101`).
- **Read-Only Root Filesystem:** Container runs with `read_only: true`. Temporary paths (`/tmp`, `/var/run`) are mounted as `tmpfs`.
- **Capability Drop:** All Linux capabilities dropped (`cap_drop: ALL`).
- **Privilege Escalation Prevention:** `security_opt: [no-new-privileges:true]`.
- **Resource Constraints:** `mem_limit: 256m`, `pids_limit: 64`.
- **Build Tool Elimination:** The runtime image contains zero compilers, no Python runtime, no Git, and no PDF tooling.

---

## 5. Least-Privilege CI and Fork PR Isolation (Task 4.1)

### 5.1 Threat Analysis for Fork Pull Requests
Pull requests from forks of public repositories can submit modified workflow definitions, poisoned dependencies, or test scripts designed to exfiltrate repository secrets (such as Cloudflare API tokens or Hetzner server keys).

### 5.2 CI Safeguards Implemented in `.github/workflows/ci.yml`
1. **Restricted Workflow Permissions:** Top-level permissions are strictly pinned to `permissions: contents: read`. GITHUB_TOKEN has zero write permissions.
2. **Prohibition of `pull_request_target`:** The CI workflow uses standard `pull_request` event triggers. It **never uses** `pull_request_target`, ensuring untrusted fork code cannot run with repository write privileges or access repository secrets.
3. **No Secrets Passed to PR Jobs:** All PR validation jobs (`validate`, `security-audit`, `docker-parity`) run without access to repository secrets.
4. **Guarded Deployment Triggers:** Any deployment or release jobs require:
   - `github.repository == 'c2ventures/elecciones2026'`
   - `github.event_name == 'push'`
   - `github.ref == 'refs/heads/main'`
5. **Secret and Leak Scans:** Automated secret scanning verifies that no API keys, private keys, or passwords exist in repository files or commits.

---

## 6. Verification Evidence and Acceptance

| Requirement | Verification Method | Status |
|---|---|---|
| Zero runtime dependencies | Inspected `pyproject.toml` and imports | **PASS** |
| Safe PDF processing (zero native parsers) | Inspected `src/elecciones2026/importer.py` | **PASS** |
| Digest-pinned Docker bases | Inspected `Dockerfile` image references | **PASS** |
| Container vulnerability scan & remediation | Trivy scan and `apk upgrade tiff zlib` | **PASS** |
| Read-only non-privileged container serving | Tested via Docker run and `tests/test_docker_parity.py` | **PASS** |
| ADR-0001 cache and security headers | Verified via HTTP curl and integration tests | **PASS** |
| Fork PR deploy secret isolation | Verified via `.github/workflows/ci.yml` audit and `tests/test_ci_security.py` | **PASS** |
