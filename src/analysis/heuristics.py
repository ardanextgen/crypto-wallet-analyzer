# ============================================================================
# HEURISTICS.PY - Risiko-Analyse Heuristiken
# ============================================================================
#
# Was sind Heuristiken?
# - Faustregeln zur Bewertung von Risiken
# - Basieren auf Mustern, die bei Scams häufig auftreten
# - Kein 100%iger Beweis, aber starke Indikatoren
#
# Die 6 Heuristiken:
# 1. Wallet-Alter: Neue Wallets sind verdächtiger
# 2. Transaktionsvolumen: Zu wenige oder zu viele TXs
# 3. Token-Konzentration: Alles in einem Token = riskant
# 4. Scam-Interaktion: Kontakt mit bekannten Scams
# 5. Mixer-Nutzung: Privacy-Tools = erhöhtes Risiko
# 6. Ein-/Ausgangs-Muster: Schnelles Durchleiten von Geldern
#
# Jede Heuristik gibt einen Score von 0-100:
# - 0 = kein Risiko
# - 1-30 = niedriges Risiko
# - 31-60 = mittleres Risiko
# - 61-100 = hohes Risiko
# ============================================================================

from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from decimal import Decimal
import logging

from ..blockchain.data_models import WalletData, Transaction, TokenHolding
from .scam_lists import get_scam_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# HEURISTIK 1: WALLET-ALTER
# ============================================================================
def calculate_wallet_age_score(wallet_data: WalletData) -> Tuple[float, str]:
    """
    Bewertet das Alter der Wallet.

    Logik:
    - Wallet älter als 2 Jahre: Score = 0 (sehr vertrauenswürdig)
    - Wallet älter als 1 Jahr: Score = 10 (vertrauenswürdig)
    - Wallet älter als 6 Monate: Score = 20 (ok)
    - Wallet älter als 3 Monate: Score = 40 (etwas verdächtig)
    - Wallet älter als 1 Monat: Score = 60 (verdächtig)
    - Wallet jünger als 1 Monat: Score = 90 (sehr verdächtig)
    - Keine Transaktionen: Score = 100 (komplett neu)

    Warum?
    - Scammer erstellen oft neue Wallets für jeden Betrug
    - Langlebige Wallets haben etablierte Reputation
    - Aber: Auch neue Wallets können legitim sein!

    Args:
        wallet_data: WalletData-Objekt

    Returns:
        Tuple (score, explanation)
    """
    age_days = wallet_data.get_wallet_age_days()

    # Keine Transaktionen = komplett neu
    if age_days is None or age_days == 0:
        return (100.0, "Wallet hat keine Transaktionshistorie (komplett neu)")

    # Berechne Score basierend auf Alter
    if age_days >= 730:  # 2+ Jahre
        score = 0.0
        explanation = f"Wallet ist {age_days} Tage alt (~{age_days // 365} Jahre) - sehr etabliert"

    elif age_days >= 365:  # 1-2 Jahre
        score = 10.0
        explanation = f"Wallet ist {age_days} Tage alt (~{age_days // 365} Jahr) - etabliert"

    elif age_days >= 180:  # 6-12 Monate
        score = 20.0
        explanation = f"Wallet ist {age_days} Tage alt (~{age_days // 30} Monate) - relativ etabliert"

    elif age_days >= 90:  # 3-6 Monate
        score = 40.0
        explanation = f"Wallet ist {age_days} Tage alt (~{age_days // 30} Monate) - mittel"

    elif age_days >= 30:  # 1-3 Monate
        score = 60.0
        explanation = f"Wallet ist {age_days} Tage alt (~{age_days // 30} Monate) - relativ neu"

    else:  # < 1 Monat
        score = 90.0
        explanation = f"Wallet ist nur {age_days} Tage alt - sehr neu!"

    logger.debug(f"Wallet-Alter Score: {score} ({explanation})")
    return (score, explanation)


# ============================================================================
# HEURISTIK 2: TRANSAKTIONSVOLUMEN
# ============================================================================
def calculate_transaction_volume_score(wallet_data: WalletData) -> Tuple[float, str]:
    """
    Bewertet die Anzahl der Transaktionen.

    Logik:
    - Zu wenige TXs (<5): Möglicherweise Test-Wallet oder Scam-Vorbereitung
    - Zu viele TXs (>1000): Könnte Bot oder Mixer sein
    - Sweet Spot (50-500): Normale User-Aktivität
    - Moderate Anzahl (5-50 oder 500-1000): Leicht erhöhtes Risiko

    Warum?
    - Normale User haben 50-500 Transaktionen
    - Scam-Wallets haben oft sehr wenige (<10) oder sehr viele (>1000)
    - Aber: Auch Power-User können >1000 TXs haben!

    Args:
        wallet_data: WalletData-Objekt

    Returns:
        Tuple (score, explanation)
    """
    tx_count = wallet_data.total_transactions

    if tx_count == 0:
        score = 100.0
        explanation = "Keine Transaktionen vorhanden"

    elif tx_count < 5:
        score = 80.0
        explanation = f"Nur {tx_count} Transaktionen - sehr wenig Aktivität"

    elif tx_count < 10:
        score = 60.0
        explanation = f"{tx_count} Transaktionen - wenig Aktivität"

    elif tx_count < 50:
        score = 30.0
        explanation = f"{tx_count} Transaktionen - moderate Aktivität"

    elif tx_count <= 500:
        score = 0.0
        explanation = f"{tx_count} Transaktionen - normale User-Aktivität"

    elif tx_count <= 1000:
        score = 30.0
        explanation = f"{tx_count} Transaktionen - hohe Aktivität"

    else:  # > 1000
        score = 60.0
        explanation = f"{tx_count} Transaktionen - sehr hohe Aktivität (möglicherweise Bot)"

    logger.debug(f"TX-Volumen Score: {score} ({explanation})")
    return (score, explanation)


# ============================================================================
# HEURISTIK 3: TOKEN-KONZENTRATION
# ============================================================================
def calculate_token_concentration_score(wallet_data: WalletData) -> Tuple[float, str]:
    """
    Bewertet die Verteilung der Assets.

    Logik:
    - Wenn >90% in einem Token: Score = 100 (sehr konzentriert)
    - Wenn >80% in einem Token: Score = 80 (stark konzentriert)
    - Wenn >60% in einem Token: Score = 50 (konzentriert)
    - Wenn <30% max. in einem Token: Score = 0 (gut diversifiziert)

    Warum?
    - Scammer halten oft nur einen Token (den sie gerade stehlen)
    - Normale User diversifizieren ihre Assets
    - Aber: Auch legitime User können fokussiert investieren!

    Args:
        wallet_data: WalletData-Objekt

    Returns:
        Tuple (score, explanation)
    """
    # Berechne Gesamt-Wert (ETH + Tokens)
    eth_balance_decimal = wallet_data.get_eth_balance_decimal()

    # Sammle alle Asset-Werte
    asset_values = {'ETH': eth_balance_decimal}

    for token in wallet_data.token_holdings:
        if token.usd_value and token.usd_value > 0:
            asset_values[token.token_symbol] = token.usd_value
        else:
            # Falls kein USD-Wert, nutze Token-Balance als Proxy
            asset_values[token.token_symbol] = token.get_balance_decimal()

    # Berechne Gesamt-Wert
    total_value = sum(asset_values.values())

    # Wenn kein Wert, Score = 0 (kann nicht beurteilen)
    if total_value == 0:
        return (0.0, "Keine Assets vorhanden - kann nicht beurteilen")

    # Finde höchste Konzentration
    max_asset = max(asset_values, key=asset_values.get)
    max_percentage = (asset_values[max_asset] / total_value) * 100

    # Berechne Score
    if max_percentage > 90:
        score = 100.0
        explanation = f"{max_percentage:.1f}% in {max_asset} - extrem konzentriert!"

    elif max_percentage > 80:
        score = 80.0
        explanation = f"{max_percentage:.1f}% in {max_asset} - stark konzentriert"

    elif max_percentage > 60:
        score = 50.0
        explanation = f"{max_percentage:.1f}% in {max_asset} - konzentriert"

    elif max_percentage > 40:
        score = 20.0
        explanation = f"{max_percentage:.1f}% in {max_asset} - leicht konzentriert"

    else:
        score = 0.0
        explanation = f"{max_percentage:.1f}% max. in einem Asset - gut diversifiziert"

    logger.debug(f"Token-Konzentration Score: {score} ({explanation})")
    return (score, explanation)


# ============================================================================
# HEURISTIK 4: SCAM-CONTRACT-INTERAKTION
# ============================================================================
def calculate_scam_interaction_score(wallet_data: WalletData) -> Tuple[float, str]:
    """
    Prüft Interaktionen mit bekannten Scam-Adressen.

    Logik:
    - Jede Interaktion mit Scam-Contract: +20 Score (max 100)
    - Viele Interaktionen = sehr verdächtig

    Warum?
    - Kontakt mit Scams ist starkes Warnsignal
    - Könnte Opfer oder Täter sein
    - Mehrere Interaktionen = wahrscheinlich Täter

    Args:
        wallet_data: WalletData-Objekt

    Returns:
        Tuple (score, explanation)
    """
    scam_manager = get_scam_manager()

    scam_interactions = []
    flagged_addresses = set()

    # Prüfe alle Transaktionen
    for tx in wallet_data.transactions:
        # Prüfe "to" Adresse
        if tx.to_address:
            score, reason = scam_manager.get_address_risk_score(tx.to_address)

            # Nur Scams (nicht Mixer), Score > 90
            if score >= 90 and tx.to_address.lower() not in flagged_addresses:
                flagged_addresses.add(tx.to_address.lower())
                scam_interactions.append({
                    'address': tx.to_address,
                    'score': score,
                    'reason': reason,
                    'tx_hash': tx.hash
                })

    # Berechne Gesamt-Score
    interaction_count = len(scam_interactions)

    if interaction_count == 0:
        score = 0.0
        explanation = "Keine Interaktionen mit bekannten Scam-Adressen"

    elif interaction_count == 1:
        score = 40.0
        explanation = f"1 Interaktion mit Scam-Adresse erkannt"

    elif interaction_count <= 3:
        score = 70.0
        explanation = f"{interaction_count} Interaktionen mit Scam-Adressen erkannt!"

    else:
        score = 100.0
        explanation = f"{interaction_count} Interaktionen mit Scam-Adressen erkannt - WARNUNG!"

    logger.debug(f"Scam-Interaktion Score: {score} ({explanation})")
    return (score, explanation)


# ============================================================================
# HEURISTIK 5: MIXER-NUTZUNG
# ============================================================================
def calculate_mixer_usage_score(wallet_data: WalletData) -> Tuple[float, str]:
    """
    Prüft Nutzung von Privacy-Mixern (Tornado Cash etc.).

    Logik:
    - Tornado Cash 100 ETH: Score = 90 (sehr hohes Risiko)
    - Tornado Cash 10 ETH: Score = 70
    - Tornado Cash 1 ETH: Score = 50
    - Tornado Cash 0.1 ETH: Score = 40
    - Andere Mixer: Score = 60

    Warum?
    - Mixer werden oft für Geldwäsche genutzt
    - Aber: Auch legitime Privacy-Gründe möglich!
    - Höhere Beträge = höheres Risiko

    Args:
        wallet_data: WalletData-Objekt

    Returns:
        Tuple (score, explanation)
    """
    scam_manager = get_scam_manager()

    mixer_interactions = []
    highest_mixer_score = 0

    # Prüfe alle Transaktionen
    for tx in wallet_data.transactions:
        if tx.to_address:
            if scam_manager.is_mixer_address(tx.to_address):
                score, reason = scam_manager.get_address_risk_score(tx.to_address)
                highest_mixer_score = max(highest_mixer_score, score)

                mixer_interactions.append({
                    'address': tx.to_address,
                    'score': score,
                    'reason': reason,
                    'value': tx.get_value_in_eth()
                })

    # Berechne Gesamt-Score
    if not mixer_interactions:
        score = 0.0
        explanation = "Keine Mixer-Nutzung erkannt"
    else:
        # Nutze höchsten Mixer-Score
        score = float(highest_mixer_score)
        mixer_count = len(mixer_interactions)
        explanation = f"{mixer_count} Mixer-Interaktion(en) erkannt (höchster Score: {score})"

    logger.debug(f"Mixer-Nutzung Score: {score} ({explanation})")
    return (score, explanation)


# ============================================================================
# HEURISTIK 6: INFLOW/OUTFLOW-MUSTER
# ============================================================================
def calculate_inflow_outflow_score(wallet_data: WalletData) -> Tuple[float, str]:
    """
    Analysiert Ein- und Auszahlungs-Muster.

    Logik:
    - Wenn >95% der Einzahlungen sofort wieder ausgezahlt: Score = 90
    - Wenn >80% ausgezahlt: Score = 60
    - Wenn Balance gehalten wird: Score = 0

    Warum?
    - Scammer leiten Gelder oft schnell durch (Tumbling)
    - Normale User halten Balance im Wallet
    - Aber: Auch Trader können schnell Geld bewegen!

    Args:
        wallet_data: WalletData-Objekt

    Returns:
        Tuple (score, explanation)
    """
    wallet_address = wallet_data.address.lower()

    total_inflow = Decimal(0)
    total_outflow = Decimal(0)

    # Berechne Ein- und Ausgänge
    for tx in wallet_data.transactions:
        value = Decimal(tx.value)

        # Eingehende Transaktion
        if tx.to_address and tx.to_address.lower() == wallet_address:
            total_inflow += value

        # Ausgehende Transaktion
        if tx.from_address and tx.from_address.lower() == wallet_address:
            total_outflow += value

    # Verhindere Division durch 0
    if total_inflow == 0:
        return (0.0, "Keine eingehenden Transaktionen - kann nicht beurteilen")

    # Berechne Outflow-Ratio
    outflow_ratio = float(total_outflow / total_inflow)

    # Berechne Score
    if outflow_ratio > 0.95:
        score = 90.0
        explanation = f"{outflow_ratio * 100:.1f}% der Einzahlungen wurden ausgezahlt - Durchleitungs-Muster!"

    elif outflow_ratio > 0.80:
        score = 60.0
        explanation = f"{outflow_ratio * 100:.1f}% der Einzahlungen wurden ausgezahlt - hohes Durchleitungs-Muster"

    elif outflow_ratio > 0.60:
        score = 30.0
        explanation = f"{outflow_ratio * 100:.1f}% der Einzahlungen wurden ausgezahlt - moderates Durchleitungs-Muster"

    else:
        score = 0.0
        explanation = f"{outflow_ratio * 100:.1f}% der Einzahlungen wurden ausgezahlt - normale Balance-Haltung"

    logger.debug(f"Inflow/Outflow Score: {score} ({explanation})")
    return (score, explanation)


# ============================================================================
# ALLE HEURISTIKEN AUSFÜHREN
# ============================================================================
def calculate_all_heuristics(wallet_data: WalletData) -> Dict:
    """
    Führt alle 6 Heuristiken aus.

    Args:
        wallet_data: WalletData-Objekt

    Returns:
        Dictionary mit allen Scores und Erklärungen
    """
    logger.info("🔍 Berechne alle Heuristiken...")

    results = {}

    # Heuristik 1: Wallet-Alter
    score, explanation = calculate_wallet_age_score(wallet_data)
    results['wallet_age'] = {'score': score, 'explanation': explanation}

    # Heuristik 2: Transaktionsvolumen
    score, explanation = calculate_transaction_volume_score(wallet_data)
    results['transaction_volume'] = {'score': score, 'explanation': explanation}

    # Heuristik 3: Token-Konzentration
    score, explanation = calculate_token_concentration_score(wallet_data)
    results['token_concentration'] = {'score': score, 'explanation': explanation}

    # Heuristik 4: Scam-Interaktion
    score, explanation = calculate_scam_interaction_score(wallet_data)
    results['scam_interaction'] = {'score': score, 'explanation': explanation}

    # Heuristik 5: Mixer-Nutzung
    score, explanation = calculate_mixer_usage_score(wallet_data)
    results['mixer_usage'] = {'score': score, 'explanation': explanation}

    # Heuristik 6: Inflow/Outflow
    score, explanation = calculate_inflow_outflow_score(wallet_data)
    results['inflow_outflow'] = {'score': score, 'explanation': explanation}

    logger.info("✅ Alle Heuristiken berechnet")
    return results


# ============================================================================
# BEISPIEL-VERWENDUNG
# ============================================================================
if __name__ == "__main__":
    # Dies würde ein echtes WalletData-Objekt benötigen
    print("Heuristiken-Modul geladen!")
    print("Verwende calculate_all_heuristics(wallet_data) um alle Scores zu berechnen")
