# 🎯 sd card

## 📋 overview
specialized utility for Raspberry Pi SD card management, system imaging, and embedded deployment. handles OS installation, backup creation, and optimization for single-board computers running unibos.

## 🔧 current capabilities
### ✅ fully functional
- **sd card imaging** - write OS images to SD cards
- **backup creation** - full card backup with compression
- **card cloning** - duplicate SD cards exactly
- **partition management** - resize and modify partitions
- **boot configuration** - edit config.txt and cmdline.txt
- **wifi setup** - pre-configure wireless networks
- **ssh enabling** - enable SSH before first boot
- **overclock settings** - safe overclocking profiles
- **card health check** - test SD card integrity

### 🚧 in development
- network boot setup
- multi-card batch operations
- automatic shrinking
- card speed optimization

### 📅 planned features
- pxe boot server
- cluster deployment
- emmc support
- nvme boot configuration

## 💻 technical implementation
### core functions
- `SDCardManager` class - main SD card handler
- `ImageWriter` class - OS image operations
- `PartitionManager` class - partition handling
- `BootConfig` class - boot configuration
- `write_image()` - flash OS to card
- `backup_card()` - create card backup
- `configure_boot()` - modify boot settings
- `test_card()` - integrity verification

### database models
- `SDCard` - registered SD cards
- `OSImage` - available OS images
- `BackupImage` - card backups
- `BootProfile` - boot configurations
- `CardHealth` - health check results

### api integrations
- **dd** - low-level card writing
- **fdisk/parted** - partition management
- **pishrink** - image shrinking
- **rpi-imager** - raspberry pi imager
- **badblocks** - card testing

## 🎮 how to use
1. navigate to main menu
2. select "dev tools" (d)
3. choose "💾 sd card" (s)
4. sd card manager interface:
   - press '1' for write image
   - press '2' for backup card
   - press '3' for clone card
   - press '4' for configure boot
   - press '5' for partition manager
   - press '6' for card health check
   - press '7' for batch operations
5. write image workflow:
   - insert SD card
   - select OS image
   - configure options (SSH, WiFi)
   - write and verify
   - safe eject
6. backup workflow:
   - insert source card
   - choose compression level
   - select destination
   - create backup
   - verify integrity

## 📊 data flow
- **input sources**:
  - OS image files
  - SD card devices
  - configuration files
  - network settings
  - boot parameters
- **processing steps**:
  1. detect SD card
  2. unmount partitions
  3. write/read data
  4. modify configurations
  5. verify integrity
  6. remount if needed
  7. safe eject
- **output destinations**:
  - SD card device
  - backup images
  - configuration files
  - log files
  - health reports

## 🔌 integrations
- **forge smithy** - unibos deployment to Pi
- **system scrolls** - hardware detection
- **anvil repair** - card recovery
- **database setup** - embedded database

## ⚡ performance metrics
- write speed: 10-90 MB/s (card dependent)
- backup speed: 50 MB/s typical
- verification: 100 MB/s read
- supports up to 1TB cards
- batch operations: 10 cards parallel
- compression ratio: 40-60%

## 🐛 known limitations
- requires root/admin access
- USB 2.0 limits speed to ~30MB/s
- some cards incompatible with Pi
- large cards take time to backup
- network boot requires Pi 3B+ or newer

## 📈 version history
- v1.0 - basic image writing
- v2.0 - backup functionality
- v3.0 - boot configuration
- v4.0 - partition management
- v5.0 - batch operations
- current - complete SD toolkit

## 🛠️ development status
**completion: 77%**
- image writing: ✅ complete
- backup/restore: ✅ complete
- configuration: ✅ complete
- partitioning: ✅ complete
- health checks: ✅ complete
- network boot: 🚧 in progress (40%)
- batch ops: 🚧 in progress (60%)
- nvme support: 📅 planned