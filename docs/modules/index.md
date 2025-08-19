# 🎯 unibos modules documentation

## 📋 overview
comprehensive documentation for all unibos modules, tools, and development utilities. each module follows a standardized format with detailed technical specifications, usage instructions, and development status.

## 📊 documentation standards

each module documentation includes:
- 📋 **overview** - comprehensive description of functionality
- 🔧 **current capabilities** - features that are fully functional
- 🚧 **in development** - features being actively worked on
- 📅 **planned features** - roadmap for future development
- 💻 **technical implementation** - core functions and architecture
- 🎮 **how to use** - step-by-step usage instructions
- 📊 **data flow** - input sources, processing, and outputs
- 🔌 **integrations** - connections with other modules
- ⚡ **performance metrics** - speed, capacity, and benchmarks
- 🐛 **known limitations** - current constraints and workarounds
- 📈 **version history** - evolution timeline
- 🛠️ **development status** - completion percentage with breakdown

## 🚀 main modules

### core applications
- [🪐 recaria](recaria.md) - space exploration and simulation platform (65% complete)
- [📡 birlikteyiz](birlikteyiz.md) - decentralized mesh network communication (70% complete)
- [📈 kişisel enflasyon](kisisel_enflasyon.md) - personal inflation tracking system (82% complete)
- [💰 currencies](currencies.md) - real-time exchange rates and crypto tracking (85% complete)

### business systems
- [💸 wimm](wimm.md) - comprehensive financial management (75% complete)
- [📦 wims](wims.md) - inventory and asset management (72% complete)
- [🍽️ restopos](restopos.md) - professional restaurant POS system (80% complete)

### content management
- [📄 documents](documents.md) - intelligent document processing with OCR (78% complete)
- [🎬 movies](movies.md) - movie and TV series collection manager (75% complete)
- [🎵 music](music.md) - spotify-integrated music management (78% complete)

## 🛠️ system tools

### administration & maintenance
- [🔮 system scrolls](system_scrolls.md) - comprehensive system monitoring (88% complete)
- [🔒 castle guard](castle_guard.md) - security management and access control (85% complete)
- [🔧 forge smithy](forge_smithy.md) - system setup and configuration (82% complete)
- [🛠️ anvil repair](anvil_repair.md) - system repair and maintenance (79% complete)

### development tools
- [📦 code forge](code_forge.md) - integrated development environment (76% complete)
- [🌐 web ui](web_ui.md) - web server management platform (83% complete)

## 💻 developer tools

### specialized utilities
- [🤖 ai builder](ai_builder.md) - AI integration and development platform (74% complete)
- [🗄️ database setup](database_setup.md) - database management toolkit (81% complete)
- [💾 sd card](sd_card.md) - raspberry pi SD card management (77% complete)
- [📊 version manager](version_manager.md) - version control and releases (86% complete)

## 🎮 navigation guide

### keyboard shortcuts (CLI)
- `m` - open modules menu
- `t` - open tools menu
- `d` - open dev tools menu
- `↑↓` - navigate up/down
- `←→` - back/forward navigation
- `enter` - select item
- `esc`/`q` - go back/quit
- `h` - help/documentation
- `1-9` - quick select items

### access patterns
1. **modules**: main menu → modules (m) → select module
2. **tools**: main menu → tools (t) → select tool
3. **dev tools**: main menu → dev tools (d) → select utility

### web interface
- **base url**: http://localhost:8000/
- **modules**: http://localhost:8000/modules/{module-name}/
- **api docs**: http://localhost:8000/api/docs/
- **admin**: http://localhost:8000/admin/

## 🔌 integration matrix

### cross-module data flows
```
documents → kişisel enflasyon (receipt OCR → price tracking)
documents → wimm (invoice processing → financial records)
currencies → wimm (exchange rates → multi-currency)
restopos → wimm (sales data → revenue tracking)
restopos → wims (sales → inventory deduction)
wims → wimm (inventory valuation → assets)
movies → music (soundtracks connection)
all modules → castle guard (authentication/authorization)
all modules → system scrolls (monitoring/metrics)
```

### shared services
- **authentication**: castle guard provides system-wide auth
- **database**: PostgreSQL/SQLite managed by database setup
- **monitoring**: system scrolls tracks all module health
- **ai services**: ai builder provides ML capabilities
- **web interface**: web ui serves all web UIs
- **version control**: version manager handles updates

## 📈 system statistics

### completion overview
| category | average completion | modules |
|----------|-------------------|---------|
| main modules | 76% | 10 modules |
| system tools | 83% | 6 tools |
| dev tools | 78% | 4 utilities |
| **overall** | **78%** | **20 total** |

### maturity levels
- **production ready** (>80%): currencies, kişisel enflasyon, restopos, system scrolls, castle guard, web ui, version manager
- **beta stage** (70-80%): documents, music, movies, wimm, wims, birlikteyiz, code forge, database setup, sd card, forge smithy, anvil repair, ai builder
- **alpha stage** (<70%): recaria

### feature statistics
- **implemented features**: 500+
- **in development**: 45+ features
- **planned features**: 60+ features
- **api endpoints**: 150+
- **database models**: 200+

## 🔄 version information
- **current version**: v460
- **release date**: 2025-08-12
- **documentation standard**: v2.0
- **api version**: v1.0
- **python version**: 3.11+
- **node version**: 18+

## 📚 additional resources

### documentation
- [tools overview](tools_overview.md) - detailed tools documentation
- [dev tools overview](dev_tools_overview.md) - developer utilities guide
- [api reference](../../API.md) - complete API documentation
- [changelog](../../CHANGELOG.md) - detailed version history

### configuration
- **main config**: `/src/config/`
- **module configs**: `/backend/apps/{module}/`
- **web config**: `/backend/unibos_backend/settings/`
- **logs**: `/unibos.log`, `/backend/logs/`

### development
- **version file**: `/src/VERSION.json`
- **dev log**: `/DEVELOPMENT_LOG.md`
- **archives**: `/archive/versions/`
- **backups**: `/backups/`

## 🌟 key features

### system-wide
- **multi-language support**: 10 languages (TR, EN, DE, FR, ES, IT, RU, AR, CN, JP)
- **real-time updates**: WebSocket support for live data
- **offline capability**: works without internet (limited features)
- **cross-platform**: Linux, macOS, Windows, Raspberry Pi
- **modular architecture**: install only what you need
- **api-first design**: everything accessible via API
- **security-focused**: encryption, authentication, audit logs

### unique capabilities
- **mesh networking**: communicate without internet (birlikteyiz)
- **personal inflation**: track your real cost of living
- **space simulation**: explore the universe (recaria)
- **ai integration**: multiple AI providers supported
- **restaurant POS**: complete hospitality solution
- **document OCR**: intelligent receipt processing

## 👤 credits
- **author**: berk hatırlı
- **location**: bitez, bodrum, muğla, türkiye
- **license**: proprietary
- **support**: via github issues