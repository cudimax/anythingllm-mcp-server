#!/usr/bin/env python3
"""
Usage example and testing utility for Enhanced Invoice Metadata Extractor
"""

import json
import sys
from pathlib import Path

# Add the extractor to path (adjust as needed)
# sys.path.append('/path/to/your/extractor')

from invoice_metadata_extractor import EnhancedInvoiceMetadataExtractor
from config import VLLM_CONFIG, PROCESSING_CONFIG, OUTPUT_CONFIG

def test_single_invoice(invoice_file_path: str, vllm_url: str = None):
    """Test extraction on a single invoice file"""
    if not vllm_url:
        vllm_url = VLLM_CONFIG["base_url"]
    
    print(f"🧪 Testing single invoice: {invoice_file_path}")
    
    # Load invoice data
    try:
        with open(invoice_file_path, 'r', encoding='utf-8') as f:
            invoice_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading invoice file: {e}")
        return None
    
    # Create extractor instance
    invoices_dir = str(Path(invoice_file_path).parent)
    extractor = EnhancedInvoiceMetadataExtractor(invoices_dir, vllm_url)
    
    # Extract metadata
    result = extractor.extract_metadata_from_invoice(invoice_data)
    
    # Display results
    print(f"\n📄 Results for: {result['metadata'].get('original_filename', 'Unknown')}")
    print(f"🔧 Extraction method: {result['extraction_method']}")
    print(f"\n📋 Extracted Metadata:")
    
    metadata = result['metadata']
    for key, value in metadata.items():
        if value is not None and value != "":
            if isinstance(value, dict):
                print(f"  {key}: {json.dumps(value, indent=4)}")
            else:
                print(f"  {key}: {value}")
    
    print(f"\n📊 Confidence Score: {metadata.get('extraction_confidence', 'N/A')}")
    
    return result

def test_vllm_connection(vllm_url: str = None):
    """Test connection to vLLM API"""
    if not vllm_url:
        vllm_url = VLLM_CONFIG["base_url"]
    
    print(f"🔗 Testing vLLM connection to: {vllm_url}")
    
    from invoice_metadata_extractor import vLLMClient
    
    client = vLLMClient(vllm_url)
    
    test_content = """
    RECHNUNG
    
    Rechnungsnummer: 2024-001
    Rechnungsdatum: 15.03.2024
    
    Kunde: Test GmbH
    
    Leistung: Beratung
    Betrag: CHF 1,500.00
    Mehrwertsteuer: CHF 116.25
    Total: CHF 1,616.25
    """
    
    result = client.extract_structured_data(test_content)
    
    if result:
        print("✅ vLLM connection successful!")
        print(f"📋 Test extraction result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return True
    else:
        print("❌ vLLM connection failed!")
        return False

def batch_process_invoices(invoices_directory: str, vllm_url: str = None):
    """Process all invoices in a directory"""
    if not vllm_url:
        vllm_url = VLLM_CONFIG["base_url"]
    
    print(f"🚀 Starting batch processing of: {invoices_directory}")
    
    extractor = EnhancedInvoiceMetadataExtractor(invoices_directory, vllm_url)
    results = extractor.save_chromadb_ready_data()
    
    return results

def validate_extraction_results(results_file: str):
    """Validate and analyze extraction results"""
    print(f"🔍 Validating results from: {results_file}")
    
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
    except Exception as e:
        print(f"❌ Error loading results file: {e}")
        return
    
    total_docs = len(results)
    vllm_extractions = sum(1 for r in results if r['extraction_method'] == 'vLLM')
    regex_extractions = total_docs - vllm_extractions
    
    # Analyze extraction quality
    high_confidence = sum(1 for r in results 
                         if r['metadata'].get('extraction_confidence', 0) > 0.7)
    
    missing_key_fields = []
    key_fields = ['date', 'amount', 'invoice_number']
    
    for result in results:
        metadata = result['metadata']
        missing = [field for field in key_fields 
                  if field not in metadata or not metadata[field]]
        if missing:
            missing_key_fields.append({
                'file': metadata.get('original_filename', 'Unknown'),
                'missing_fields': missing
            })
    
    # Print analysis
    print(f"\n📊 Validation Results:")
    print(f"  Total documents processed: {total_docs}")
    print(f"  vLLM extractions: {vllm_extractions} ({vllm_extractions/total_docs*100:.1f}%)")
    print(f"  Regex fallback: {regex_extractions} ({regex_extractions/total_docs*100:.1f}%)")
    print(f"  High confidence (>70%): {high_confidence} ({high_confidence/total_docs*100:.1f}%)")
    print(f"  Documents missing key fields: {len(missing_key_fields)}")
    
    if missing_key_fields:
        print(f"\n⚠️ Documents with missing key fields:")
        for doc in missing_key_fields[:5]:  # Show first 5
            print(f"    {doc['file']}: missing {', '.join(doc['missing_fields'])}")
        if len(missing_key_fields) > 5:
            print(f"    ... and {len(missing_key_fields) - 5} more")
    
    return {
        'total_docs': total_docs,
        'vllm_success_rate': vllm_extractions / total_docs,
        'high_confidence_rate': high_confidence / total_docs,
        'missing_fields_count': len(missing_key_fields)
    }

def export_to_csv(results_file: str, output_csv: str = None):
    """Export results to CSV format"""
    import pandas as pd
    
    if not output_csv:
        output_csv = results_file.replace('.json', '.csv')
    
    print(f"📤 Exporting to CSV: {output_csv}")
    
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        # Flatten metadata for CSV
        flattened = []
        for result in results:
            row = {
                'document_id': result['document_id'],
                'extraction_method': result['extraction_method']
            }
            row.update(result['metadata'])
            flattened.append(row)
        
        df = pd.DataFrame(flattened)
        df.to_csv(output_csv, index=False, encoding='utf-8')
        
        print(f"✅ Successfully exported {len(flattened)} records to {output_csv}")
        
    except Exception as e:
        print(f"❌ Error exporting to CSV: {e}")

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Invoice Metadata Extractor')
    parser.add_argument('action', choices=[
        'test-connection', 'test-single', 'batch-process', 
        'validate', 'export-csv'
    ])
    parser.add_argument('--file', help='Single invoice file path')
    parser.add_argument('--directory', help='Invoices directory path')
    parser.add_argument('--results', help='Results file path')
    parser.add_argument('--vllm-url', help='vLLM API URL')
    parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    if args.action == 'test-connection':
        test_vllm_connection(args.vllm_url)
    
    elif args.action == 'test-single':
        if not args.file:
            print("❌ --file parameter required for test-single")
            return
        test_single_invoice(args.file, args.vllm_url)
    
    elif args.action == 'batch-process':
        if not args.directory:
            print("❌ --directory parameter required for batch-process")
            return
        batch_process_invoices(args.directory, args.vllm_url)
    
    elif args.action == 'validate':
        if not args.results:
            print("❌ --results parameter required for validate")
            return
        validate_extraction_results(args.results)
    
    elif args.action == 'export-csv':
        if not args.results:
            print("❌ --results parameter required for export-csv")
            return
        export_to_csv(args.results, args.output)

if __name__ == "__main__":
    # Example usage:
    print("🔧 Enhanced Invoice Metadata Extractor - Usage Examples")
    print("\nCommand line examples:")
    print("  python usage_example.py test-connection")
    print("  python usage_example.py test-single --file /path/to/invoice.json")
    print("  python usage_example.py batch-process --directory /path/to/invoices/")
    print("  python usage_example.py validate --results invoices_for_chromadb.json")
    print("  python usage_example.py export-csv --results invoices_for_chromadb.json")
    
    # If running directly, show available options
    if len(sys.argv) == 1:
        print("\n📋 Available actions: test-connection, test-single, batch-process, validate, export-csv")
        print("Use --help for detailed usage information")
    else:
        main()
