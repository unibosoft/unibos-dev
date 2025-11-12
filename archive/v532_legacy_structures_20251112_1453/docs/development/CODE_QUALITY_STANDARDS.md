# 🎯 CODE QUALITY STANDARDS

> **Amaç:** UNIBOS projesinde kod kalitesi, güvenlik ve best practice standartları.
> **Ref:** [CLAUDE_SESSION_PROTOCOL.md](CLAUDE_SESSION_PROTOCOL.md) - Oturum protokolü

---

## 🌍 TİMEZONE ENFORCEMENT (KRİTİK!)

### Istanbul Timezone Kuralı

**MUTLAKA:** Tüm timestamp'ler Istanbul timezone'da olmalı!

```python
# ❌ YANLIŞ: UTC veya sistem timezone
from datetime import datetime
now = datetime.now()  # Sistem timezone kullanır

# ✅ DOĞRU: Istanbul timezone explicit
import pytz
from datetime import datetime

ISTANBUL_TZ = pytz.timezone('Europe/Istanbul')
now = datetime.now(ISTANBUL_TZ)

# veya Django settings'de:
TIME_ZONE = 'Europe/Istanbul'
USE_TZ = True
```

### Kontrol Listesi

**Her timestamp oluşturduğunda:**
- [ ] `Europe/Istanbul` timezone kullanıldı mı?
- [ ] `USE_TZ = True` Django settings'de aktif mi?
- [ ] Model'lerdeki `DateTimeField` timezone-aware mı?
- [ ] API response'larda timezone bilgisi var mı?

### Test Etme

```python
# Django shell'de test et
from django.utils import timezone
import pytz

ISTANBUL_TZ = pytz.timezone('Europe/Istanbul')
now = timezone.now().astimezone(ISTANBUL_TZ)

print(now)  # 2025-11-09 14:30:45+03:00
print(now.tzinfo)  # Europe/Istanbul
```

**Beklenen Çıktı:** `+03:00` veya `+02:00` (DST'ye göre)

### Yaygın Hatalar ve Çözümleri

#### Hata 1: Naive Datetime

```python
# ❌ YANLIŞ
from datetime import datetime
timestamp = datetime.now()  # Naive datetime (timezone yok)

# ✅ DOĞRU
from django.utils import timezone
import pytz

ISTANBUL_TZ = pytz.timezone('Europe/Istanbul')
timestamp = timezone.now().astimezone(ISTANBUL_TZ)
```

#### Hata 2: UTC ile Karıştırma

```python
# ❌ YANLIŞ
import datetime
timestamp = datetime.datetime.utcnow()  # UTC, Istanbul değil!

# ✅ DOĞRU
from django.utils import timezone
import pytz

ISTANBUL_TZ = pytz.timezone('Europe/Istanbul')
timestamp = timezone.now().astimezone(ISTANBUL_TZ)
```

#### Hata 3: String'den Parse Ederken

```python
# ❌ YANLIŞ
from datetime import datetime
dt = datetime.strptime("2025-11-09 14:30:45", "%Y-%m-%d %H:%M:%S")  # Naive!

# ✅ DOĞRU
from datetime import datetime
import pytz

ISTANBUL_TZ = pytz.timezone('Europe/Istanbul')
dt = datetime.strptime("2025-11-09 14:30:45", "%Y-%m-%d %H:%M:%S")
dt = ISTANBUL_TZ.localize(dt)
```

---

## 🛡️ CRASH PREVENTION (Anti-Crash Checks)

### Null/None Checks

**Kural:** Her external input, database query veya API call sonrası null check yapılmalı!

```python
# ❌ YANLIŞ: Null check yok
def get_document_owner(document_id):
    document = Document.objects.get(id=document_id)
    return document.owner.username  # owner None olabilir! CRASH!

# ✅ DOĞRU: Null check var
def get_document_owner(document_id):
    try:
        document = Document.objects.get(id=document_id)
        if document and document.owner:
            return document.owner.username
        return "Unknown Owner"
    except Document.DoesNotExist:
        return "Document Not Found"
```

### Try-Except Best Practices

```python
# ❌ YANLIŞ: Genel exception catch
try:
    # risky operation
    pass
except:  # Çok geniş!
    pass

# ✅ DOĞRU: Specific exceptions
try:
    document = Document.objects.get(id=doc_id)
except Document.DoesNotExist:
    logger.warning(f"Document {doc_id} not found")
    return None
except ValidationError as e:
    logger.error(f"Validation error: {e}")
    return None
```

### Database Query Güvenliği

```python
# ❌ YANLIŞ: .get() crash edebilir
document = Document.objects.get(id=doc_id)  # DoesNotExist!

# ✅ DOĞRU: .filter().first() güvenli
document = Document.objects.filter(id=doc_id).first()
if not document:
    return HttpResponseNotFound()

# veya try-except kullan
try:
    document = Document.objects.get(id=doc_id)
except Document.DoesNotExist:
    return HttpResponseNotFound()
```

### API Call Güvenliği

```python
# ❌ YANLIŞ: Timeout yok, error handling yok
import requests
response = requests.get(api_url)
data = response.json()

# ✅ DOĞRU: Timeout, error handling, retry logic
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def safe_api_call(url, timeout=10):
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.3)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error(f"Timeout calling {url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"API call failed: {e}")
        return None
```

---

## 🔧 DJANGO SERVER RESTART KURALLLARI

### Restart Gerektiren Değişiklikler

**MUTLAKA restart et:**
- Python kod değişiklikleri (`.py` dosyaları)
- Model değişiklikleri
- Settings değişiklikleri
- URL routing değişiklikleri
- Yeni dependency ekleme (`pip install`)

**Restart GEREKMİYOR:**
- Template değişiklikleri (`.html`)
- Static files (CSS, JS) - `collectstatic` sonrası
- Database içerik değişiklikleri

### Development Server Restart

```bash
# Runserver otomatik restart eder, ancak bazen manuel gerekir

# 1. Ctrl+C ile durdur
# 2. Yeniden başlat:
cd /Users/berkhatirli/Desktop/unibos/apps/web/backend
DJANGO_SETTINGS_MODULE=unibos_backend.settings.development \
  ./venv/bin/python3 manage.py runserver

# veya Daphne (ASGI):
DJANGO_SETTINGS_MODULE=unibos_backend.settings.development \
  ./venv/bin/daphne -b 0.0.0.0 -p 8000 unibos_backend.asgi:application
```

### Production Server Restart

```bash
# ASLA manuel komut kullanma!
# Script kullan:
./tools/scripts/rocksteady_deploy.sh deploy

# Bu script otomatik olarak:
# 1. Git pull
# 2. Dependency install
# 3. Migration
# 4. Collectstatic
# 5. Gunicorn restart
# 6. Nginx restart
```

### Celery Restart (Background Tasks)

```bash
# Development:
pkill -f celery
cd /Users/berkhatirli/Desktop/unibos/apps/web/backend
./start_celery.sh

# Production (script içinde):
# sudo systemctl restart celery
# sudo systemctl restart celery-beat
```

---

## 📝 CODE STYLE STANDARDS

### Python (PEP 8)

```python
# Imports: Standard library → Third party → Local
import os
import sys

import django
from django.db import models

from apps.documents.models import Document

# Class names: PascalCase
class DocumentAnalyzer:
    pass

# Function names: snake_case
def analyze_document(document_id):
    pass

# Constants: UPPER_CASE
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

### Django Best Practices

```python
# ✅ DOĞRU: Manager kullan
class Document(models.Model):
    # ...

    @classmethod
    def get_active_documents(cls):
        return cls.objects.filter(is_active=True)

# ❌ YANLIŞ: View'da business logic
def document_list(request):
    docs = Document.objects.filter(is_active=True, owner=request.user)
    # Çok fazla logic view'da!
    # ...

# ✅ DOĞRU: Manager/Service layer kullan
class DocumentManager(models.Manager):
    def get_user_active_documents(self, user):
        return self.filter(is_active=True, owner=user)

class Document(models.Model):
    objects = DocumentManager()
    # ...

def document_list(request):
    docs = Document.objects.get_user_active_documents(request.user)
    # View temiz!
```

### SQL Injection Prevention

```python
# ❌ YANLIŞ: SQL injection riski
from django.db import connection

def get_documents(owner_name):
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM documents WHERE owner='{owner_name}'")
    # SQL INJECTION!

# ✅ DOĞRU: Parameterized queries
from django.db import connection

def get_documents(owner_name):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM documents WHERE owner=%s", [owner_name])

# veya daha iyisi: ORM kullan
def get_documents(owner_name):
    return Document.objects.filter(owner__username=owner_name)
```

### XSS Prevention

```django
{# ❌ YANLIŞ: XSS riski #}
{{ user_input|safe }}  {# DANGEROUS! #}

{# ✅ DOĞRU: Auto-escape #}
{{ user_input }}  {# Django otomatik escape eder #}

{# veya explicit escape: #}
{{ user_input|escape }}
```

---

## 🧪 TESTING STANDARDS

### Test Coverage

**Minimum coverage:** %70 (hedef: %90)

```bash
# Coverage report
cd apps/web/backend
./venv/bin/pytest --cov=apps --cov-report=html

# Report'u aç
open htmlcov/index.html
```

### Test Yazma Kuralları

```python
# Test dosyası: test_*.py veya *_test.py
# Test class: Test* ile başlamalı
# Test method: test_* ile başlamalı

import pytest
from django.test import TestCase
from apps.documents.models import Document

class TestDocumentModel(TestCase):
    def setUp(self):
        # Her test öncesi çalışır
        self.document = Document.objects.create(
            title="Test Doc",
            # ...
        )

    def test_document_creation(self):
        """Document başarıyla oluşturulmalı"""
        self.assertIsNotNone(self.document.id)
        self.assertEqual(self.document.title, "Test Doc")

    def test_document_owner_null_handling(self):
        """Owner None olduğunda crash etmemeli"""
        self.document.owner = None
        self.document.save()

        # get_owner_name() None-safe olmalı
        owner_name = self.document.get_owner_name()
        self.assertEqual(owner_name, "Unknown")

    def tearDown(self):
        # Her test sonrası cleanup
        pass
```

---

## 🔒 SECURITY CHECKLIST

### Her Feature için Kontrol Et:

- [ ] **SQL Injection:** Parameterized queries kullanıldı mı?
- [ ] **XSS:** User input escape ediliyor mu?
- [ ] **CSRF:** Django CSRF token'ı kullanılıyor mu?
- [ ] **Authentication:** Login required decorator var mı?
- [ ] **Authorization:** User permission check var mı?
- [ ] **File Upload:** File type/size validation var mı?
- [ ] **Secrets:** API keys/passwords environment variable'da mı?
- [ ] **HTTPS:** Production'da HTTPS zorunlu mu?

### Django Security Settings

```python
# settings.py (production)

# HTTPS enforcement
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

## 📊 PERFORMANCE BEST PRACTICES

### Database Query Optimization

```python
# ❌ YANLIŞ: N+1 problem
documents = Document.objects.all()
for doc in documents:
    print(doc.owner.username)  # Her iterasyonda DB query!

# ✅ DOĞRU: select_related (ForeignKey)
documents = Document.objects.select_related('owner').all()
for doc in documents:
    print(doc.owner.username)  # Tek query!

# ✅ DOĞRU: prefetch_related (ManyToMany)
documents = Document.objects.prefetch_related('tags').all()
for doc in documents:
    print(doc.tags.all())  # Optimize edilmiş!
```

### Caching

```python
from django.core.cache import cache

# Cache kullan
def get_expensive_data(key):
    data = cache.get(key)
    if data is None:
        # Cache miss - compute
        data = expensive_computation()
        cache.set(key, data, timeout=3600)  # 1 hour
    return data
```

### Async Support (Django 4.2+)

```python
# Async view
from django.http import JsonResponse
import asyncio

async def async_document_list(request):
    documents = await Document.objects.filter(is_active=True).all()
    return JsonResponse({'documents': list(documents.values())})
```

---

## ✅ PRE-COMMIT CHECKLIST

Her commit öncesi kontrol et:

### Code Quality
- [ ] PEP 8 uyumlu (linter pass)
- [ ] Type hints eklenmiş (Python 3.9+)
- [ ] Docstrings yazılmış
- [ ] TODO/FIXME'ler temizlenmiş veya documented

### Functionality
- [ ] Istanbul timezone kullanıldı
- [ ] Null checks var
- [ ] Error handling var
- [ ] Tests yazıldı ve pass

### Security
- [ ] SQL injection korumalı
- [ ] XSS korumalı
- [ ] CSRF token var
- [ ] Secrets hardcoded değil

### Django Specific
- [ ] Migration oluşturuldu (`makemigrations`)
- [ ] Migration çalıştırıldı (`migrate`)
- [ ] Server test edildi (crash yok)
- [ ] Static files collect edildi (gerekirse)

---

## 🔗 İLGİLİ DOSYALAR

- **[CLAUDE_SESSION_PROTOCOL.md](CLAUDE_SESSION_PROTOCOL.md)** ← Oturum protokolü
- **[SCREENSHOT_MANAGEMENT.md](SCREENSHOT_MANAGEMENT.md)** ← Screenshot yönetimi
- **[VERSIONING_RULES.md](VERSIONING_RULES.md)** ← Versiyonlama kuralları
- **[RULES.md](../../RULES.md)** ← Ana kurallar

---

## 📝 Son Güncelleme

**Tarih:** 2025-11-09
**Değişiklik:** İlk oluşturma - Kod kalitesi standartları dokümante edildi
**Neden:** Istanbul timezone enforcement, crash prevention, Django best practices standardizasyonu

---

**⬆️ Üst Dosya:** [CLAUDE_SESSION_PROTOCOL.md](CLAUDE_SESSION_PROTOCOL.md)
