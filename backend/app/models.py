from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.orm import Base
from datetime import datetime


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


class CommunityPost(Base):
    __tablename__ = "community_posts"

    post_id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)  # "festival", "restaurant", etc.
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    password = Column(String, nullable=False)  # 평문 저장 (교육 목적)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    view_count = Column(Integer, default=0)
