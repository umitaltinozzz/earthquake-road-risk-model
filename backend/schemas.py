from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# Bina oluşturma şeması
class BuildingCreate(BaseModel):
    lat: float
    lon: float
    kat_sayisi: int
    bina_yasi: int
    malzeme: str
    egim: int = 0
    egim_yonu: str = "kuzey"
    zemin_turu: str = "normal"

# Bina şeması
class Building(BuildingCreate):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Risk analizi şeması
class RiskAnalysis(BaseModel):
    building_id: int
    risk_score: float
    risk_level: str
    color: str

# Moloz yayılım şeması
class MolozYayilim(BaseModel):
    bina_id: int
    lat: float
    lon: float
    yayilim_cap: float
    risk_seviyesi: str
    yonler: Optional[Dict[str, float]] = None

# Güvenli kaçış rotası şeması
class GüvenliKacisRota(BaseModel):
    rota: List[List[float]]
    mesafe: float
    sure: float
    riskli_yollar: bool 