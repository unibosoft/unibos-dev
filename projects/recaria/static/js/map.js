/* map.js - Harita işlevselliği için JavaScript */

// Harita değişkenleri
let map;
let playerMarker;
let buildingsLayer;
let roadsLayer;
let pointsLayer;
let currentPosition = { lat: 37.031, lng: 27.303 }; // Bodrum merkezi varsayılan konum
let lastFetchPosition = { lat: 0, lng: 0 };
let fetchRadius = 150; // metre cinsinden
let fetchThreshold = 0.6; // Merkezden %60 uzaklaşınca yeni veri çek

// Harita başlatma
function initMap() {
    // Leaflet haritasını başlat
    map = L.map('map-container', {
        center: [currentPosition.lat, currentPosition.lng],
        zoom: 18,
        minZoom: 15,
        maxZoom: 20,
        zoomControl: false // Kendi zoom kontrollerimizi kullanacağız
    });

    // OpenStreetMap katmanı
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Oyuncu işaretçisi
    const playerIcon = L.icon({
        iconUrl: '/static/img/player-marker.png',
        iconSize: [32, 32],
        iconAnchor: [16, 16]
    });
    
    playerMarker = L.marker([currentPosition.lat, currentPosition.lng], {
        icon: playerIcon,
        zIndexOffset: 1000
    }).addTo(map);

    // Katmanları oluştur
    buildingsLayer = L.layerGroup().addTo(map);
    roadsLayer = L.layerGroup().addTo(map);
    pointsLayer = L.layerGroup().addTo(map);

    // İlk veri çekme
    fetchMapData(currentPosition.lat, currentPosition.lng, fetchRadius);

    // Harita olaylarını dinle
    map.on('moveend', onMapMoveEnd);
    
    // Zoom kontrolleri
    document.getElementById('btn-zoom-in').addEventListener('click', () => {
        map.zoomIn();
    });
    
    document.getElementById('btn-zoom-out').addEventListener('click', () => {
        map.zoomOut();
    });
    
    // Konuma git butonu
    document.getElementById('btn-center-map').addEventListener('click', centerOnPlayer);
    
    // Katman görünürlük kontrolleri
    document.getElementById('toggle-buildings').addEventListener('change', function() {
        toggleLayerVisibility(buildingsLayer, this.checked);
    });
    
    document.getElementById('toggle-roads').addEventListener('change', function() {
        toggleLayerVisibility(roadsLayer, this.checked);
    });
    
    document.getElementById('toggle-points').addEventListener('change', function() {
        toggleLayerVisibility(pointsLayer, this.checked);
    });
    
    // Gerçek konum izni iste
    requestGeolocation();
}

// Gerçek konum izni iste
function requestGeolocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                currentPosition.lat = position.coords.latitude;
                currentPosition.lng = position.coords.longitude;
                
                // Oyuncu konumunu güncelle
                updatePlayerPosition();
                
                // Haritayı oyuncu konumuna merkezle
                centerOnPlayer();
                
                // Konum etrafındaki verileri çek
                fetchMapData(currentPosition.lat, currentPosition.lng, fetchRadius);
                
                // Sürekli konum güncellemesi
                navigator.geolocation.watchPosition(
                    (position) => {
                        currentPosition.lat = position.coords.latitude;
                        currentPosition.lng = position.coords.longitude;
                        updatePlayerPosition();
                        
                        // Koordinat bilgisini güncelle
                        updateCoordinatesDisplay();
                        
                        // Yeni veri çekme kontrolü
                        checkFetchNewData();
                    },
                    (error) => {
                        console.error('Konum izleme hatası:', error);
                        addToGameLog('Konum izleme hatası: ' + error.message);
                    },
                    { enableHighAccuracy: true, maximumAge: 10000, timeout: 10000 }
                );
            },
            (error) => {
                console.error('Konum erişim hatası:', error);
                addToGameLog('Konum erişim hatası: ' + error.message);
            }
        );
    } else {
        console.error('Tarayıcınız konum hizmetlerini desteklemiyor.');
        addToGameLog('Tarayıcınız konum hizmetlerini desteklemiyor.');
    }
}

// Oyuncu konumunu güncelle
function updatePlayerPosition() {
    playerMarker.setLatLng([currentPosition.lat, currentPosition.lng]);
    updateCoordinatesDisplay();
}

// Haritayı oyuncu konumuna merkezle
function centerOnPlayer() {
    map.setView([currentPosition.lat, currentPosition.lng], map.getZoom());
    addToGameLog('Harita oyuncu konumuna merkezlendi.');
}

// Koordinat göstergesini güncelle
function updateCoordinatesDisplay() {
    document.getElementById('current-coords').textContent = 
        currentPosition.lat.toFixed(6) + ', ' + currentPosition.lng.toFixed(6);
}

// Harita hareket bittiğinde
function onMapMoveEnd() {
    const center = map.getCenter();
    
    // Harita merkezi değiştiğinde yeni veri çekme kontrolü
    checkFetchNewData();
}

// Yeni veri çekme kontrolü
function checkFetchNewData() {
    const mapCenter = map.getCenter();
    const distance = calculateDistance(
        mapCenter.lat, mapCenter.lng,
        lastFetchPosition.lat, lastFetchPosition.lng
    );
    
    // Eğer son çekilen konumdan belirli bir mesafe uzaklaştıysak yeni veri çek
    if (distance > fetchRadius * fetchThreshold || 
        (lastFetchPosition.lat === 0 && lastFetchPosition.lng === 0)) {
        fetchMapData(mapCenter.lat, mapCenter.lng, fetchRadius);
    }
}

// İki nokta arasındaki mesafeyi hesapla (metre cinsinden)
function calculateDistance(lat1, lon1, lat2, lon2) {
    if (lat2 === 0 && lon2 === 0) return Infinity;
    
    const R = 6371e3; // Dünya yarıçapı (metre)
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;

    const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ/2) * Math.sin(Δλ/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    return R * c;
}

// API'den harita verilerini çek
function fetchMapData(lat, lng, radius) {
    // Çekme konumunu güncelle
    lastFetchPosition.lat = lat;
    lastFetchPosition.lng = lng;
    
    addToGameLog('Harita verileri çekiliyor...');
    
    // Bağlantı durumunu güncelle
    updateConnectionStatus('connecting');
    
    // API'den veri çekme
    fetch(`/api/geo/?lat=${lat}&lon=${lng}&radius=${radius}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('API yanıt hatası: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            // Verileri işle ve haritaya ekle
            processMapData(data);
            
            // Bağlantı durumunu güncelle
            updateConnectionStatus('connected');
            
            addToGameLog('Harita verileri başarıyla güncellendi.');
        })
        .catch(error => {
            console.error('Veri çekme hatası:', error);
            addToGameLog('Veri çekme hatası: ' + error.message);
            
            // Bağlantı durumunu güncelle
            updateConnectionStatus('disconnected');
            
            // Demo veri kullan
            useDemoData(lat, lng, radius);
        });
}

// Demo veri kullan (API bağlantısı olmadığında)
function useDemoData(lat, lng, radius) {
    addToGameLog('Demo veriler kullanılıyor...');
    
    // Demo GeoJSON verisi
    const demoData = {
        center: [lat, lng],
        radius: radius,
        features: [
            // Yollar (LineString)
            {
                type: "Feature",
                geometry: {
                    type: "LineString",
                    coordinates: [
                        [lng - 0.001, lat - 0.001],
                        [lng, lat],
                        [lng + 0.001, lat + 0.001]
                    ]
                },
                properties: {
                    type: "road",
                    name: "Ana Cadde"
                }
            },
            {
                type: "Feature",
                geometry: {
                    type: "LineString",
                    coordinates: [
                        [lng - 0.0005, lat],
                        [lng + 0.0005, lat]
                    ]
                },
                properties: {
                    type: "road",
                    name: "Yan Sokak"
                }
            },
            // Binalar (Polygon)
            {
                type: "Feature",
                geometry: {
                    type: "Polygon",
                    coordinates: [[
                        [lng - 0.0003, lat - 0.0003],
                        [lng - 0.0003, lat - 0.0001],
                        [lng - 0.0001, lat - 0.0001],
                        [lng - 0.0001, lat - 0.0003],
                        [lng - 0.0003, lat - 0.0003]
                    ]]
                },
                properties: {
                    type: "building",
                    name: "Market"
                }
            },
            {
                type: "Feature",
                geometry: {
                    type: "Polygon",
                    coordinates: [[
                        [lng + 0.0001, lat + 0.0001],
                        [lng + 0.0001, lat + 0.0003],
                        [lng + 0.0003, lat + 0.0003],
                        [lng + 0.0003, lat + 0.0001],
                        [lng + 0.0001, lat + 0.0001]
                    ]]
                },
                properties: {
                    type: "building",
                    name: "Kafe"
                }
            },
            // Noktalar (Point)
            {
                type: "Feature",
                geometry: {
                    type: "Point",
                    coordinates: [lng, lat + 0.0005]
                },
                properties: {
                    type: "point",
                    name: "İlgi Noktası",
                    description: "Önemli bir yer"
                }
            }
        ]
    };
    
    // Demo verileri işle
    processMapData(demoData);
}

// Harita verilerini işle ve göster
function processMapData(data) {
    // Mevcut katmanları temizle
    buildingsLayer.clearLayers();
    roadsLayer.clearLayers();
    pointsLayer.clearLayers();
    
    // Özellikleri işle
    data.features.forEach(feature => {
        if (feature.geometry.type === "LineString") {
            // Yollar
            const road = L.polyline(
                feature.geometry.coordinates.map(coord => [coord[1], coord[0]]), 
                {
                    color: '#FFCC00',
                    weight: 5,
                    opacity: 0.7
                }
            );
            
            if (feature.properties && feature.properties.name) {
                road.bindTooltip(feature.properties.name);
            }
            
            road.on('click', () => {
                onFeatureClick(feature);
            });
            
            roadsLayer.addLayer(road);
            
        } else if (feature.geometry.type === "Polygon") {
            // Binalar
            const building = L.polygon(
                feature.geometry.coordinates[0].map(coord => [coord[1], coord[0]]),
                {
                    color: '#CC0000',
                    fillColor: '#FF0000',
                    fillOpacity: 0.5,
                    weight: 2
                }
            );
            
            if (feature.properties && feature.properties.name) {
                building.bindTooltip(feature.properties.name);
            }
            
            building.on('click', () => {
                onFeatureClick(feature);
            });
            
            buildingsLayer.addLayer(building);
            
        } else if (feature.geometry.type === "Point") {
            // Noktalar
            const pointIcon = L.icon({
                iconUrl: '/static/img/point-marker.png',
                iconSize: [24, 24],
                iconAnchor: [12, 12]
            });
            
            const point = L.marker(
                [feature.geometry.coordinates[1], feature.geometry.coordinates[0]],
                { icon: pointIcon }
            );
            
            if (feature.properties && feature.properties.name) {
                point.bindTooltip(feature.properties.name);
            }
            
            point.on('click', () => {
                onFeatureClick(feature);
            });
            
            pointsLayer.addLayer(point);
        }
    });
    
    // Oyuncu puanını güncelle (keşif bazlı)
    updatePlayerScore(data.features.length);
}

// Harita öğesine tıklandığında
function onFeatureClick(feature) {
    const featureType = feature.properties.type || 'bilinmeyen';
    const featureName = feature.properties.name || 'İsimsiz';
    const featureDesc = feature.properties.description || '';
    
    let message = `${featureType.toUpperCase()}: ${featureName}`;
    if (featureDesc) {
        message += ` - ${featureDesc}`;
    }
    
    addToGameLog(message);
    
    // Etkileşim puanı ekle
    addPlayerScore(5);
}

// Katman görünürlüğünü değiştir
function toggleLayerVisibility(layer, isVisible) {
    if (isVisible) {
        map.addLayer(layer);
    } else {
        map.removeLayer(layer);
    }
}

// Bağlantı durumunu güncelle
function updateConnectionStatus(status) {
    const indicator = document.getElementById('connection-indicator');
    const text = document.getElementById('connection-text');
    
    indicator.className = 'connection-indicator ' + status;
    
    switch (status) {
        case 'connected':
            text.textContent = 'Bağlı';
            break;
        case 'connecting':
            text.textContent = 'Bağlanıyor...';
            break;
        case 'disconnected':
            text.textContent = 'Bağlantı Yok';
            break;
    }
}

// Oyun günlüğüne mesaj ekle
function addToGameLog(message) {
    const gameLog = document.getElementById('game-log');
    const entry = document.createElement('p');
    entry.innerHTML = `<span class="log-time">${getCurrentTime()}</span> ${message}`;
    
    gameLog.appendChild(entry);
    gameLog.scrollTop = gameLog.scrollHeight;
    
    // Maksimum 50 log tutma
    while (gameLog.children.length > 50) {
        gameLog.removeChild(gameLog.firstChild);
    }
}

// Şu anki zamanı al (HH:MM:SS)
function getCurrentTime() {
    const now = new Date();
    return now.toTimeString().substring(0, 8);
}

// Oyuncu puanını güncelle
function updatePlayerScore(basePoints) {
    const currentScore = parseInt(document.getElementById('player-score').textContent) || 0;
    const newPoints = Math.floor(basePoints * 2);
    
    document.getElementById('player-score').textContent = currentScore + newPoints;
    
    // Seviye kontrolü
    checkPlayerLevel();
    
    // Keşif yüzdesini güncelle
    updateExplorationPercentage();
}

// Oyuncuya puan ekle
function addPlayerScore(points) {
    const currentScore = parseInt(document.getElementById('player-score').textContent) || 0;
    document.getElementById('player-score').textContent = currentScore + points;
    
    // Seviye kontrolü
    checkPlayerLevel();
}

// Oyuncu seviyesini kontrol et
function checkPlayerLevel() {
    const currentScore = parseInt(document.getElementById('player-score').textContent) || 0;
    const currentLevel = parseInt(document.getElementById('player-level').textContent) || 1;
    
    // Her 100 puan için 1 seviye
    const newLevel = Math.floor(currentScore / 100) + 1;
    
    if (newLevel > currentLevel) {
        document.getElementById('player-level').textContent = newLevel;
        addToGameLog(`Tebrikler! Seviye ${newLevel}'e yükseldiniz.`);
    }
}

// Keşif yüzdesini güncelle
function updateExplorationPercentage() {
    const currentScore = parseInt(document.getElementById('player-score').textContent) || 0;
    
    // Basit bir formül: Her 500 puan için %1 keşif
    const explorationPercentage = Math.min(100, Math.floor(currentScore / 500));
    
    document.getElementById('player-exploration').textContent = explorationPercentage + '%';
}

// Sayfa yüklendiğinde haritayı başlat
document.addEventListener('DOMContentLoaded', function() {
    initMap();
});
