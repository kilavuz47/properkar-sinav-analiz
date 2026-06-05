from sqlalchemy import Column, Integer, String, Float, ForeignKey
from backend.database import Base

class School(Base):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True, index=True)
    il = Column(String, index=True)
    ilce = Column(String, index=True)
    okul_adi = Column(String)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String) # super_admin, il_admin, okul_admin, ogretmen
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)

class ExamResult(Base):
    __tablename__ = "exam_results"
    id = Column(Integer, primary_key=True, index=True)
    student_no = Column(String, index=True)
    scenario = Column(String) # Örn: 6. Sınıf Matematik Senaryo 2
    score = Column(Float)
    ai_feedback = Column(String)
    school_id = Column(Integer, ForeignKey("schools.id"))