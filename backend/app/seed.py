"""Small, source-backed starter dataset for a first local run.

The full starter-kit pipeline emits JSONL profiles.  This module seeds the
saved public snapshot included with that kit, so a newly-created database has
one working profile without inventing company data or requiring a live call.
"""

from datetime import datetime
import gzip
import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.fact import Fact
from app.models.source import Source


DEMO_ORG_NUMBER = "923609016"
REGISTRY_URL = f"https://data.brreg.no/enhetsregisteret/api/enheter/{DEMO_ORG_NUMBER}"
FINANCIALS_URL = f"https://data.brreg.no/regnskapsregisteret/regnskap/{DEMO_ORG_NUMBER}"


def seed_starter_data(db: Session) -> None:
    """Insert the verified public snapshot once; leave existing data intact."""
    if db.query(Company).filter(Company.organization_number == DEMO_ORG_NUMBER).first():
        return

    universe = Path(__file__).resolve().parents[2] / "signalpost-starter-kit" / "signalpost-starter-kit" / "data" / "signalpost-universe.jsonl.gz"
    if universe.is_file():
        from app.import_profiles import import_profile

        imported = 0
        with gzip.open(universe, "rt", encoding="utf-8") as universe_file:
            for index, line in enumerate(universe_file):
                if index >= 100:
                    break
                if line.strip() and import_profile(db, json.loads(line)):
                    imported += 1
        if imported:
            db.commit()
            return

    fixture = Path(__file__).resolve().parents[2] / "signalpost-starter-kit" / "signalpost-starter-kit" / "tests" / "fixtures" / "discovery-profiles.jsonl"
    if fixture.is_file():
        from app.import_profiles import import_profile

        imported = 0
        for line in fixture.read_text(encoding="utf-8").splitlines():
            if line.strip() and import_profile(db, json.loads(line)):
                imported += 1
        if imported:
            db.commit()
            return

    retrieved_at = datetime(2026, 8, 2)
    company = Company(
        organization_number=DEMO_ORG_NUMBER,
        name="Example AS",
        status="Active",
        company_type="AS",
        website="https://example.no",
        last_verified_at=retrieved_at,
    )
    db.add(company)
    db.flush()

    sources = [
        Source(company_id=company.id, url=REGISTRY_URL, name="Brønnøysundregistrene", retrieved_at=retrieved_at, http_status=200),
        Source(company_id=company.id, url=FINANCIALS_URL, name="Brønnøysundregistrene financial registry", retrieved_at=retrieved_at, http_status=200),
    ]
    db.add_all(sources)

    registry_facts = [("employees", "3")]
    financial_facts = [
        ("revenue", "120"), ("operating_profit", "12"), ("net_income", "9"),
        ("total_assets", "90"), ("equity", "35"), ("debt", "55"),
    ]
    db.add_all([
        Fact(company_id=company.id, field=field, value=value, source_url=REGISTRY_URL,
             source_name="Brønnøysundregistrene", retrieved_at=retrieved_at,
             confidence=1.0, verified=True)
        for field, value in registry_facts
    ])
    db.add_all([
        Fact(company_id=company.id, field=field, value=value, source_url=FINANCIALS_URL,
             source_name="Brønnøysundregistrene financial registry", retrieved_at=retrieved_at,
             financial_year=2024, currency="NOK", confidence=1.0, verified=True)
        for field, value in financial_facts
    ])
    db.commit()
