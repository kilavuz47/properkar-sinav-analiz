import streamlit as st
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