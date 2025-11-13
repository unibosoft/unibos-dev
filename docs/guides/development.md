# UNIBOS Development Guide

**Last Updated:** 2025-11-13
**Target Version:** v533+

---

## Overview

This guide covers the daily development workflow for UNIBOS, from making changes to testing and deploying.

---

## Prerequisites

Before starting development:

1. ✅ Completed [setup.md](setup.md)
2. ✅ UNIBOS CLI installed (`unibos --version`)
3. ✅ Development environment running
4. ✅ Read [RULES.md](../../RULES.md) in root directory

---

## Quick Start

```bash
# 1. Start development server
cd /path/to/unibos
unibos dev run

# 2. Open browser
open http://127.0.0.1:8000

# 3. Make changes to code

# 4. Django auto-reloads (watch console)

# 5. Test changes
unibos dev test

# 6. Check status
unibos status
```

---

## Development Workflow

### Daily Routine

#### Morning Checklist

```bash
# 1. Pull latest changes
git pull origin v533_migration

# 2. Update dependencies (if changed)
cd core/web
source venv/bin/activate
pip install -r requirements.txt

# 3. Run migrations (if any)
unibos db migrate

# 4. Check system status
unibos status --detailed

# 5. Start development server
unibos dev run
```

#### During Development

```bash
# Make changes to code...

# Run tests frequently
unibos dev test modules.birlikteyiz

# Check logs
unibos dev logs --follow

# Django shell for debugging
unibos dev shell
```

#### End of Day

```bash
# 1. Run all tests
unibos dev test

# 2. Check for uncommitted changes
git status

# 3. Commit work
git add .
git commit -m "feat(module): description"

# 4. Push to remote
git push origin v533_migration
```

---

## Project Structure

### v533 Architecture

UNIBOS v533 uses a two-layer structure:

```
unibos/
├── core/                 # Core functionality
│   ├── cli/              # CLI tool
│   ├── web/              # Django web app
│   │   ├── unibos_backend/  # Main Django project
│   │   ├── apps/         # Core Django apps
│   │   │   ├── authentication/
│   │   │   ├── common/
│   │   │   ├── core/
│   │   │   ├── users/
│   │   │   └── web_ui/
│   │   └── manage.py
│   └── deployment/       # Deployment scripts
├── modules/              # UNIBOS modules
│   ├── birlikteyiz/      # Earthquake tracking
│   ├── documents/        # Document management
│   ├── music/            # Music library
│   ├── personal_inflation/  # Expense tracking
│   ├── restopos/         # Restaurant finder
│   ├── wimm/             # Personal finance
│   └── ...
└── data/                 # Runtime data (gitignored)
    ├── modules/          # Module file uploads
    │   ├── documents/
    │   ├── music/
    │   └── wimm/
    └── shared/           # Shared data
```

### Module Structure

Each module follows this structure:

```
modules/<module_name>/
├── __init__.py
├── models.py           # Database models
├── views.py            # Views/API endpoints
├── urls.py             # URL routing
├── admin.py            # Django admin integration
├── tests.py            # Tests
├── templates/          # HTML templates
│   └── <module_name>/
├── static/             # Static files (JS, CSS, images)
│   └── <module_name>/
└── migrations/         # Database migrations
```

---

## Creating a New Module

### Step 1: Create Module Directory

```bash
mkdir -p modules/mymodule
cd modules/mymodule
touch __init__.py
```

### Step 2: Create Models

`modules/mymodule/models.py`:

```python
from django.db import models
from apps.core.models import TimestampedModel

class MyModel(TimestampedModel):
    """Example model."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to='mymodule/uploads/',  # Relative to MEDIA_ROOT
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'mymodule_mymodel'
        verbose_name = 'My Model'
        verbose_name_plural = 'My Models'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
```

### Step 3: Create Views

`modules/mymodule/views.py`:

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import MyModel

@login_required
def index(request):
    """Module index view."""
    items = MyModel.objects.all()
    return render(request, 'mymodule/index.html', {
        'items': items
    })
```

### Step 4: Create URLs

`modules/mymodule/urls.py`:

```python
from django.urls import path
from . import views

app_name = 'mymodule'

urlpatterns = [
    path('', views.index, name='index'),
]
```

### Step 5: Register Module

Add to `core/web/unibos_backend/urls.py`:

```python
urlpatterns = [
    # ... existing patterns ...
    path('mymodule/', include('modules.mymodule.urls')),
]
```

### Step 6: Create Migrations

```bash
unibos dev makemigrations mymodule
unibos dev migrate
```

### Step 7: Register in Admin

`modules/mymodule/admin.py`:

```python
from django.contrib import admin
from .models import MyModel

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
```

### Step 8: Create Templates

`modules/mymodule/templates/mymodule/index.html`:

```html
{% extends "base.html" %}

{% block title %}My Module{% endblock %}

{% block content %}
<div class="container">
    <h1>My Module</h1>

    {% for item in items %}
    <div class="item">
        <h2>{{ item.name }}</h2>
        <p>{{ item.description }}</p>
    </div>
    {% endfor %}
</div>
{% endblock %}
```

### Step 9: Create Data Directory

```bash
mkdir -p data/modules/mymodule
```

### Step 10: Write Tests

`modules/mymodule/tests.py`:

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import MyModel

User = get_user_model()

class MyModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )

    def test_create_model(self):
        """Test creating a MyModel instance."""
        obj = MyModel.objects.create(
            name='Test',
            description='Test description'
        )
        self.assertEqual(obj.name, 'Test')
        self.assertTrue(obj.created_at)
```

Run tests:

```bash
unibos dev test mymodule
```

---

## Working with Existing Modules

### Finding Module Code

```bash
# List all modules
ls modules/

# Search for specific functionality
grep -r "earthquake" modules/

# Find FileField usage
grep -r "FileField\|ImageField" modules/*/models.py
```

### Understanding Module Data Paths

All module file uploads go to `data/modules/<module>/`:

```python
# Example: Document upload
file = models.FileField(upload_to='documents/uploads/')

# Final path: /data/modules/documents/uploads/filename.pdf
```

**Important:** MEDIA_ROOT is set to `data/modules/`, so FileField paths are relative to that.

### Modifying Existing Modules

1. **Read the code** - Understand current implementation
2. **Check tests** - Ensure existing tests pass
3. **Make changes** - Implement your changes
4. **Update tests** - Add tests for new functionality
5. **Run migrations** - If models changed
6. **Test thoroughly** - Run all module tests
7. **Commit** - Use conventional commits

Example workflow:

```bash
# 1. Read the code
cat modules/birlikteyiz/models.py

# 2. Check existing tests
unibos dev test birlikteyiz

# 3. Make changes
vim modules/birlikteyiz/models.py

# 4. Create migration if needed
unibos dev makemigrations birlikteyiz

# 5. Run migration
unibos dev migrate

# 6. Test
unibos dev test birlikteyiz

# 7. Commit
git add modules/birlikteyiz/
git commit -m "feat(birlikteyiz): add earthquake filtering"
```

---

## Database Management

### Creating Migrations

```bash
# Auto-detect changes
unibos dev makemigrations

# For specific module
unibos dev makemigrations birlikteyiz

# With custom name
unibos dev makemigrations birlikteyiz --name add_magnitude_filter
```

### Running Migrations

```bash
# Run all pending migrations
unibos db migrate

# Run specific migration
unibos db migrate birlikteyiz 0002

# Show migration plan (dry run)
unibos db migrate --plan

# Fake migration (mark as applied)
unibos db migrate --fake
```

### Migration Status

```bash
# Show all migrations
unibos db status

# Show pending only
unibos db status --pending

# Show for specific app
unibos db status birlikteyiz
```

### Database Shell

```bash
# Django shell
unibos dev shell

# Direct database access (PostgreSQL)
psql -U unibos -d unibos

# Direct database access (SQLite)
sqlite3 core/web/db.sqlite3
```

---

## Testing

### Running Tests

```bash
# All tests
unibos dev test

# Specific module
unibos dev test modules.birlikteyiz

# Specific test class
unibos dev test modules.birlikteyiz.tests.EarthquakeTestCase

# Specific test method
unibos dev test modules.birlikteyiz.tests.EarthquakeTestCase.test_create_earthquake

# With coverage
unibos dev test --coverage

# Keep database (faster for repeated runs)
unibos dev test --keepdb
```

### Writing Tests

Follow Django's testing best practices:

```python
from django.test import TestCase, Client
from django.urls import reverse
from .models import MyModel

class MyModelTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.obj = MyModel.objects.create(name='Test')

    def test_model_creation(self):
        """Test model creation."""
        self.assertEqual(self.obj.name, 'Test')

    def test_view_access(self):
        """Test view access."""
        response = self.client.get(reverse('mymodule:index'))
        self.assertEqual(response.status_code, 200)

    def test_model_str(self):
        """Test string representation."""
        self.assertEqual(str(self.obj), 'Test')
```

---

## Debugging

### Django Shell

```bash
unibos dev shell
```

Example debugging session:

```python
# Import models
from modules.birlikteyiz.models import Earthquake

# Query data
earthquakes = Earthquake.objects.filter(magnitude__gte=5.0)
print(f"Found {earthquakes.count()} large earthquakes")

# Inspect object
eq = earthquakes.first()
print(f"ID: {eq.id}")
print(f"Magnitude: {eq.magnitude}")
print(f"Location: {eq.location}")

# Test functionality
from modules.birlikteyiz.utils import fetch_earthquakes
data = fetch_earthquakes()
print(f"Fetched {len(data)} earthquakes from API")
```

### Logging

UNIBOS uses Python's logging module:

```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

View logs:

```bash
# Tail logs
unibos dev logs --follow

# Filter by level
unibos dev logs --level ERROR

# Last 100 lines
unibos dev logs --lines 100
```

### Django Debug Toolbar

If installed, access at: [http://127.0.0.1:8000/__debug__/](http://127.0.0.1:8000/__debug__/)

---

## Code Style

### Python Style Guide

- Follow PEP 8
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use docstrings for all functions/classes

### Imports Order

```python
# Standard library
import os
import sys

# Django
from django.db import models
from django.shortcuts import render

# Third-party
import requests

# Local
from apps.core.models import TimestampedModel
from .utils import helper_function
```

### Naming Conventions

- **Models:** `PascalCase` (e.g., `Earthquake`, `MyModel`)
- **Functions/methods:** `snake_case` (e.g., `fetch_earthquakes`)
- **Variables:** `snake_case` (e.g., `earthquake_data`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_RESULTS`)
- **Private:** `_leading_underscore` (e.g., `_internal_function`)

---

## Git Workflow

### Branches

- `main` - Stable production branch
- `v533_migration` - Current development branch
- `feature/<name>` - Feature branches
- `fix/<name>` - Bug fix branches

### Commit Messages

Follow Conventional Commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Code style (formatting, no logic change)
- `refactor` - Code refactoring
- `test` - Adding tests
- `chore` - Maintenance tasks

**Examples:**

```bash
git commit -m "feat(birlikteyiz): add magnitude filter to earthquake map"
git commit -m "fix(documents): correct thumbnail generation path"
git commit -m "docs: update development guide with v533 structure"
git commit -m "refactor(cli): extract splash screen to separate module"
```

### Daily Workflow

```bash
# Start of day
git pull origin v533_migration

# Make changes...
# ... code, test, repeat ...

# Commit
git add .
git commit -m "feat(module): description"

# Push
git push origin v533_migration
```

---

## Common Tasks

### Add a New Model Field

```bash
# 1. Edit models.py
vim modules/mymodule/models.py

# 2. Create migration
unibos dev makemigrations mymodule

# 3. Review migration
cat modules/mymodule/migrations/000X_*.py

# 4. Run migration
unibos db migrate

# 5. Test
unibos dev test mymodule
```

### Update Dependencies

```bash
# Add new package
pip install new-package

# Update requirements.txt
pip freeze > core/web/requirements.txt

# Commit
git add core/web/requirements.txt
git commit -m "chore: add new-package dependency"
```

### Clear Database and Start Fresh

```bash
# ⚠️ WARNING: This deletes all data!

# Backup first
unibos db backup

# Remove database
rm core/web/db.sqlite3

# Remove migrations (optional, for clean slate)
find modules -name "migrations" -type d -exec rm -rf {}/0*.py \;

# Recreate migrations
unibos dev makemigrations

# Run migrations
unibos db migrate

# Create superuser
unibos dev shell
# ... create user in shell ...
```

---

## Next Steps

- **Deployment:** [deployment.md](deployment.md)
- **Troubleshooting:** [troubleshooting.md](troubleshooting.md)
- **Architecture:** [../design/v533-architecture.md](../design/v533-architecture.md)

---

## See Also

- **Rules:** [../../RULES.md](../../RULES.md)
- **TODO:** [../../TODO.md](../../TODO.md)
- **CLI Guide:** [cli.md](cli.md)

---

**Questions?** Check [troubleshooting.md](troubleshooting.md) or create an issue.
