# ============================================================================
# SCAM_LISTS.PY - Laden und Verarbeiten von Scam-Adressen
# ============================================================================
#
# Was macht dieses Modul?
# - Lädt die scam_addresses.json Datei
# - Stellt Funktionen bereit um Adressen zu prüfen
# - Berechnet Risiko-Scores basierend auf Address-Typ
#
# Verwendung:
#     from analysis.scam_lists import is_scam_address, get_address_risk_score
#     if is_scam_address("0x123..."):
#         print("WARNUNG: Scam-Adresse erkannt!")
# ============================================================================

import json
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# SCAM LIST MANAGER KLASSE
# ============================================================================
class ScamListManager:
    """
    Verwaltet Scam-Adressen-Listen und Risiko-Bewertungen.
    """

    def __init__(self, data_file: Optional[str] = None):
        """
        Initialisiert Manager und lädt Scam-Daten.

        Args:
            data_file: Pfad zur scam_addresses.json (optional)
        """
        # Finde data_file automatisch wenn nicht gegeben
        if not data_file:
            # Gehe vom aktuellen Modul-Pfad aus
            current_dir = Path(__file__).parent.parent.parent
            data_file = current_dir / "data" / "scam_addresses.json"

        self.data_file = data_file
        self.data = self._load_scam_data()

        # Erstelle schnelle Lookup-Sets
        self._build_lookup_tables()

    def _load_scam_data(self) -> Dict:
        """
        Lädt Scam-Daten aus JSON-Datei.

        Returns:
            Dictionary mit allen Scam-Daten
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"✅ Scam-Daten geladen von {self.data_file}")
                return data

        except FileNotFoundError:
            logger.error(f"❌ Scam-Datei nicht gefunden: {self.data_file}")
            # Gebe leere Struktur zurück
            return {
                "scam_contracts": {},
                "mixer_addresses": {},
                "suspicious_patterns": {},
                "whitelisted_contracts": {},
                "risk_scoring_weights": {}
            }

        except json.JSONDecodeError as e:
            logger.error(f"❌ Fehler beim Parsen der Scam-Datei: {e}")
            return {}

    def _build_lookup_tables(self):
        """
        Erstellt schnelle Lookup-Tabellen für Adress-Suche.

        Sets sind schneller als Listen für 'in' Checks:
        - List: O(n) - muss jedes Element prüfen
        - Set: O(1) - direkter Hash-Lookup
        """
        # Normalisiere alle Adressen zu lowercase für case-insensitive Vergleich
        self.scam_addresses = set()
        self.mixer_addresses = set()
        self.whitelisted_addresses = set()

        # Sammle alle Scam-Contract-Adressen
        scam_contracts = self.data.get("scam_contracts", {})
        for category in scam_contracts.values():
            if isinstance(category, list):
                for item in category:
                    if isinstance(item, dict) and 'address' in item:
                        self.scam_addresses.add(item['address'].lower())

        # Sammle alle Mixer-Adressen
        mixer_addresses = self.data.get("mixer_addresses", {})
        for category in mixer_addresses.values():
            if isinstance(category, list):
                for item in category:
                    if isinstance(item, dict) and 'address' in item:
                        self.mixer_addresses.add(item['address'].lower())

        # Sammle Burn-Adressen (auch verdächtig)
        burn_addresses = self.data.get("suspicious_patterns", {}).get("burn_addresses", [])
        for addr in burn_addresses:
            self.scam_addresses.add(addr.lower())

        # Sammle Whitelisted-Adressen
        whitelisted = self.data.get("whitelisted_contracts", {})
        for category in whitelisted.values():
            if isinstance(category, list):
                for item in category:
                    if isinstance(item, dict) and 'address' in item:
                        self.whitelisted_addresses.add(item['address'].lower())

        logger.info(f"   📊 {len(self.scam_addresses)} Scam-Adressen geladen")
        logger.info(f"   🌪️  {len(self.mixer_addresses)} Mixer-Adressen geladen")
        logger.info(f"   ✅ {len(self.whitelisted_addresses)} Whitelisted-Adressen geladen")

    # ========================================================================
    # ADRESS-PRÜFUNG
    # ========================================================================
    def is_scam_address(self, address: str) -> bool:
        """
        Prüft ob eine Adresse als Scam bekannt ist.

        Args:
            address: Ethereum-Adresse

        Returns:
            True wenn Scam, False sonst
        """
        return address.lower() in self.scam_addresses

    def is_mixer_address(self, address: str) -> bool:
        """
        Prüft ob eine Adresse ein Privacy-Mixer ist.

        Args:
            address: Ethereum-Adresse

        Returns:
            True wenn Mixer, False sonst
        """
        return address.lower() in self.mixer_addresses

    def is_whitelisted(self, address: str) -> bool:
        """
        Prüft ob eine Adresse whitelisted (vertrauenswürdig) ist.

        Args:
            address: Ethereum-Adresse

        Returns:
            True wenn whitelisted, False sonst
        """
        return address.lower() in self.whitelisted_addresses

    # ========================================================================
    # RISIKO-BEWERTUNG
    # ========================================================================
    def get_address_risk_score(self, address: str) -> Tuple[int, str]:
        """
        Berechnet Risiko-Score für eine Adresse.

        Args:
            address: Ethereum-Adresse

        Returns:
            Tuple (score, reason)
            - score: 0-100 (0 = sicher, 100 = sehr riskant)
            - reason: Beschreibung warum
        """
        addr_lower = address.lower()

        # Whitelisted = kein Risiko
        if addr_lower in self.whitelisted_addresses:
            return (0, "Whitelisted (vertrauenswürdige Adresse)")

        # Scam-Adresse = maximales Risiko
        if addr_lower in self.scam_addresses:
            return (100, "WARNUNG: Bekannte Scam-Adresse!")

        # Mixer = mittleres Risiko
        if addr_lower in self.mixer_addresses:
            # Finde spezifischen Mixer für genauen Score
            weights = self.data.get("risk_scoring_weights", {})

            # Prüfe ob es Tornado Cash ist und welche Größe
            mixer_data = self._get_mixer_details(address)
            if mixer_data:
                if "100 ETH" in mixer_data.get("name", ""):
                    return (weights.get("tornado_cash_100eth", 90),
                           "Tornado Cash 100 ETH (hohes Risiko)")
                elif "10 ETH" in mixer_data.get("name", ""):
                    return (weights.get("tornado_cash_10eth", 70),
                           "Tornado Cash 10 ETH (erhöhtes Risiko)")
                elif "1 ETH" in mixer_data.get("name", ""):
                    return (weights.get("tornado_cash_1eth", 50),
                           "Tornado Cash 1 ETH (mittleres Risiko)")
                elif "0.1 ETH" in mixer_data.get("name", ""):
                    return (weights.get("tornado_cash_0.1eth", 40),
                           "Tornado Cash 0.1 ETH (mittleres Risiko)")

            # Generischer Mixer
            return (weights.get("other_mixer", 60), "Privacy Mixer (erhöhtes Risiko)")

        # Unbekannte Adresse = kein zusätzliches Risiko
        return (0, "Unbekannte Adresse (kein spezifisches Risiko)")

    def _get_mixer_details(self, address: str) -> Optional[Dict]:
        """
        Holt Details zu einer Mixer-Adresse.

        Args:
            address: Ethereum-Adresse

        Returns:
            Dictionary mit Mixer-Details oder None
        """
        addr_lower = address.lower()
        mixer_addresses = self.data.get("mixer_addresses", {})

        for category in mixer_addresses.values():
            if isinstance(category, list):
                for item in category:
                    if isinstance(item, dict) and item.get('address', '').lower() == addr_lower:
                        return item

        return None

    # ========================================================================
    # BATCH-ANALYSE
    # ========================================================================
    def analyze_addresses(self, addresses: List[str]) -> Dict:
        """
        Analysiert mehrere Adressen gleichzeitig.

        Args:
            addresses: Liste von Ethereum-Adressen

        Returns:
            Dictionary mit Analyse-Ergebnissen
        """
        results = {
            'total_addresses': len(addresses),
            'scam_count': 0,
            'mixer_count': 0,
            'whitelisted_count': 0,
            'unknown_count': 0,
            'highest_risk_score': 0,
            'flagged_addresses': []
        }

        for addr in addresses:
            if self.is_whitelisted(addr):
                results['whitelisted_count'] += 1
            elif self.is_scam_address(addr):
                results['scam_count'] += 1
                score, reason = self.get_address_risk_score(addr)
                results['flagged_addresses'].append({
                    'address': addr,
                    'score': score,
                    'reason': reason
                })
                results['highest_risk_score'] = max(results['highest_risk_score'], score)
            elif self.is_mixer_address(addr):
                results['mixer_count'] += 1
                score, reason = self.get_address_risk_score(addr)
                results['flagged_addresses'].append({
                    'address': addr,
                    'score': score,
                    'reason': reason
                })
                results['highest_risk_score'] = max(results['highest_risk_score'], score)
            else:
                results['unknown_count'] += 1

        return results


# ============================================================================
# GLOBAL SINGLETON INSTANCE
# ============================================================================
# Erstelle eine globale Instanz für einfache Verwendung
_scam_manager = None

def get_scam_manager() -> ScamListManager:
    """
    Gibt die globale ScamListManager-Instanz zurück.
    Erstellt sie beim ersten Aufruf (Singleton Pattern).

    Returns:
        ScamListManager Instanz
    """
    global _scam_manager
    if _scam_manager is None:
        _scam_manager = ScamListManager()
    return _scam_manager


# ============================================================================
# CONVENIENCE-FUNKTIONEN
# ============================================================================
def is_scam_address(address: str) -> bool:
    """Convenience-Funktion für schnellen Scam-Check"""
    return get_scam_manager().is_scam_address(address)


def is_mixer_address(address: str) -> bool:
    """Convenience-Funktion für schnellen Mixer-Check"""
    return get_scam_manager().is_mixer_address(address)


def get_address_risk_score(address: str) -> Tuple[int, str]:
    """Convenience-Funktion für Risiko-Score"""
    return get_scam_manager().get_address_risk_score(address)


# ============================================================================
# BEISPIEL-VERWENDUNG
# ============================================================================
if __name__ == "__main__":
    # Manager erstellen
    manager = ScamListManager()

    # Test-Adressen
    test_addresses = [
        "0x12D66f87A04A9E220743712cE6d9bB1B5616B8Fc",  # Tornado Cash
        "0x0000000000000000000000000000000000000000",  # Null Address
        "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",  # Uniswap (whitelisted)
    ]

    print("\n🔍 ADRESS-ANALYSE\n")
    print("=" * 60)

    for addr in test_addresses:
        score, reason = manager.get_address_risk_score(addr)
        print(f"\nAdresse: {addr[:20]}...")
        print(f"Score: {score}/100")
        print(f"Grund: {reason}")

    # Batch-Analyse
    print("\n" + "=" * 60)
    print("\n📊 BATCH-ANALYSE\n")
    results = manager.analyze_addresses(test_addresses)
    print(f"Gesamt: {results['total_addresses']}")
    print(f"Scams: {results['scam_count']}")
    print(f"Mixer: {results['mixer_count']}")
    print(f"Whitelisted: {results['whitelisted_count']}")
    print(f"Höchster Risiko-Score: {results['highest_risk_score']}")
