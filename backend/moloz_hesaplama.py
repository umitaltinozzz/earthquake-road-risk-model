import math
from typing import List, Dict, Tuple, Any

def hesapla_bina_hacmi(kat_sayisi: int, taban_alani: float = 100.0) -> float:
    """
    Binanın toplam hacmini hesaplar
    
    Args:
        kat_sayisi: Bina kat sayısı
        taban_alani: Binanın taban alanı (m²), varsayılan 100m²
        
    Returns:
        float: Binanın toplam hacmi (m³)
    """
    # Ortalama kat yüksekliği 3 metre olarak kabul edilir
    kat_yuksekligi = 3.0
    
    # Toplam hacim = taban alanı * kat yüksekliği * kat sayısı
    toplam_hacim = taban_alani * kat_yuksekligi * kat_sayisi
    
    return toplam_hacim

def hesapla_moloz_hacmi(bina_hacmi: float) -> float:
    """
    Bina çöktüğünde oluşacak moloz hacmini hesaplar
    
    Args:
        bina_hacmi: Binanın toplam hacmi (m³)
        
    Returns:
        float: Moloz hacmi (m³)
    """
    # Moloz hacmi, bina hacminin yaklaşık %50'si olarak kabul edilir
    # (Boşluklar, pencereler, kapılar vs. nedeniyle)
    moloz_hacmi = bina_hacmi * 0.5
    
    return moloz_hacmi

def hesapla_yayilim_alani(moloz_hacmi: float, egim: int = 0, egim_yonu: str = "kuzey") -> Tuple[float, Dict[str, float]]:
    """
    Molozun yayılacağı alanı hesaplar
    
    Args:
        moloz_hacmi: Moloz hacmi (m³)
        egim: Arazinin eğimi (derece)
        egim_yonu: Eğimin yönü (kuzey, güney, doğu, batı)
        
    Returns:
        Tuple[float, Dict[str, float]]: Yayılım alanı (m²) ve yönlere göre yayılım mesafeleri
    """
    # Ortalama moloz yüksekliği (m)
    ortalama_yukseklik = 1.5
    
    # Temel yayılım alanı (düz arazi için)
    temel_alan = moloz_hacmi / ortalama_yukseklik
    
    # Yayılım yarıçapı (m) - daire şeklinde yayıldığını varsayarsak
    temel_yaricap = math.sqrt(temel_alan / math.pi)
    
    # Eğim faktörü - eğim arttıkça yayılım mesafesi artar
    egim_faktoru = 1.0 + (egim / 45.0)  # 45 derece eğimde 2 kat daha fazla yayılım
    
    # Yönlere göre yayılım mesafeleri
    yonler = {
        "kuzey": temel_yaricap,
        "güney": temel_yaricap,
        "doğu": temel_yaricap,
        "batı": temel_yaricap
    }
    
    # Eğim yönüne göre yayılım mesafelerini ayarla
    if egim > 0:
        egim_yonu = egim_yonu.lower()
        
        if egim_yonu == "kuzey":
            yonler["güney"] = temel_yaricap * egim_faktoru
            yonler["kuzey"] = temel_yaricap * 0.5  # Eğim yukarı doğru olduğu için daha az yayılım
        elif egim_yonu == "güney":
            yonler["kuzey"] = temel_yaricap * egim_faktoru
            yonler["güney"] = temel_yaricap * 0.5
        elif egim_yonu == "doğu":
            yonler["batı"] = temel_yaricap * egim_faktoru
            yonler["doğu"] = temel_yaricap * 0.5
        elif egim_yonu == "batı":
            yonler["doğu"] = temel_yaricap * egim_faktoru
            yonler["batı"] = temel_yaricap * 0.5
    
    # Toplam yayılım alanı (m²)
    # Elips şeklinde bir alan olarak hesaplanır
    a = (yonler["doğu"] + yonler["batı"]) / 2
    b = (yonler["kuzey"] + yonler["güney"]) / 2
    yayilim_alani = math.pi * a * b
    
    # En büyük yayılım mesafesi, yayılım yarıçapı olarak kullanılacak
    max_yaricap = max(yonler.values())
    
    return max_yaricap, yonler

def hesapla_moloz_yayilim(building: Any) -> Dict:
    """
    Bir bina için moloz yayılım alanını hesaplar
    
    Args:
        building: Bina nesnesi
        
    Returns:
        Dict: Moloz yayılım bilgileri
    """
    # Bina hacmini hesapla
    bina_hacmi = hesapla_bina_hacmi(building.kat_sayisi)
    
    # Moloz hacmini hesapla
    moloz_hacmi = hesapla_moloz_hacmi(bina_hacmi)
    
    # Yayılım alanını hesapla
    yaricap, yonler = hesapla_yayilim_alani(moloz_hacmi, building.egim, building.egim_yonu)
    
    # Risk seviyesini belirle
    risk_seviyesi = "Yüksek" if yaricap > 15 else "Orta" if yaricap > 10 else "Düşük"
    
    return {
        "bina_id": building.id,
        "lat": building.lat,
        "lon": building.lon,
        "yayilim_cap": yaricap,
        "risk_seviyesi": risk_seviyesi,
        "yonler": yonler
    }

def hesapla_tum_moloz_alanlari(buildings: List[Any]) -> List[Dict]:
    """
    Tüm binalar için moloz yayılım alanlarını hesaplar
    
    Args:
        buildings: Bina nesneleri listesi
        
    Returns:
        List[Dict]: Moloz yayılım bilgileri listesi
    """
    moloz_alanlari = []
    
    for building in buildings:
        moloz_alani = hesapla_moloz_yayilim(building)
        moloz_alanlari.append(moloz_alani)
    
    return moloz_alanlari

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