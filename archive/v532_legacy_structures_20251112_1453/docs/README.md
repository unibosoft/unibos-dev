# unibos documentation

## overview
centralized documentation hub for the unibos cli system

## documentation structure

### 📁 /docs/modules/
module-specific documentation

- [module index](./modules/index.md) - complete module listing
- individual module documentation files
- tools and dev tools overviews

### module categories

#### main modules
- [recaria](./modules/recaria.md) - space exploration
- [birlikteyiz](./modules/birlikteyiz.md) - mesh network
- [kişisel enflasyon](./modules/kisisel_enflasyon.md) - inflation tracker
- [currencies](./modules/currencies.md) - exchange rates

#### business modules  
- [wimm](./modules/wimm.md) - financial management
- [wims](./modules/wims.md) - inventory system
- [restopos](./modules/restopos.md) - restaurant pos

#### content modules
- [documents](./modules/documents.md) - document manager
- [movies](./modules/movies.md) - movie collection
- [music](./modules/music.md) - music library

#### system tools
- [tools overview](./modules/tools_overview.md) - admin tools
- [dev tools overview](./modules/dev_tools_overview.md) - development

## documentation standards

### formatting rules
- **all lowercase** - no capitals except acronyms
- **concise descriptions** - clear and minimal
- **consistent structure** - same format across docs
- **version tracking** - current version noted

### standard sections
each module documentation includes:
1. overview - brief description
2. current version - version number
3. key features - main capabilities
4. quick start - how to access/use
5. technical details - implementation info
6. recent updates - latest changes

## quick links

### main documentation
- [project readme](/README.md)
- [architecture](/ARCHITECTURE.md)
- [installation](/INSTALLATION.md)
- [api reference](/API.md)
- [features](/FEATURES.md)

### development
- [development log](/DEVELOPMENT_LOG.md)
- [claude guidelines](/CLAUDE.md)
- [version management](/VERSION_MANAGEMENT.md)
- [troubleshooting](/TROUBLESHOOTING.md)

## access points

### cli navigation
```
main menu → modules → [select module]
main menu → tools → [select tool]
main menu → dev tools → [select dev tool]
```

### web interface
```
http://localhost:8000/
http://localhost:8000/modules/
http://localhost:8000/api/
```

### api endpoints
```
/api/auth/ - authentication
/api/modules/ - module list
/api/{module}/ - module api
```

## version information
- current version: v460
- total modules: 10 main + tools
- supported languages: 10
- last updated: 2025-08-12

## contact
- author: berk hatırlı
- location: bitez, bodrum, türkiye