"""Tests for local/production Docker path and container parity (Package E3.2).

Verifies acceptance criteria for OpenSpec tasks 4.1 and 4.5:
- Same static artifact served in both preview and production.
- Pinned and scanned base images by cryptographic digest.
- Non-privileged execution (UID 101), read-only root filesystem, dropped capabilities.
- Zero build-only tools or credentials in the serving container.
- ADR-0001 Cache-Control and security headers configured and served.
"""

from __future__ import annotations

import os
import re
import shutil
import socket
import subprocess
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCKERFILE_PATH = ROOT_DIR / "Dockerfile"
COMPOSE_PATH = ROOT_DIR / "compose.yaml"
NGINX_CONF_PATH = ROOT_DIR / "nginx" / "default.conf"

PINNED_PYTHON_DIGEST = "sha256:1b668429b3511ab407d8e00648891631b0b1a4d7e15e3ca70f38ab5b91ad4ab4"
PINNED_NGINX_DIGEST = "sha256:0c53a1f2890c3526bfd201440f0fd3970e5b78f80630f58284aad0d34b5ec7bd"


def find_free_port() -> int:
    """Find an available local TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def is_docker_available() -> bool:
    """Check if Docker CLI and daemon are reachable."""
    paths = [
        os.environ.get("PATH", ""),
        "/Applications/Docker.app/Contents/Resources/bin",
        "/usr/local/bin",
        "/usr/bin",
    ]
    env_path = ":".join([p for p in paths if p])
    env = os.environ.copy()
    env["PATH"] = env_path
    try:
        res = subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
            timeout=5,
        )
        return res.returncode == 0
    except Exception:
        return False


class TestDockerConfiguration(unittest.TestCase):
    """Test suite for Dockerfile, compose.yaml, and Nginx configurations."""

    def test_dockerfile_multistage_and_pinned_digests(self) -> None:
        """Verify Dockerfile uses multi-stage build and pins bases by cryptographic digest."""
        self.assertTrue(DOCKERFILE_PATH.is_file(), f"Missing Dockerfile at {DOCKERFILE_PATH}")
        content = DOCKERFILE_PATH.read_text(encoding="utf-8")

        # 1. Multi-stage builder stage
        self.assertIn("AS builder", content, "Dockerfile must define a builder stage")
        self.assertIn(
            f"python:3.12-alpine@{PINNED_PYTHON_DIGEST}",
            content,
            "Builder stage must use digest-pinned Python base image",
        )

        # 2. Multi-stage runtime serving stage
        self.assertIn("AS runtime", content, "Dockerfile must define a runtime stage")
        self.assertIn(
            f"nginx/nginx-unprivileged:1.30.7-alpine3.24@{PINNED_NGINX_DIGEST}",
            content,
            "Runtime stage must use digest-pinned unprivileged Nginx base image",
        )

        # 3. Static artifact copy from builder
        self.assertIn(
            "COPY --from=builder",
            content,
            "Runtime stage must copy static artifacts from builder stage",
        )
        self.assertIn(
            "/usr/share/nginx/html",
            content,
            "Static artifacts must be copied to Nginx document root",
        )

        # 4. Non-privileged user specification
        self.assertIn("USER 101", content, "Runtime stage must explicitly run as USER 101")

        # 5. Non-privileged port exposure and healthcheck
        self.assertIn("EXPOSE 8080", content, "Dockerfile must expose non-privileged port 8080")
        self.assertIn("HEALTHCHECK", content, "Dockerfile must declare a container HEALTHCHECK")
        self.assertIn("http://127.0.0.1:8080/", content, "Health check must query port 8080")

    def test_compose_yaml_least_privilege_and_hardening(self) -> None:
        """Verify compose.yaml specifies read-only rootfs, tmpfs, and security hardening."""
        self.assertTrue(COMPOSE_PATH.is_file(), f"Missing compose.yaml at {COMPOSE_PATH}")
        content = COMPOSE_PATH.read_text(encoding="utf-8")

        # 1. Read-only root filesystem
        self.assertIn("read_only: true", content, "compose.yaml must enforce read_only: true")

        # 2. Tmpfs for transient files
        self.assertIn("/tmp", content, "compose.yaml must mount tmpfs for /tmp")

        # 3. Privilege escalation prevention
        self.assertIn(
            "no-new-privileges:true",
            content,
            "compose.yaml must prohibit privilege escalation via no-new-privileges:true",
        )

        # 4. Capability drop
        self.assertIn("ALL", content, "compose.yaml must drop ALL Linux capabilities")

        # 5. Resource limits within ADR-0001 budget
        self.assertIn("mem_limit: 256m", content, "compose.yaml must specify mem_limit: 256m")
        self.assertIn("pids_limit: 64", content, "compose.yaml must limit pids to 64")

        # 6. Port binding support
        self.assertIn("8080", content, "compose.yaml must bind service to port 8080")

    def test_nginx_configuration_cache_and_security_headers(self) -> None:
        """Verify Nginx configuration codifies ADR-0001 cache and security headers."""
        self.assertTrue(NGINX_CONF_PATH.is_file(), f"Missing Nginx config at {NGINX_CONF_PATH}")
        content = NGINX_CONF_PATH.read_text(encoding="utf-8")

        # 1. Non-privileged port and server tokens
        self.assertIn("listen       8080;", content)
        self.assertIn("server_tokens off;", content)

        # 2. ADR-0001 Cache-Control rules
        # Fingerprinted comparison JS is immutable; stable names revalidate.
        self.assertIn('Cache-Control "public, max-age=31536000, immutable"', content)
        self.assertIn('location ~* "^/comparison-data\\.[0-9a-f]{16}\\.js$" {', content)
        self.assertIn('location ~* \\.(?:css|js)$ {', content)
        self.assertIn('location ^~ /tokens/ {', content)
        self.assertIn('Cache-Control "public, no-cache"', content)
        self.assertLess(content.index('location ~* "^/comparison-data'), content.index('location ~* \\.(?:css|js)$'))
        # HTML pages (300s, stale-while-revalidate=86400)
        self.assertIn('Cache-Control "public, max-age=300, stale-while-revalidate=86400"', content)
        # Security & crawler files (3600s, stale-while-revalidate=86400)
        self.assertIn('Cache-Control "public, max-age=3600, stale-while-revalidate=86400"', content)

        # 3. Security headers
        self.assertIn('X-Content-Type-Options "nosniff"', content)
        self.assertIn('X-Frame-Options "DENY"', content)
        self.assertIn('Referrer-Policy "strict-origin-when-cross-origin"', content)
        self.assertIn('Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()"', content)
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("default-src 'self'", content)
        self.assertIn("object-src 'none'", content)
        self.assertIn("frame-ancestors 'none'", content)


class TestLiveDockerContainerParity(unittest.TestCase):
    """Integration test suite executing real Docker container when Docker daemon is available."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.docker_ready = is_docker_available()
        cls.container_name = f"test_parity_{int(time.time())}"
        cls.port = find_free_port()
        cls.env = os.environ.copy()
        cls.env["PATH"] = ":".join(
            [
                p
                for p in [
                    cls.env.get("PATH", ""),
                    "/Applications/Docker.app/Contents/Resources/bin",
                    "/usr/local/bin",
                    "/usr/bin",
                ]
                if p
            ]
        )

        if cls.docker_ready:
            # Build the container image
            build_cmd = [
                "docker",
                "build",
                "-t",
                f"{cls.container_name}:latest",
                str(ROOT_DIR),
            ]
            subprocess.run(build_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=cls.env)

            # Run container with production hardening flags
            run_cmd = [
                "docker",
                "run",
                "-d",
                "--rm",
                "-p",
                f"127.0.0.1:{cls.port}:8080",
                "--read-only",
                "--tmpfs",
                "/tmp",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges:true",
                "--name",
                cls.container_name,
                f"{cls.container_name}:latest",
            ]
            subprocess.run(run_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=cls.env)

            # Wait for container HTTP readiness
            ready = False
            for _ in range(30):
                try:
                    req = urllib.request.Request(f"http://127.0.0.1:{cls.port}/")
                    with urllib.request.urlopen(req, timeout=1) as resp:
                        if resp.status == 200:
                            ready = True
                            break
                except Exception:
                    time.sleep(0.2)
            if not ready:
                raise RuntimeError("Docker test container failed to become ready on HTTP port")

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.docker_ready:
            subprocess.run(
                ["docker", "stop", cls.container_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=cls.env,
            )
            subprocess.run(
                ["docker", "rmi", f"{cls.container_name}:latest"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=cls.env,
            )

    def test_container_serves_html_and_adherence_to_adr0001(self) -> None:
        """Verify running container serves HTML with ADR-0001 cache and security headers."""
        if not self.docker_ready:
            self.skipTest("Docker daemon not available in test environment")

        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            headers = resp.headers
            self.assertIn("text/html", headers.get("Content-Type", ""))
            self.assertIn("max-age=300", headers.get("Cache-Control", ""))
            self.assertIn("stale-while-revalidate=86400", headers.get("Cache-Control", ""))
            self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
            self.assertEqual(headers.get("X-Frame-Options"), "DENY")
            self.assertIn("default-src 'self'", headers.get("Content-Security-Policy", ""))

            body = resp.read().decode("utf-8")
            self.assertIn('<html lang="es">', body)
            self.assertTrue("Elecciones" in body or "Generales" in body)

    def test_container_revalidates_stable_name_styles_and_scripts(self) -> None:
        """Stable URLs must not pin old comparison/quiz UI across releases."""
        if not self.docker_ready:
            self.skipTest("Docker daemon not available in test environment")

        for asset in ["styles.css", "tokens/tokens.css", "app.js", "sharing.js"]:
            req = urllib.request.Request(f"http://127.0.0.1:{self.port}/{asset}")
            with urllib.request.urlopen(req, timeout=5) as resp:
                self.assertEqual(resp.status, 200)
                cache_ctrl = resp.headers.get("Cache-Control", "")
                self.assertEqual(cache_ctrl, "public, no-cache")
                self.assertEqual(resp.headers.get("X-Content-Type-Options"), "nosniff")

    def test_container_keeps_fingerprinted_comparison_bundle_immutable(self) -> None:
        """The content-addressed comparison bundle retains long-lived caching."""
        if not self.docker_ready:
            self.skipTest("Docker daemon not available in test environment")

        origin = f"http://127.0.0.1:{self.port}"
        with urllib.request.urlopen(origin, timeout=5) as resp:
            html = resp.read().decode("utf-8")
        match = re.search(r'comparison-data\.[0-9a-f]{16}\.js', html)
        self.assertIsNotNone(match)
        with urllib.request.urlopen(f"{origin}/{match.group(0)}", timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get("Cache-Control"), "public, max-age=31536000, immutable")
        for route in ("cuestionario/", "simulador/"):
            with urllib.request.urlopen(origin + "/" + route, timeout=5) as resp:
                page = resp.read().decode("utf-8")
            stylesheet = re.search(r'(?:quiz|simulator)\.[0-9a-f]{16}\.css', page)
            self.assertIsNotNone(stylesheet)
            with urllib.request.urlopen(origin + "/" + stylesheet.group(), timeout=5) as resp:
                self.assertEqual(resp.headers.get("Cache-Control"), "public, max-age=31536000, immutable")

    def test_container_preserves_social_metadata_and_serves_preview_png(self) -> None:
        """E3.1a: verify the shipped home page is not replaced by the prototype."""
        if not self.docker_ready:
            self.skipTest("Docker daemon not available in test environment")

        origin = f"http://127.0.0.1:{self.port}"
        for route in ('/', '/?topic=housing&partyA=pp&partyB=erc',
                      '/temas/housing/?partyA=pp&partyB=erc&answer=private'):
            with self.subTest(route=route):
                with urllib.request.urlopen(origin + route, timeout=5) as resp:
                    body = resp.read().decode('utf-8')
                canonical = 'https://xn--eleccionesespaa2026-83b.es' + route.split('?')[0]
                self.assertIn(f'<link rel="canonical" href="{canonical}">', body)
                self.assertIn(f'<meta property="og:url" content="{canonical}">', body)
                self.assertIn('<meta property="og:locale" content="es_ES">', body)
                image = re.search(r'<meta property="og:image" content="https://xn--eleccionesespaa2026-83b.es(/assets/social-preview-[0-9a-f]{16}\.png)">', body)
                self.assertIsNotNone(image)
                with urllib.request.urlopen(origin + image.group(1), timeout=5) as resp:
                    self.assertEqual(resp.headers.get('Content-Type'), 'image/png')
                    self.assertIn('immutable', resp.headers.get('Cache-Control', ''))
                    self.assertEqual(resp.read(), (ROOT_DIR / 'site/assets/social-preview.png').read_bytes())

    def test_container_serves_crawler_policies_with_1h_cache(self) -> None:
        """Verify robots.txt and sitemap.xml are served with 1-hour cache header."""
        if not self.docker_ready:
            self.skipTest("Docker daemon not available in test environment")

        for policy_file in ["robots.txt", "sitemap.xml", "security.txt"]:
            req = urllib.request.Request(f"http://127.0.0.1:{self.port}/{policy_file}")
            with urllib.request.urlopen(req, timeout=5) as resp:
                self.assertEqual(resp.status, 200)
                cache_ctrl = resp.headers.get("Cache-Control", "")
                self.assertIn("max-age=3600", cache_ctrl)
                self.assertIn("stale-while-revalidate=86400", cache_ctrl)

    def test_container_runs_as_non_privileged_user(self) -> None:
        """Verify container process runs as UID 101 (nginx) and not root (UID 0)."""
        if not self.docker_ready:
            self.skipTest("Docker daemon not available in test environment")

        proc = subprocess.run(
            ["docker", "exec", self.container_name, "id", "-u"],
            capture_output=True,
            text=True,
            check=True,
            env=self.env,
        )
        uid = proc.stdout.strip()
        self.assertEqual(uid, "101", "Serving container must run as unprivileged UID 101")

    def test_origin_does_not_retain_fixture_request_metadata(self) -> None:
        """E4.4: successful and missing-file requests must not enter Docker logs."""
        if not self.docker_ready:
            self.skipTest("Docker daemon not available in test environment")
        marker = "quiz-origin-privacy-fixture"
        since = str(int(time.time()))
        origin = f"http://127.0.0.1:{self.port}"
        for route in ("/cuestionario/", "/styles.css", f"/{marker}.js"):
            request = urllib.request.Request(origin + route, headers={"User-Agent": marker})
            try:
                with urllib.request.urlopen(request, timeout=5) as response:
                    self.assertEqual(response.status, 200)
                    response.read()
            except urllib.error.HTTPError as error:
                self.assertEqual(error.code, 404)
                error.close()
        time.sleep(0.2)
        recorded = subprocess.run(
            ["docker", "logs", "--since", since, self.container_name],
            capture_output=True, text=True, check=True, env=self.env, timeout=5,
        )
        # Do not print raw logs, even when the assertion fails.
        self.assertFalse(marker in recorded.stdout + recorded.stderr,
                         "Synthetic visitor request metadata reached the container logs")
        config = subprocess.run(
            ["docker", "exec", self.container_name, "nginx", "-T"],
            capture_output=True, text=True, check=True, env=self.env, timeout=5,
        )
        self.assertIn("access_log off;", config.stdout)
        self.assertIn("error_log /dev/null;", config.stdout)

    def test_container_filesystem_is_read_only(self) -> None:
        """Verify write attempts to root filesystem are rejected."""
        if not self.docker_ready:
            self.skipTest("Docker daemon not available in test environment")

        proc = subprocess.run(
            ["docker", "exec", self.container_name, "touch", "/etc/exploit_test"],
            capture_output=True,
            text=True,
            env=self.env,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Read-only file system", proc.stderr)

    def test_container_has_no_build_tools(self) -> None:
        """Verify serving image contains zero compilers, no Python runtime, and no git."""
        if not self.docker_ready:
            self.skipTest("Docker daemon not available in test environment")

        for prohibited_tool in ["python", "python3", "pip", "gcc", "make", "git"]:
            proc = subprocess.run(
                ["docker", "exec", self.container_name, "which", prohibited_tool],
                capture_output=True,
                text=True,
                env=self.env,
            )
            self.assertNotEqual(
                proc.returncode,
                0,
                f"Prohibited build tool '{prohibited_tool}' found in serving container",
            )


if __name__ == "__main__":
    unittest.main()
