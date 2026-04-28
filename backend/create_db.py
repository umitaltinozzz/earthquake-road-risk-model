import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import random

from database import init_db, async_session
import models
import schemas

# Örnek bina verileri
SAMPLE_BUILDINGS = [
    {
        "lat": 40.990766, 
        "lon": 28.896810, 
        "kat_sayisi": 5, 
        "bina_yasi": 25, 
        "malzeme": "betonarme",
        "egim": 5,
        "egim_yonu": "güney",
        "zemin_turu": "normal"
    },
    {
        "lat": 40.989568, 
        "lon": 28.895263, 
        "kat_sayisi": 8, 
        "bina_yasi": 40, 
        "malzeme": "yığma",
        "egim": 10,
        "egim_yonu": "doğu",
        "zemin_turu": "yumuşak"
    },
    {
        "lat": 40.991236, 
        "lon": 28.896789, 
        "kat_sayisi": 3, 
        "bina_yasi": 15, 
        "malzeme": "betonarme",
        "egim": 2,
        "egim_yonu": "kuzey",
        "zemin_turu": "sağlam"
    }
]

async def create_sample_data():
    """
    Örnek verileri veritabanına ekler
    """
    # Veritabanını başlat
    await init_db()
    
    # Örnek binaları ekle
    async with async_session() as session:
        for building_data in SAMPLE_BUILDINGS:
            building = models.Building(**building_data)
            session.add(building)
        
        await session.commit()
    
    print("Örnek veriler başarıyla eklendi!")

if __name__ == "__main__":
    asyncio.run(create_sample_data()) 