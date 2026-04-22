"""Environment-backed application settings loader with validation and startup fail-fast checks."""

import os
import sys
from pathlib import Path

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file, with validation.
    Critical settings are validated at startup, and any issues will cause the application to exit with an error message.
    """
    
    # --- Sensor settings ---
    DS18B20_DEVICE_ID: str = Field(
        ...,
        description="Linux 1-wire device identifier for the DS18B20 temperature sensor (for example: 28-xxxxxxxxxxxx).",
    )
    DS18B20_SAMPLING_INTERVAL_SECONDS: float = Field(
        2.0,
        description="Polling interval in seconds for DS18B20 reads.",
    )
    
    AM2302_CALIBRATION_OFFSET: float = Field(
        1.0,
        description="Calibration offset applied to AM2302 temperature measurements.",
    )
    AM2302_SAMPLING_INTERVAL_SECONDS: float = Field(
        2.0,
        description="Polling interval in seconds for AM2302 temperature/humidity reads.",
    )

    # --- Database ---
    DB_PATH: str = Field(
        ...,
        description="Absolute filesystem path to the SQLite database file used for persisted sensor readings.",
    )

    # --- Sampling logic ---
    THRESHOLD_DELTA_T_HIGH: float = Field(
        0.125,
        description="Minimum temperature change threshold (high-precision path) that triggers storing a new sample.",
    )
    THRESHOLD_DELTA_T_LOW: float = Field(
        0.3,
        description="Minimum temperature change threshold (low-precision path) that triggers storing a new sample.",
    )
    THRESHOLD_DELTA_RH: float = Field(
        1.0,
        description="Minimum relative-humidity delta that triggers storing a new sample.",
    )

    # --- Buffering and flushing ---
    BUFFER_MAX_READINGS: int = Field(
        10_000,
        description="In-memory buffer limit before back-pressure or forced flush behavior applies.",
    )
    FLUSH_EVERY_SECONDS: float = Field(
        300.0,
        description="Time-based flush interval in seconds for writing buffered readings to the database.",
    )
    FLUSH_EVERY_READINGS: int = Field(
        1_000,
        description="Count-based flush trigger: write buffer to database after this many new readings.",
    )
    RETENTION_INTERVAL_SECONDS: float = Field(
        3600.0,
        description="Interval in seconds for running the retention cleanup job.",
    )

    # --- Data retention ---
    RETENTION_HOURS: int = Field(
        24,
        description="Maximum age of stored readings in hours before they are deleted by retention cleanup.",
    )

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
