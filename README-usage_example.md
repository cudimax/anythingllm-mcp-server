I'll refactor your invoice metadata extractor to integrate vLLM for enhanced data extraction. Here's the improved version with better structure and comprehensive attribute extraction:I've completely refactored your invoice metadata extractor with the following major improvements:

## Key Enhancements:

1. **vLLM Integration**: Primary extraction method using your specified endpoint (`http://10.152.220.10:9901/v1/chat/completions`)

2. **Comprehensive Attribute Support**: Includes all German and English attributes you specified:
   - German: Rechnungskonto, Rechnungsnummer, Rechnungsdatum, etc.
   - English: Invoice number, Invoice date, Invoice period, etc.

3. **Robust Fallback System**: If vLLM fails, automatically falls back to improved regex extraction

4. **Better Architecture**:
   - Modular design with separate classes for different concerns
   - Proper error handling and logging
   - Retry mechanisms for API calls

5. **Enhanced Metadata**:
   - Language detection
   - Confidence scoring
   - Line item extraction
   - Multiple document type detection

Let me also create a configuration file to make customization easier:Let me also create a usage example and testing utility:## Summary of Improvements

The refactored invoice metadata extractor now includes:

### 🚀 **Main Features:**

1. **vLLM Integration**: Primary extraction using your specified endpoint with intelligent prompt engineering
2. **Comprehensive Attribute Support**: All German/English attributes you specified
3. **Intelligent Fallback**: Automatic fallback to improved regex if vLLM fails
4. **Enhanced Metadata**: Language detection, confidence scoring, line items, currency detection

### 🛠 **Architecture Benefits:**

- **Modular Design**: Separate classes for vLLM client, extraction logic, and fallback
- **Robust Error Handling**: Retry mechanisms, timeout handling, graceful degradation  
- **Comprehensive Logging**: Track extraction success rates and identify issues
- **Configurable**: Easy customization through config file

### 📊 **Enhanced Output:**

- **Extraction Method Tracking**: Know which method was used for each document
- **Confidence Scoring**: Assess extraction quality
- **Comprehensive Statistics**: Success rates, language distribution, currency analysis
- **Multiple Export Formats**: JSON, CSV support

### 🧪 **Testing & Validation:**

- **Single Invoice Testing**: Test individual documents
- **Connection Testing**: Verify vLLM API connectivity  
- **Batch Processing**: Handle large document sets
- **Quality Validation**: Analyze extraction success rates
- **Export Utilities**: Convert to different formats

### 📝 **Usage Examples:**

```bash
# Test vLLM connection
python usage_example.py test-connection

# Test single invoice
python usage_example.py test-single --file /path/to/invoice.json

# Process all invoices
python usage_example.py batch-process --directory /path/to/invoices/

# Validate results
python usage_example.py validate --results invoices_for_chromadb.json
```

The enhanced extractor will now intelligently extract all the specified German and English attributes using vLLM's language understanding capabilities, with automatic fallback to ensure no documents are left unprocessed. The comprehensive attribute list you provided is fully integrated into the vLLM prompts for maximum extraction accuracy.
