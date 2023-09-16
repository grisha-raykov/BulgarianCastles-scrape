from sqlalchemy import Column, String, Integer, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Castle(Base):
    __tablename__ = "castles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    description = Column(Text)
    location_text = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    coordinates_original = Column(String)
    literature = Column(Text)
    has_error = Column(Boolean, default=False)
    error_message = Column(Text)


class ScrapedURL(Base):
    __tablename__ = "scraped_urls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
