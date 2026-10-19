"""Maintainer Triage CLI for User Improvement Proposals.

Package E8.5: Offline review tool to inspect, trim spam/fake submissions,
and convert approved suggestions into GitHub roadmap tasks.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

# Ensure src/ is on the Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from elecciones2026.feedback import (
    SQLiteProposalRepository,
    VALID_CATEGORIES,
    VALID_STATUSES,
)

DEFAULT_DB_PATH = "data/feedback.db"


def cmd_stats(repo: SQLiteProposalRepository) -> int:
    """Print aggregate stats of stored proposals."""
    st = repo.stats()
    total = sum(st.values())
    print("\n=== Estado del Buzón de Propuestas ===")
    print(f"Total registradas: {total}")
    print("-" * 38)
    for status, count in st.items():
        print(f"  • {status.upper():<12}: {count}")
    print("-" * 38)
    return 0


def cmd_list(
    repo: SQLiteProposalRepository,
    status: Optional[str] = "pending",
    category: Optional[str] = None,
    limit: int = 50,
) -> int:
    """List proposals matching criteria."""
    proposals = repo.list_proposals(status=status, category=category, limit=limit)
    if not proposals:
        print(f"\nNo se encontraron propuestas con estado '{status}'.")
        return 0

    print(f"\n=== Propuestas [{status or 'TODAS'}] (Mostrando {len(proposals)}) ===")
    for p in proposals:
        print("-" * 70)
        print(f"ID: {p.id}")
        print(f"Fecha: {p.created_at} | Categoría: {p.category} | Estado: {p.status}")
        print(f"Texto: {p.text}")
        if p.reviewer_notes:
            print(f"Notas: {p.reviewer_notes}")
        if p.action_ticket:
            print(f"Tarea: {p.action_ticket}")
    print("-" * 70)
    return 0


def cmd_review(repo: SQLiteProposalRepository, category: Optional[str] = None) -> int:
    """Interactive triage loop for pending proposals."""
    pending = repo.list_proposals(status="pending", category=category, limit=100)
    if not pending:
        print("\nNo hay propuestas pendientes de revisión en este momento.")
        return 0

    print(f"\nIniciando sesión interactiva de triaje ({len(pending)} pendientes)...\n")

    for idx, p in enumerate(pending, 1):
        print("=" * 70)
        print(f"[{idx}/{len(pending)}] Propuesta {p.id}")
        print(f"Fecha: {p.created_at} | Categoría: {p.category}")
        print(f"Longitud: {p.char_count} caracteres | Duración de redacción: {p.completion_time_ms} ms")
        print("-" * 70)
        print(p.text)
        print("-" * 70)

        while True:
            choice = input(
                "Acción: [c]onsiderar | [s]pam/trim | [r]echazar | [g]ithub issue snippet | [n]ext | [q]uit: "
            ).strip().lower()

            if choice == "q":
                print("\nSesión de triaje finalizada.")
                return 0
            elif choice == "n":
                break
            elif choice == "s":
                repo.update_status(p.id, "spam", reviewer_notes="Marcado como spam/descarte")
                print("-> Marcado como SPAM.")
                break
            elif choice == "r":
                reason = input("Motivo de rechazo (opcional): ").strip()
                repo.update_status(p.id, "rejected", reviewer_notes=reason or "Fuera de alcance")
                print("-> Marcado como RECHAZADO.")
                break
            elif choice == "c":
                notes = input("Notas del revisor / paquete de destino: ").strip()
                repo.update_status(p.id, "considered", reviewer_notes=notes or "Considerado constructivo")
                print("-> Marcado como CONSIDERADO.")
                break
            elif choice == "g":
                print("\n--- Snippet para GitHub Issue / OpenSpec Task ---")
                print(f"### Propuesta ciudadana: Mejora en {p.category}")
                print(f"> {p.text}\n")
                print(f"- **ID interno:** `{p.id}`")
                print(f"- **Fecha:** {p.created_at}")
                print(f"- **Categoría:** {p.category}")
                print("--------------------------------------------------\n")
            else:
                print("Opción no reconocida. Elige c, s, r, g, n o q.")

    print("\nTriaje de propuestas pendientes completado.")
    return 0


def cmd_export(repo: SQLiteProposalRepository, output_path: Optional[str] = None) -> int:
    """Export considered proposals into a markdown summary."""
    considered = repo.list_proposals(status="considered", limit=500)
    if not considered:
        print("No hay propuestas con estado 'considered' para exportar.")
        return 0

    lines = [
        "# Propuestas de Mejora Seleccionadas para la Hoja de Ruta",
        "",
        f"Fecha de exportación: {considered[0].created_at if considered else 'N/A'}",
        f"Total propuestas consideradas: {len(considered)}",
        "",
        "| ID | Categoría | Propuesta | Notas de Revisión |",
        "|---|---|---|---|",
    ]

    for p in considered:
        safe_text = p.text.replace("|", "\\|").replace("\n", " ")
        safe_notes = (p.reviewer_notes or "").replace("|", "\\|")
        lines.append(f"| `{p.id[:18]}...` | {p.category} | {safe_text} | {safe_notes} |")

    content = "\n".join(lines) + "\n"
    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
        print(f"Exportadas {len(considered)} propuestas a {output_path}")
    else:
        print(content)
    return 0


def cmd_prune(repo: SQLiteProposalRepository) -> int:
    """Prune expired nonces and stale rate-limit entries."""
    count = repo.prune_expired()
    print(f"Eliminadas {count} entradas expiradas de seguridad y control de tasa.")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline Triage CLI for Elecciones 2026 Improvement Proposal Box"
    )
    parser.add_argument(
        "--db",
        default=DEFAULT_DB_PATH,
        help=f"Path to SQLite database file (default: {DEFAULT_DB_PATH})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: stats
    subparsers.add_parser("stats", help="Show summary counts by status")

    # Subcommand: list
    list_parser = subparsers.add_parser("list", help="List proposals")
    list_parser.add_argument(
        "--status",
        choices=list(VALID_STATUSES) + ["all"],
        default="pending",
        help="Filter by status (default: pending)",
    )
    list_parser.add_argument(
        "--category",
        choices=list(VALID_CATEGORIES),
        default=None,
        help="Filter by category",
    )
    list_parser.add_argument("--limit", type=int, default=50, help="Max items to list")

    # Subcommand: review
    review_parser = subparsers.add_parser("review", help="Interactive triage of pending proposals")
    review_parser.add_argument(
        "--category",
        choices=list(VALID_CATEGORIES),
        default=None,
        help="Filter pending proposals by category",
    )

    # Subcommand: export
    export_parser = subparsers.add_parser("export", help="Export considered proposals to Markdown")
    export_parser.add_argument("--out", default=None, help="Output markdown file path")

    # Subcommand: prune
    subparsers.add_parser("prune", help="Prune expired nonces and stale rate limits")

    args = parser.parse_args(argv)

    repo = SQLiteProposalRepository(args.db)

    try:
        if args.command == "stats":
            return cmd_stats(repo)
        elif args.command == "list":
            st = None if args.status == "all" else args.status
            return cmd_list(repo, status=st, category=args.category, limit=args.limit)
        elif args.command == "review":
            return cmd_review(repo, category=args.category)
        elif args.command == "export":
            return cmd_export(repo, output_path=args.out)
        elif args.command == "prune":
            return cmd_prune(repo)
        else:
            parser.print_help()
            return 1
    finally:
        repo.close()


if __name__ == "__main__":
    sys.exit(main())
