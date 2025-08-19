# 🎯 movies

## 📋 overview
comprehensive movie and TV series collection manager with metadata fetching, watchlist organization, and viewing tracking. integrates with TMDB and OMDB APIs for automatic poster downloads, cast information, and personalized recommendations.

## 🔧 current capabilities
### ✅ fully functional
- **collection management** - organize personal movie/series library
- **metadata fetching** - automatic cast, crew, synopsis from TMDB/OMDB
- **watchlist system** - multiple themed watchlists with priorities
- **rating system** - personal ratings and reviews
- **watch tracking** - episode progress for TV series
- **search engine** - advanced filtering by genre, year, rating
- **poster gallery** - high-quality artwork with caching
- **recommendations** - AI-based suggestions from viewing history
- **trending feed** - current popular movies and shows

### 🚧 in development
- torrent integration for availability checking
- subtitle download automation
- social features (share lists)
- calendar for upcoming releases

### 📅 planned features
- streaming service availability
- group watch parties
- movie night scheduler
- collection statistics dashboard

## 💻 technical implementation
### core functions
- `Movie` model - movie data with metadata
- `Series` model - TV show with seasons/episodes
- `Collection` model - user movie collections
- `Watchlist` model - organized watch queues
- `WatchHistory` model - viewing progress tracking
- `fetch_metadata()` - TMDB/OMDB API calls
- `generate_recommendations()` - ML-based suggestions

### database models
- `Movie` - film data with TMDB/IMDB IDs
- `Series` - TV shows with season structure
- `Episode` - individual episode tracking
- `Collection` - user's movie libraries
- `Watchlist` - categorized watch queues
- `WatchHistory` - viewing timestamps and progress
- `Review` - user ratings and comments
- `Genre` - movie categories

### api integrations
- **TMDB API** - primary metadata source
- **OMDB API** - fallback and additional data
- **YouTube API** - trailer fetching
- **JustWatch API** - streaming availability (planned)
- **OpenSubtitles API** - subtitle downloads (planned)

## 🎮 how to use
1. navigate to main menu
2. select "modules" (m)
3. choose "🎬 movies" (v)
4. movie hub interface:
   - press '1' for search movies
   - press '2' for my collection
   - press '3' for watchlists
   - press '4' for currently watching
   - press '5' for discover/trending
   - press '6' for recommendations
   - press '7' for statistics
5. adding movies:
   - search by title or IMDB ID
   - select from results
   - auto-fetches all metadata
   - add to collection/watchlist
6. series tracking:
   - mark episodes as watched
   - tracks next episode to watch
   - season progress indicators
   - automatic "up next" suggestions

## 📊 data flow
- **input sources**:
  - TMDB API search
  - OMDB API metadata
  - user manual entries
  - barcode scanning (DVDs)
  - import from CSV/JSON
- **processing steps**:
  1. search movie/series
  2. fetch metadata from APIs
  3. download and cache posters
  4. store in database
  5. update collections
  6. calculate recommendations
  7. track viewing progress
- **output destinations**:
  - PostgreSQL database
  - poster cache directory
  - export to CSV/JSON
  - recommendation engine
  - statistics dashboard

## 🔌 integrations
- **documents** - store movie tickets and receipts
- **WIMM** - track movie subscription costs
- **music** - soundtrack connections
- **currencies** - international box office data

## ⚡ performance metrics
- metadata fetch: 1-2 seconds per movie
- search results: <500ms
- poster caching: 100MB per 100 movies
- supports 10,000+ movie library
- recommendation calculation: <1 second
- concurrent API calls: 10 per second

## 🐛 known limitations
- TMDB API rate limit: 40 requests/10 seconds
- poster storage can consume significant disk space
- some regional content lacks metadata
- subtitle integration not yet complete
- streaming availability limited to major services

## 📈 version history
- v0.5 - basic movie database
- v0.7 - TMDB integration
- v0.8 - series tracking added
- v0.9 - watchlist and collections
- v1.0 - recommendations and trending
- v1.1 - improved caching system

## 🛠️ development status
**completion: 75%**
- collection management: ✅ complete
- metadata fetching: ✅ complete
- watchlists: ✅ complete
- series tracking: ✅ complete
- recommendations: ✅ complete
- subtitle integration: 🚧 in progress (30%)
- streaming availability: 🚧 in progress (20%)
- social features: 📅 planned