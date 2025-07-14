# EnergyOpti-Pro

SaaS for energy optimization.

## Setup
1. pip install -r requirements.txt
2. Set .env
3. Alembic: alembic init -t async alembic, edit env.py, revision & upgrade.
4. Seed: python scripts/seed_initial_data.py
5. Run: uvicorn main:app --reload
6. Test: pytest tests/
7. Quality: python scripts/run_quality_checks.py
8. Deploy: docker-compose up -d