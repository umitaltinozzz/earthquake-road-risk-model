import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, Circle, Polyline, Polygon } from 'react-leaflet';
import { LatLng, Icon, DivIcon } from 'leaflet';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';

// Leaflet varsayılan ikon sorunu için çözüm
import L from 'leaflet';
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconShadowUrl from 'leaflet/dist/images/marker-shadow.png';

// Leaflet ikon ayarları
const DefaultIcon = L.icon({
  iconUrl,
  shadowUrl: iconShadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// Bina tipi için arayüz
interface Building {
  id: number;
  lat: number;
  lon: number;
  kat_sayisi: number;
  bina_yasi: number;
  malzeme: string;
  created_at: string;
  updated_at: string | null;
  egim: number;
  egim_yonu: string;
  zemin_turu: string;
}

// Risk analizi için arayüz
interface RiskAnalysis {
  building_id: number;
  risk_score: number;
  risk_level: string;
  color: string;
}

// Moloz yayılım alanı için arayüz
interface MolozYayilim {
  bina_id: number;
  lat: number;
  lon: number;
  yayilim_cap: number;
  risk_seviyesi: string;
  yonler?: {
    kuzey: number;
    güney: number;
    doğu: number;
    batı: number;
  };
}

// Güvenli kaçış rotası için arayüz
interface GüvenliKacisRota {
  rota: [number, number][];
  mesafe: number;
  sure: number;
  riskli_yollar: boolean;
}

// Toplanma alanı için arayüz
interface ToplanmaAlani {
  id: number;
  ad: string;
  lat: number;
  lon: number;
}

// Form verileri için arayüz
interface FormData {
  kat_sayisi: number;
  bina_yasi: number;
  malzeme: string;
  egim: number;
  egim_yonu: string;
  zemin_turu: string;
}

// API ve Admin ayarları
const API_BASE_URL = 'http://localhost:8000';

// Axios instance oluştur
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: false // CORS için credentials'ı devre dışı bırak
});

// Sümer Mahallesi sınırları güncellendi
const sumerMahallesiKoordinatlar: [number, number][] = [
  [40.982444, 28.890655],
  [40.993394, 28.892758],
  [40.993799, 28.897157],
  [40.992632, 28.896728],
  [40.990527, 28.899324],
  [40.986931, 28.898294],
  [40.986785, 28.899046],
  [40.985797, 28.898423],
  [40.982768, 28.897844]
];

// Toplanma alanı ikonu
const toplanmaAlaniIcon = new DivIcon({
  className: 'custom-div-icon',
  html: `<div style="background-color: green; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">T</div>`,
  iconSize: [20, 20],
  iconAnchor: [10, 10]
});

// Risk seviyesine göre ikon oluşturma
const createRiskIcon = (color: string) => {
  return new DivIcon({
    className: 'custom-div-icon',
    html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white;"></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  });
};

// Harita olaylarını dinleyen bileşen
const MapEvents: React.FC<{
  onMapClick: (position: LatLng) => void;
}> = ({ onMapClick }) => {
  useMapEvents({
    click: (e) => {
      onMapClick(e.latlng);
    }
  });
  return null;
};

const MapComponent: React.FC = () => {
  // Tıklanan konum state'i
  const [clickedPosition, setClickedPosition] = useState<LatLng | null>(null);
  
  // Form verisi state'i
  const [formData, setFormData] = useState<FormData>({
    kat_sayisi: 1,
    bina_yasi: 0,
    malzeme: 'Betonarme',
    egim: 0,
    egim_yonu: 'Kuzey',
    zemin_turu: 'Sert Zemin'
  });
  
  // Kaydedilen binalar state'i
  const [buildings, setBuildings] = useState<Building[]>([]);
  
  // Risk analizleri state'i
  const [riskAnalyses, setRiskAnalyses] = useState<{[key: number]: RiskAnalysis}>({});
  
  // Moloz yayılım alanları state'i
  const [molozAlanlar, setMolozAlanlar] = useState<MolozYayilim[]>([]);
  
  // Güvenli kaçış rotası state'i
  const [kacisRotasi, setKacisRotasi] = useState<GüvenliKacisRota | null>(null);
  
  // Toplanma alanları state'i
  const [toplanmaAlanlari, setToplanmaAlanlari] = useState<ToplanmaAlani[]>([]);
  
  // Kullanıcı konumu state'i
  const [userPosition, setUserPosition] = useState<[number, number] | null>(null);
  
  // Form açık/kapalı state'i
  const [isFormOpen, setIsFormOpen] = useState<boolean>(false);
  
  // Yükleniyor state'i
  const [loading, setLoading] = useState<boolean>(true);
  
  // Mesaj state'i
  const [message, setMessage] = useState<string | null>(null);

  // Giriş durumu için state
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [username, setUsername] = useState<string>('');
  const [isAdmin, setIsAdmin] = useState<boolean>(false); // Admin kontrolü için yeni state

  // Başlangıçta tüm verileri yükle
  useEffect(() => {
    fetchAllData();
  }, []);

  // Tüm verileri API'den çek
  const fetchAllData = async () => {
    try {
      setLoading(true);
      setMessage(null);
      
      // Binaları getir
      const buildingsResponse = await api.get('/get_buildings/');
      setBuildings(buildingsResponse.data as Building[]);
      
      // Risk analizlerini getir
      const riskAnalysesResponse = await api.get('/risk_analysis/');
      // Risk analizlerini building_id'ye göre map'le
      const riskMap: {[key: number]: RiskAnalysis} = {};
      (riskAnalysesResponse.data as RiskAnalysis[]).forEach((risk: RiskAnalysis) => {
        riskMap[risk.building_id] = risk;
      });
      
      setRiskAnalyses(riskMap);
      
      // Moloz yayılım alanlarını getir
      const molozResponse = await api.get('/moloz_yayilim/');
      setMolozAlanlar(molozResponse.data as MolozYayilim[]);
      
      // Toplanma alanlarını getir
      const toplanmaResponse = await api.get('/toplanma_alanlari/');
      setToplanmaAlanlari(toplanmaResponse.data as ToplanmaAlani[]);
      
      setLoading(false);
    } catch (error) {
      console.error('Veri yüklenirken hata oluştu:', error);
      setMessage('Sunucuya bağlanılamıyor. Lütfen daha sonra tekrar deneyin.');
      setLoading(false);
    }
  };

  // Haritada bir noktaya tıklandığında
  const handleMapClick = (position: LatLng) => {
    console.log('Tıklanan koordinatlar:', position.lat, position.lng);
    setClickedPosition(position);
    setIsFormOpen(true);
  };

  // Form input değişikliklerini izle
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    // Sayısal değerler için validasyon
    if (name === 'kat_sayisi' || name === 'bina_yasi' || name === 'egim') {
      const numValue = parseInt(value);
      if (!isNaN(numValue)) {
        setFormData({
          ...formData,
          [name]: numValue
        });
      }
    } else {
      setFormData({
        ...formData,
        [name]: value
      });
    }
  };

  // Form gönderme işleyicisi güncellendi
  const handleSubmit = async (formData: FormData) => {
    if (!clickedPosition) return;
    
    // Form validasyonu
    if (formData.kat_sayisi <= 0) {
      setMessage('Kat sayısı 0\'dan büyük olmalıdır');
      return;
    }
    
    if (formData.bina_yasi < 0) {
      setMessage('Bina yaşı negatif olamaz');
      return;
    }
    
    if (formData.egim < 0 || formData.egim > 45) {
      setMessage('Eğim 0-45 derece arasında olmalıdır');
      return;
    }
    
    if (!formData.malzeme) {
      setMessage('Yapı malzemesi seçilmelidir');
      return;
    }
    
    if (!formData.egim_yonu) {
      setMessage('Eğim yönü seçilmelidir');
      return;
    }
    
    if (!formData.zemin_turu) {
      setMessage('Zemin türü seçilmelidir');
      return;
    }
    
    const buildingData = {
      lat: clickedPosition.lat,
      lon: clickedPosition.lng,
      kat_sayisi: formData.kat_sayisi,
      bina_yasi: formData.bina_yasi,
      malzeme: formData.malzeme,
      egim: formData.egim,
      egim_yonu: formData.egim_yonu,
      zemin_turu: formData.zemin_turu
    };
    
    try {
      // Save building through the API
      await api.post('/add_building/', buildingData);
      
      setMessage('Bina başarıyla kaydedildi!');
      
      // Tüm verileri yeniden yükle
      fetchAllData();
      
      // Formu kapat
      setIsFormOpen(false);
      
      // 3 saniye sonra mesajı temizle
      setTimeout(() => {
        setMessage(null);
      }, 3000);
    } catch (error: any) {
      console.error('Bina kaydedilirken hata oluştu:', error);
      if (error.response?.status === 401) {
        setMessage('Yetkisiz erişim! Bina eklemek için admin yetkisi gereklidir.');
      } else if (error.response?.status === 400) {
        setMessage(error.response.data.detail || 'Geçersiz bina bilgileri!');
      } else {
        setMessage('Bina kaydedilirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.');
      }
      
      // 3 saniye sonra mesajı temizle
      setTimeout(() => {
        setMessage(null);
      }, 3000);
    }
  };

  // Risk seviyesine göre renk döndür (risk analizi yoksa varsayılan renk)
  const getBuildingRiskColor = (buildingId: number): string => {
    return riskAnalyses[buildingId]?.color || 'blue';
  };
  
  // Kullanıcı konumunu belirle ve güvenli kaçış rotasını hesapla
  const handleSetUserPosition = async (position: LatLng) => {
    const userPos: [number, number] = [position.lat, position.lng];
    setUserPosition(userPos);
    
    try {
      // Güvenli kaçış rotasını hesapla
      const response = await api.get('/guvenli_kacis/', {
        params: {
          lat: position.lat,
          lon: position.lng
        }
      });
      
      const kacisRotasiData = response.data as GüvenliKacisRota;
      setKacisRotasi(kacisRotasiData);
      
      // Riskli yollar varsa uyarı mesajı göster
      if (kacisRotasiData.riskli_yollar) {
        setMessage('Bu rota riskli yollardan geçiyor, dikkatli olun!');
        
        // 5 saniye sonra mesajı temizle
        setTimeout(() => {
          setMessage(null);
        }, 5000);
      }
    } catch (error) {
      console.error('Güvenli kaçış rotası hesaplanırken hata oluştu:', error);
      setMessage('Güvenli kaçış rotası hesaplanırken bir hata oluştu!');
      
      // 3 saniye sonra mesajı temizle
      setTimeout(() => {
        setMessage(null);
      }, 3000);
    }
  };

  // Backend durdurma fonksiyonu
  const stopBackend = async () => {
    try {
      setLoading(true);
      setMessage("Backend durdurma isteği gönderiliyor...");
      
      const response = await api.post('/stop_server/');
      
      setMessage("Backend başarıyla durduruldu!");
      setTimeout(() => {
        setMessage("Sunucu bağlantısı kesildi. Sayfayı yenileyin veya daha sonra tekrar deneyin.");
      }, 3000);
      
    } catch (error) {
      console.error('Backend durdurulurken hata oluştu:', error);
      setMessage('Backend durdurma işlemi başarısız oldu!');
      setLoading(false);
    }
  };

  // BuildingForm bileşeni
  const BuildingForm: React.FC<{onSubmit: (formData: FormData) => void}> = ({ onSubmit }) => {
    const [localFormData, setLocalFormData] = useState<FormData>({
      kat_sayisi: 1,
      bina_yasi: 0,
      malzeme: 'Betonarme',
      egim: 0,
      egim_yonu: 'Kuzey',
      zemin_turu: 'Sert Zemin'
    });

    const handleLocalSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      onSubmit(localFormData);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const { name, value } = e.target;
      
      // Sayısal değerler için validasyon
      if (name === 'kat_sayisi' || name === 'bina_yasi' || name === 'egim') {
        const numValue = parseInt(value);
        if (!isNaN(numValue)) {
          setLocalFormData({
            ...localFormData,
            [name]: numValue
          });
        }
      } else {
        setLocalFormData({
          ...localFormData,
          [name]: value
        });
      }
    };

    return (
      <form onSubmit={handleLocalSubmit}>
        <div>
          <label htmlFor="kat_sayisi">Bina Kat Sayısı:</label>
          <input
            type="number"
            id="kat_sayisi"
            name="kat_sayisi"
            min="1"
            value={localFormData.kat_sayisi}
            onChange={handleInputChange}
            required
          />
        </div>
        <div>
          <label htmlFor="bina_yasi">Bina Yaşı:</label>
          <input
            type="number"
            id="bina_yasi"
            name="bina_yasi"
            min="0"
            value={localFormData.bina_yasi}
            onChange={handleInputChange}
            required
          />
        </div>
        <div>
          <label htmlFor="malzeme">Yapı Malzemesi:</label>
          <select
            id="malzeme"
            name="malzeme"
            value={localFormData.malzeme}
            onChange={handleInputChange}
            required
          >
            <option value="Betonarme">Betonarme</option>
            <option value="Çelik">Çelik</option>
            <option value="Yığma Tuğla">Yığma Tuğla</option>
            <option value="Ahşap">Ahşap</option>
          </select>
        </div>
        <div>
          <label htmlFor="egim">Eğim (Derece):</label>
          <input
            type="number"
            id="egim"
            name="egim"
            min="0"
            max="45"
            value={localFormData.egim}
            onChange={handleInputChange}
            required
          />
        </div>
        <div>
          <label htmlFor="egim_yonu">Eğim Yönü:</label>
          <select
            id="egim_yonu"
            name="egim_yonu"
            value={localFormData.egim_yonu}
            onChange={handleInputChange}
            required
          >
            <option value="Kuzey">Kuzey</option>
            <option value="Kuzeydoğu">Kuzeydoğu</option>
            <option value="Doğu">Doğu</option>
            <option value="Güneydoğu">Güneydoğu</option>
            <option value="Güney">Güney</option>
            <option value="Güneybatı">Güneybatı</option>
            <option value="Batı">Batı</option>
            <option value="Kuzeybatı">Kuzeybatı</option>
          </select>
        </div>
        <div>
          <label htmlFor="zemin_turu">Zemin Türü:</label>
          <select
            id="zemin_turu"
            name="zemin_turu"
            value={localFormData.zemin_turu}
            onChange={handleInputChange}
            required
          >
            <option value="Kaya">Kaya</option>
            <option value="Sert Zemin">Sert Zemin</option>
            <option value="Orta Sert">Orta Sert</option>
            <option value="Gevşek Zemin">Gevşek Zemin</option>
          </select>
        </div>
        <button type="submit">Kaydet</button>
      </form>
    );
  };

  return (
    <div style={{ height: '100vh', width: '100%', position: 'relative' }}>
      {loading ? (
        <div style={{ 
          position: 'absolute', 
          top: '50%', 
          left: '50%', 
          transform: 'translate(-50%, -50%)',
          zIndex: 1000,
          background: 'rgba(255, 255, 255, 0.8)',
          padding: '20px',
          borderRadius: '5px'
        }}>
          Yükleniyor...
        </div>
      ) : null}
      
      {message && (
        <div style={{ 
          position: 'absolute', 
          top: '20px', 
          left: '50%', 
          transform: 'translateX(-50%)',
          zIndex: 1000,
          background: 'rgba(0, 0, 0, 0.7)',
          color: 'white',
          padding: '10px 20px',
          borderRadius: '5px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.2)'
        }}>
          {message}
        </div>
      )}
      
      <MapContainer 
        center={[40.998, 28.904]} 
        zoom={14} 
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Haritada Sümer Mahallesi sınırlarını göster */}
        <Polygon
          positions={sumerMahallesiKoordinatlar}
          pathOptions={{
            color: 'red',
            weight: 2,
            fillOpacity: 0,
            interactive: false // Tıklamayı devre dışı bırak
          }}
        />
        
        {/* Harita tıklama olaylarını dinle */}
        <MapEvents onMapClick={handleMapClick} />
        
        {/* Tıklanan konum için marker ve form */}
        {clickedPosition && isFormOpen && (
          <Marker position={clickedPosition} icon={DefaultIcon}>
            <Popup>
              <BuildingForm onSubmit={handleSubmit} />
            </Popup>
          </Marker>
        )}
        
        {/* Kaydedilen binaları göster */}
        {buildings.map((building) => (
          <Marker 
            key={building.id} 
            position={[building.lat, building.lon]} 
            icon={createRiskIcon(getBuildingRiskColor(building.id))}
          >
            <Popup>
              <div>
                <h3>Bina Bilgileri</h3>
                <p><strong>Kat Sayısı:</strong> {building.kat_sayisi}</p>
                <p><strong>Bina Yaşı:</strong> {building.bina_yasi}</p>
                <p><strong>Yapı Malzemesi:</strong> {building.malzeme}</p>
                <p><strong>Eğim:</strong> {building.egim}° ({building.egim_yonu} yönünde)</p>
                <p><strong>Zemin Türü:</strong> {building.zemin_turu}</p>
                
                {riskAnalyses[building.id] && (
                  <div style={{ marginTop: '10px', borderTop: '1px solid #ccc', paddingTop: '10px' }}>
                    <h4>Risk Analizi</h4>
                    <p><strong>Risk Skoru:</strong> {(riskAnalyses[building.id].risk_score * 100).toFixed(2)}%</p>
                    <p><strong>Risk Seviyesi:</strong> {riskAnalyses[building.id].risk_level}</p>
                    <div 
                      style={{ 
                        backgroundColor: riskAnalyses[building.id].color, 
                        width: '100%', 
                        height: '10px', 
                        borderRadius: '5px',
                        marginTop: '5px'
                      }} 
                    />
                  </div>
                )}
                
                <div style={{ marginTop: '10px' }}>
                  <button 
                    onClick={() => handleSetUserPosition(new LatLng(building.lat, building.lon))}
                    style={{
                      padding: '5px 10px',
                      backgroundColor: '#4CAF50',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    Buradan Kaçış Rotası Hesapla
                  </button>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
        
        {/* Moloz yayılım alanlarını göster */}
        {molozAlanlar.map((moloz) => (
          <React.Fragment key={`moloz-${moloz.bina_id}`}>
            {moloz.yonler ? (
              // Eğim varsa elips şeklinde göster
              <>
                {/* Kuzey-Güney yönünde elips */}
                <Circle
                  center={[moloz.lat, moloz.lon]}
                  pathOptions={{ color: 'red', fillColor: 'red', fillOpacity: 0.3 }}
                  radius={moloz.yonler.kuzey}
                  eventHandlers={{
                    click: () => handleSetUserPosition(new LatLng(moloz.lat, moloz.lon))
                  }}
                />
                <Circle
                  center={[moloz.lat, moloz.lon]}
                  pathOptions={{ color: 'red', fillColor: 'red', fillOpacity: 0.3 }}
                  radius={moloz.yonler.güney}
                  eventHandlers={{
                    click: () => handleSetUserPosition(new LatLng(moloz.lat, moloz.lon))
                  }}
                />
                {/* Doğu-Batı yönünde elips */}
                <Circle
                  center={[moloz.lat, moloz.lon]}
                  pathOptions={{ color: 'red', fillColor: 'red', fillOpacity: 0.3 }}
                  radius={moloz.yonler.doğu}
                  eventHandlers={{
                    click: () => handleSetUserPosition(new LatLng(moloz.lat, moloz.lon))
                  }}
                />
                <Circle
                  center={[moloz.lat, moloz.lon]}
                  pathOptions={{ color: 'red', fillColor: 'red', fillOpacity: 0.3 }}
                  radius={moloz.yonler.batı}
                  eventHandlers={{
                    click: () => handleSetUserPosition(new LatLng(moloz.lat, moloz.lon))
                  }}
                />
              </>
            ) : (
              // Eğim yoksa daire şeklinde göster
              <Circle
                center={[moloz.lat, moloz.lon]}
                pathOptions={{ color: 'red', fillColor: 'red', fillOpacity: 0.3 }}
                radius={moloz.yayilim_cap}
                eventHandlers={{
                  click: () => handleSetUserPosition(new LatLng(moloz.lat, moloz.lon))
                }}
              />
            )}
          </React.Fragment>
        ))}
        
        {/* Toplanma alanlarını göster */}
        {toplanmaAlanlari.map((alan) => (
          <Marker
            key={`toplanma-${alan.id}`}
            position={[alan.lat, alan.lon]}
            icon={toplanmaAlaniIcon}
          >
            <Popup>
              <div>
                <h3>Toplanma Alanı</h3>
                <p><strong>Ad:</strong> {alan.ad}</p>
                <p><strong>Koordinatlar:</strong> {alan.lat.toFixed(6)}, {alan.lon.toFixed(6)}</p>
                <p className="text-success"><strong>Bilgi:</strong> Bu alan deprem sonrası güvenli toplanma noktasıdır.</p>
              </div>
            </Popup>
          </Marker>
        ))}
        
        {/* Kullanıcı konumunu göster */}
        {userPosition && (
          <Marker
            position={userPosition}
            icon={new DivIcon({
              className: 'custom-div-icon',
              html: `<div style="background-color: blue; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white;"></div>`,
              iconSize: [20, 20],
              iconAnchor: [10, 10]
            })}
          >
            <Popup>
              <div>
                <h3>Konumunuz</h3>
                <p><strong>Koordinatlar:</strong> {userPosition[0].toFixed(6)}, {userPosition[1].toFixed(6)}</p>
              </div>
            </Popup>
          </Marker>
        )}
        
        {/* Güvenli kaçış rotasını göster */}
        {kacisRotasi && (
          <Polyline
            positions={kacisRotasi.rota}
            pathOptions={{
              color: kacisRotasi.riskli_yollar ? 'orange' : 'blue',
              weight: 5,
              opacity: 0.7,
              dashArray: kacisRotasi.riskli_yollar ? '10, 10' : undefined
            }}
          >
            <Popup>
              <div>
                <h3>Güvenli Kaçış Rotası</h3>
                <p><strong>Mesafe:</strong> {(kacisRotasi.mesafe / 1000).toFixed(2)} km</p>
                <p><strong>Tahmini Süre:</strong> {Math.round(kacisRotasi.sure / 60)} dakika</p>
                {kacisRotasi.riskli_yollar && (
                  <p className="text-warning"><strong>Uyarı:</strong> Bu rota riskli yollardan geçiyor, dikkatli olun!</p>
                )}
              </div>
            </Popup>
          </Polyline>
        )}
      </MapContainer>
      
      {/* Risk seviyesi açıklamaları */}
      <div style={{
        position: 'absolute',
        bottom: '20px',
        right: '20px',
        backgroundColor: 'white',
        padding: '10px',
        borderRadius: '5px',
        boxShadow: '0 0 10px rgba(0,0,0,0.2)',
        zIndex: 1000
      }}>
        <h4 style={{ margin: '0 0 10px 0' }}>Risk Seviyeleri</h4>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
          <div style={{ width: '20px', height: '20px', backgroundColor: 'green', borderRadius: '50%', marginRight: '10px' }} />
          <span>Düşük Risk</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
          <div style={{ width: '20px', height: '20px', backgroundColor: 'yellow', borderRadius: '50%', marginRight: '10px' }} />
          <span>Orta Risk</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
          <div style={{ width: '20px', height: '20px', backgroundColor: 'orange', borderRadius: '50%', marginRight: '10px' }} />
          <span>Orta-Yüksek Risk</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '15px' }}>
          <div style={{ width: '20px', height: '20px', backgroundColor: 'red', borderRadius: '50%', marginRight: '10px' }} />
          <span>Yüksek Risk</span>
        </div>
        
        <h4 style={{ margin: '0 0 10px 0' }}>Harita Sembolleri</h4>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
          <div style={{ width: '20px', height: '20px', backgroundColor: 'red', opacity: 0.3, marginRight: '10px' }} />
          <span>Moloz Yayılım Alanı</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
          <div style={{ width: '20px', height: '20px', backgroundColor: 'green', borderRadius: '50%', marginRight: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold', fontSize: '12px' }}>T</div>
          <span>Toplanma Alanı</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
          <div style={{ width: '20px', height: '20px', backgroundColor: 'blue', borderRadius: '50%', marginRight: '10px' }} />
          <span>Konumunuz</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div style={{ width: '20px', height: '5px', backgroundColor: 'blue', marginRight: '10px' }} />
          <span>Güvenli Kaçış Rotası</span>
        </div>
      </div>
      
      {/* Kullanıcı konumu belirleme butonu */}
      <div style={{
        position: 'absolute',
        top: '20px',
        left: '20px',
        zIndex: 1000
      }}>
        <button
          onClick={() => {
            if (navigator.geolocation) {
              navigator.geolocation.getCurrentPosition(
                (position) => {
                  const userPos: [number, number] = [position.coords.latitude, position.coords.longitude];
                  setUserPosition(userPos);
                  handleSetUserPosition(new LatLng(userPos[0], userPos[1]));
                },
                (error) => {
                  console.error('Konum alınamadı:', error);
                  setMessage('Konum alınamadı. Lütfen konum izinlerini kontrol edin.');
                  setTimeout(() => setMessage(null), 3000);
                }
              );
            } else {
              setMessage('Tarayıcınız konum hizmetlerini desteklemiyor.');
              setTimeout(() => setMessage(null), 3000);
            }
          }}
          style={{
            padding: '10px 15px',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            boxShadow: '0 2px 5px rgba(0,0,0,0.2)'
          }}
        >
          Konumumu Bul ve Kaçış Rotası Hesapla
        </button>
      </div>
    </div>
  );
};

export default MapComponent; 
