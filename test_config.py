"""
Configuration testing and validation for Zotero Knowledge Base system.

This file contains functions to test and validate the configuration
settings defined in config.py.
"""

import os
from config import (
    ZOTERO_DATA_DIR, ZOTERO_DB_PATH, 
    MINERU_DIR, MAGIC_PDF_CONFIG_FILENAME,
    DEFAULT_ENCODING, STORAGE_DIR_NAME
)


def validate_paths():
    """Validate that essential paths exist."""
    validation_results = {}

    # Check Zotero data directory
    validation_results['zotero_data_dir'] = os.path.exists(ZOTERO_DATA_DIR)
       
    # Check Zotero database
    validation_results['zotero_db'] = os.path.exists(ZOTERO_DB_PATH)
    
    # Check Zotero storage directory
    validation_results['zotero_storage_dir'] = os.path.exists(os.path.join(ZOTERO_DATA_DIR, STORAGE_DIR_NAME))

    # Check MinerU config file
    validation_results['mineru_config_file'] = os.path.exists(os.path.join(MINERU_DIR, MAGIC_PDF_CONFIG_FILENAME))
    
    return validation_results


def print_config_summary():
    """Print a summary of the current configuration."""
    print("Zotero Knowledge Base Configuration")
    print("=" * 80)
    print(f"Zotero Data Directory: {ZOTERO_DATA_DIR}")
    print(f"Zotero Database: {ZOTERO_DB_PATH}")
    print(f"MinerU Config Directory: {MINERU_DIR}")
    print(f"Default Encoding: {DEFAULT_ENCODING}")
    print()
    
    # Validate paths
    validation = validate_paths()
    print("Path Validation:")
    for path_name, exists in validation.items():
        status = "✅ EXISTS" if exists else "❌ NOT FOUND"
        print(f"  {path_name}: {status}")


if __name__ == "__main__":
    print_config_summary()
