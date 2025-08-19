# 🎯 music

## 📋 overview
spotify-integrated music management system that organizes your library without storing files. features playlist creation, listening statistics, music discovery, and detailed analytics with open-source artwork support.

## 🔧 current capabilities
### ✅ fully functional
- **spotify integration** - full library sync with real-time updates
- **playlist management** - create, edit, collaborate on playlists
- **listening tracking** - detailed history and statistics
- **music discovery** - recommendations based on taste profile
- **analytics dashboard** - top tracks, artists, genres, listening patterns
- **offline metadata** - cached data for offline browsing
- **artwork management** - high-quality album art with fallbacks
- **social features** - share playlists and statistics
- **scrobbling** - Last.fm integration for tracking

### 🚧 in development
- local file integration
- lyrics synchronization
- concert/tour tracking
- vinyl collection catalog

### 📅 planned features
- multi-service support (Apple Music, YouTube Music)
- DJ mixing features
- music production tools
- podcast management

## 💻 technical implementation
### core functions
- `SpotifyClient` class - API communication handler
- `Track` model - song metadata and analytics
- `Playlist` model - playlist management
- `ListeningHistory` model - playback tracking
- `MusicAnalytics` class - statistics generator
- `sync_library()` - Spotify library synchronization
- `generate_recommendations()` - music discovery algorithm

### database models
- `Track` - song metadata with Spotify IDs
- `Artist` - artist information and genres
- `Album` - album data with tracklists
- `Playlist` - user and collaborative playlists
- `ListeningHistory` - detailed play records
- `UserProfile` - music preferences and settings
- `Analytics` - aggregated statistics

### api integrations
- **Spotify Web API** - primary music service
- **Last.fm API** - scrobbling and additional metadata
- **MusicBrainz API** - open music database
- **Genius API** - lyrics (in development)
- **Bandcamp API** - indie music discovery
- **SoundCloud API** - user uploads and mixes

## 🎮 how to use
1. navigate to main menu
2. select "modules" (m)
3. choose "🎵 music" (u)
4. music hub interface:
   - press '1' for library
   - press '2' for playlists
   - press '3' for now playing
   - press '4' for discover
   - press '5' for statistics
   - press '6' for history
   - press '7' for settings
5. spotify connection:
   - authorize via OAuth 2.0
   - grant necessary permissions
   - auto-syncs library
6. playlist management:
   - create new playlists
   - add/remove tracks
   - reorder songs
   - set collaborative mode
   - generate smart playlists
7. statistics view:
   - top 50 tracks/artists
   - listening time by period
   - genre distribution
   - mood analysis
   - discovery rate

## 📊 data flow
- **input sources**:
  - Spotify API real-time
  - user playlist creation
  - Last.fm scrobbles
  - manual track additions
  - import from CSV/JSON
- **processing steps**:
  1. authenticate with Spotify
  2. sync library metadata
  3. track listening events
  4. calculate statistics
  5. generate recommendations
  6. cache for offline use
  7. update analytics
- **output destinations**:
  - PostgreSQL database
  - statistics dashboard
  - export playlists
  - social sharing
  - Last.fm profile

## 🔌 integrations
- **movies** - soundtrack connections
- **documents** - concert ticket storage
- **WIMM** - subscription cost tracking
- **kişisel enflasyon** - concert ticket price tracking

## ⚡ performance metrics
- library sync: 2-5 seconds for 1000 tracks
- playlist operations: <200ms
- statistics calculation: <1 second
- supports 50,000+ track library
- real-time playback sync: <100ms latency
- cache size: ~500MB for 10,000 tracks

## 🐛 known limitations
- requires Spotify Premium for full features
- playback control limited to Spotify Connect devices
- some regional tracks unavailable
- offline playback not supported (metadata only)
- rate limits: 180 requests per minute

## 📈 version history
- v0.5 - basic Spotify integration
- v0.7 - playlist management
- v0.8 - listening history tracking
- v0.9 - analytics dashboard
- v1.0 - recommendations and discovery
- v1.1 - Last.fm integration

## 🛠️ development status
**completion: 78%**
- Spotify integration: ✅ complete
- playlist management: ✅ complete
- analytics: ✅ complete
- recommendations: ✅ complete
- scrobbling: ✅ complete
- lyrics sync: 🚧 in progress (35%)
- multi-service: 📅 planned
- local files: 📅 planned