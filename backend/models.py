from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from backend.database import Base

class School(Base):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True, index=True)
    il = Column(String, index=True)
    ilce = Column(String, index=True)
    okul_adi = Column(String)

class ExamScenario(Base):
    __tablename__ = "exam_scenarios"
    id = Column(Integer, primary_key=True, index=True)
    isim = Column(String) 
    kazanimlar = Column(JSON) 

class DetailedExamResult(Base):
    __tablename__ = "detailed_results"
    id = Column(Integer, primary_key=True, index=True)
    student_no = Column(String, index=True)
    scenario_id = Column(Integer, ForeignKey("exam_scenarios.id"))
    school_id = Column(Integer, ForeignKey("schools.id"))
    soru_puanlari = Column(JSON) 
    toplam_puan = Column(Float)
