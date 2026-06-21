from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from database import Base

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    skills = Column(Text, nullable=False)  # Comma-separated
    created_at = Column(DateTime, default=datetime.utcnow)

class ResumeResult(Base):
    __tablename__ = "resume_results"

    id = Column(Integer, primary_key=True, index=True)
    job_description_id = Column(Integer, nullable=False)
    filename = Column(String, nullable=False)
    candidate_name = Column(String, nullable=True)
    match_score = Column(Float, nullable=False)
    matched_skills = Column(Text, nullable=False)  # Comma-separated
    missing_skills = Column(Text, nullable=False)  # Comma-separated
    report_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)