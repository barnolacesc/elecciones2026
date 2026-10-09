"""Component plan validation for Elecciones 2026.

Verifies that site/COMPONENT-PLAN.md includes required wireframes (360/390/430px),
component inventory, component states, accessibility constraints (WCAG 2.2 AA),
and explicit prohibitions against profile UI, fake verification claims, and interactive forms.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List


REQUIRED_SECTIONS = [
    "Executive Summary and Scope",
    "Local Design Tokens Integration",
    "Component Inventory and Specification",
    "Phone Wireframes",
    "Accessibility Audit and Testing Protocol",
    "Prohibited Elements Checklist",
]

REQUIRED_VIEWPORTS = [
    "360",
    "390",
    "430",
]

REQUIRED_COMPONENTS = [
    "SkipLink",
    "TopBar",
    "PreviewBanner",
    "HeroSection",
    "SelectorControls",
    "MeasureComparison",
    "PartyPositionCard",
    "RelationshipBadge",
    "StatusBadge",
    "ShareControl",
    "MethodologyNotice",
    "Footer",
]

REQUIRED_STATES = [
    "default",
    "hover",
    "focus-visible",
    "active",
    "disabled",
    "missing",
]

EXCLUSION_CHECKS = [
    (r"(no\s+profile\s+ui|strictly\s+no\s+profile|no\s+avatar)", "Explicit exclusion of profile / account UI"),
    (r"(no\s+fake\s+verification|100%\s+verificado|no\s+deceptive\s+verification)", "Explicit exclusion of fake verification claims"),
    (r"(no\s+fake\s+report\s+form|no\s+working\s+feedback\s+form|no\s+interactive\s+report\s+form)", "Explicit exclusion of interactive report forms in MVP"),
]


@dataclass
class ComponentPlanValidationResult:
    valid: bool
    errors: list[str]
    checked_sections: list[str]
    checked_components: list[str]
    checked_viewports: list[str]


def validate_component_plan_text(content: str) -> ComponentPlanValidationResult:
    """Validate the markdown content of COMPONENT-PLAN.md."""
    errors: list[str] = []
    checked_sections: list[str] = []
    checked_components: list[str] = []
    checked_viewports: list[str] = []

    content_lower = content.lower()

    # Check required section headings
    for sec in REQUIRED_SECTIONS:
        if sec.lower() in content_lower:
            checked_sections.append(sec)
        else:
            errors.append(f"Missing required section in component plan: '{sec}'.")

    # Check required viewports in wireframes
    for vp in REQUIRED_VIEWPORTS:
        pattern = rf"\b{vp}\s*(?:css\s*)?px\b"
        if re.search(pattern, content_lower):
            checked_viewports.append(vp)
        else:
            errors.append(f"Missing required wireframe viewport: {vp} CSS px.")

    # Check required components
    for comp in REQUIRED_COMPONENTS:
        if comp.lower() in content_lower:
            checked_components.append(comp)
        else:
            errors.append(f"Missing specification for component: '{comp}'.")

    # Check required component states
    for st in REQUIRED_STATES:
        if st.lower() not in content_lower:
            errors.append(f"Missing required component state specification: '{st}'.")

    # Check explicit exclusions
    for regex_pat, desc in EXCLUSION_CHECKS:
        if not re.search(regex_pat, content_lower):
            errors.append(f"Missing mandatory prohibition requirement: {desc}.")

    # Check touch target rule
    if "44px" not in content_lower and "44 px" not in content_lower:
        errors.append("Missing explicit 44px touch target specification.")

    return ComponentPlanValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        checked_sections=checked_sections,
        checked_components=checked_components,
        checked_viewports=checked_viewports,
    )


def validate_component_plan_file(path: Path) -> ComponentPlanValidationResult:
    """Validate a COMPONENT-PLAN.md file path."""
    if not path.is_file():
        return ComponentPlanValidationResult(False, [f"Component plan file not found: {path}"], [], [], [])
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return ComponentPlanValidationResult(False, [f"Failed to read file {path}: {e}"], [], [], [])
    return validate_component_plan_text(content)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Elecciones 2026 component plan.")
    subparsers = parser.add_subparsers(dest="command")

    val_parser = subparsers.add_parser("validate", help="Validate component plan Markdown")
    val_parser.add_argument(
        "file",
        nargs="?",
        default="site/COMPONENT-PLAN.md",
        help="Path to COMPONENT-PLAN.md (default: site/COMPONENT-PLAN.md)",
    )

    args = parser.parse_args()
    if args.command == "validate" or args.command is None:
        target = Path(args.file if hasattr(args, "file") else "site/COMPONENT-PLAN.md")
        result = validate_component_plan_file(target)
        if result.valid:
            print(f"Component plan valid ({len(result.checked_sections)} sections, {len(result.checked_components)} components, viewports {', '.join(result.checked_viewports)} px verified).")
            return 0
        else:
            print("Component plan validation failed with errors:")
            for err in result.errors:
                print(f"  ✗ {err}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
