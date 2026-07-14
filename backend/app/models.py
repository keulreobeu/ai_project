from sqlalchemy import Column, Integer, String, Float
from app.orm import Base


class Place(Base):
    __tablename__ = "places"

    place_id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, nullable=False)
    content_type_id = Column(Integer, nullable=False)
    external_content_id = Column(String)
    title = Column(String)
    address1 = Column(String)
    address2 = Column(String)
    zipcode = Column(String)
    tel = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    thumbnail_url = Column(String)
    image_url = Column(String)
    map_level = Column(String)
    source_data = Column(String)
    created_at = Column(String)
    updated_at = Column(String)
