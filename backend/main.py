from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Tuple, Optional, Dict
import math

import crud
import models
import schemas
from database import get_db, init_db
from moloz_hesaplama import hesapla_tum_moloz_alanlari, yol_moloz_altinda_mi
from route_service import hesapla_rota

app = FastAPI(title="Deprem Risk Analizi API")

# CORS ayarları güncellendi
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Toplanma alanları güncellendi
TOPLANMA_ALANLARI = [
    {"id": 1, "ad": "Sümer Toplanma Alanı 1", "lat": 40.990766, "lon": 28.896810},
    {"id": 2, "ad": "Sümer Toplanma Alanı 2", "lat": 40.985568, "lon": 28.896263}
]

# Uygulama başlangıcında veritabanını başlat
@app.on_event("startup")
async def startup_db_client():
    await init_db()

# Ana sayfa
@app.get("/")
async def read_root():
    return {"message": "Deprem Risk Analizi API'sine Hoş Geldiniz"}

# Tüm binaları getir
@app.get("/get_buildings/", response_model=List[schemas.Building])
async def get_buildings(db: AsyncSession = Depends(get_db)):
    buildings = await crud.get_buildings(db)
    return buildings

# Bina ekle (admin doğrulaması kaldırıldı)
@app.post("/add_building/", response_model=schemas.Building)
async def add_building(
    building: schemas.BuildingCreate, 
    db: AsyncSession = Depends(get_db)
):
    # Boş veya hatalı değer kontrolü
    if building.kat_sayisi <= 0:
        raise HTTPException(status_code=400, detail="Kat sayısı 0'dan büyük olmalıdır")
    if building.bina_yasi < 0:
        raise HTTPException(status_code=400, detail="Bina yaşı negatif olamaz")
    if not building.malzeme:
        raise HTTPException(status_code=400, detail="Yapı malzemesi belirtilmelidir")
    
    return await crud.create_building(db, building)

# Bina risk analizi
@app.get("/risk_analysis/{building_id}", response_model=schemas.RiskAnalysis)
async def risk_analysis(building_id: int, db: AsyncSession = Depends(get_db)):
    building = await crud.get_building(db, building_id)
    if building is None:
        raise HTTPException(status_code=404, detail="Bina bulunamadı")
    
    return await crud.calculate_risk(building)

# Tüm binaların risk analizini getir
@app.get("/risk_analysis/", response_model=List[schemas.RiskAnalysis])
async def all_buildings_risk_analysis(db: AsyncSession = Depends(get_db)):
    buildings = await crud.get_buildings(db)
    risk_analyses = []
    
    for building in buildings:
        risk_analysis = await crud.calculate_risk(building)
        risk_analyses.append(risk_analysis)
    
    return risk_analyses

# Moloz yayılım alanlarını getir
@app.get("/moloz_yayilim/", response_model=List[schemas.MolozYayilim])
async def get_moloz_yayilim(db: AsyncSession = Depends(get_db)):
    buildings = await crud.get_buildings(db)
    
    # Tüm binaların moloz yayılım alanlarını hesapla
    moloz_alanlari = hesapla_tum_moloz_alanlari(buildings)
    
    return moloz_alanlari

# Belirli bir binanın moloz yayılım alanını getir
@app.get("/moloz_yayilim/{building_id}", response_model=schemas.MolozYayilim)
async def get_building_moloz_yayilim(building_id: int, db: AsyncSession = Depends(get_db)):
    building = await crud.get_building(db, building_id)
    if building is None:
        raise HTTPException(status_code=404, detail="Bina bulunamadı")
    
    # Binanın moloz yayılım alanını hesapla
    moloz_alani = hesapla_tum_moloz_alanlari([building])[0]
    
    return moloz_alani

# En yakın toplanma alanını bul
def bul_en_yakin_toplanma_alani(lat: float, lon: float) -> dict:
    """
    Verilen konuma en yakın toplanma alanını bulur
    
    Args:
        lat: Enlem
        lon: Boylam
        
    Returns:
        dict: En yakın toplanma alanı
    """
    en_yakin = None
    en_kisa_mesafe = float('inf')
    
    for alan in TOPLANMA_ALANLARI:
        # İki nokta arasındaki mesafeyi hesapla (Haversine formülü)
        # Dünya üzerinde yaklaşık 1 derece = 111.32 km = 111320 m
        lat_fark = abs(alan["lat"] - lat) * 111320
        lon_fark = abs(alan["lon"] - lon) * 111320 * math.cos(math.radians(lat))
        
        # Kuş uçuşu mesafe (metre)
        mesafe = math.sqrt(lat_fark**2 + lon_fark**2)
        
        if mesafe < en_kisa_mesafe:
            en_kisa_mesafe = mesafe
            en_yakin = alan
    
    return en_yakin

# Güvenli kaçış rotası hesapla
@app.get("/guvenli_kacis/", response_model=schemas.GüvenliKacisRota)
async def hesapla_guvenli_kacis(lat: float, lon: float, db: AsyncSession = Depends(get_db)):
    # Tüm binaların moloz yayılım alanlarını hesapla
    buildings = await crud.get_buildings(db)
    moloz_alanlari = hesapla_tum_moloz_alanlari(buildings)
    
    # En yakın toplanma alanını bul
    toplanma_alani = bul_en_yakin_toplanma_alani(lat, lon)
    
    # OpenRouteService API ile rota hesapla
    # API lon,lat sırasını kullanır, bizim verilerimiz lat,lon sırasında
    baslangic = (lon, lat)
    bitis = (toplanma_alani["lon"], toplanma_alani["lat"])
    
    # Rota hesapla - artık async değil, doğrudan çağrılabilir
    rota_bilgileri = hesapla_rota(baslangic, bitis, moloz_alanlari)
    
    return rota_bilgileri

# Toplanma alanlarını getir
@app.get("/toplanma_alanlari/")
async def get_toplanma_alanlari():
    return TOPLANMA_ALANLARI

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 