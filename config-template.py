"""
Configuration file for Zotero Knowledge Base system.

This file contains all hardcoded paths, directories, file extensions, 
and other configuration constants used across the Zotero knowledge base scripts.
"""

# ================================
# CORE DIRECTORIES AND PATHS
# ================================

# Zotero data directory
ZOTERO_DATA_DIR = "D:\\AppData\\ZoteroData\\"

# Zotero database file
ZOTERO_DB_PATH = "D:\\AppData\\ZoteroData\\zotero.sqlite"

# Zotero storage directory name
STORAGE_DIR_NAME = "storage"

# MinerU configuration directory
MINERU_DIR = "D:\\Files\\Coding\\Python\\mineru"

# Magic PDF configuration filename
MAGIC_PDF_CONFIG_FILENAME = "magic-pdf.json"

# ================================
# OUTPUT DIRECTORY AND FILE NAMES
# ================================

# Metadata CSV filename
METADATA_CSV_FILENAME = "zotero_metadata.csv"

# Annotations CSV filename
ANNOTATIONS_CSV_FILENAME = "zotero_annotations.csv"

# Default batch output directory
DEFAULT_BATCH_OUTPUT_DIR = "fulltexts"

# Images subdirectory name
IMAGES_DIR_NAME = "images"

# Default annotations output directory 
DEFAULT_ANNOTATIONS_OUTPUT_DIR = "annotations"

# ================================
# OTHER CONFIGURATION
# ================================

# Default text encoding for file operations
DEFAULT_ENCODING = "utf-8"

# Default maximum number of pages to process
DEFAULT_MAX_PAGES = 100