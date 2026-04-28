from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import os
from pathlib import Path

# Veri modeli
class Building(BaseModel):
    lat: float
    lon: float
    kat_sayisi: int
    bina_yasi: int
    malzeme: str

# Veri dosyası yolu
DATA_FILE = Path("data/buildings.json")

# Veri dosyasının var olduğundan emin ol
os.makedirs(DATA_FILE.parent, exist_ok=True)
if not DATA_FILE.exists():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# FastAPI uygulaması
app = FastAPI(title="Deprem Haritası API")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme için tüm originlere izin ver
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Binaları getir
@app.get("/get_buildings/", response_model=List[Building])
async def get_buildings():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            buildings = json.load(f)
        return buildings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Veri okuma hatası: {str(e)}")

# Bina ekle
@app.post("/add_building/", response_model=Building)
async def add_building(building: Building):
    try:
        # Mevcut binaları oku
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            buildings = json.load(f)
        
        # Yeni binayı ekle
        building_dict = building.dict()
        buildings.append(building_dict)
        
        # Dosyaya kaydet
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(buildings, f, ensure_ascii=False, indent=2)
        
        return building
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bina ekleme hatası: {str(e)}")

# Ana sayfa
@app.get("/")
async def read_root():
    return {"message": "Deprem Haritası API'sine Hoş Geldiniz"}

# Uygulama çalıştırma (doğrudan çalıştırıldığında)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 