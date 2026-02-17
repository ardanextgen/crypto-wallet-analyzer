# ============================================================================
# MAIN.PY - Command-Line Interface (CLI)
# ============================================================================
#
# Was macht dieses CLI?
# - Akzeptiert Wallet-Adresse als Argument
# - Lädt Blockchain-Daten
# - Führt Risiko-Analyse durch
# - Generiert AI-Report
# - Zeigt formatierte Ausgabe
# - Optional: Export als JSON
#
# Verwendung:
#   python -m src.cli.main 0x123...
#   python -m src.cli.main 0x123... --json output.json
#   python -m src.cli.main  (interaktive Eingabe)
# ============================================================================

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Rich-Bibliothek für schöne Terminal-Ausgabe
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich import print as rprint

# Unsere Module
from ..blockchain.web3_client import Web3Client
from ..blockchain.etherscan_client import EtherscanClient
from ..analysis.risk_engine import RiskEngine
from ..ai.report_generator import AIReportGenerator
from ..blockchain.data_models import CompleteAnalysis

# Console für Rich
console = Console()


# ============================================================================
# HAUPT-ANALYSE-FUNKTION
# ============================================================================
def analyze_wallet(address: str, generate_ai: bool = True) -> CompleteAnalysis:
    """
    Führt vollständige Wallet-Analyse durch.

    Args:
        address: Ethereum Wallet-Adresse
        generate_ai: AI-Report generieren? (default: True)

    Returns:
        CompleteAnalysis-Objekt

    Raises:
        Exception bei Fehlern
    """
    # Progress-Anzeige erstellen
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        # Schritt 1: Web3-Verbindung
        task1 = progress.add_task("🔗 Verbinde zu Ethereum-Blockchain...", total=None)
        web3_client = Web3Client()
        progress.update(task1, completed=True)

        # Schritt 2: Etherscan-Verbindung
        task2 = progress.add_task("🔍 Initialisiere Etherscan Client...", total=None)
        etherscan_client = EtherscanClient()
        progress.update(task2, completed=True)

        # Schritt 3: Wallet-Daten laden
        task3 = progress.add_task("📊 Lade Wallet-Daten...", total=None)

        # Hole Daten von Etherscan (Transaktionen, Tokens)
        wallet_data = etherscan_client.get_complete_wallet_data(address, max_transactions=100)

        # Ergänze ETH-Balance von Web3
        eth_balance = web3_client.get_eth_balance(address)
        wallet_data.eth_balance = eth_balance

        progress.update(task3, completed=True)

        # Schritt 4: Risiko-Analyse
        task4 = progress.add_task("🎯 Berechne Risiko-Score...", total=None)
        risk_engine = RiskEngine()
        risk_score = risk_engine.analyze(wallet_data)
        progress.update(task4, completed=True)

        # Schritt 5: AI-Report (optional)
        ai_report = None
        if generate_ai:
            task5 = progress.add_task("🤖 Generiere AI-Report...", total=None)
            try:
                ai_generator = AIReportGenerator()
                ai_report = ai_generator.generate_report(wallet_data, risk_score)
                progress.update(task5, completed=True)
            except Exception as e:
                progress.update(task5, description=f"⚠️  AI-Report übersprungen: {e}")
                console.print(f"[yellow]⚠️  AI-Report konnte nicht generiert werden: {e}[/yellow]")

    # Erstelle komplette Analyse
    complete_analysis = CompleteAnalysis(
        wallet_data=wallet_data,
        risk_score=risk_score,
        ai_report=ai_report,
        analysis_timestamp=datetime.now()
    )

    return complete_analysis


# ============================================================================
# FORMATIERTE AUSGABE
# ============================================================================
def display_analysis(analysis: CompleteAnalysis):
    """
    Zeigt Analyse-Ergebnisse formatiert an.

    Args:
        analysis: CompleteAnalysis-Objekt
    """
    console.print()  # Leerzeile

    # Header
    console.print(Panel.fit(
        "🔍 [bold cyan]KRYPTO-WALLET ANALYSE[/bold cyan]",
        border_style="cyan"
    ))

    # ========================================================================
    # WALLET-INFORMATIONEN
    # ========================================================================
    wallet_table = Table(title="📊 Wallet-Informationen", show_header=False)
    wallet_table.add_column("Feld", style="cyan")
    wallet_table.add_column("Wert", style="white")

    wallet_table.add_row("Adresse", analysis.wallet_data.address)
    wallet_table.add_row(
        "ETH Balance",
        f"{analysis.wallet_data.get_eth_balance_decimal():.4f} ETH"
    )
    wallet_table.add_row(
        "Wallet-Alter",
        f"{analysis.wallet_data.get_wallet_age_days()} Tage (~{analysis.wallet_data.get_wallet_age_days() // 30} Monate)"
        if analysis.wallet_data.get_wallet_age_days() else "Unbekannt"
    )
    wallet_table.add_row("Transaktionen", str(analysis.wallet_data.total_transactions))
    wallet_table.add_row("Token-Holdings", str(len(analysis.wallet_data.token_holdings)))

    console.print(wallet_table)
    console.print()

    # ========================================================================
    # RISIKO-SCORE
    # ========================================================================
    risk = analysis.risk_score

    # Farbe basierend auf Risiko-Level
    if risk.risk_level == "low":
        score_color = "green"
        risk_emoji = "✅"
    elif risk.risk_level == "medium":
        score_color = "yellow"
        risk_emoji = "⚠️"
    else:
        score_color = "red"
        risk_emoji = "🚨"

    # Risiko-Header
    console.print(Panel.fit(
        f"{risk_emoji} [bold {score_color}]RISIKO-SCORE: {risk.total_score:.1f}/100[/bold {score_color}]\n"
        f"Level: [bold {score_color}]{risk.risk_level.upper()}[/bold {score_color}]",
        border_style=score_color
    ))

    # Detail-Scores Tabelle
    score_table = Table(title="🎯 Detail-Scores", show_header=True)
    score_table.add_column("Heuristik", style="cyan")
    score_table.add_column("Score", justify="right")
    score_table.add_column("Bewertung", justify="center")

    def get_score_emoji(score: float) -> str:
        """Gibt Emoji basierend auf Score zurück"""
        if score <= 30:
            return "✅ Gut"
        elif score <= 60:
            return "⚠️  Mittel"
        else:
            return "🚨 Hoch"

    score_table.add_row(
        "Wallet-Alter",
        f"{risk.wallet_age_score:.1f}",
        get_score_emoji(risk.wallet_age_score)
    )
    score_table.add_row(
        "Transaktionsvolumen",
        f"{risk.transaction_volume_score:.1f}",
        get_score_emoji(risk.transaction_volume_score)
    )
    score_table.add_row(
        "Token-Konzentration",
        f"{risk.token_concentration_score:.1f}",
        get_score_emoji(risk.token_concentration_score)
    )
    score_table.add_row(
        "Scam-Interaktion",
        f"[bold]{risk.scam_interaction_score:.1f}[/bold]",
        get_score_emoji(risk.scam_interaction_score)
    )
    score_table.add_row(
        "Mixer-Nutzung",
        f"{risk.mixer_usage_score:.1f}",
        get_score_emoji(risk.mixer_usage_score)
    )
    score_table.add_row(
        "Ein-/Ausgangs-Muster",
        f"{risk.inflow_outflow_score:.1f}",
        get_score_emoji(risk.inflow_outflow_score)
    )

    console.print(score_table)
    console.print()

    # ========================================================================
    # FLAGS/WARNUNGEN
    # ========================================================================
    if risk.flags:
        console.print("[bold red]🚩 Erkannte Warnungen:[/bold red]")
        for flag in risk.flags:
            console.print(f"  • {flag}")
        console.print()

    # ========================================================================
    # AI-REPORT
    # ========================================================================
    if analysis.ai_report:
        ai = analysis.ai_report

        console.print(Panel(
            f"[bold]Zusammenfassung:[/bold]\n{ai.summary}\n\n"
            f"[bold]Risiko-Einschätzung:[/bold]\n{ai.risk_assessment}",
            title="🤖 AI-Analyse",
            border_style="magenta"
        ))

        if ai.key_factors:
            console.print("\n[bold magenta]🔑 Hauptfaktoren:[/bold magenta]")
            for i, factor in enumerate(ai.key_factors, 1):
                console.print(f"  {i}. {factor}")

        if ai.recommendations:
            console.print("\n[bold green]💡 Empfehlungen:[/bold green]")
            for i, rec in enumerate(ai.recommendations, 1):
                console.print(f"  {i}. {rec}")

    console.print()


# ============================================================================
# JSON-EXPORT
# ============================================================================
def export_to_json(analysis: CompleteAnalysis, filepath: str):
    """
    Exportiert Analyse als JSON-Datei.

    Args:
        analysis: CompleteAnalysis-Objekt
        filepath: Ziel-Dateipfad
    """
    # Konvertiere zu Dict (Pydantic hat .dict() Methode)
    data = analysis.model_dump()

    # Schreibe JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    console.print(f"[green]✅ Analyse exportiert nach:[/green] {filepath}")


# ============================================================================
# COMMAND-LINE ARGUMENT PARSING
# ============================================================================
def parse_arguments():
    """
    Parst Command-Line Argumente.

    Returns:
        Argparse Namespace
    """
    parser = argparse.ArgumentParser(
        description='🔍 Krypto-Wallet-Analyse-Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python -m src.cli.main 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
  python -m src.cli.main 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --json vitalik.json
  python -m src.cli.main --no-ai 0x123...  (ohne AI-Report)

Bekannte Test-Adressen:
  Vitalik Buterin: 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
  Uniswap Router:  0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D
        """
    )

    parser.add_argument(
        'address',
        nargs='?',  # Optional (für interaktive Eingabe)
        help='Ethereum Wallet-Adresse (0x...)'
    )

    parser.add_argument(
        '--json',
        metavar='FILE',
        help='Exportiere Ergebnis als JSON'
    )

    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Überspringe AI-Report-Generierung (schneller, spart API-Kosten)'
    )

    return parser.parse_args()


# ============================================================================
# MAIN-FUNKTION
# ============================================================================
def main():
    """
    Haupt-Einstiegspunkt für CLI.
    """
    # Banner
    console.print()
    console.print(Panel.fit(
        "[bold cyan]🔍 KRYPTO-WALLET-ANALYSE-TOOL[/bold cyan]\n"
        "Analysiert Ethereum-Wallets auf Scam-Risiken",
        border_style="cyan"
    ))
    console.print()

    # Parse Argumente
    args = parse_arguments()

    # Wallet-Adresse
    address = args.address

    # Interaktive Eingabe falls keine Adresse gegeben
    if not address:
        address = console.input("[cyan]Ethereum Wallet-Adresse eingeben:[/cyan] ")

    # Validierung (einfach)
    if not address.startswith('0x') or len(address) != 42:
        console.print("[red]❌ Ungültige Ethereum-Adresse![/red]")
        console.print("[yellow]Format: 0x + 40 Hex-Zeichen (42 Zeichen total)[/yellow]")
        sys.exit(1)

    try:
        # Führe Analyse durch
        console.print(f"[cyan]Analysiere Wallet:[/cyan] {address}\n")

        analysis = analyze_wallet(
            address,
            generate_ai=not args.no_ai
        )

        # Zeige Ergebnisse
        display_analysis(analysis)

        # JSON-Export (optional)
        if args.json:
            export_to_json(analysis, args.json)

        # Abschluss-Nachricht
        console.print()
        console.print(Panel.fit(
            "[green]✅ Analyse abgeschlossen![/green]\n"
            f"Timestamp: {analysis.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            border_style="green"
        ))

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Analyse abgebrochen[/yellow]")
        sys.exit(0)

    except Exception as e:
        console.print(f"\n[red]❌ Fehler bei der Analyse:[/red]")
        console.print(f"[red]{e}[/red]")

        # Detaillierte Fehlermeldung für Debugging
        import traceback
        console.print("\n[dim]Detaillierter Fehler:[/dim]")
        console.print(Syntax(traceback.format_exc(), "python", theme="monokai"))

        sys.exit(1)


# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    main()
