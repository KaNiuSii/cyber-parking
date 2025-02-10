# database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./parking.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ParkingLogs(Base):
    __tablename__ = "ParkingLogs"
    Id = Column(Integer, primary_key=True, index=True)
    JSONDump = Column(JSON)

class LicensePlates(Base):
    __tablename__ = "LicensePlates"
    Id = Column(Integer, primary_key=True, index=True)
    Plate = Column(String, unique=True, index=True)

class EntranceInfo(Base):
    __tablename__ = "EntranceInfo"
    Id = Column(Integer, primary_key=True, index=True)
    EntryTime = Column(DateTime)
    Plate = Column(String)

class ExitInfo(Base):
    __tablename__ = "ExitInfo"
    Id = Column(Integer, primary_key=True, index=True)
    ExitTime = Column(DateTime)
    Plate = Column(String)

class ParkingCost(Base):
    __tablename__ = "ParkingCost"
    Id = Column(Integer, primary_key=True, index=True)
    Plate = Column(String)
    ParkedTime = Column(Float)   
    ParkingCost = Column(Float)     

def init_db():
    Base.metadata.create_all(bind=engine)
