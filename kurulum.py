import os

# 1. Oluşturulacak Klasörler
klasorler = [
    "backend",
    "frontend"
]

for klasor in klasorler:
    os.makedirs(klasor, exist_ok=True)
    print(f"📁 Klasör oluşturuldu: {klasor}/")

# 2. Dosya İçerikleri
dosyalar = {
    ".env": """# Supabase API Bağlantıları
SUPABASE_URL=https://smlpeljbtkvvtspvizuy.supabase.co
SUPABASE_KEY=sb_publishable_XX4Vfrk_Bj7IzWs-LHN3qg_Wh-TGtVD

# SQLAlchemy PostgreSQL Bağlantısı (Supabase panelinden kendi şifrenle değiştir)
DATABASE_URL=postgresql://postgres:[SENİN_VERİTABANI_ŞİFREN]@db.smlpeljbtkvvtspvizuy.supabase.co:5432/postgres
""",

    "requirements.txt": """fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-dotenv
supabase
streamlit
pydantic
requests
""",

    "backend/__init__.py": "",

    "backend/database.py": """import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Supabase PostgreSQL Bağlantı Adresi
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Engine oluştur (PostgreSQL için)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",

    "backend/models.py": """from sqlalchemy import Column, Integer, String, Float, ForeignKey
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
""",

    "backend/main.py": """from fastapi import FastAPI, Depends
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
""",

    "frontend/app.py": """import streamlit as st
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Süper Yönetici - Sınav Analiz", layout="wide")

# Backend API Adresi (Şu an lokalde çalışıyoruz)
API_URL = "http://127.0.0.1:8000"

st.title("📊 Klasik Sınav Analiz ve Havuz Sistemi")
st.markdown("---")

# Menü (Sol Kenar Çubuğu)
menu = st.sidebar.selectbox(
    "Modül Seçiniz",
    ["Süper Yönetici Paneli", "Sınav Sonucu Yükle", "Okul Analizi"]
)

if menu == "Sınav Sonucu Yükle":
    st.subheader("📝 Ortak Sınav Sonucu Girişi")
    with st.form("sinav_formu"):
        ogrenci_no = st.text_input("Öğrenci Numarası")
        senaryo = st.selectbox("Senaryo Seçimi", ["6. Sınıf Mat - Senaryo 1", "6. Sınıf Mat - Senaryo 2", "6. Sınıf Mat - Senaryo 3"])
        puan = st.number_input("Sınav Puanı", min_value=0.0, max_value=100.0)
        okul_id = st.number_input("Okul ID", min_value=1, value=1)
        
        submit_button = st.form_submit_button("Sonucu Kaydet ve Analiz Et")
        
        if submit_button:
            response = requests.post(
                f"{API_URL}/sinav_ekle/",
                params={"ogrenci_no": ogrenci_no, "senaryo": senaryo, "puan": puan, "okul_id": okul_id}
            )
            if response.status_code == 200:
                st.success("Sınav sonucu veritabanına başarıyla yazıldı!")
                st.info(f"Yapay Zeka Yorumu: {response.json()['veri']['ai_feedback']}")

elif menu == "Okul Analizi":
    st.subheader("📈 Veritabanındaki Sonuçlar (Supabase'den Çekiliyor)")
    try:
        response = requests.get(f"{API_URL}/sonuclar/")
        if response.status_code == 200:
            veriler = response.json()
            if veriler:
                st.table(veriler)
            else:
                st.warning("Henüz sisteme girilmiş bir sınav sonucu yok.")
    except Exception as e:
        st.error("API'ye bağlanılamadı. Backend'in çalıştığından emin olun.")

elif menu == "Süper Yönetici Paneli":
    st.subheader("🌐 Türkiye Geneli Havuz Yönetimi")
    st.info("Bu modül üzerinden ileride Excel/PDF şablonları havuza yüklenecek ve tüm il/ilçelere dağıtımı yapılacaktır.")
"""
}

# 3. Dosyaları Oluşturma ve Yazma
for dosya_yolu, icerik in dosyalar.items():
    with open(dosya_yolu, "w", encoding="utf-8") as f:
        f.write(icerik)
    print(f"📄 Dosya oluşturuldu: {dosya_yolu}")

print("\n✅ Kurulum tamamlandı! Tüm klasörler ve dosyalar başarıyla oluşturuldu.")
print("👉 Lütfen '.env' dosyasını açıp 'DATABASE_URL' içindeki şifrenizi güncellemeyi unutmayın.")