# ============================================================================
# SETUP.PY - Package-Installation und Konfiguration
# ============================================================================
#
# Was macht diese Datei?
# - Definiert Metadaten über unser Projekt (Name, Version, Autor)
# - Listet alle Dependencies auf
# - Ermöglicht Installation via "pip install -e ." (Development Mode)
#
# Vorteile von "pip install -e .":
# - Unser Package ist überall importierbar
# - Änderungen am Code sind sofort aktiv (kein Re-Install nötig)
# - Dependencies werden automatisch installiert
# ============================================================================

from setuptools import setup, find_packages

# Lies die README.md für die Long Description (wird auf PyPI angezeigt)
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Lies die Requirements aus der requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh
                   if line.strip() and not line.startswith("#")]

setup(
    # ========================================================================
    # PROJEKT-METADATEN
    # ========================================================================
    name="crypto-wallet-analyzer",  # Package-Name
    version="0.1.0",                # Aktuelle Version (Semantic Versioning)
    author="Your Name",             # Dein Name
    author_email="your.email@example.com",  # Deine E-Mail
    description="Ein Tool zur Analyse von Krypto-Wallets und Berechnung von Scam-Risiko-Scores",
    long_description=long_description,
    long_description_content_type="text/markdown",

    # ========================================================================
    # URLS und LINKS
    # ========================================================================
    url="https://github.com/yourusername/crypto-wallet-analyzer",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/crypto-wallet-analyzer/issues",
        "Documentation": "https://github.com/yourusername/crypto-wallet-analyzer/blob/main/README.md",
    },

    # ========================================================================
    # PACKAGE-KONFIGURATION
    # ========================================================================
    # find_packages(): Findet automatisch alle Python-Packages (Ordner mit __init__.py)
    packages=find_packages(),

    # Python-Version Requirement
    python_requires=">=3.9",

    # Dependencies (aus requirements.txt)
    install_requires=requirements,

    # ========================================================================
    # KLASSIFIKATOREN (für PyPI)
    # ========================================================================
    # Diese Tags helfen Nutzern, das Package zu finden
    classifiers=[
        "Development Status :: 3 - Alpha",  # Alpha = noch in Entwicklung
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],

    # ========================================================================
    # ENTRY POINTS (CLI-Befehle)
    # ========================================================================
    # Erstellt ausführbare Befehle, die nach Installation verfügbar sind
    # Beispiel: "crypto-analyze" im Terminal aufrufen
    entry_points={
        "console_scripts": [
            # Befehl: crypto-analyze
            # Führt aus: src.cli.main:main() Funktion
            "crypto-analyze=src.cli.main:main",
        ],
    },

    # ========================================================================
    # ZUSÄTZLICHE DATEIEN
    # ========================================================================
    # Include non-Python files (wie JSON-Daten)
    include_package_data=True,
    package_data={
        # Inkludiere alle .json Dateien im data/ Ordner
        "": ["data/*.json"],
    },

    # ========================================================================
    # KEYWORDS (für Suche)
    # ========================================================================
    keywords="ethereum blockchain wallet analysis scam-detection crypto security",

    # ========================================================================
    # LICENSE
    # ========================================================================
    license="MIT",
)
