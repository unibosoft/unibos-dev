# 🎯 documents

## 📋 overview
intelligent document management system with advanced OCR processing, AI-powered analysis, and automated data extraction. handles receipts, invoices, contracts, and general documents with full-text search, categorization, and cross-module integration for financial and inventory tracking.

## 🔧 current capabilities
### ✅ fully functional
- **multi-format OCR** - extracts text from JPG, PNG, PDF with 85%+ accuracy
- **AI invoice processing** - parses receipts with store, items, prices (77.8% accuracy)
- **batch upload** - processes 50-100 documents simultaneously
- **thumbnail generation** - automatic preview images for all documents
- **full-text search** - searches across OCR text and metadata
- **tag system** - hierarchical tagging with custom categories
- **recycle bin** - soft delete with 30-day recovery period
- **document sharing** - secure sharing links with expiry dates
- **gamification** - points and achievements for document processing

### 🚧 in development
- multi-language OCR (English, Arabic in testing)
- handwriting recognition
- document templates for common formats
- automatic categorization using ML

### 📅 planned features
- digital signature verification
- document workflow automation
- cloud storage integration (Google Drive, Dropbox)
- mobile app scanning

## 💻 technical implementation
### core functions
- `Document` model - main document storage with metadata
- `ParsedReceipt` model - structured receipt data
- `ReceiptItem` model - individual line items from receipts
- `OCRTemplate` model - store-specific parsing templates
- `advanced_ocr_parser.py` - OCR processing pipeline
- `ai_ocr_enhancer.py` - AI enhancement using Mistral/Ollama
- `document_detector.py` - document type classification
- `thumbnail_service.py` - preview generation

### database models
- `Document` - file storage, OCR text, processing status
- `ParsedReceipt` - structured receipt data (store, date, total)
- `ReceiptItem` - line items with prices and quantities
- `DocumentBatch` - batch upload tracking
- `OCRTemplate` - parsing rules for known stores
- `DocumentShare` - sharing links and permissions

### api integrations
- **Tesseract OCR** - primary text extraction (Turkish + English)
- **Ollama/Llama2** - local AI for invoice parsing
- **Mistral API** - cloud AI fallback (optional)
- **HuggingFace** - document classification models
- **OpenCV** - image preprocessing and enhancement

## 🎮 how to use
1. navigate to main menu
2. select "modules" (m)
3. choose "📄 documents" (d)
4. main document hub options:
   - press '1' for browse documents
   - press '2' for search
   - press '3' for upload (drag & drop supported)
   - press '4' for OCR scanner
   - press '5' for invoice processor
   - press '6' for tag manager
   - press '7' for analytics dashboard
   - press '8' for recycle bin
5. invoice processor workflow:
   - upload receipt image
   - system auto-detects store and date
   - review extracted items
   - confirm or edit details
   - data syncs to kişisel enflasyon

## 📊 data flow
- **input sources**:
  - file uploads (web/CLI interface)
  - scanner integration
  - email attachments (via API)
  - mobile app photos
- **processing steps**:
  1. file validation and virus scan
  2. thumbnail generation
  3. OCR text extraction
  4. AI enhancement for invoices
  5. data structuring and validation
  6. cross-module data sync
- **output destinations**:
  - PostgreSQL database (metadata)
  - file system (documents + thumbnails)
  - kişisel enflasyon (price data)
  - WIMM (financial records)
  - WIMS (inventory updates)

## 🔌 integrations
- **kişisel enflasyon** - automatic product price tracking from receipts
- **WIMM** - links documents to transactions and invoices
- **WIMS** - updates inventory from purchase documents
- **currencies** - converts foreign currency receipts
- **restopos** - imports supplier invoices

## ⚡ performance metrics
- OCR processing: 2-5 seconds per page
- AI parsing: 3-7 seconds per receipt
- batch upload: 100 files in <2 minutes
- thumbnail generation: <500ms per image
- search query: <100ms for 10,000 documents
- supports 500GB+ document storage

## 🐛 known limitations
- OCR accuracy drops to 60% for handwritten text
- PDF processing limited to 100 pages
- AI parsing requires 4GB+ RAM for local models
- some Turkish store formats need manual templates
- batch uploads timeout at 500 files

## 📈 version history
- v0.5 - basic document upload and storage
- v0.7 - added Tesseract OCR integration
- v0.9 - AI invoice parsing with Ollama
- v1.0 - full feature set with gamification
- v1.1 - improved Turkish receipt accuracy
- v1.2 - batch processing optimizations

## 🛠️ development status
**completion: 78%**
- document storage: ✅ complete
- OCR processing: ✅ complete
- AI parsing: ✅ complete
- search system: ✅ complete
- gamification: ✅ complete
- multi-language OCR: 🚧 in progress (40%)
- handwriting recognition: 📅 planned
- cloud integration: 📅 planned