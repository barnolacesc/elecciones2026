"""Validation and flow logic for Spanish home and selection views.

Package E2.2: Spanish home and one-topic/two-party selection.
Verifies touch/keyboard accessibility, 44px touch targets, zero horizontal overflow,
strict lack of visitor accounts or profiles, 8 core topics, and Spanish copy.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from elecciones2026.methodology import CORE_TOPIC_IDS, Taxonomy, load_taxonomy

PROHIBITED_PROFILE_PATTERNS = [
    r"\bperfil\b",
    r"\bavatar\b",
    r"\blogin\b",
    r"\bmi\s+cuenta\b",
    r"\biniciar\s+sesi[oó]n\b",
    r"\bregistrarse\b",
]

PROHIBITED_VERIFICATION_PATTERNS = [
    r"100%\s+verificado",
    r"100%\s+oficial",
    r"\bauditado\s+al\s+100%",
    r"\bcertificado\s+oficial",
]

PROHIBITED_EXTERNAL_CDN = [
    r"cdn\.tailwindcss\.com",
    r"fonts\.googleapis\.com",
    r"fonts\.gstatic\.com",
    r"cdnjs\.cloudflare\.com",
    r"cdn\.jsdelivr\.net",
    r"unpkg\.com",
]

# Words that would indicate unintended Catalan leakage in Spanish public copy
CATALAN_LEAKAGE_WORDS = [
    r"\bhabitatge\b",
    r"\beducaci[oó]\b",
    r"\bsanitat\b",
    r"\bserveis\s+socials\b",
    r"\btreball\b",
    r"\bimmigraci[oó]\b",
    r"\bdrets\b",
    r"\binici\b",
    r"\bm[eè]tode\b",
    r"\bfonts\b",
]


@dataclass
class UIValidationResult:
    valid: bool
    errors: list[str]


def validate_selection(
    topic: str,
    party_a: str,
    party_b: str,
    taxonomy: Optional[Taxonomy] = None,
) -> tuple[bool, Optional[str]]:
    """Validate a one-topic and two-party comparison request.

    Enforces:
      - Valid topic from taxonomy or core 8 topics.
      - Exactly two distinct parties (rejects identical selections).
      - Non-empty party selections.
    """
    valid_topics = (
        {t.id for t in taxonomy.topics} if taxonomy else set(CORE_TOPIC_IDS)
    )

    if not topic or topic not in valid_topics:
        return False, f"Tema no válido. Debe ser uno de los 8 temas oficiales: {', '.join(sorted(valid_topics))}."

    if not party_a or not party_b:
        return False, "Debes seleccionar dos partidos para realizar la comparación."

    if party_a == party_b:
        return False, "Por favor, selecciona dos candidaturas distintas para realizar la comparación."

    return True, None


def validate_html_structure(
    content: str, taxonomy: Optional[Taxonomy] = None
) -> list[str]:
    """Validate HTML content of site/index.html."""
    errors: list[str] = []
    content_lower = content.lower()

    # 1. Document Language: must declare lang="es"
    if '<html lang="es">' not in content and "<html lang='es'>" not in content:
        errors.append("HTML element must declare lang=\"es\".")

    # 2. Viewport meta
    if 'name="viewport"' not in content_lower or "width=device-width" not in content_lower:
        errors.append("Missing standard mobile responsive viewport meta tag.")

    # 3. Skip Link
    if 'class="skip-link"' not in content or 'href="#contenido"' not in content:
        errors.append("Missing accessible skip link pointing to #contenido.")

    # 4. Semantic Landmarks
    for landmark in ["<header", "<main", "<footer"]:
        if landmark not in content_lower:
            errors.append(f"Missing required landmark element: {landmark}.")

    # 5. Form controls: Form with role="search" or role="form"
    if 'id="selection-form"' not in content:
        errors.append("Missing #selection-form element.")

    # 6. Topic select and 8 core topics
    if 'id="topic-select"' not in content:
        errors.append("Missing #topic-select control.")
    else:
        expected_topics = (
            {t.id for t in taxonomy.topics} if taxonomy else set(CORE_TOPIC_IDS)
        )
        for tid in expected_topics:
            if f'value="{tid}"' not in content:
                errors.append(f"Topic selector missing required topic option: '{tid}'.")

    # 7. Party selectors: exactly two party selectors
    if 'id="party-a-select"' not in content:
        errors.append("Missing #party-a-select control.")
    if 'id="party-b-select"' not in content:
        errors.append("Missing #party-b-select control.")

    # 8. Check labels for all selects
    for select_id in ["topic-select", "party-a-select", "party-b-select"]:
        if f'for="{select_id}"' not in content:
            errors.append(f"Missing <label for=\"{select_id}\">.")

    # 9. Compare button
    if 'id="compare-submit"' not in content and 'btn-compare' not in content:
        errors.append("Missing compare submission button.")

    # 10. Selection error live region
    if 'id="selection-error"' not in content:
        errors.append("Missing #selection-error live region.")
    else:
        if 'role="alert"' not in content and 'aria-live="assertive"' not in content:
            errors.append("#selection-error must have role=\"alert\" or aria-live=\"assertive\".")

    # 11. Alphabetical sorting within party option groups
    def extract_option_texts(select_chunk: str) -> list[str]:
        # Extract text content of options inside candidaturas optgroup
        optgroup_match = re.search(
            r'<optgroup[^>]*label="[^"]*(?:candidaturas|oficiales)[^"]*"[^>]*>(.*?)</optgroup>',
            select_chunk,
            re.DOTALL | re.IGNORECASE,
        )
        if not optgroup_match:
            return []
        options = re.findall(r'<option[^>]*>(.*?)</option>', optgroup_match.group(1))
        return [re.sub(r"<.*?>", "", o).strip() for o in options]

    party_a_match = re.search(r'<select[^>]*id="party-a-select"[^>]*>(.*?)</select>', content, re.DOTALL)
    if party_a_match:
        texts = extract_option_texts(party_a_match.group(1))
        if texts:
            sorted_texts = sorted(texts, key=lambda s: s.lower())
            if texts != sorted_texts:
                errors.append(f"Party options in #party-a-select are not sorted alphabetically: {texts} vs {sorted_texts}")

    # 12. Script tag pointing to ./app.js
    if 'src="./app.js"' not in content and 'src="app.js"' not in content:
        errors.append("Missing script tag loading ./app.js.")

    # 13. Prohibited profile / account patterns
    for pat in PROHIBITED_PROFILE_PATTERNS:
        if re.search(pat, content_lower):
            errors.append(f"Prohibited account/profile UI pattern detected in HTML: '{pat}'.")

    # 14. Prohibited fake verification claims
    for pat in PROHIBITED_VERIFICATION_PATTERNS:
        if re.search(pat, content_lower):
            errors.append(f"Prohibited fake verification claim detected in HTML: '{pat}'.")

    # 15. Prohibited external CDNs
    for pat in PROHIBITED_EXTERNAL_CDN:
        if re.search(pat, content_lower):
            errors.append(f"External CDN dependency detected: '{pat}'.")

    # 16. Catalan leakage in Spanish copy
    # Exclude English / code / attributes by scanning text content
    text_only = re.sub(r"<[^>]+>", " ", content_lower)
    for pat in CATALAN_LEAKAGE_WORDS:
        if re.search(pat, text_only):
            errors.append(f"Accidental Catalan text detected in Spanish public copy: '{pat}'.")

    return errors


def validate_css_accessibility(content: str) -> list[str]:
    """Validate CSS rules for touch target sizes and zero horizontal overflow."""
    errors: list[str] = []

    # Touch target minimums
    if "44px" not in content and "--touch-target-min" not in content:
        errors.append("CSS missing mandatory 44px minimum touch target definition.")

    # Comfortable touch target
    if "48px" not in content and "--touch-target-comfortable" not in content:
        errors.append("CSS missing 48px comfortable touch target definition.")

    # Focus indicators
    if ":focus-visible" not in content and "--focus-ring" not in content:
        errors.append("CSS missing visible keyboard focus (:focus-visible) indicators.")

    # Zero horizontal overflow: overflow-x hidden on root/body
    if "overflow-x" not in content:
        errors.append("CSS missing overflow-x containment to prevent horizontal scroll.")

    # Box-sizing border-box
    if "box-sizing: border-box" not in content:
        errors.append("CSS missing global box-sizing: border-box reset.")

    # Breakpoints for 360, 390, 430 px
    for bp in ["360", "390", "430"]:
        if bp not in content:
            errors.append(f"CSS missing required viewport reference for {bp}px.")

    return errors


def validate_js_app(content: str) -> list[str]:
    """Validate client-side app.js logic."""
    errors: list[str] = []

    # Check for same-party validation logic
    if "partyA === partyB" not in content and "partyA == partyB" not in content:
        errors.append("app.js missing same-party rejection validation logic.")

    # Check aria-invalid manipulation
    if "aria-invalid" not in content:
        errors.append("app.js missing accessible aria-invalid error management.")

    # Check URL parameter handling
    if "URLSearchParams" not in content and "replaceState" not in content:
        errors.append("app.js missing URL parameter state synchronization.")

    # Check share handler
    if "share" not in content.lower():
        errors.append("app.js missing share handler.")

    # Check absence of PII / tracking
    for forbidden in ["cookie", "localstorage.user", "analytics", "tracking", "fingerprint"]:
        if forbidden in content.lower():
            errors.append(f"app.js contains prohibited tracking or PII pattern: '{forbidden}'.")

    return errors


def validate_ui_flow_files(
    html_path: Path,
    css_path: Optional[Path] = None,
    js_path: Optional[Path] = None,
    taxonomy_path: Optional[Path] = None,
) -> UIValidationResult:
    """Validate HTML, CSS, and JS files for package E2.2."""
    errors: list[str] = []

    taxonomy = None
    if taxonomy_path and taxonomy_path.is_file():
        taxonomy = load_taxonomy(taxonomy_path)

    if not html_path.is_file():
        return UIValidationResult(False, [f"HTML file not found: {html_path}"])

    html_content = html_path.read_text(encoding="utf-8")
    errors.extend(validate_html_structure(html_content, taxonomy=taxonomy))

    if css_path and css_path.is_file():
        css_content = css_path.read_text(encoding="utf-8")
        errors.extend(validate_css_accessibility(css_content))

    if js_path and js_path.is_file():
        js_content = js_path.read_text(encoding="utf-8")
        errors.extend(validate_js_app(js_content))

    return UIValidationResult(valid=len(errors) == 0, errors=errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Elecciones 2026 Spanish UI flow.")
    subparsers = parser.add_subparsers(dest="command")

    val_parser = subparsers.add_parser("validate", help="Validate UI flow files")
    val_parser.add_argument(
        "file",
        nargs="?",
        default="site/index.html",
        help="Path to site/index.html (default: site/index.html)",
    )

    args = parser.parse_args()
    if args.command == "validate" or args.command is None:
        target_html = Path(args.file if hasattr(args, "file") else "site/index.html")
        root = target_html.resolve().parent.parent if target_html.parent.name == "site" else target_html.resolve().parent
        css_path = root / "site" / "styles.css"
        js_path = root / "site" / "app.js"
        taxonomy_path = root / "content" / "taxonomy.json"

        result = validate_ui_flow_files(
            html_path=target_html,
            css_path=css_path if css_path.is_file() else None,
            js_path=js_path if js_path.is_file() else None,
            taxonomy_path=taxonomy_path if taxonomy_path.is_file() else None,
        )

        if result.valid:
            print("OK: Spanish UI flow, selection controls, and accessibility validated successfully.")
            return 0
        else:
            print("UI flow validation failed with errors:")
            for err in result.errors:
                print(f"  ✗ {err}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
