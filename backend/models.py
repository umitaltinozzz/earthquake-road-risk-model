from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from database import Base

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    kat_sayisi = Column(Integer, nullable=False)
    bina_yasi = Column(Integer, nullable=False)
    malzeme = Column(String, nullable=False)
    egim = Column(Integer, default=0)
    egim_yonu = Column(String, default="kuzey")
    zemin_turu = Column(String, default="normal")
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now) 