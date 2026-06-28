# CivicFlow Business logic package (Gemini multi-agent flow, Firestore interaction)
# analytics_service is imported here to ensure the singleton is available via
# `from app.services import analytics_service` in routes.py.
from app.services import analytics_service  # noqa: F401
