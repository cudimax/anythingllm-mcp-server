#!/usr/bin/env python3
"""
Flexible configuration loader for Enhanced Invoice Metadata Extractor
Supports both Python (.py) and JSON (.json) configuration files
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import importlib.util

logger = logging.getLogger(__name__)

class ConfigurationLoader:
    """Flexible configuration loader supporting multiple formats"""
    
    def __init__(self):
        self.config_cache = {}
        self.default_config = self._get_default_config()
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or return defaults"""
        
        # Try to find config file automatically if not provided
        if not config_path:
            config_path = self._find_config_file()
        
        if not config_path:
            logger.info("No configuration file found, using defaults")
            return self.default_config
        
        # Check cache
        if config_path in self.config_cache:
            return self.config_cache[config_path]
        
        config_path = Path(config_path)
        
        try:
            if config_path.suffix.lower() == '.json':
                config = self._load_json_config(config_path)
            elif config_path.suffix.lower() == '.py':
                config = self._load_python_config(config_path)
            else:
                logger.warning(f"Unsupported config format: {config_path.suffix}")
                config = self.default_config
            
            # Merge with defaults to ensure all keys exist
            config = self._merge_with_defaults(config)
            
            # Apply environment variable overrides
            config = self._apply_env_overrides(config)
            
            # Cache the loaded config
            self.config_cache[str(config_path)] = config
            
            logger.info(f"Configuration loaded from: {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {e}")
            logger.info("Falling back to default configuration")
            return self.default_config
    
    def _find_config_file(self) -> Optional[str]:
        """Automatically find configuration file"""
        possible_configs = [
            "config.json",
            "config.py", 
            "invoice_extractor_config.json",
            "invoice_extractor_config.py",
            os.path.expanduser("~/.invoice_extractor/config.json"),
            "/etc/invoice_extractor/config.json"
        ]
        
        for config_file in possible_configs:
            if os.path.exists(config_file):
                return config_file
        
        return None
    
    def _load_json_config(self, config_path: Path) -> Dict[str, Any]:
        """Load JSON configuration file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Remove comment fields (fields starting with _)
        config = self._clean_json_comments(config)
        return config
    
    def _load_python_config(self, config_path: Path) -> Dict[str, Any]:
        """Load Python configuration file"""
        spec = importlib.util.spec_from_file_location("config", config_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        
        # Extract configuration dictionaries
        config = {}
        for attr_name in dir(config_module):
            if attr_name.endswith('_CONFIG') or attr_name in ['DIRECTORIES']:
                config[attr_name.lower().replace('_config', '')] = getattr(config_module, attr_name)
        
        return config
    
    def _clean_json_comments(self, obj: Any) -> Any:
        """Remove comment fields from JSON configuration"""
        if isinstance(obj, dict):
            return {k: self._clean_json_comments(v) for k, v in obj.items() 
                   if not k.startswith('_')}
        elif isinstance(obj, list):
            return [self._clean_json_comments(item) for item in obj]
        else:
            return obj
    
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults"""
        merged = self.default_config.copy()
        
        for section, values in config.items():
            if section in merged:
                if isinstance(values, dict) and isinstance(merged[section], dict):
                    merged[section].update(values)
                else:
                    merged[section] = values
            else:
                merged[section] = values
        
        return merged
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides"""
        env_mappings = {
            'VLLM_URL': ('vllm', 'base_url'),
            'VLLM_TIMEOUT': ('vllm', 'timeout'),
            'VLLM_MODEL': ('vllm', 'model'),
            'VLLM_TEMPERATURE': ('vllm', 'temperature'),
            'VLLM_MAX_TOKENS': ('vllm', 'max_tokens'),
            'BATCH_SIZE': ('processing', 'batch_size'),
            'LOG_LEVEL': ('logging', 'level'),
            'OUTPUT_FILE': ('output', 'default_output_file'),
            'INVOICES_DIR': ('directories', 'invoices_dir'),
            'MIN_CONFIDENCE': ('quality', 'min_confidence_score')
        }
        
        for env_var, (section, key) in env_mappings.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                
                # Type conversion
                if key in ['timeout', 'max_tokens', 'batch_size']:
                    value = int(value)
                elif key in ['temperature', 'min_confidence_score']:
                    value = float(value)
                elif key in ['enable_parallel_processing', 'backup_enabled']:
                    value = value.lower() == 'true'
                
                if section in config:
                    config[section][key] = value
                    logger.info(f"Environment override: {env_var} -> {section}.{key} = {value}")
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "vllm": {
                "base_url": "http://10.152.220.10:9901/v1",
                "timeout": 30,
                "max_retries": 3,
                "temperature": 0.1,
                "max_tokens": 1000,
                "model": "default"
            },
            "processing": {
                "content_truncate_length": 2000,
                "max_content_for_llm": 4000,
                "batch_size": 10,
                "enable_parallel_processing": False
            },
            "extraction_fields": {
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
            },
            "locale": {
                "default_currency": "CHF",
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
            },
            "output": {
                "default_output_file": "invoices_for_chromadb.json",
                "backup_enabled": True,
                "export_formats": ["json", "csv"],
                "include_raw_content": True,
                "include_extraction_metadata": True
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_logging": True,
                "log_file": "invoice_extraction.log"
            },
            "quality": {
                "min_confidence_score": 0.5,
                "enable_validation": True,
                "flag_suspicious_amounts": True,
                "max_amount_threshold": 100000,
                "enable_duplicate_detection": True
            },
            "directories": {
                "invoices_dir": "/opt/rag-preprocessor/storage/documents/stepx",
                "output_dir": "./output",
                "logs_dir": "./logs",
                "backup_dir": "./backups"
            }
        }
    
    def save_config(self, config: Dict[str, Any], output_path: str, format_type: str = "json"):
        """Save configuration to file"""
        output_path = Path(output_path)
        
        try:
            if format_type.lower() == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported save format: {format_type}")
            
            logger.info(f"Configuration saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving config to {output_path}: {e}")
    
    def validate_config(self, config: Dict[str, Any]) -> list:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check required sections
        required_sections = ['vllm', 'processing', 'output', 'directories']
        for section in required_sections:
            if section not in config:
                issues.append(f"Missing required section: {section}")
        
        # Validate vLLM configuration
        if 'vllm' in config:
            vllm_config = config['vllm']
            if not vllm_config.get('base_url'):
                issues.append("vLLM base_url is required")
            if vllm_config.get('timeout', 0) <= 0:
                issues.append("vLLM timeout must be positive")
        
        # Validate directories
        if 'directories' in config:
            dirs = config['directories']
            if not dirs.get('invoices_dir'):
                issues.append("invoices_dir is required")
        
        # Validate quality settings
        if 'quality' in config:
            quality = config['quality']
            confidence = quality.get('min_confidence_score', 0)
            if not 0 <= confidence <= 1:
                issues.append("min_confidence_score must be between 0 and 1")
        
        return issues

# Global configuration loader instance
config_loader = ConfigurationLoader()

def get_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to get configuration"""
    return config_loader.load_config(config_path)

def get_section(section_name: str, config_path: Optional[str] = None) -> Dict[str, Any]:
    """Get specific configuration section"""
    config = get_config(config_path)
    return config.get(section_name, {})

# Example usage functions
if __name__ == "__main__":
    # Example: Load configuration
    config = get_config()
    print("Loaded configuration:")
    print(json.dumps(config, indent=2))
    
    # Example: Get specific section
    vllm_config = get_section('vllm')
    print(f"\nvLLM Configuration: {vllm_config}")
    
    # Example: Validate configuration
    issues = config_loader.validate_config(config)
    if issues:
        print(f"\nConfiguration issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ Configuration is valid")
