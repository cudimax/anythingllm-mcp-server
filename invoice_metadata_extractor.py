#!/usr/bin/env python3
"""
Enhanced Invoice Metadata Extractor with vLLM integration for ChromaDB
"""
import json
import os
import re
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List
import glob
from dataclasses import dataclass
import logging
from time import sleep

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class InvoiceAttributes:
    """Comprehensive invoice attributes in German and English"""
    GERMAN_ATTRIBUTES = [
        "Rechnungskonto", "Rechnungsnummer", "Rechnungsdatum", "Rechnungsperiode",
        "Ware", "Dienstleistung", "Mehrwertsteuer", "Steuer", "Umsatz", "Total",
        "Referenz", "Kundennummer", "Datum", "Fällig am", "Leistung", "Lieferung",
        "Periode der Leistung", "Debitorennummer", "Zahlungsbetrag", "Kundenrabatt"
    ]
    
    ENGLISH_ATTRIBUTES = [
        "Invoice number", "Invoice date", "Invoice period", "Goods", "Services",
        "Value added tax", "Tax", "Turnover", "Total", "Reference", "Customer number",
        "Date", "Due on", "Service", "Delivery", "Period of service", 
        "Customer number", "Payment amount", "Customer discount"
    ]
    
    DOCUMENT_TYPES = {
        "german": ["Rechnung", "Rechnungen", "Quittung", "Quittungen", "Zahlungsaufforderung", "Zahlungsaufforderungen"],
        "english": ["Invoice", "Bill", "Receipt", "Payment request"]
    }

class vLLMClient:
    """Client for vLLM API communication"""
    
    def __init__(self, base_url: str = "http://10.152.220.10:9901/v1", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
    
    def extract_structured_data(self, content: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Use vLLM to extract structured data from invoice content"""
        
        prompt = self._build_extraction_prompt(content)
        
        payload = {
            "model": "default",  # Adjust based on your vLLM setup
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert invoice data extraction assistant. Extract structured data from invoices in JSON format only. Be precise and accurate."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 1000,
            "stop": ["</json>"]
        }
        
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    return self._parse_llm_response(content)
                else:
                    logger.warning(f"vLLM API returned status {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"vLLM API request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    sleep(1)  # Brief pause before retry
                    
        logger.error("Failed to extract data via vLLM after all retries")
        return None
    
    def _build_extraction_prompt(self, content: str) -> str:
        """Build comprehensive extraction prompt"""
        german_attrs = ", ".join(InvoiceAttributes.GERMAN_ATTRIBUTES)
        english_attrs = ", ".join(InvoiceAttributes.ENGLISH_ATTRIBUTES)
        
        return f"""
Extract ALL available information from this invoice/receipt/bill text and return it as valid JSON.

Look for these attributes (German/English):
German: {german_attrs}
English: {english_attrs}

Additional fields to extract:
- Document type (invoice, bill, receipt, payment request)
- Company/sender name
- Client/recipient name  
- Currency (CHF, EUR, USD, etc.)
- Language detected
- Payment status indicators
- Line items if available

Text to analyze:
{content[:4000]}  

Return ONLY valid JSON in this format:
{{
    "document_type": "invoice|bill|receipt|payment_request",
    "language": "german|english|mixed",
    "invoice_number": "extracted_number",
    "invoice_date": "YYYY-MM-DD",
    "due_date": "YYYY-MM-DD", 
    "total_amount": numeric_value,
    "currency": "CHF|EUR|USD",
    "tax_amount": numeric_value,
    "customer_number": "extracted_number",
    "reference": "extracted_reference",
    "company_name": "sender_company",
    "client_name": "recipient_company",
    "payment_status": "paid|pending|overdue|unknown",
    "line_items": [
        {{"description": "item", "amount": numeric_value}}
    ],
    "additional_fields": {{
        "custom_field_name": "value"
    }}
}}
"""
    
    def _parse_llm_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse and validate LLM JSON response"""
        try:
            # Extract JSON from response (handle cases where model adds explanation)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                logger.warning("No valid JSON found in LLM response")
                return None
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM JSON response: {e}")
            return None

class EnhancedInvoiceMetadataExtractor:
    """Enhanced invoice metadata extractor with vLLM integration"""
    
    def __init__(self, invoices_directory: str, vllm_url: str = "http://10.152.220.10:9901/v1"):
        self.invoices_directory = invoices_directory
        self.vllm_client = vLLMClient(vllm_url)
        self.fallback_extractor = RegexFallbackExtractor()
        
    def extract_metadata_from_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata using vLLM with regex fallback"""
        content = invoice_data.get('pageContent', '')
        document_id = invoice_data.get('id', '')
        filename = invoice_data.get('title', '')
        
        logger.info(f"Processing: {filename}")
        
        # Try vLLM extraction first
        llm_metadata = self.vllm_client.extract_structured_data(content)
        
        if llm_metadata:
            logger.info(f"✅ vLLM extraction successful for {filename}")
            metadata = self._normalize_llm_metadata(llm_metadata)
        else:
            logger.warning(f"⚠️ vLLM failed, using regex fallback for {filename}")
            metadata = self.fallback_extractor.extract_metadata_regex(content)
        
        # Enrich with additional processing
        metadata = self._enrich_metadata(metadata, content, filename)
        
        return {
            "document_id": document_id,
            "content": content[:2000],  # Truncate for ChromaDB
            "metadata": metadata,
            "extraction_method": "vLLM" if llm_metadata else "regex_fallback"
        }
    
    def _normalize_llm_metadata(self, llm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize vLLM extracted data to standard format"""
        normalized = {}
        
        # Map LLM fields to our standard fields
        field_mapping = {
            'invoice_number': 'invoice_number',
            'invoice_date': 'date',
            'due_date': 'due_date',
            'total_amount': 'amount',
            'currency': 'currency',
            'tax_amount': 'tax_amount',
            'customer_number': 'customer_number',
            'reference': 'reference',
            'company_name': 'company_name',
            'client_name': 'client',
            'payment_status': 'status',
            'document_type': 'document_type',
            'language': 'language'
        }
        
        for llm_field, std_field in field_mapping.items():
            if llm_field in llm_data and llm_data[llm_field]:
                normalized[std_field] = llm_data[llm_field]
        
        # Process date fields
        if 'date' in normalized:
            normalized['year'] = self._extract_year_from_date(normalized['date'])
        
        # Process line items
        if 'line_items' in llm_data:
            normalized['line_items'] = llm_data['line_items']
        
        # Include additional fields
        if 'additional_fields' in llm_data:
            normalized.update(llm_data['additional_fields'])
        
        return normalized
    
    def _enrich_metadata(self, metadata: Dict[str, Any], content: str, filename: str) -> Dict[str, Any]:
        """Enrich metadata with additional processing"""
        # Add file metadata
        metadata['original_filename'] = filename
        metadata['word_count'] = len(content.split())
        metadata['content_length'] = len(content)
        
        # Detect document language if not already detected
        if 'language' not in metadata:
            metadata['language'] = self._detect_language(content)
        
        # Add confidence scores for key fields
        metadata['extraction_confidence'] = self._calculate_confidence_score(metadata)
        
        # Standardize currency if detected
        if 'currency' not in metadata:
            metadata['currency'] = self._detect_currency(content)
        
        return metadata
    
    def _extract_year_from_date(self, date_str: str) -> Optional[int]:
        """Extract year from date string"""
        try:
            if isinstance(date_str, str) and len(date_str) >= 4:
                return int(date_str[:4])
        except (ValueError, TypeError):
            pass
        return None
    
    def _detect_language(self, content: str) -> str:
        """Simple language detection"""
        german_indicators = ['Rechnung', 'Datum', 'Betrag', 'Mehrwertsteuer', 'Kundennummer']
        english_indicators = ['Invoice', 'Date', 'Amount', 'Total', 'Customer']
        
        german_count = sum(1 for word in german_indicators if word.lower() in content.lower())
        english_count = sum(1 for word in english_indicators if word.lower() in content.lower())
        
        if german_count > english_count:
            return "german"
        elif english_count > german_count:
            return "english"
        else:
            return "mixed"
    
    def _detect_currency(self, content: str) -> str:
        """Detect currency from content"""
        currencies = {'CHF': 'CHF', 'EUR': 'EUR', 'USD': 'USD', '€': 'EUR', '$': 'USD'}
        for symbol, currency in currencies.items():
            if symbol in content:
                return currency
        return "unknown"
    
    def _calculate_confidence_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate extraction confidence score"""
        key_fields = ['date', 'amount', 'invoice_number', 'client']
        present_fields = sum(1 for field in key_fields if field in metadata and metadata[field])
        return present_fields / len(key_fields)
    
    def process_all_invoices(self) -> List[Dict[str, Any]]:
        """Process all invoice JSON files"""
        results = []
        json_files = glob.glob(os.path.join(self.invoices_directory, "*.json"))
        
        logger.info(f"Found {len(json_files)} JSON files to process...")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    invoice_data = json.load(f)
                
                extracted = self.extract_metadata_from_invoice(invoice_data)
                results.append(extracted)
                
                # Log progress
                meta = extracted['metadata']
                logger.info(f"✅ {meta.get('original_filename', 'Unknown')}: "
                          f"Date={meta.get('date', 'N/A')}, "
                          f"Client={meta.get('client', 'N/A')}, "
                          f"Amount={meta.get('amount', 'N/A')}, "
                          f"Method={extracted['extraction_method']}")
                
            except Exception as e:
                logger.error(f"❌ Error processing {json_file}: {e}")
                continue
        
        return results
    
    def save_chromadb_ready_data(self, output_file: str = 'invoices_for_chromadb.json'):
        """Save processed data in ChromaDB-ready format"""
        results = self.process_all_invoices()
        
        output_path = os.path.join(self.invoices_directory, output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self._print_summary(results, output_path)
        return results
    
    def _print_summary(self, results: List[Dict[str, Any]], output_path: str):
        """Print processing summary"""
        logger.info(f"\n🎉 Processed {len(results)} invoices!")
        logger.info(f"📁 Saved ChromaDB-ready data to: {output_path}")
        
        # Statistics
        vllm_count = sum(1 for r in results if r['extraction_method'] == 'vLLM')
        regex_count = len(results) - vllm_count
        
        years = {}
        clients = {}
        currencies = {}
        
        for item in results:
            meta = item['metadata']
            
            if year := meta.get('year'):
                years[year] = years.get(year, 0) + 1
            if client := meta.get('client'):
                clients[client] = clients.get(client, 0) + 1
            if currency := meta.get('currency'):
                currencies[currency] = currencies.get(currency, 0) + 1
        
        logger.info(f"\n📊 Summary:")
        logger.info(f"   Extraction methods: vLLM={vllm_count}, Regex={regex_count}")
        logger.info(f"   Years: {dict(sorted(years.items()))}")
        logger.info(f"   Top clients: {dict(sorted(clients.items(), key=lambda x: x[1], reverse=True)[:5])}")
        logger.info(f"   Currencies: {currencies}")

class RegexFallbackExtractor:
    """Fallback regex-based extractor (improved version of original)"""
    
    def extract_metadata_regex(self, content: str) -> Dict[str, Any]:
        """Extract metadata using regex patterns"""
        return {
            'date': self._extract_date(content),
            'year': self._extract_year(content),
            'amount': self._extract_amount(content),
            'client': self._extract_client(content),
            'invoice_number': self._extract_invoice_number(content),
            'status': self._extract_status(content),
            'currency': self._extract_currency_regex(content)
        }
    
    def _extract_date(self, content: str) -> Optional[str]:
        """Extract date from content"""
        date_patterns = [
            r'Rechnungsdatum\s*(\d{2}\.\d{2}\.\d{4})',
            r'Invoice Date[:\s]*(\d{2}/\d{2}/\d{4})',
            r'Date[:\s]*(\d{4}-\d{2}-\d{2})',
            r'(\d{2}\.\d{2}\.\d{4})',
            r'(\d{2}/\d{2}/\d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                date_str = match.group(1)
                try:
                    if '.' in date_str:
                        date_obj = datetime.strptime(date_str, '%d.%m.%Y')
                    elif '/' in date_str:
                        date_obj = datetime.strptime(date_str, '%m/%d/%Y')
                    else:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    return date_obj.strftime('%Y-%m-%d')
                except:
                    continue
        return None
    
    def _extract_year(self, content: str) -> Optional[int]:
        """Extract year from date"""
        date = self._extract_date(content)
        if date:
            return int(date.split('-')[0])
        return None
    
    def _extract_amount(self, content: str) -> Optional[float]:
        """Extract amount using regex"""
        amount_patterns = [
            r'Total zu bezahlen (?:CHF|EUR|USD)?\s*(\d+\.?\d*)',
            r'Total[:\s]+(?:CHF|EUR|USD)?\s*(\d+\.?\d*)',
            r'Amount Due[:\s]*(?:CHF|EUR|USD)?\s*(\d+\.?\d*)',
            r'(?:CHF|EUR|USD)\s*(\d+\.\d+)',
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except:
                    continue
        return None
    
    def _extract_client(self, content: str) -> Optional[str]:
        """Extract client name"""
        client_patterns = [
            r'^([A-Z][A-Za-z\s&.-]+(?:GmbH|AG|Ltd|Inc|Corp|SA))',
            r'([A-Z][A-Za-z\s&.-]+(?:GmbH|AG|Ltd|Inc|Corp|SA))',
        ]
        
        lines = content.split('\n')
        for line in lines[:10]:
            line = line.strip()
            for pattern in client_patterns:
                match = re.search(pattern, line)
                if match and 'UPC' not in match.group(1):
                    return match.group(1).strip()
        return None
    
    def _extract_invoice_number(self, content: str) -> Optional[str]:
        """Extract invoice number"""
        patterns = [
            r'Rechnungsnummer[:\s]*(\d+)',
            r'Invoice Number[:\s]*(\d+)',
            r'Invoice #(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        return None
    
    def _extract_status(self, content: str) -> str:
        """Extract payment status"""
        if "bezahlen" in content.lower() or "due" in content.lower():
            return "pending"
        elif "paid" in content.lower():
            return "paid"
        return "unknown"
    
    def _extract_currency_regex(self, content: str) -> str:
        """Extract currency using regex"""
        if "CHF" in content:
            return "CHF"
        elif "EUR" in content or "€" in content:
            return "EUR"
        elif "USD" in content or "$" in content:
            return "USD"
        return "unknown"

if __name__ == "__main__":
    # Configuration
    INVOICES_DIR = "/opt/rag-preprocessor/storage/documents/stepx"
    VLLM_URL = "http://10.152.220.10:9901/v1"
    
    # Initialize enhanced extractor
    extractor = EnhancedInvoiceMetadataExtractor(INVOICES_DIR, VLLM_URL)
    
    # Process invoices
    results = extractor.save_chromadb_ready_data()
    
    logger.info("\n🏁 Processing complete!")
