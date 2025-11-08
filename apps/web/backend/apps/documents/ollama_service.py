"""
Ollama Integration Service for Intelligent Receipt Processing
Uses MiniCPM-v (8B), Gemma3, and Llama2 models for advanced OCR analysis
MiniCPM-v 2.6: Top OCRBench performer, beats GPT-4o, supports 30+ languages
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
import re
from dataclasses import dataclass, asdict
import asyncio
import aiohttp

logger = logging.getLogger('documents.ollama')


@dataclass
class ReceiptField:
    """Data class for receipt fields"""
    name: str
    value: Any
    confidence: float
    source: str  # 'ocr', 'ollama', 'user'
    alternatives: List[Any] = None
    
    def to_dict(self):
        return asdict(self)


class OllamaService:
    """
    Service for integrating with Ollama models
    Supports MiniCPM-v 2.6, Gemma3, and Llama2 for multilingual receipt processing
    """

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.models = {
            'minicpm-v': 'minicpm-v:latest',  # Top OCRBench performer, 30+ languages
            'gemma3': 'gemma3:latest',
            'llama2': 'llama2:latest',
            'mistral': 'mistral:latest'  # Fallback option
        }
        self.current_model = 'minicpm-v'  # Changed from 'gemma3' to 'minicpm-v'
        self.timeout = 180  # Increased for MiniCPM-v processing (was 120)
        
        # Turkish receipt prompts
        self.prompts = {
            'extract_receipt': self._get_receipt_extraction_prompt(),
            'validate_data': self._get_validation_prompt(),
            'improve_ocr': self._get_ocr_improvement_prompt(),
            'extract_items': self._get_item_extraction_prompt(),
        }
        
        # Check Ollama availability
        self.available = self.check_availability()
        
    def check_availability(self) -> bool:
        """Check if Ollama is running and models are available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [m['name'] for m in models]
                logger.info(f"Ollama available with models: {available_models}")
                
                # Check for our preferred models
                for model_key, model_name in self.models.items():
                    if any(model_name in m for m in available_models):
                        self.current_model = model_key
                        logger.info(f"Using model: {model_name}")
                        return True
                        
                logger.warning("Preferred models not found in Ollama")
                return False
            return False
        except Exception as e:
            logger.error(f"Ollama not available: {e}")
            return False

    def is_available(self) -> bool:
        """Check if Ollama service is available"""
        return self.available

    def analyze_receipt(self, ocr_text: str, image_base64: Optional[str] = None) -> Dict:
        """
        Analyze receipt using Ollama model

        Args:
            ocr_text: Raw OCR text from receipt (optional - can be empty for vision mode)
            image_base64: Base64 encoded image for vision models

        Returns:
            Structured receipt data with confidence scores
        """
        if not self.available:
            return {'error': 'Ollama service not available'}

        try:
            # Use vision mode if image provided and no OCR text
            if image_base64 and not ocr_text:
                # Optimized prompt for MiniCPM-v vision OCR
                if self.current_model == 'minicpm-v':
                    prompt = """Perform complete OCR on this document image. Extract every word, number, and symbol visible in the image.
Start from the very top and continue to the very bottom. Include all transaction details, codes, and footer information.
Do not summarize or skip anything - transcribe EVERYTHING you can see."""
                else:
                    prompt = """Transcribe all text from this image:"""
            else:
                # Use OCR text if available
                prompt = self.prompts['extract_receipt'].format(ocr_text=ocr_text or '')

            # Call Ollama with vision
            response = self._call_ollama(prompt, image_base64)

            if response.get('error'):
                return response

            # Get the raw text response
            raw_response = response.get('response', '')

            # Parse the response
            parsed_data = self._parse_ollama_response(raw_response)

            # Add metadata
            parsed_data['model_used'] = self.current_model
            parsed_data['processing_time'] = response.get('processing_time', 0)

            # Validate and enhance data
            validated_data = self.validate_extracted_data(parsed_data, ocr_text)

            # Add success flag
            validated_data['success'] = True
            validated_data['raw_response'] = raw_response

            return validated_data

        except Exception as e:
            logger.error(f"Error analyzing receipt with Ollama: {e}")
            return {'error': str(e)}
    
    def _call_ollama(self, prompt: str, image_base64: Optional[str] = None) -> Dict:
        """Make API call to Ollama"""
        try:
            start_time = datetime.now()

            # Model-specific parameters optimized for OCR performance
            if self.current_model == 'minicpm-v':
                # MiniCPM-v optimal parameters for OCR tasks
                options = {
                    'temperature': 0.1,    # Low temperature for precise OCR (accuracy over creativity)
                    'top_p': 0.8,          # Focused sampling for better text recognition
                    'top_k': 40,           # Conservative vocabulary selection
                    'num_predict': 8000,   # Higher limit for comprehensive document OCR
                    'repeat_penalty': 1.1  # Slight penalty to reduce repetition in long texts
                }
            else:
                # Gemma3/other models - previous optimized settings
                options = {
                    'temperature': 0.7,  # Optimized for better completeness
                    'top_p': 0.95,       # Official Gemma3 recommendation
                    'top_k': 64,         # Official Gemma3 recommendation
                    'num_predict': 6000, # Increased for longer receipts
                    'repeat_penalty': 1.0  # Disabled for Gemma3
                }

            payload = {
                'model': self.models[self.current_model],
                'prompt': prompt,
                'stream': False,
                'options': options
            }

            # Add image if available (for vision models)
            if image_base64:
                payload['images'] = [image_base64]
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                processing_time = (datetime.now() - start_time).total_seconds()
                result['processing_time'] = processing_time
                return result
            else:
                return {'error': f"Ollama API error: {response.status_code}"}
                
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return {'error': 'Request timed out'}
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            return {'error': str(e)}
    
    def _get_receipt_extraction_prompt(self) -> str:
        """Get prompt for receipt data extraction"""
        return """You are an expert at analyzing Turkish receipts (fiş/fatura). 
Extract the following information from this receipt text:

{ocr_text}

Please extract and return in JSON format:
{{
    "store_info": {{
        "name": "store name",
        "address": "full address",
        "phone": "phone number",
        "tax_id": "vergi no"
    }},
    "transaction": {{
        "date": "DD-MM-YYYY format",
        "time": "HH:MM format",
        "receipt_no": "fiş/fatura number",
        "cashier": "kasiyer name/id"
    }},
    "items": [
        {{
            "name": "product name",
            "quantity": quantity as number,
            "unit_price": price as number,
            "total_price": total as number,
            "barcode": "barcode if available",
            "category": "detected category"
        }}
    ],
    "financial": {{
        "subtotal": subtotal as number,
        "tax_amount": KDV amount as number,
        "tax_rate": KDV rate as percentage,
        "discount": discount amount as number,
        "total": total amount as number
    }},
    "payment": {{
        "method": "credit_card/cash/debit_card",
        "card_last_digits": "last 4 digits if card",
        "approval_code": "onay kodu if available"
    }}
}}

Important notes:
- Convert all amounts to decimal numbers (e.g., "12,50" becomes 12.50)
- Dates should be in DD-MM-YYYY format
- Detect common Turkish store chains (Migros, A101, BİM, ŞOK, Carrefour, etc.)
- Handle Turkish characters properly (ğ, ü, ş, ı, ö, ç)
- If a field is not found, use null
- For items, try to clean product names and remove codes/numbers at the end
"""
    
    def _get_validation_prompt(self) -> str:
        """Get prompt for data validation"""
        return """You are validating extracted receipt data for accuracy.

Original OCR text:
{ocr_text}

Extracted data:
{extracted_data}

Please validate:
1. Does the total match the sum of items plus tax minus discounts?
2. Is the date format correct and realistic?
3. Are the item prices reasonable?
4. Is the store name correctly identified?
5. Are there any obvious errors or inconsistencies?

Return validation result in JSON:
{{
    "is_valid": true/false,
    "confidence": 0-100,
    "errors": ["list of errors"],
    "warnings": ["list of warnings"],
    "suggestions": {{
        "field_name": "suggested correction"
    }}
}}
"""
    
    def _get_ocr_improvement_prompt(self) -> str:
        """Get prompt for improving OCR text"""
        return """You are an OCR correction expert for Turkish receipts.

Raw OCR text with possible errors:
{ocr_text}

Please:
1. Fix common OCR errors (0 vs O, 1 vs I, etc.)
2. Correct Turkish character recognition (i vs ı, g vs ğ, etc.)
3. Fix spacing and line break issues
4. Identify and correct misread numbers in prices
5. Clean up product names

Return the corrected text maintaining the original structure as much as possible.
Also provide a confidence score (0-100) for your corrections.
"""
    
    def _get_item_extraction_prompt(self) -> str:
        """Get prompt for detailed item extraction"""
        return """Extract product items from this Turkish receipt text:

{ocr_text}

For each item, identify:
- Product name (clean and normalized)
- Quantity and unit (adet, kg, lt, etc.)
- Unit price
- Total price
- Any discounts applied
- Category (food, beverage, household, etc.)

Focus on the middle section of the receipt where items are listed.
Look for patterns like:
- PRODUCT NAME  QUANTITY x PRICE = TOTAL
- PRODUCT NAME
  QUANTITY UNIT @ PRICE    TOTAL

Return as JSON array of items.
"""
    
    def _parse_ollama_response(self, response_text: str) -> Dict:
        """Parse Ollama model response"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # Fallback: try to parse structured text
                return self._parse_structured_text(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Ollama response as JSON: {e}")
            return self._parse_structured_text(response_text)
        except Exception as e:
            logger.error(f"Error parsing Ollama response: {e}")
            return {}
    
    def _parse_structured_text(self, text: str) -> Dict:
        """Fallback parser for non-JSON responses"""
        parsed = {
            'store_info': {},
            'transaction': {},
            'items': [],
            'financial': {},
            'payment': {}
        }
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if 'store' in line.lower() or 'mağaza' in line.lower():
                current_section = 'store_info'
            elif 'transaction' in line.lower() or 'işlem' in line.lower():
                current_section = 'transaction'
            elif 'item' in line.lower() or 'ürün' in line.lower():
                current_section = 'items'
            elif 'total' in line.lower() or 'toplam' in line.lower():
                current_section = 'financial'
            elif 'payment' in line.lower() or 'ödeme' in line.lower():
                current_section = 'payment'
            
            # Extract key-value pairs
            if ':' in line and current_section:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                
                if current_section == 'items':
                    # Handle items specially
                    parsed['items'].append({'name': value})
                else:
                    parsed[current_section][key] = value
        
        return parsed
    
    def validate_extracted_data(self, data: Dict, original_ocr: str) -> Dict:
        """Validate and enhance extracted data"""
        validation_results = {
            'is_valid': True,
            'confidence': 0,
            'errors': [],
            'warnings': []
        }
        
        confidence_scores = []
        
        # Validate store info
        if data.get('store_info'):
            store = data['store_info']
            if store.get('name'):
                confidence_scores.append(90)
            else:
                validation_results['errors'].append('Store name not found')
                confidence_scores.append(20)
        
        # Validate transaction data
        if data.get('transaction'):
            trans = data['transaction']
            if trans.get('date'):
                # Validate date format
                if self._validate_date(trans['date']):
                    confidence_scores.append(95)
                else:
                    validation_results['warnings'].append('Date format may be incorrect')
                    confidence_scores.append(50)
        
        # Validate financial data
        if data.get('financial'):
            fin = data['financial']
            if fin.get('total'):
                # Check if total is reasonable
                try:
                    total = float(fin['total'])
                    if 0 < total < 100000:  # Reasonable range for receipts
                        confidence_scores.append(85)
                    else:
                        validation_results['warnings'].append('Total amount seems unusual')
                        confidence_scores.append(40)
                except:
                    validation_results['errors'].append('Invalid total amount')
                    confidence_scores.append(10)
        
        # Validate items
        if data.get('items') and len(data['items']) > 0:
            valid_items = 0
            for item in data['items']:
                if item.get('name') and item.get('total_price'):
                    valid_items += 1
            
            item_confidence = (valid_items / len(data['items'])) * 100
            confidence_scores.append(item_confidence)
        else:
            validation_results['warnings'].append('No items found')
            confidence_scores.append(30)
        
        # Calculate overall confidence
        if confidence_scores:
            validation_results['confidence'] = sum(confidence_scores) / len(confidence_scores)
        
        validation_results['is_valid'] = len(validation_results['errors']) == 0
        
        # Add validation results to data
        data['validation'] = validation_results
        
        return data
    
    def _validate_date(self, date_str: str) -> bool:
        """Validate date format"""
        patterns = [
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
            r'\d{2}\.\d{2}\.\d{4}',  # DD.MM.YYYY
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
        ]
        
        for pattern in patterns:
            if re.match(pattern, date_str):
                return True
        return False
    
    async def analyze_batch_async(self, receipts: List[Dict]) -> List[Dict]:
        """Analyze multiple receipts asynchronously"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for receipt in receipts:
                task = self._analyze_receipt_async(
                    session,
                    receipt['ocr_text'],
                    receipt.get('image_base64')
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            return results
    
    async def _analyze_receipt_async(self, session: aiohttp.ClientSession, 
                                    ocr_text: str, image_base64: Optional[str] = None) -> Dict:
        """Async version of receipt analysis"""
        if not self.available:
            return {'error': 'Ollama service not available'}
        
        try:
            prompt = self.prompts['extract_receipt'].format(ocr_text=ocr_text)
            
            payload = {
                'model': self.models[self.current_model],
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.3,
                    'top_p': 0.9,
                    'num_predict': 2048
                }
            }
            
            if image_base64 and self.current_model in ['minicpm-v', 'gemma3']:
                payload['images'] = [image_base64]
            
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    parsed_data = self._parse_ollama_response(result.get('response', ''))
                    return self.validate_extracted_data(parsed_data, ocr_text)
                else:
                    return {'error': f"Ollama API error: {response.status}"}
                    
        except asyncio.TimeoutError:
            return {'error': 'Request timed out'}
        except Exception as e:
            return {'error': str(e)}
    
    def improve_ocr_text(self, ocr_text: str) -> Dict:
        """Use Ollama to improve OCR text quality"""
        if not self.available:
            return {'improved_text': ocr_text, 'confidence': 0}
        
        try:
            prompt = self.prompts['improve_ocr'].format(ocr_text=ocr_text)
            response = self._call_ollama(prompt)
            
            if response.get('error'):
                return {'improved_text': ocr_text, 'confidence': 0}
            
            improved_text = response.get('response', ocr_text)
            
            # Extract confidence if mentioned
            confidence = 75  # Default confidence
            confidence_match = re.search(r'confidence[:\s]+(\d+)', improved_text, re.IGNORECASE)
            if confidence_match:
                confidence = int(confidence_match.group(1))
                # Remove confidence from text
                improved_text = re.sub(r'confidence[:\s]+\d+\s*', '', improved_text, flags=re.IGNORECASE)
            
            return {
                'improved_text': improved_text.strip(),
                'confidence': confidence,
                'model_used': self.current_model
            }
            
        except Exception as e:
            logger.error(f"Error improving OCR text: {e}")
            return {'improved_text': ocr_text, 'confidence': 0}
    
    def extract_items_detailed(self, ocr_text: str) -> List[Dict]:
        """Extract detailed item information"""
        if not self.available:
            return []
        
        try:
            prompt = self.prompts['extract_items'].format(ocr_text=ocr_text)
            response = self._call_ollama(prompt)
            
            if response.get('error'):
                return []
            
            # Parse items from response
            response_text = response.get('response', '')
            items = self._parse_items_response(response_text)
            
            # Enhance items with categories
            for item in items:
                item['category'] = self._detect_category(item.get('name', ''))
                item['confidence'] = self._calculate_item_confidence(item)
            
            return items
            
        except Exception as e:
            logger.error(f"Error extracting items: {e}")
            return []
    
    def _parse_items_response(self, response_text: str) -> List[Dict]:
        """Parse items from Ollama response"""
        items = []
        
        try:
            # Try JSON first
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                items = json.loads(json_match.group())
                return items
        except:
            pass
        
        # Fallback to line parsing
        lines = response_text.split('\n')
        for line in lines:
            if any(char.isdigit() for char in line):  # Line contains numbers
                item = self._parse_item_line(line)
                if item:
                    items.append(item)
        
        return items
    
    def _parse_item_line(self, line: str) -> Optional[Dict]:
        """Parse a single item line"""
        # Pattern: PRODUCT_NAME QUANTITY x PRICE = TOTAL
        patterns = [
            r'(.+?)\s+(\d+[,.]?\d*)\s*[xX*]\s*(\d+[,.]?\d*)\s*=?\s*(\d+[,.]?\d*)',
            r'(.+?)\s+(\d+[,.]?\d*)\s+(\d+[,.]?\d*)',
            r'(.+?)\s+(\d+[,.]?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                groups = match.groups()
                item = {'name': groups[0].strip()}
                
                if len(groups) >= 2:
                    item['quantity'] = self._parse_number(groups[1])
                if len(groups) >= 3:
                    item['unit_price'] = self._parse_number(groups[2])
                if len(groups) >= 4:
                    item['total_price'] = self._parse_number(groups[3])
                
                return item
        
        return None
    
    def _parse_number(self, text: str) -> float:
        """Parse number from text"""
        try:
            # Replace comma with dot for decimal
            text = text.replace(',', '.')
            return float(text)
        except:
            return 0.0
    
    def _detect_category(self, product_name: str) -> str:
        """Detect product category from name"""
        categories = {
            'food': ['ekmek', 'süt', 'yoğurt', 'peynir', 'et', 'tavuk', 'balık', 
                    'meyve', 'sebze', 'makarna', 'pirinç', 'un', 'yağ'],
            'beverage': ['su', 'kola', 'meyve suyu', 'çay', 'kahve', 'ayran', 
                        'gazoz', 'enerji içeceği', 'maden suyu'],
            'household': ['deterjan', 'sabun', 'şampuan', 'tuvalet kağıdı', 
                         'peçete', 'temizlik', 'bulaşık'],
            'snacks': ['çikolata', 'bisküvi', 'cips', 'kraker', 'gofret', 
                      'şeker', 'sakız'],
            'personal_care': ['diş macunu', 'deodorant', 'parfüm', 'krem', 
                            'makyaj', 'tıraş'],
            'other': []
        }
        
        product_lower = product_name.lower()
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in product_lower:
                    return category
        
        return 'other'
    
    def _calculate_item_confidence(self, item: Dict) -> float:
        """Calculate confidence score for an item"""
        confidence = 0
        max_score = 100
        
        # Check required fields
        if item.get('name'):
            confidence += 30
        if item.get('total_price'):
            confidence += 30
        if item.get('quantity'):
            confidence += 20
        if item.get('unit_price'):
            confidence += 20
        
        # Validate price calculation
        if item.get('quantity') and item.get('unit_price') and item.get('total_price'):
            expected = item['quantity'] * item['unit_price']
            actual = item['total_price']
            if abs(expected - actual) < 0.1:  # Allow small rounding difference
                confidence = min(confidence + 10, max_score)
        
        return confidence


class IntelligentAgent:
    """
    Intelligent agent for receipt field extraction and validation
    Uses Ollama models with learning capabilities
    """
    
    def __init__(self, ollama_service: OllamaService):
        self.ollama = ollama_service
        self.extraction_rules = {}
        self.validation_rules = {}
        self.learning_history = []
        
    def extract_fields(self, ocr_text: str, document_type: str = 'receipt') -> Dict:
        """Extract fields intelligently based on document type"""
        
        # Get base extraction from Ollama
        base_extraction = self.ollama.analyze_receipt(ocr_text)
        
        # Apply learned rules
        enhanced_extraction = self.apply_learned_rules(base_extraction, ocr_text)
        
        # Validate extraction
        validation_result = self.validate_extraction(enhanced_extraction, ocr_text)
        
        # Combine results
        final_result = {
            'fields': enhanced_extraction,
            'validation': validation_result,
            'confidence_scores': self.calculate_field_confidence(enhanced_extraction, validation_result),
            'suggestions': self.generate_suggestions(enhanced_extraction, validation_result)
        }
        
        return final_result
    
    def apply_learned_rules(self, extraction: Dict, ocr_text: str) -> Dict:
        """Apply previously learned extraction rules"""
        enhanced = extraction.copy()
        
        # Apply store-specific rules if store is detected
        if extraction.get('store_info', {}).get('name'):
            store_name = extraction['store_info']['name'].lower()
            if store_name in self.extraction_rules:
                rules = self.extraction_rules[store_name]
                enhanced = self._apply_rules(enhanced, rules, ocr_text)
        
        return enhanced
    
    def _apply_rules(self, data: Dict, rules: Dict, ocr_text: str) -> Dict:
        """Apply specific extraction rules"""
        for field, rule in rules.items():
            if 'pattern' in rule:
                match = re.search(rule['pattern'], ocr_text, re.IGNORECASE)
                if match:
                    # Navigate to the field in data
                    keys = field.split('.')
                    target = data
                    for key in keys[:-1]:
                        if key not in target:
                            target[key] = {}
                        target = target[key]
                    target[keys[-1]] = match.group(1) if match.groups() else match.group(0)
        
        return data
    
    def validate_extraction(self, extraction: Dict, ocr_text: str) -> Dict:
        """Validate extracted data"""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'field_validity': {}
        }
        
        # Validate store info
        if extraction.get('store_info'):
            store_valid = self._validate_store_info(extraction['store_info'])
            validation['field_validity']['store_info'] = store_valid
            if not store_valid['is_valid']:
                validation['errors'].extend(store_valid['errors'])
        
        # Validate financial data
        if extraction.get('financial'):
            financial_valid = self._validate_financial_data(extraction['financial'], extraction.get('items', []))
            validation['field_validity']['financial'] = financial_valid
            if not financial_valid['is_valid']:
                validation['errors'].extend(financial_valid['errors'])
        
        # Validate items
        if extraction.get('items'):
            items_valid = self._validate_items(extraction['items'])
            validation['field_validity']['items'] = items_valid
            if not items_valid['is_valid']:
                validation['warnings'].extend(items_valid['warnings'])
        
        validation['is_valid'] = len(validation['errors']) == 0
        
        return validation
    
    def _validate_store_info(self, store_info: Dict) -> Dict:
        """Validate store information"""
        result = {'is_valid': True, 'errors': [], 'warnings': []}
        
        if not store_info.get('name'):
            result['errors'].append('Store name is missing')
            result['is_valid'] = False
        
        # Validate tax ID format if present
        if store_info.get('tax_id'):
            if not re.match(r'^\d{10,11}$', store_info['tax_id']):
                result['warnings'].append('Tax ID format may be incorrect')
        
        return result
    
    def _validate_financial_data(self, financial: Dict, items: List[Dict]) -> Dict:
        """Validate financial calculations"""
        result = {'is_valid': True, 'errors': [], 'warnings': []}
        
        # Calculate expected total from items
        if items:
            calculated_total = sum(float(item.get('total_price', 0)) for item in items)
            
            if financial.get('subtotal'):
                subtotal = float(financial['subtotal'])
                if abs(calculated_total - subtotal) > 1.0:  # Allow 1 TL difference
                    result['warnings'].append(f'Subtotal mismatch: calculated {calculated_total:.2f}, found {subtotal:.2f}')
            
            # Validate total with tax
            if financial.get('total') and financial.get('tax_amount'):
                total = float(financial['total'])
                tax = float(financial.get('tax_amount', 0))
                expected_total = calculated_total + tax
                
                if abs(expected_total - total) > 1.0:
                    result['errors'].append(f'Total mismatch: expected {expected_total:.2f}, found {total:.2f}')
                    result['is_valid'] = False
        
        return result
    
    def _validate_items(self, items: List[Dict]) -> Dict:
        """Validate items data"""
        result = {'is_valid': True, 'errors': [], 'warnings': []}
        
        for i, item in enumerate(items):
            if not item.get('name'):
                result['warnings'].append(f'Item {i+1} has no name')
            
            # Validate price calculation
            if item.get('quantity') and item.get('unit_price') and item.get('total_price'):
                expected = float(item['quantity']) * float(item['unit_price'])
                actual = float(item['total_price'])
                
                if abs(expected - actual) > 0.1:
                    result['warnings'].append(
                        f'Item {item.get("name", i+1)}: price calculation mismatch'
                    )
        
        return result
    
    def calculate_field_confidence(self, extraction: Dict, validation: Dict) -> Dict:
        """Calculate confidence scores for each field"""
        confidence_scores = {}
        
        # Base confidence from Ollama
        if extraction.get('validation', {}).get('confidence'):
            base_confidence = extraction['validation']['confidence']
        else:
            base_confidence = 50
        
        # Adjust based on validation
        for field, validity in validation.get('field_validity', {}).items():
            if validity['is_valid']:
                confidence_scores[field] = min(base_confidence + 20, 100)
            else:
                confidence_scores[field] = max(base_confidence - 30, 0)
        
        # Individual field confidence
        if extraction.get('store_info', {}).get('name'):
            confidence_scores['store_name'] = 90 if validation['is_valid'] else 60
        
        if extraction.get('financial', {}).get('total'):
            confidence_scores['total_amount'] = 85 if validation['is_valid'] else 50
        
        return confidence_scores
    
    def generate_suggestions(self, extraction: Dict, validation: Dict) -> List[Dict]:
        """Generate suggestions for improving extraction"""
        suggestions = []
        
        # Suggest corrections for validation errors
        for error in validation.get('errors', []):
            if 'mismatch' in error.lower():
                suggestions.append({
                    'type': 'correction',
                    'field': 'financial',
                    'message': 'Review financial calculations',
                    'priority': 'high'
                })
        
        # Suggest missing fields
        if not extraction.get('store_info', {}).get('name'):
            suggestions.append({
                'type': 'missing',
                'field': 'store_name',
                'message': 'Store name could not be detected',
                'priority': 'medium'
            })
        
        if not extraction.get('items'):
            suggestions.append({
                'type': 'missing',
                'field': 'items',
                'message': 'No items were detected',
                'priority': 'high'
            })
        
        return suggestions
    
    def learn_from_feedback(self, original_extraction: Dict, corrections: Dict, 
                           ocr_text: str, store_name: str = None):
        """Learn from user corrections"""
        
        # Record learning history
        self.learning_history.append({
            'timestamp': datetime.now(),
            'original': original_extraction,
            'corrections': corrections,
            'store': store_name
        })
        
        # Extract patterns from corrections
        if store_name:
            if store_name not in self.extraction_rules:
                self.extraction_rules[store_name] = {}
            
            # Learn field positions
            for field, corrected_value in corrections.items():
                if corrected_value and corrected_value != original_extraction.get(field):
                    # Find pattern in OCR text
                    pattern = self._find_pattern(corrected_value, ocr_text)
                    if pattern:
                        self.extraction_rules[store_name][field] = {
                            'pattern': pattern,
                            'confidence': 0.8
                        }
        
        # Update validation rules based on corrections
        self._update_validation_rules(corrections)
        
        logger.info(f"Learned from feedback: {len(corrections)} corrections for {store_name or 'unknown store'}")
    
    def _find_pattern(self, value: str, text: str) -> Optional[str]:
        """Find extraction pattern for a value in text"""
        # Escape special regex characters in value
        escaped_value = re.escape(str(value))
        
        # Look for the value with context
        pattern = rf'(\w+[\s:]*){escaped_value}'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            # Create a pattern that captures the value
            context = match.group(1)
            return rf'{re.escape(context)}([\d\w\s,.]+)'
        
        return None
    
    def _update_validation_rules(self, corrections: Dict):
        """Update validation rules based on corrections"""
        # Analyze correction patterns
        for field, value in corrections.items():
            if field not in self.validation_rules:
                self.validation_rules[field] = {
                    'format': None,
                    'range': None,
                    'required': True
                }
            
            # Learn format patterns
            if isinstance(value, str):
                if re.match(r'^\d{2}[-/.]\d{2}[-/.]\d{4}$', value):
                    self.validation_rules[field]['format'] = 'date'
                elif re.match(r'^\d+([,.]\d{2})?$', value):
                    self.validation_rules[field]['format'] = 'currency'
            
            # Learn value ranges
            if isinstance(value, (int, float)):
                if 'range' not in self.validation_rules[field]:
                    self.validation_rules[field]['range'] = {'min': value, 'max': value}
                else:
                    self.validation_rules[field]['range']['min'] = min(
                        self.validation_rules[field]['range']['min'], value
                    )
                    self.validation_rules[field]['range']['max'] = max(
                        self.validation_rules[field]['range']['max'], value
                    )