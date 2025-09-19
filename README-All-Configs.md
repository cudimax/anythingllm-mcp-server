# Configuration System for Enhanced Invoice Metadata Extractor

[![Configuration Formats](https://img.shields.io/badge/formats-YAML%20%7C%20JSON%20%7C%20Python-blue.svg)](https://github.com/your-repo)  
[![Environment Variables](https://img.shields.io/badge/env--vars-supported-green.svg)](https://github.com/your-repo)  
[![Auto Discovery](https://img.shields.io/badge/auto--discovery-enabled-brightgreen.svg)](https://github.com/your-repo)

A flexible, multi-format configuration system that supports YAML, JSON, and Python configuration files with automatic discovery, validation, and environment variable overrides.

## 📋 Table of Contents

- [Configuration Options](#configuration-options)
- [Recommendations](#recommendations)
- [Quick Start](#quick-start)
- [Configuration Formats](#configuration-formats)
- [Environment Variables](#environment-variables)
- [Advanced Usage](#advanced-usage)
- [Migration Tools](#migration-tools)
- [Integration Examples](#integration-examples)
- [Troubleshooting](#troubleshooting)

## 🎯 Configuration Options

The Enhanced Invoice Metadata Extractor supports four flexible configuration approaches:

### Option 1: YAML Configuration (`config.yaml`) ⭐ **Recommended**

**Best for:** End users, production deployments, teams

```yaml
# config.yaml
vllm:
  base_url: "http://10.152.220.10:9901/v1"
  timeout: 30
  temperature: 0.1

processing:
  batch_size: 10
  content_truncate_length: 2000

directories:
  invoices_dir: "/path/to/invoices"
  output_dir: "./output"
```

**Pros:**
- ✅ Human-readable with comments
- ✅ Hierarchical structure
- ✅ Supports complex data types
- ✅ Industry standard

**Cons:**
- ❌ Requires PyYAML dependency

### Option 2: JSON Configuration (`config.json`)

**Best for:** Simple deployments, Docker containers, APIs

```json
{
  "vllm": {
    "base_url": "http://10.152.220.10:9901/v1",
    "timeout": 30,
    "temperature": 0.1
  },
  "processing": {
    "batch_size": 10,
    "content_truncate_length": 2000
  }
}
```

**Pros:**
- ✅ Universal format
- ✅ No additional dependencies
- ✅ Lightweight

**Cons:**
- ❌ No comments support
- ❌ Less readable for complex configurations

### Option 3: Python Configuration (`config.py`)

**Best for:** Developers, complex logic, dynamic configurations

```python
# config.py
import os

VLLM_CONFIG = {
    "base_url": os.getenv("VLLM_URL", "http://10.152.220.10:9901/v1"),
    "timeout": int(os.getenv("VLLM_TIMEOUT", "30")),
    "temperature": float(os.getenv("VLLM_TEMPERATURE", "0.1"))
}

PROCESSING_CONFIG = {
    "batch_size": int(os.getenv("BATCH_SIZE", "10")),
    "content_truncate_length": 2000
}
```

**Pros:**
- ✅ Full programming capabilities
- ✅ Dynamic configuration logic
- ✅ Built-in environment variable support
- ✅ Type conversion

**Cons:**
- ❌ Requires Python knowledge
- ❌ Potential security risks if not managed properly

### Option 4: Flexible Configuration Loader (`config_loader.py`)

**Best for:** All scenarios - automatically detects and loads any format

```python
from config_loader import get_config, get_section

# Automatically finds and loads config
config = get_config()

# Load specific section
vllm_settings = get_section('vllm')
```

**Features:**
- 🔍 **Auto-discovery** of configuration files
- 🔄 **Multi-format support** (YAML, JSON, Python)
- ✅ **Validation** with helpful error messages
- 🔧 **Environment variable overrides**
- 💾 **Caching** for performance
- 🛡️ **Graceful fallbacks** to defaults

## 🎯 Recommendations

### By User Type

| User Type | Recommended Format | Reason |
|-----------|-------------------|--------|
| **End Users** | YAML (`config.yaml`) | Most readable, supports comments |
| **Developers** | Python (`config.py`) | Full control, environment integration |
| **DevOps/Production** | JSON (`config.json`) | Simple, no dependencies |
| **Teams/Collaboration** | YAML (`config.yaml`) | Easy to review and modify |

### By Environment

| Environment | Format | Benefits |
|-------------|--------|----------|
| **Development** | Python | Dynamic configuration, debugging |
| **Testing** | JSON/YAML | Version controlled, predictable |
| **Staging** | JSON | Simple, container-friendly |
| **Production** | JSON/YAML | Stable, well-documented |

### By Complexity

| Configuration Complexity | Format | Notes |
|--------------------------|--------|-------|
| **Simple** (< 20 settings) | JSON | Quick setup, minimal overhead |
| **Medium** (20-50 settings) | YAML | Good balance of readability/features |
| **Complex** (50+ settings) | Python | Logic, validation, dynamic values |

## ⚡ Quick Start

### 1. Create Your First Configuration

```bash
# Option A: Create default YAML config (recommended)
python config_migration.py create-default config.yaml

# Option B: Create default JSON config
python config_migration.py create-default config.json --format json

# Option C: Copy and modify existing template
cp examples/config.yaml.template config.yaml
```

### 2. Customize Your Settings

Edit the created configuration file:

```yaml
# config.yaml - Customize these values
vllm:
  base_url: "http://YOUR-VLLM-SERVER:9901/v1"  # ← Change this
  
directories:
  invoices_dir: "/path/to/your/invoices"       # ← Change this
  output_dir: "./results"                      # ← Change this

quality:
  min_confidence_score: 0.7                   # ← Adjust as needed
```

### 3. Test Your Configuration

```bash
# Validate configuration
python config_migration.py validate config.yaml

# Test vLLM connection
python usage_example.py test-connection --config config.yaml
```

### 4. Run the Extractor

```python
from config_loader import get_config
from invoice_metadata_extractor import EnhancedInvoiceMetadataExtractor

# Load configuration
config = get_config()

# Create extractor
extractor = EnhancedInvoiceMetadataExtractor(
    config['directories']['invoices_dir'],
    config['vllm']['base_url']
)

# Process invoices
results = extractor.save_chromadb_ready_data()
```

## 📄 Configuration Formats

### Complete YAML Configuration

```yaml
# config.yaml - Complete example with all options
---
# vLLM API Configuration
vllm:
  base_url: "http://10.152.220.10:9901/v1"
  timeout: 30
  max_retries: 3
  temperature: 0.1
  max_tokens: 1000
  model: "default"

# Document Processing
processing:
  content_truncate_length: 2000
  max_content_for_llm: 4000
  batch_size: 10
  enable_parallel_processing: false

# Field Extraction
extraction_fields:
  required_fields:
    - "invoice_number"
    - "invoice_date"
    - "total_amount"
    - "client_name"
  optional_fields:
    - "due_date"
    - "tax_amount"
    - "currency"
  custom_fields:
    - "delivery_date"
    - "purchase_order_number"

# Localization
locale:
  default_currency: "CHF"
  date_formats:
    german: ["%d.%m.%Y", "%d-%m-%Y"]
    english: ["%m/%d/%Y", "%Y-%m-%d"]

# Output Settings
output:
  default_output_file: "invoices_for_chromadb.json"
  backup_enabled: true
  export_formats: ["json", "csv"]

# Logging
logging:
  level: "INFO"
  file_logging: true
  log_file: "extraction.log"

# Quality Control
quality:
  min_confidence_score: 0.5
  enable_validation: true
  max_amount_threshold: 100000

# Directories
directories:
  invoices_dir: "/opt/rag-preprocessor/storage/documents/stepx"
  output_dir: "./output"
  logs_dir: "./logs"
  backup_dir: "./backups"
```

### Equivalent JSON Configuration

```json
{
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
    "enable_parallel_processing": false
  },
  "directories": {
    "invoices_dir": "/opt/rag-preprocessor/storage/documents/stepx",
    "output_dir": "./output",
    "logs_dir": "./logs",
    "backup_dir": "./backups"
  }
}
```

### Python Configuration with Logic

```python
# config.py - Dynamic configuration example
import os
from pathlib import Path

# Environment-based configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# vLLM Configuration - changes based on environment
if ENVIRONMENT == "production":
    VLLM_CONFIG = {
        "base_url": "http://production-vllm:9901/v1",
        "timeout": 60,
        "max_retries": 5,
        "temperature": 0.05  # More deterministic in production
    }
elif ENVIRONMENT == "testing":
    VLLM_CONFIG = {
        "base_url": "http://test-vllm:9901/v1",
        "timeout": 10,
        "max_retries": 1,
        "temperature": 0.1
    }
else:  # development
    VLLM_CONFIG = {
        "base_url": os.getenv("VLLM_URL", "http://localhost:9901/v1"),
        "timeout": 30,
        "max_retries": 3,
        "temperature": 0.2  # More creative in development
    }

# Dynamic batch size based on available memory
import psutil
memory_gb = psutil.virtual_memory().total / (1024**3)
batch_size = max(5, min(20, int(memory_gb / 4)))

PROCESSING_CONFIG = {
    "batch_size": batch_size,
    "content_truncate_length": 2000,
    "enable_parallel_processing": memory_gb > 16
}

# Ensure directories exist
base_dir = Path(__file__).parent
for dir_name in ['output', 'logs', 'backups']:
    (base_dir / dir_name).mkdir(exist_ok=True)

DIRECTORIES = {
    "invoices_dir": os.getenv("INVOICES_DIR", str(base_dir / "invoices")),
    "output_dir": str(base_dir / "output"),
    "logs_dir": str(base_dir / "logs"),
    "backup_dir": str(base_dir / "backups")
}
```

## 🌍 Environment Variables

All configuration values can be overridden using environment variables:

### Standard Environment Variables

```bash
# vLLM Configuration
export VLLM_URL="http://your-server:9901/v1"
export VLLM_TIMEOUT="45"
export VLLM_MODEL="llama-2-13b"
export VLLM_TEMPERATURE="0.1"
export VLLM_MAX_TOKENS="1500"

# Processing Configuration
export BATCH_SIZE="5"
export ENABLE_PARALLEL="true"

# Directory Configuration
export INVOICES_DIR="/data/invoices"
export OUTPUT_DIR="/data/output"

# Quality Control
export MIN_CONFIDENCE="0.7"
export MAX_AMOUNT_THRESHOLD="50000"

# Logging
export LOG_LEVEL="DEBUG"
export LOG_FILE="custom_extraction.log"
```

### Docker Environment Example

```dockerfile
# Dockerfile
FROM python:3.9

ENV VLLM_URL="http://vllm-service:9901/v1"
ENV BATCH_SIZE="10"
ENV LOG_LEVEL="INFO"
ENV INVOICES_DIR="/app/data/invoices"
ENV OUTPUT_DIR="/app/data/output"

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "invoice_metadata_extractor.py"]
```

### Environment Variable Priority

The system uses the following priority order:

1. **Environment Variables** (highest priority)
2. **Configuration File** (YAML/JSON/Python)
3. **Default Values** (lowest priority)

## 🔧 Advanced Usage

### Custom Configuration Loading

```python
from config_loader import ConfigurationLoader

# Create custom loader
loader = ConfigurationLoader()

# Load from specific file
config = loader.load_config("custom_config.yaml")

# Validate configuration
issues = loader.validate_config(config)
if issues:
    for issue in issues:
        print(f"❌ {issue}")

# Update configuration programmatically
loader.update_config('vllm', 'temperature', 0.05)

# Save modified configuration
loader.save_config(config, "updated_config.yaml", "yaml")
```

### Configuration Sections

```python
from config_loader import get_section

# Load specific sections
vllm_config = get_section('vllm')
processing_config = get_section('processing')
directories = get_section('directories')

# Use in your application
extractor = EnhancedInvoiceMetadataExtractor(
    directories['invoices_dir'],
    vllm_config['base_url']
)
```

### Dynamic Configuration Updates

```python
from config_loader import ConfigurationLoader

loader = ConfigurationLoader()
config = loader.load_config()

# Update based on runtime conditions
if some_condition:
    config['processing']['batch_size'] = 5
    config['vllm']['temperature'] = 0.05

# Apply changes
extractor.update_configuration(config)
```

## 🔄 Migration Tools

### Convert Between Formats

```bash
# Convert JSON to YAML
python config_migration.py migrate config.json config.yaml

# Convert YAML to JSON
python config_migration.py migrate config.yaml config.json

# Convert Python to YAML
python config_migration.py migrate config.py config.yaml
```

### Create Default Configurations

```bash
# Create YAML config with all options
python config_migration.py create-default complete_config.yaml

# Create minimal JSON config
python config_migration.py create-default minimal_config.json --format json
```

### Configuration Validation

```bash
# Validate single configuration
python config_migration.py validate config.yaml

# Compare configurations
python config_migration.py compare config1.yaml config2.json
```

### Migration Tool Features

- **Format Detection**: Automatically detects input format
- **Validation**: Checks configuration completeness and correctness
- **Comparison**: Shows differences between configuration files
- **Default Generation**: Creates complete default configurations

## 🔗 Integration Examples

### Basic Integration

```python
# basic_integration.py
from config_loader import get_config
from invoice_metadata_extractor import EnhancedInvoiceMetadataExtractor

# Load configuration (auto-discovers config file)
config = get_config()

# Extract directory and vLLM settings
invoices_dir = config['directories']['invoices_dir']
vllm_url = config['vllm']['base_url']

# Create and run extractor
extractor = EnhancedInvoiceMetradataExtractor(invoices_dir, vllm_url)
results = extractor.save_chromadb_ready_data()

print(f"✅ Processed {len(results)} invoices")
```

### Advanced Integration with Error Handling

```python
# advanced_integration.py
from config_loader import ConfigurationLoader, get_config
from invoice_metadata_extractor import EnhancedInvoiceMetadataExtractor
import logging
import sys

def main():
    try:
        # Load and validate configuration
        config = get_config()
        
        loader = ConfigurationLoader()
        issues = loader.validate_config(config)
        
        if issues:
            print("❌ Configuration issues found:")
            for issue in issues:
                print(f"  • {issue}")
            return False
        
        # Setup logging from configuration
        log_config = config.get('logging', {})
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format=log_config.get('format', '%(asctime)s - %(levelname)s - %(message)s'),
            filename=log_config.get('log_file') if log_config.get('file_logging') else None
        )
        
        # Create extractor with full configuration
        extractor = EnhancedInvoiceMetadataExtractor(
            config['directories']['invoices_dir'],
            config['vllm']['base_url']
        )
        
        # Apply processing configuration
        extractor.batch_size = config['processing']['batch_size']
        extractor.min_confidence = config['quality']['min_confidence_score']
        
        # Process invoices
        results = extractor.save_chromadb_ready_data(
            config['output']['default_output_file']
        )
        
        logging.info(f"Successfully processed {len(results)} invoices")
        return True
        
    except Exception as e:
        logging.error(f"Processing failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

### Flask API Integration

```python
# api_integration.py
from flask import Flask, request, jsonify
from config_loader import get_config
from invoice_metadata_extractor import EnhancedInvoiceMetadataExtractor

app = Flask(__name__)

# Load configuration once at startup
config = get_config()
extractor = EnhancedInvoiceMetadataExtractor(
    config['directories']['invoices_dir'],
    config['vllm']['base_url']
)

@app.route('/extract', methods=['POST'])
def extract_invoice():
    try:
        invoice_data = request.get_json()
        result = extractor.extract_metadata_from_invoice(invoice_data)
        
        return jsonify({
            'success': True,
            'data': result,
            'confidence': result['metadata'].get('extraction_confidence', 0)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/config', methods=['GET'])
def get_config_info():
    return jsonify({
        'vllm_url': config['vllm']['base_url'],
        'batch_size': config['processing']['batch_size'],
        'min_confidence': config['quality']['min_confidence_score']
    })

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=config.get('api', {}).get('port', 5000),
        debug=config.get('api', {}).get('debug', False)
    )
```

### Docker Compose Integration

```yaml
# docker-compose.yml
version: '3.8'

services:
  invoice-extractor:
    build: .
    environment:
      - VLLM_URL=http://vllm-service:9901/v1
      - BATCH_SIZE=5
      - LOG_LEVEL=INFO
      - INVOICES_DIR=/app/data/invoices
    volumes:
      - ./data/invoices:/app/data/invoices
      - ./data/output:/app/data/output
      - ./config.yaml:/app/config.yaml
    depends_on:
      - vllm-service

  vllm-service:
    image: vllm/vllm-openai:latest
    ports:
      - "9901:8000"
    command: ["--model", "meta-llama/Llama-2-13b-chat-hf"]
```

## 🔧 Troubleshooting

### Common Configuration Issues

#### 1. Configuration File Not Found
```
❌ No configuration file found, using defaults
```
**Solution:**
```bash
# Create default configuration
python config_migration.py create-default config.yaml

# Or specify config path explicitly
python your_script.py --config /path/to/config.yaml
```

#### 2. YAML Loading Error
```
❌ PyYAML is required to load YAML configs
```
**Solution:**
```bash
pip install PyYAML

# Or use JSON format instead
python config_migration.py migrate config.yaml config.json
```

#### 3. Invalid vLLM URL
```
❌ vLLM base_url is required
```
**Solution:**
```yaml
# In config.yaml
vllm:
  base_url: "http://10.152.220.10:9901/v1"  # Must include full URL with protocol
```

#### 4. Directory Permission Issues
```
❌ Permission denied: /path/to/invoices
```
**Solution:**
```bash
# Fix permissions
chmod 755 /path/to/invoices

# Or change directory in config
directories:
  invoices_dir: "/accessible/path/to/invoices"
```

#### 5. Environment Variable Override Not Working
```
❌ Environment variable not being used
```
**Solution:**
```bash
# Check variable name format (must match expected names)
export VLLM_URL="http://server:9901/v1"  # ✅ Correct
export vllm_url="http://server:9901/v1"  # ❌ Wrong case

# Verify variable is set
echo $VLLM_URL
```

### Configuration Debugging

```python
# debug_config.py
from config_loader import ConfigurationLoader
import os

def debug_configuration():
    loader = ConfigurationLoader()
    
    # Show configuration search paths
    config_file = loader._find_config_file()
    print(f"🔍 Found config file: {config_file}")
    
    # Load and display configuration
    config = loader.load_config()
    print(f"📋 Loaded configuration sections: {list(config.keys())}")
    
    # Show environment variable overrides
    env_vars = [k for k in os.environ.keys() if k.startswith(('VLLM_', 'BATCH_', 'LOG_'))]
    if env_vars:
        print(f"🌍 Environment overrides: {env_vars}")
    
    # Validate configuration
    issues = loader.validate_config(config)
    if issues:
        print(f"❌ Configuration issues:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("✅ Configuration is valid")

if __name__ == "__main__":
    debug_configuration()
```

### Performance Optimization

#### For Large Document Sets
```yaml
# config.yaml - Optimized for performance
processing:
  batch_size: 5              # Smaller batches
  enable_parallel_processing: false  # Avoid memory issues
  content_truncate_length: 1500     # Reduce content size

vllm:
  timeout: 60               # Longer timeout for complex docs
  max_tokens: 800           # Reduce token usage
```

#### For High Accuracy
```yaml
# config.yaml - Optimized for accuracy
vllm:
  temperature: 0.05         # More deterministic
  max_tokens: 1500          # Allow longer responses

quality:
  min_confidence_score: 0.8  # Higher threshold
  enable_validation: true    # Enable all checks
```

---

## 🤝 Contributing to Configuration

### Adding New Configuration Options

1. **Update Default Configuration** in `config_loader.py`
2. **Add Environment Variable Mapping** in `_apply_env_overrides()`
3. **Update Validation Rules** in `validate_config()`
4. **Add Documentation** in this README
5. **Update Example Configurations** in all formats

### Configuration Schema

Follow this structure for new configuration sections:

```yaml
new_section:
  # Required settings (no defaults)
  required_setting: "value"
  
  # Optional settings (with sensible defaults)
  optional_setting: true
  
  # Nested configuration for complex features
  subsection:
    nested_setting: 100
    list_setting:
      - "item1"
      - "item2"
```

---

Made with ❤️ for flexible invoice processing configuration

For questions about configuration, please [open an issue](https://github.com/your-repo/issues) with the `configuration` label.
