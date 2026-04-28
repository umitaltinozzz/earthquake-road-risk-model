from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Dict
from datetime import datetime

import models
import schemas

# Bina ekleme
async def create_building(db: AsyncSession, building: schemas.BuildingCreate) -> models.Building:
    """
    Yeni bir bina ekler
    """
    db_building = models.Building(
        lat=building.lat,
        lon=building.lon,
        kat_sayisi=building.kat_sayisi,
        bina_yasi=building.bina_yasi,
        malzeme=building.malzeme,
        egim=building.egim,
        egim_yonu=building.egim_yonu,
        zemin_turu=building.zemin_turu
    )
    db.add(db_building)
    await db.commit()
    await db.refresh(db_building)
    return db_building

# Tüm binaları getir
async def get_buildings(db: AsyncSession) -> List[models.Building]:
    """
    Tüm binaları getirir
    """
    result = await db.execute(select(models.Building))
    return result.scalars().all()

# Belirli bir binayı getir
async def get_building(db: AsyncSession, building_id: int) -> Optional[models.Building]:
    """
    ID'ye göre bir binayı getirir
    """
    result = await db.execute(select(models.Building).filter(models.Building.id == building_id))
    return result.scalars().first()

# Risk hesaplama
async def calculate_risk(building: models.Building) -> schemas.RiskAnalysis:
    """
    Bir binanın risk analizini hesaplar
    """
    # Risk puanı hesaplama
    risk_score = 0
    
    # Kat sayısı faktörü (daha yüksek = daha riskli)
    if building.kat_sayisi <= 3:
        risk_score += 10
    elif building.kat_sayisi <= 6:
        risk_score += 20
    else:
        risk_score += 30
    
    # Bina yaşı faktörü (daha yaşlı = daha riskli)
    if building.bina_yasi < 10:
        risk_score += 10
    elif building.bina_yasi < 30:
        risk_score += 25
    else:
        risk_score += 40
    
    # Malzeme faktörü
    if building.malzeme.lower() == "betonarme":
        risk_score += 15
    elif building.malzeme.lower() == "çelik":
        risk_score += 10
    elif building.malzeme.lower() == "ahşap":
        risk_score += 20
    else:  # Yığma, kerpiç vb.
        risk_score += 35
    
    # Eğim faktörü
    risk_score += min(building.egim * 2, 20)  # Maksimum 20 puan
    
    # Zemin türü faktörü
    if building.zemin_turu.lower() == "sağlam":
        risk_score += 5
    elif building.zemin_turu.lower() == "normal":
        risk_score += 15
    else:  # Yumuşak, alüvyon vb.
        risk_score += 25
    
    # Risk seviyesi belirleme
    risk_level = ""
    color = ""
    
    if risk_score < 50:
        risk_level = "Düşük"
        color = "green"
    elif risk_score < 80:
        risk_level = "Orta"
        color = "yellow"
    elif risk_score < 110:
        risk_level = "Yüksek"
        color = "orange"
    else:
        risk_level = "Çok Yüksek"
        color = "red"
    
    return schemas.RiskAnalysis(
        building_id=building.id,
        risk_score=risk_score,
        risk_level=risk_level,
        color=color
    ) 