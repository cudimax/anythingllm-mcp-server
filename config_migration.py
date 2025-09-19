#!/usr/bin/env python3
"""
Configuration Format Migration Tool
Convert between JSON, YAML, and Python configuration formats
"""

import argparse
import sys
from pathlib import Path

from config_loader import ConfigurationLoader

def migrate_config(input_file: str, output_file: str, output_format: str = None):
    """Migrate configuration from one format to another"""
    
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    if not input_path.exists():
        print(f"❌ Input file not found: {input_file}")
        return False
    
    # Auto-detect output format if not specified
    if not output_format:
        output_format = output_path.suffix.lstrip('.')
        if output_format == 'yml':
            output_format = 'yaml'
    
    print(f"🔄 Converting {input_file} → {output_file} ({output_format.upper()})")
    
    try:
        # Load configuration
        loader = ConfigurationLoader()
        config = loader.load_config(str(input_path))
        
        # Save in new format
        loader.save_config(config, str(output_path), output_format)
        
        print(f"✅ Migration successful!")
        print(f"📁 Output saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_default_config(output_file: str, format_type: str = "yaml"):
    """Create a default configuration file"""
    
    print(f"📝 Creating default configuration: {output_file} ({format_type.upper()})")
    
    try:
        loader = ConfigurationLoader()
        default_config = loader.default_config
        
        loader.save_config(default_config, output_file, format_type)
        
        print(f"✅ Default configuration created!")
        print(f"📁 File saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create default config: {e}")
        return False

def validate_config_file(config_file: str):
    """Validate a configuration file"""
    
    print(f"🔍 Validating configuration: {config_file}")
    
    try:
        loader = ConfigurationLoader()
        config = loader.load_config(config_file)
        
        issues = loader.validate_config(config)
        
        if not issues:
            print("✅ Configuration is valid!")
            
            # Show summary
            sections = list(config.keys())
            print(f"📋 Configuration sections: {', '.join(sections)}")
            
            if 'vllm' in config:
                vllm_url = config['vllm'].get('base_url', 'Not configured')
                print(f"🔗 vLLM URL: {vllm_url}")
            
            if 'directories' in config:
                invoices_dir = config['directories'].get('invoices_dir', 'Not configured')
                print(f"📂 Invoices directory: {invoices_dir}")
        
        else:
            print("❌ Configuration has issues:")
            for issue in issues:
                print(f"  • {issue}")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

def compare_configs(config1: str, config2: str):
    """Compare two configuration files"""
    
    print(f"🔍 Comparing configurations:")
    print(f"  File 1: {config1}")
    print(f"  File 2: {config2}")
    
    try:
        loader = ConfigurationLoader()
        
        conf1 = loader.load_config(config1)
        conf2 = loader.load_config(config2)
        
        differences = []
        all_keys = set()
        
        def flatten_dict(d, prefix=''):
            """Flatten nested dictionary for comparison"""
            items = []
            for k, v in d.items():
                new_key = f"{prefix}.{k}" if prefix else k
                all_keys.add(new_key)
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key))
                else:
                    items.append((new_key, v))
            return items
        
        flat1 = dict(flatten_dict(conf1))
        flat2 = dict(flatten_dict(conf2))
        
        # Find differences
        for key in all_keys:
            val1 = flat1.get(key, '<missing>')
            val2 = flat2.get(key, '<missing>')
            
            if val1 != val2:
                differences.append((key, val1, val2))
        
        if not differences:
            print("✅ Configurations are identical!")
        else:
            print(f"❗ Found {len(differences)} differences:")
            for key, val1, val2 in differences:
                print(f"  {key}:")
                print(f"    File 1: {val1}")
                print(f"    File 2: {val2}")
        
        return len(differences) == 0
        
    except Exception as e:
        print(f"❌ Comparison failed: {e}")
        return False

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Configuration Migration Tool for Invoice Extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert JSON to YAML
  python config_migration.py migrate config.json config.yaml
  
  # Convert YAML to JSON
  python config_migration.py migrate config.yaml config.json
  
  # Create default YAML configuration
  python config_migration.py create-default config.yaml
  
  # Create default JSON configuration  
  python config_migration.py create-default config.json --format json
  
  # Validate configuration
  python config_migration.py validate config.yaml
  
  # Compare two configurations
  python config_migration.py compare config1.yaml config2.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Convert configuration between formats')
    migrate_parser.add_argument('input', help='Input configuration file')
    migrate_parser.add_argument('output', help='Output configuration file')
    migrate_parser.add_argument('--format', choices=['json', 'yaml', 'yml'], 
                               help='Output format (auto-detected from extension if not specified)')
    
    # Create default command
    create_parser = subparsers.add_parser('create-default', help='Create default configuration file')
    create_parser.add_argument('output', help='Output configuration file')
    create_parser.add_argument('--format', choices=['json', 'yaml', 'yml'], default='yaml',
                              help='Output format (default: yaml)')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration file')
    validate_parser.add_argument('config', help='Configuration file to validate')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two configuration files')
    compare_parser.add_argument('config1', help='First configuration file')
    compare_parser.add_argument('config2', help='Second configuration file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    success = False
    
    if args.command == 'migrate':
        success = migrate_config(args.input, args.output, args.format)
    
    elif args.command == 'create-default':
        success = create_default_config(args.output, args.format)
    
    elif args.command == 'validate':
        success = validate_config_file(args.config)
    
    elif args.command == 'compare':
        success = compare_configs(args.config1, args.config2)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
