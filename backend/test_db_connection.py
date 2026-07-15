#!/usr/bin/env python3
"""Local test script for Cloud SQL connection."""

import os
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import get_settings
from app.core.database import test_cloud_sql_connection

if __name__ == "__main__":
    settings = get_settings()

    print("=" * 60)
    print("Cloud SQL Connection Test")
    print("=" * 60)
    print()

    print("Configuration:")
    print(f"  DATABASE_URL: {settings.database_url[:50] if settings.database_url else 'Not set'}...")
    print(f"  CLOUD_SQL_HOST: {settings.cloud_sql_host}")
    print(f"  CLOUD_SQL_DB: {settings.cloud_sql_db}")
    print(f"  CLOUD_SQL_USER: {settings.cloud_sql_user}")
    print(f"  CLOUD_SQL_PASSWORD: {'***' if settings.cloud_sql_password else 'Not set'}")
    print()

    result = test_cloud_sql_connection(settings)

    print("Test Result:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    print()

    if result["status"] == "ok":
        print("✅ Connection successful!")
        sys.exit(0)
    else:
        print("❌ Connection failed!")
        sys.exit(1)
