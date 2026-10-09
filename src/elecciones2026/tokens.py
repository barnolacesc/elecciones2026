"""Design token validation for Elecciones 2026.

Verifies local design tokens in site/tokens/tokens.json against WCAG 2.2 AA contrast,
touch target constraints (min 44px), mobile-first breakpoints (360/390/430px),
and absence of forbidden tokens (profiles, fake verification badges).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def srgb_to_linear(component_8bit: int) -> float:
    """Convert an 8-bit sRGB color component (0-255) to linear light."""
    c = component_8bit / 255.0
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    """Calculate the relative luminance of an sRGB hex color (#RRGGBB).

    Formula conforms to W3C WCAG 2.1 / 2.2 relative luminance definition.
    """
    clean_hex = hex_color.lstrip("#")
    if len(clean_hex) != 6:
        raise ValueError(f"Invalid hex color format: '{hex_color}'. Expected #RRGGBB.")
    r = int(clean_hex[0:2], 16)
    g = int(clean_hex[2:4], 16)
    b = int(clean_hex[4:6], 16)
    return 0.2126 * srgb_to_linear(r) + 0.7152 * srgb_to_linear(g) + 0.0722 * srgb_to_linear(b)


def contrast_ratio(hex_foreground: str, hex_background: str) -> float:
    """Calculate WCAG contrast ratio between two hex colors."""
    lum1 = relative_luminance(hex_foreground)
    lum2 = relative_luminance(hex_background)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)


# Standard evaluated text-on-background pairs with their minimum WCAG ratio
EVALUATED_PAIRS: List[Tuple[str, str, float, str]] = [
    ("tokens.color.text.primary.value", "tokens.color.bg.canvas.value", 4.5, "Primary body text on canvas"),
    ("tokens.color.text.primary.value", "tokens.color.bg.surface.value", 4.5, "Card body text on surface"),
    ("tokens.color.text.secondary.value", "tokens.color.bg.surface.value", 4.5, "Secondary text on surface"),
    ("tokens.color.text.secondary.value", "tokens.color.bg.canvas.value", 4.5, "Secondary text on canvas"),
    ("tokens.color.text.inverse.value", "tokens.color.bg.primary.value", 4.5, "Button text on primary button"),
    ("tokens.color.text.inverse.value", "tokens.color.bg.previewBanner.value", 4.5, "Preview banner text"),
    ("tokens.color.text.notice.value", "tokens.color.bg.notice.value", 4.5, "Notice text on notice box"),
    ("tokens.color.partyA.text.value", "tokens.color.partyA.bg.value", 4.5, "Party A text on pill"),
    ("tokens.color.partyB.text.value", "tokens.color.partyB.bg.value", 4.5, "Party B text on pill"),
    ("tokens.color.status.official.text.value", "tokens.color.status.official.bg.value", 4.5, "Official status badge text"),
    ("tokens.color.status.partial.text.value", "tokens.color.status.partial.bg.value", 4.5, "Partial status badge text"),
    ("tokens.color.status.missing.text.value", "tokens.color.status.missing.bg.value", 4.5, "Missing status badge text"),
    ("tokens.color.relationship.agreement.text.value", "tokens.color.relationship.agreement.bg.value", 4.5, "Agreement relationship text"),
    ("tokens.color.relationship.divergence.text.value", "tokens.color.relationship.divergence.bg.value", 4.5, "Divergence relationship text"),
    ("tokens.color.relationship.qualification.text.value", "tokens.color.relationship.qualification.bg.value", 4.5, "Qualification relationship text"),
]

FORBIDDEN_TOKEN_KEYS = {
    "profile",
    "account",
    "login",
    "avatar",
    "verifiedBadge",
    "fakeVerification",
    "hundredPercentVerified",
}

REQUIRED_BREAKPOINTS = {
    "mobileCompact": "360px",
    "mobileBaseline": "390px",
    "mobileLarge": "430px",
    "desktop": "760px",
}


@dataclass
class TokenValidationResult:
    valid: bool
    errors: list[str]
    contrast_checks: list[dict[str, Any]]
    token_count: int


def _get_nested_value(data: dict[str, Any], path: str) -> Any:
    parts = path.split(".")
    curr = data
    for part in parts:
        if not isinstance(curr, dict) or part not in curr:
            return None
        curr = curr[part]
    return curr


def validate_tokens_data(data: dict[str, Any]) -> TokenValidationResult:
    """Validate a parsed design tokens dictionary."""
    errors: list[str] = []
    contrast_checks: list[dict[str, Any]] = []

    # Check top-level structure
    if "tokens" not in data:
        errors.append("Missing top-level 'tokens' object.")
        return TokenValidationResult(False, errors, [], 0)

    tokens = data["tokens"]
    required_categories = ["color", "typography", "spacing", "size", "radius", "border", "focus", "breakpoint"]
    for cat in required_categories:
        if cat not in tokens:
            errors.append(f"Missing required token category: '{cat}'.")

    # Check forbidden keys anywhere in the token tree
    def check_forbidden(d: Any, prefix: str = "") -> None:
        if isinstance(d, dict):
            for k, v in d.items():
                if k.lower() in {fk.lower() for fk in FORBIDDEN_TOKEN_KEYS}:
                    errors.append(f"Forbidden token key detected: '{prefix}{k}'.")
                check_forbidden(v, f"{prefix}{k}.")

    check_forbidden(tokens)

    # Check minimum touch target
    touch_min_val = _get_nested_value(data, "tokens.size.touchTargetMin.value")
    if not touch_min_val:
        errors.append("Missing 'tokens.size.touchTargetMin.value'.")
    else:
        m = re.match(r"^(\d+)\s*px$", str(touch_min_val))
        if not m:
            errors.append(f"Invalid format for touchTargetMin: '{touch_min_val}'. Must be in px format.")
        else:
            px_val = int(m.group(1))
            if px_val < 44:
                errors.append(f"touchTargetMin is {px_val}px, which violates WCAG 2.5.5 minimum 44px.")

    # Check required breakpoints
    breakpoints = _get_nested_value(data, "tokens.breakpoint")
    if not isinstance(breakpoints, dict):
        errors.append("Missing or invalid 'tokens.breakpoint' object.")
    else:
        for bp_key, expected_val in REQUIRED_BREAKPOINTS.items():
            if bp_key not in breakpoints:
                errors.append(f"Missing required breakpoint '{bp_key}'.")
            else:
                actual_val = breakpoints[bp_key].get("value")
                if actual_val != expected_val:
                    errors.append(f"Breakpoint '{bp_key}' has value '{actual_val}', expected '{expected_val}'.")

    # Evaluate color contrast ratios
    for fg_path, bg_path, min_ratio, desc in EVALUATED_PAIRS:
        fg_hex = _get_nested_value(data, fg_path)
        bg_hex = _get_nested_value(data, bg_path)
        if not fg_hex or not bg_hex:
            errors.append(f"Could not resolve colors for pair '{desc}': fg={fg_hex}, bg={bg_hex}.")
            continue

        try:
            ratio = contrast_ratio(str(fg_hex), str(bg_hex))
            passed = ratio >= min_ratio
            contrast_checks.append({
                "pair": desc,
                "fg": fg_hex,
                "bg": bg_hex,
                "ratio": round(ratio, 2),
                "min_ratio": min_ratio,
                "passed": passed,
            })
            if not passed:
                errors.append(
                    f"Contrast failure: '{desc}' ({fg_hex} on {bg_hex}) ratio is {ratio:.2f}:1, "
                    f"minimum required is {min_ratio}:1."
                )
        except Exception as e:
            errors.append(f"Error calculating contrast for '{desc}': {e}")

    # Count total leaf tokens
    def count_leaves(d: Any) -> int:
        if isinstance(d, dict):
            if "value" in d:
                return 1
            return sum(count_leaves(v) for v in d.values())
        return 0

    total_tokens = count_leaves(tokens)
    return TokenValidationResult(len(errors) == 0, errors, contrast_checks, total_tokens)


def validate_tokens_file(path: Path) -> TokenValidationResult:
    """Validate a JSON design tokens file."""
    if not path.is_file():
        return TokenValidationResult(False, [f"File not found: {path}"], [], 0)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return TokenValidationResult(False, [f"JSON parse error in {path}: {e}"], [], 0)
    return validate_tokens_data(data)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Elecciones 2026 design tokens.")
    subparsers = parser.add_subparsers(dest="command")

    val_parser = subparsers.add_parser("validate", help="Validate design tokens JSON")
    val_parser.add_argument(
        "file",
        nargs="?",
        default="site/tokens/tokens.json",
        help="Path to tokens.json file (default: site/tokens/tokens.json)",
    )

    args = parser.parse_args()
    if args.command == "validate" or args.command is None:
        target = Path(args.file if hasattr(args, "file") else "site/tokens/tokens.json")
        result = validate_tokens_file(target)
        if result.valid:
            print(f"Tokens valid ({result.token_count} tokens loaded, {len(result.contrast_checks)} contrast checks passed).")
            for chk in result.contrast_checks:
                print(f"  ✓ {chk['pair']}: {chk['ratio']}:1 (min {chk['min_ratio']}:1)")
            return 0
        else:
            print("Token validation failed with errors:")
            for err in result.errors:
                print(f"  ✗ {err}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
