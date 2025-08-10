# config/core/settings.py

import os

ENVIRONMENT = os.getenv("APP_ENV", "development")  # "production" | "staging" | "development"
DEBUG       = ENVIRONMENT != "production"

# Example feature flag
FEATURE_X_ENABLED = os.getenv("FEATURE_X", "false").lower() == "true"