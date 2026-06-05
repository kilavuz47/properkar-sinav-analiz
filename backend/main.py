from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.database import engine, get_db, Base
import backend.models as models

# Tabloları Supabase üzerinde otomatik oluştur
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ulusal Sınav Analiz API")

@app.get("/")
def read_root():
    return {"durum": "Sistem Aktif", "mesaj": "Sınav Havuz Sistemi API'sine Hoş Geldiniz"}

@app.post("/sinav_ekle/")
def sinav_sonucu_ekle(ogrenci_no: str, senaryo: str, puan: float, okul_id: int, db: Session = Depends(get_db)):
    # Klasik sınav analizi için temel AI geri bildirimi
    feedback = ""
    if puan < 50:
        feedback = "Problem çözme ve cebirsel ifadeler konusunda ek çalışma gereklidir."
    else:
        feedback = "Kazanım hedeflerine ulaşılmıştır."
        
    yeni_sonuc = models.ExamResult(
        student_no=ogrenci_no,
        scenario=senaryo,
        score=puan,
        ai_feedback=feedback,
        school_id=okul_id
    )
    db.add(yeni_sonuc)
    db.commit()
    db.refresh(yeni_sonuc)
    return {"mesaj": "Başarıyla kaydedildi", "veri": yeni_sonuc}

@app.get("/sonuclar/")
def sonuclari_getir(db: Session = Depends(get_db)):
    return db.query(models.ExamResult).all()