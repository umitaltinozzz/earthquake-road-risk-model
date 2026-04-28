import math
import requests
import os
from typing import List, Dict, Tuple, Any
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# OpenRouteService API anahtarı
ORS_API_KEY = os.getenv("ORS_API_KEY", "")
ORS_API_URL = "https://api.openrouteservice.org/v2/directions/foot-walking/geojson"

def hesapla_rota(baslangic: Tuple[float, float], bitis: Tuple[float, float], moloz_alanlari: List[Dict]) -> Dict:
    """
    İki nokta arasındaki rotayı hesaplar
    
    Args:
        baslangic: Başlangıç noktası (lon, lat)
        bitis: Bitiş noktası (lon, lat)
        moloz_alanlari: Moloz yayılım alanları listesi
        
    Returns:
        Dict: Rota bilgileri
    """
    try:
        # OpenRouteService API kullanarak rota hesapla
        if ORS_API_KEY:
            # API isteği için headers ve body
            headers = {
                'Authorization': ORS_API_KEY,
                'Content-Type': 'application/json; charset=utf-8',
                'Accept': 'application/json, application/geo+json'
            }
            
            body = {
                "coordinates": [
                    [baslangic[0], baslangic[1]],
                    [bitis[0], bitis[1]]
                ],
                "instructions": "false",
                "preference": "shortest",
                "units": "m"
            }
            
            # API isteği gönder
            response = requests.post(ORS_API_URL, json=body, headers=headers)
            
            # Başarılı yanıt alındıysa
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Rotayı al
                    coordinates = data["features"][0]["geometry"]["coordinates"]
                    
                    # Koordinatları [lat, lon] formatına çevir
                    rota = [[coord[1], coord[0]] for coord in coordinates]
                    
                    # Mesafe ve süreyi al
                    mesafe = data["features"][0]["properties"]["segments"][0]["distance"]  # metre
                    sure = data["features"][0]["properties"]["segments"][0]["duration"] / 60  # dakika
                    
                    # Rota üzerindeki noktaların moloz altında olup olmadığını kontrol et
                    riskli_yollar = False
                    for i in range(1, len(rota) - 1):  # Başlangıç ve bitiş noktalarını kontrol etme
                        nokta = (rota[i][1], rota[i][0])  # (lon, lat) formatına çevir
                        if yol_moloz_altinda_mi(nokta, moloz_alanlari):
                            riskli_yollar = True
                            break
                    
                    return {
                        "rota": rota,
                        "mesafe": mesafe,
                        "sure": sure,
                        "riskli_yollar": riskli_yollar
                    }
                except Exception as e:
                    print(f"API yanıtı işlenirken hata: {e}")
                    print(f"API yanıtı: {response.text}")
            else:
                print(f"OpenRouteService API hatası: {response.status_code} - {response.text}")
        
        # API anahtarı yoksa veya API isteği başarısız olduysa basit rota hesapla
        print("OpenRouteService API kullanılamadı, basit rota hesaplanıyor...")
        
        # Başlangıç ve bitiş noktaları
        baslangic_lon, baslangic_lat = baslangic
        bitis_lon, bitis_lat = bitis
        
        # Kuş uçuşu mesafe (metre)
        # Dünya üzerinde yaklaşık 1 derece = 111.32 km = 111320 m
        lat_fark = abs(bitis_lat - baslangic_lat) * 111320
        lon_fark = abs(bitis_lon - baslangic_lon) * 111320 * math.cos(math.radians(baslangic_lat))
        kus_ucusu_mesafe = math.sqrt(lat_fark**2 + lon_fark**2)
        
        # Basit bir rota oluştur (düz çizgi)
        # 10 nokta içeren bir rota
        rota = []
        for i in range(11):
            oran = i / 10
            lat = baslangic_lat + (bitis_lat - baslangic_lat) * oran
            lon = baslangic_lon + (bitis_lon - baslangic_lon) * oran
            rota.append([lat, lon])
        
        # Rota üzerindeki noktaların moloz altında olup olmadığını kontrol et
        riskli_yollar = False
        for i in range(1, len(rota) - 1):  # Başlangıç ve bitiş noktalarını kontrol etme
            nokta = (rota[i][1], rota[i][0])  # (lon, lat) formatına çevir
            if yol_moloz_altinda_mi(nokta, moloz_alanlari):
                riskli_yollar = True
                break
        
        # Tahmini süre (dakika) - ortalama yürüme hızı 5 km/saat = 83.33 m/dakika
        sure = kus_ucusu_mesafe / 83.33
        
        return {
            "rota": rota,
            "mesafe": kus_ucusu_mesafe,
            "sure": sure,
            "riskli_yollar": riskli_yollar
        }
    except Exception as e:
        print(f"Rota hesaplanırken hata oluştu: {e}")
        # Hata durumunda basit bir rota döndür
        return {
            "rota": [[baslangic_lat, baslangic_lon], [bitis_lat, bitis_lon]],
            "mesafe": 0,
            "sure": 0,
            "riskli_yollar": False
        }

def yol_moloz_altinda_mi(yol_noktasi: Tuple[float, float], moloz_alanlari: List[Dict]) -> bool:
    """
    Bir yol noktasının moloz altında olup olmadığını kontrol eder
    
    Args:
        yol_noktasi: Yol noktasının koordinatları (lon, lat)
        moloz_alanlari: Moloz yayılım alanları listesi
        
    Returns:
        bool: Yol noktası moloz altındaysa True, değilse False
    """
    lon, lat = yol_noktasi
    
    for moloz in moloz_alanlari:
        # Moloz merkezi ile yol noktası arasındaki mesafeyi hesapla
        # Dünya üzerinde yaklaşık 1 derece = 111.32 km = 111320 m
        lat_fark = abs(moloz["lat"] - lat) * 111320
        lon_fark = abs(moloz["lon"] - lon) * 111320 * math.cos(math.radians(lat))
        
        # Kuş uçuşu mesafe (metre)
        mesafe = math.sqrt(lat_fark**2 + lon_fark**2)
        
        # Eğim yönüne göre kontrol
        if "yonler" in moloz:
            # Yol noktasının moloz merkezine göre hangi yönde olduğunu belirle
            yon = ""
            if lat > moloz["lat"]:
                yon = "kuzey"
            else:
                yon = "güney"
                
            if lon > moloz["lon"]:
                yon += "-doğu" if yon else "doğu"
            else:
                yon += "-batı" if yon else "batı"
            
            # Basitleştirme için ana yönleri kullan
            if "kuzey" in yon:
                yaricap = moloz["yonler"]["kuzey"]
            elif "güney" in yon:
                yaricap = moloz["yonler"]["güney"]
            elif "doğu" in yon:
                yaricap = moloz["yonler"]["doğu"]
            elif "batı" in yon:
                yaricap = moloz["yonler"]["batı"]
            else:
                yaricap = moloz["yayilim_cap"]
        else:
            yaricap = moloz["yayilim_cap"]
        
        # Mesafe yayılım yarıçapından küçükse, yol noktası moloz altındadır
        if mesafe < yaricap:
            return True
    
    return False 
