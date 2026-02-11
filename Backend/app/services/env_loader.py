"""Environment-backed application settings loader with validation and startup fail-fast checks."""

import os
import sys
from pathlib import Path

from pydantic import ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # TODO: CLARIFY AND DOCUMENT EACH SETTING BELOW
    """
    Application settings loaded from environment variables or .env file, with validation.
    Critical settings are validated at startup, and any issues will cause the application to exit with an error message.
    """
    
    # --- Sensor settings ---
    DS18B20_DEVICE_ID: str
    DS18B20_SAMPLING_INTERVAL_SECONDS: float = 2.0
    
    AM2302_CALIBRATION_OFFSET: float = 1.0
    AM2302_SAMPLING_INTERVAL_SECONDS: float = 2.0

    # --- Database ---
    DB_PATH: str

    # --- Sampling logic ---
    THRESHOLD_DELTA_T_HIGH: float = 0.02
    THRESHOLD_DELTA_T_LOW: float = 0.1
    THRESHOLD_DELTA_RH: float = 0.1

    # --- Buffering and flushing ---
    BUFFER_MAX_READINGS: int = 10_000
    FLUSH_EVERY_SECONDS: float = 300.0
    FLUSH_EVERY_READINGS: int = 1_000
    RETENTION_INTERVAL_SECONDS: float = 3600.0

    # --- Data retention ---
    RETENTION_HOURS: int = 24

    # --- Pydantic configuration ---
    model_config = SettingsConfigDict(       
        env_file=os.path.join(os.path.dirname(__file__), '../../airmetrics.env'),
        env_file_encoding='utf-8',
        env_file_required=True,
        extra='ignore'
    )

    @field_validator('DB_PATH')
    @classmethod
    def check_db_folder_exists(cls, db_path: str) -> str:
        db_folder = Path(db_path).parent
        
        if not db_folder.exists():
            raise ValueError(f"Database folder does not exist: {db_folder}")
        
        if not db_folder.is_dir():
            raise ValueError(f"Database path is not a directory: {db_folder}")
        
        if not db_folder.is_absolute():
            raise ValueError(f"Database path must be absolute: {db_path}")

        if not os.access(db_folder, os.W_OK):
            raise ValueError(f"Database folder is not writable: {db_folder}")

        return db_path


try:
    # Try to load and validate the configuration
    settings = Settings()
    print("Config loaded successfully")

except ValidationError as e:
    print("Critical configuration error:")
    # print detailed validation errors
    for error in e.errors():
        loc = error['loc'][0]
        msg = error['msg']
        print(f"   - {loc}: {msg}")
    sys.exit(1)

except Exception as e:
    print(f"Unexpected system error: {e}")
    sys.exit(1)
