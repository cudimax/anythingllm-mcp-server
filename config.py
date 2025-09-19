#!/usr/bin/env python3
"""
Configuration file for Enhanced Invoice Metadata Extractor
Import this module to access configuration settings.

Usage:
    from config import VLLM_CONFIG, PROCESSING_CONFIG
"""

import os
from pathlib import Path

# vLLM Configuration
VLLM_CONFIG = {
    "base_url": os.getenv("VLLM_URL", "http://10.152.220.10:9901/v1"),
    "timeout": int(os.getenv("VLLM_TIMEOUT", "30")),
    "max_retries": int(os.getenv("VLLM_MAX_RETRIES", "3")),
    "temperature": float(os.getenv("VLLM_TEMPERATURE", "0.1")),
    "max_tokens": int(os.getenv("VLLM_MAX_TOKENS", "1000")),
    "model": os.getenv("VLLM_MODEL", "default")  # Adjust based on your vLLM setup
}

# Processing Configuration
PROCESSING_CONFIG = {
    "content_truncate_length": int(os.getenv("CONTENT_TRUNCATE_LENGTH", "2000")),  # For ChromaDB storage
    "max_content_for_llm": int(os.getenv("MAX_CONTENT_FOR_LLM", "4000")),         # Max content sent to vLLM
    "batch_size": int(os.getenv("BATCH_SIZE", "10")),                            # Process in batches if needed
    "enable_parallel_processing": os.getenv("ENABLE_PARALLEL", "false").lower() == "true"
}

# Extraction Fields Configuration
EXTRACTION_FIELDS = {
    "required_fields": [
        "invoice_number", "invoice_date", "total_amount", "client_name"
    ],
    "optional_fields": [
        "due_date", "tax_amount", "customer_number", "reference", 
        "company_name", "payment_status", "currency", "line_items"
    ],
    "custom_fields": [
        "delivery_date", "purchase_order_number", "payment_terms",
        "billing_address", "shipping_address"
    ]
}

# Language and Locale Configuration
LOCALE_CONFIG = {
    "default_currency": os.getenv("DEFAULT_CURRENCY", "CHF"),
    "date_formats": {
        "german": ["%d.%m.%Y", "%d-%m-%Y"],
        "english": ["%m/%d/%Y", "%Y-%m-%d"],
        "iso": ["%Y-%m-%d"]
    },
    "currency_symbols": {
        "CHF": ["CHF", "Fr.", "Fr"],
        "EUR": ["EUR", "€", "Euro"],
        "USD": ["USD", "$", "Dollar"]
    }
}

# Output Configuration
OUTPUT_CONFIG = {
    "default_output_file": os.getenv("OUTPUT_FILE", "invoices_for_chromadb.json"),
    "backup_enabled": os.getenv("BACKUP_ENABLED", "true").lower() == "true",
    "export_formats": ["json", "csv"],  # Available: json, csv, xlsx
    "include_raw_content": os.getenv("INCLUDE_RAW_CONTENT", "true").lower() == "true",
    "include_extraction_metadata": os.getenv("INCLUDE_METADATA", "true").lower() == "true"
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),  # DEBUG, INFO, WARNING, ERROR
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_logging": os.getenv("FILE_LOGGING", "true").lower() == "true",
    "log_file": os.getenv("LOG_FILE", "invoice_extraction.log")
}

# Quality Control Configuration
QUALITY_CONFIG = {
    "min_confidence_score": float(os.getenv("MIN_CONFIDENCE", "0.5")),
    "enable_validation": os.getenv("ENABLE_VALIDATION", "true").lower() == "true",
    "flag_suspicious_amounts": os.getenv("FLAG_SUSPICIOUS", "true").lower() == "true",
    "max_amount_threshold": float(os.getenv("MAX_AMOUNT_THRESHOLD", "100000")),
    "enable_duplicate_detection": os.getenv("ENABLE_DUPLICATE_DETECTION", "true").lower() == "true"
}

# Directory Configurations
DIRECTORIES = {
    "invoices_dir": os.getenv("INVOICES_DIR", "/opt/rag-preprocessor/storage/documents/stepx"),
    "output_dir": os.getenv("OUTPUT_DIR", "./output"),
    "logs_dir": os.getenv("LOGS_DIR", "./logs"),
    "backup_dir": os.getenv("BACKUP_DIR", "./backups")
}

# Ensure directories exist
for dir_path in DIRECTORIES.values():
    Path(dir_path).mkdir(parents=True, exist_ok=True)

def get_config(section=None):
    """Get configuration section or all config"""
    config_map = {
        'vllm': VLLM_CONFIG,
        'processing': PROCESSING_CONFIG,
        'extraction': EXTRACTION_FIELDS,
        'locale': LOCALE_CONFIG,
        'output': OUTPUT_CONFIG,
        'logging': LOGGING_CONFIG,
        'quality': QUALITY_CONFIG,
        'directories': DIRECTORIES
    }
    
    if section:
        return config_map.get(section.lower())
    return config_map

def update_config(section, key, value):
    """Update configuration value dynamically"""
    config_map = {
        'vllm': VLLM_CONFIG,
        'processing': PROCESSING_CONFIG,
        'locale': LOCALE_CONFIG,
        'output': OUTPUT_CONFIG,
        'logging': LOGGING_CONFIG,
        'quality': QUALITY_CONFIG,
        'directories': DIRECTORIES
    }
    
    if section.lower() in config_map and key in config_map[section.lower()]:
        config_map[section.lower()][key] = value
        return True
    return False
