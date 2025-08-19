/* game.js - Unicorn Bodrum Entertainment oyun mantığı için JavaScript */

// Oyun değişkenleri
let gameInitialized = false;
let playerData = {
    level: 1,
    score: 0,
    exploration: 0,
    inventory: [],
    discoveredLocations: [],
    achievements: []
};

// Phaser oyun nesnesi
let phaserGame;

// Oyun başlatma
function initGame() {
    if (gameInitialized) return;
    
    // Phaser oyun konfigürasyonu
    const config = {
        type: Phaser.AUTO,
        parent: 'game-overlay',
        width: window.innerWidth,
        height: window.innerHeight,
        transparent: true,
        physics: {
            default: 'arcade',
            arcade: {
                gravity: { y: 0 },
                debug: false
            }
        },
        scene: {
            preload: preload,
            create: create,
            update: update
        }
    };
    
    // Phaser oyununu başlat
    phaserGame = new Phaser.Game(config);
    
    // Pencere boyutu değiştiğinde oyunu yeniden boyutlandır
    window.addEventListener('resize', resizeGame);
    
    gameInitialized = true;
    
    // Oyun günlüğüne başlangıç mesajı ekle
    addToGameLog('Unicorn Bodrum Entertainment oyunu başlatıldı. Keşfe başlamak için haritada ilerleyin.');
}

// Phaser preload fonksiyonu
function preload() {
    // Oyun varlıklarını yükle
    this.load.image('player', '/static/img/player-sprite.png');
    this.load.image('collectible', '/static/img/collectible.png');
    this.load.image('achievement', '/static/img/achievement.png');
    
    // Efekt ve animasyonlar için sprite'lar
    this.load.spritesheet('explosion', '/static/img/explosion.png', { 
        frameWidth: 64, 
        frameHeight: 64 
    });
}

// Phaser create fonksiyonu
function create() {
    // Oyun nesnelerini oluştur
    this.player = this.add.sprite(400, 300, 'player').setScale(0.5);
    this.player.setVisible(false); // Leaflet marker kullanıyoruz, bu sadece efektler için
    
    // Animasyonları tanımla
    this.anims.create({
        key: 'explode',
        frames: this.anims.generateFrameNumbers('explosion', { start: 0, end: 15 }),
        frameRate: 20,
        repeat: 0
    });
    
    // Oyun olaylarını dinle
    this.input.on('pointerdown', function (pointer) {
        // Tıklama efekti
        createClickEffect(this, pointer.x, pointer.y);
    }, this);
    
    // Oyun arayüzü hazır
    console.log('Phaser oyun arayüzü hazır');
}

// Phaser update fonksiyonu
function update() {
    // Oyun mantığı güncellemeleri
    updateGameElements();
}

// Oyun elemanlarını güncelle
function updateGameElements() {
    // Burada oyun mantığı güncellemeleri yapılacak
    // Örneğin: Animasyonlar, efektler, vb.
}

// Tıklama efekti oluştur
function createClickEffect(scene, x, y) {
    const effect = scene.add.sprite(x, y, 'explosion').setScale(0.5);
    effect.play('explode');
    effect.once('animationcomplete', () => {
        effect.destroy();
    });
}

// Oyunu yeniden boyutlandır
function resizeGame() {
    if (!phaserGame) return;
    
    const width = window.innerWidth;
    const height = window.innerHeight;
    
    phaserGame.scale.resize(width, height);
}

// Keşif noktası ekle
function addDiscoveryPoint(lat, lng, name, type) {
    // Keşfedilen konumu kaydet
    const location = {
        lat: lat,
        lng: lng,
        name: name,
        type: type,
        timestamp: new Date().toISOString()
    };
    
    playerData.discoveredLocations.push(location);
    
    // Keşif puanı ekle
    let points = 10; // Varsayılan puan
    
    switch (type) {
        case 'building':
            points = 15;
            break;
        case 'road':
            points = 5;
            break;
        case 'point':
            points = 25;
            break;
    }
    
    addPlayerScore(points);
    addToGameLog(`Yeni keşif: ${name} (${type}) - ${points} puan kazandınız!`);
    
    // Başarı kontrolü
    checkAchievements();
    
    // Sunucuya keşif bilgisini gönder
    sendDiscoveryToServer(location);
}

// Başarıları kontrol et
function checkAchievements() {
    const achievements = [
        {
            id: 'first_discovery',
            name: 'İlk Keşif',
            description: 'İlk konumu keşfettin!',
            condition: () => playerData.discoveredLocations.length >= 1,
            points: 50
        },
        {
            id: 'explorer_novice',
            name: 'Acemi Kaşif',
            description: '10 konum keşfettin!',
            condition: () => playerData.discoveredLocations.length >= 10,
            points: 100
        },
        {
            id: 'road_master',
            name: 'Yol Ustası',
            description: '5 yol keşfettin!',
            condition: () => playerData.discoveredLocations.filter(loc => loc.type === 'road').length >= 5,
            points: 75
        },
        {
            id: 'building_explorer',
            name: 'Bina Kaşifi',
            description: '5 bina keşfettin!',
            condition: () => playerData.discoveredLocations.filter(loc => loc.type === 'building').length >= 5,
            points: 75
        },
        {
            id: 'point_collector',
            name: 'Nokta Toplayıcı',
            description: '3 ilgi noktası keşfettin!',
            condition: () => playerData.discoveredLocations.filter(loc => loc.type === 'point').length >= 3,
            points: 100
        }
    ];
    
    // Kazanılmamış başarıları kontrol et
    achievements.forEach(achievement => {
        if (!playerData.achievements.includes(achievement.id) && achievement.condition()) {
            // Başarı kazanıldı
            playerData.achievements.push(achievement.id);
            
            // Puanları ekle
            addPlayerScore(achievement.points);
            
            // Başarı bildirimini göster
            showAchievementNotification(achievement);
        }
    });
}

// Başarı bildirimi göster
function showAchievementNotification(achievement) {
    addToGameLog(`🏆 BAŞARI KAZANILDI: ${achievement.name} - ${achievement.description} (${achievement.points} puan)`);
    
    // Burada görsel bir bildirim de eklenebilir
    if (phaserGame && phaserGame.scene.scenes[0]) {
        const scene = phaserGame.scene.scenes[0];
        const notification = scene.add.sprite(
            window.innerWidth / 2, 
            100, 
            'achievement'
        ).setScale(0.7);
        
        const text = scene.add.text(
            window.innerWidth / 2, 
            150, 
            `${achievement.name}\n${achievement.points} puan`, 
            { 
                fontFamily: 'Arial', 
                fontSize: '18px', 
                fill: '#fff',
                align: 'center'
            }
        ).setOrigin(0.5);
        
        // Animasyon
        scene.tweens.add({
            targets: [notification, text],
            y: '+=20',
            alpha: { from: 0, to: 1 },
            duration: 1000,
            ease: 'Power2',
            yoyo: true,
            hold: 2000,
            onComplete: () => {
                notification.destroy();
                text.destroy();
            }
        });
    }
}

// Sunucuya keşif bilgisini gönder
function sendDiscoveryToServer(discovery) {
    // API endpoint'i
    const url = '/api/discovery/';
    
    // Bağlantı durumunu güncelle
    updateConnectionStatus('connecting');
    
    // API'ye veri gönder
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(discovery)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('API yanıt hatası: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log('Keşif sunucuya kaydedildi:', data);
        updateConnectionStatus('connected');
    })
    .catch(error => {
        console.error('Keşif gönderme hatası:', error);
        updateConnectionStatus('disconnected');
        
        // Çevrimdışı modda kaydet
        saveDiscoveryOffline(discovery);
    });
}

// Keşfi çevrimdışı kaydet
function saveDiscoveryOffline(discovery) {
    // LocalStorage'a kaydet
    let offlineDiscoveries = JSON.parse(localStorage.getItem('offlineDiscoveries') || '[]');
    offlineDiscoveries.push(discovery);
    localStorage.setItem('offlineDiscoveries', JSON.stringify(offlineDiscoveries));
    
    addToGameLog('Keşif çevrimdışı kaydedildi. Bağlantı sağlandığında otomatik gönderilecek.');
}

// Çevrimdışı keşifleri senkronize et
function syncOfflineDiscoveries() {
    const offlineDiscoveries = JSON.parse(localStorage.getItem('offlineDiscoveries') || '[]');
    
    if (offlineDiscoveries.length === 0) return;
    
    addToGameLog(`${offlineDiscoveries.length} çevrimdışı keşif senkronize ediliyor...`);
    
    // API endpoint'i
    const url = '/api/discoveries/bulk/';
    
    // API'ye toplu veri gönder
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ discoveries: offlineDiscoveries })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('API yanıt hatası: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log('Çevrimdışı keşifler senkronize edildi:', data);
        
        // Başarılı senkronizasyon sonrası LocalStorage'ı temizle
        localStorage.removeItem('offlineDiscoveries');
        
        addToGameLog(`${offlineDiscoveries.length} çevrimdışı keşif başarıyla senkronize edildi.`);
    })
    .catch(error => {
        console.error('Senkronizasyon hatası:', error);
        addToGameLog('Senkronizasyon hatası: ' + error.message);
    });
}

// Oyuncu verilerini sunucudan yükle
function loadPlayerData() {
    // API endpoint'i
    const url = '/api/player/';
    
    // Bağlantı durumunu güncelle
    updateConnectionStatus('connecting');
    
    // API'den veri çek
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('API yanıt hatası: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            // Oyuncu verilerini güncelle
            playerData = data;
            
            // UI'ı güncelle
            updatePlayerUI();
            
            // Bağlantı durumunu güncelle
            updateConnectionStatus('connected');
            
            addToGameLog('Oyuncu verileri yüklendi.');
            
            // Çevrimdışı keşifleri senkronize et
            syncOfflineDiscoveries();
        })
        .catch(error => {
            console.error('Oyuncu verisi yükleme hatası:', error);
            addToGameLog('Oyuncu verisi yükleme hatası: ' + error.message);
            
            // Bağlantı durumunu güncelle
            updateConnectionStatus('disconnected');
            
            // LocalStorage'dan yükle
            loadPlayerDataFromLocalStorage();
        });
}

// Oyuncu verilerini LocalStorage'dan yükle
function loadPlayerDataFromLocalStorage() {
    const savedData = localStorage.getItem('playerData');
    
    if (savedData) {
        playerData = JSON.parse(savedData);
        updatePlayerUI();
        addToGameLog('Oyuncu verileri yerel depodan yüklendi.');
    }
}

// Oyuncu verilerini LocalStorage'a kaydet
function savePlayerDataToLocalStorage() {
    localStorage.setItem('playerData', JSON.stringify(playerData));
}

// Oyuncu UI'ını güncelle
function updatePlayerUI() {
    document.getElementById('player-level').textContent = playerData.level;
    document.getElementById('player-score').textContent = playerData.score;
    document.getElementById('player-exploration').textContent = playerData.exploration + '%';
}

// Keşif butonuna tıklandığında
document.getElementById('btn-explore').addEventListener('click', function() {
    // Harita merkezindeki konumu keşfet
    const mapCenter = map.getCenter();
    addDiscoveryPoint(mapCenter.lat, mapCenter.lng, 'Keşfedilen Bölge', 'area');
});

// Etkileşim butonuna tıklandığında
document.getElementById('btn-interact').addEventListener('click', function() {
    // En yakın özellikle etkileşime geç
    interactWithNearestFeature();
});

// Envanter butonuna tıklandığında
document.getElementById('btn-inventory').addEventListener('click', function() {
    // Envanter UI'ını göster
    showInventory();
});

// En yakın özellikle etkileşime geç
function interactWithNearestFeature() {
    // Burada en yakın özelliği bulma ve etkileşim mantığı olacak
    addToGameLog('Yakında etkileşime girebileceğiniz bir özellik bulunamadı.');
}

// Envanter UI'ını göster
function showInventory() {
    if (playerData.inventory.length === 0) {
        addToGameLog('Envanteriniz boş.');
    } else {
        addToGameLog('Envanter içeriği:');
        playerData.inventory.forEach(item => {
            addToGameLog(`- ${item.name} (${item.type})`);
        });
    }
}

// Sayfa yüklendiğinde oyunu başlat
document.addEventListener('DOMContentLoaded', function() {
    // Harita başlatıldıktan sonra oyunu başlat
    setTimeout(() => {
        initGame();
        
        // Oyuncu verilerini yükle
        loadPlayerData();
    }, 1000);
    
    // Periyodik olarak oyuncu verilerini kaydet
    setInterval(() => {
        savePlayerDataToLocalStorage();
    }, 30000); // Her 30 saniyede bir
});
