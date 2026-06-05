import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import io

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Ulusal Sınav Havuzu", layout="wide")
API_URL = "https://sinav-sistemi-api-xxxx.onrender.com" # Kendi Render linkinle değiştir

# --- EXCEL ŞABLONU ÜRETİCİ FONKSİYON ---
def df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Şablon')
    return output.getvalue()

# --- GİRİŞ EKRANI (ŞİFRE ALTYAPISI İÇİN HAZIRLIK) ---
if "giriş_yapildi" not in st.session_state:
    st.session_state.giriş_yapildi = False
    st.session_state.kullanici_rolu = None

if not st.session_state.giriş_yapildi:
    st.markdown("<h1 style='text-align: center;'>Gazi Ortaokulu Sınav Havuz Sistemi</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.info("Sistem şu an test aşamasında olduğu için şifresiz rol seçimi aktiftir. İleride kurumsal şifre ile giriş yapılacaktır.")
        rol = st.selectbox("Sisteme Giriş Rolünüz:", ["Öğretmen", "Süper Yönetici / İdareci"])
        sifre = st.text_input("Şifre (Şu an boş bırakabilirsiniz)", type="password")
        
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            st.session_state.giriş_yapildi = True
            st.session_state.kullanici_rolu = rol
            st.rerun()
    st.stop() # Giriş yapılmadıysa alt kodları çalıştırma

# --- ANA SİSTEM (GİRİŞ YAPILDIKTAN SONRA) ---
st.sidebar.title(f"👤 {st.session_state.kullanici_rolu} Paneli")
if st.sidebar.button("Çıkış Yap"):
    st.session_state.giriş_yapildi = False
    st.rerun()

st.sidebar.markdown("---")

# YÖNETİCİ MODÜLÜ
if st.session_state.kullanici_rolu == "Süper Yönetici / İdareci":
    st.header("⚙️ Sınav Havuzu ve Senaryo Yönetimi")
    
    col_ders, col_sinav = st.columns(2)
    with col_ders:
        ders_adi = st.selectbox("Ders Seçimi", ["Matematik", "Türkçe", "Fen Bilimleri", "Sosyal Bilgiler"])
    with col_sinav:
        sinav_adi = st.text_input("Sınav Adı", value="2. Dönem 2. Ortak Yazılı")
        
    st.markdown(f"### {ders_adi} - {sinav_adi} İçin Senaryo Tanımlama")
    
    # Yönetici için Örnek Senaryo Şablonu İndirme
    st.write("1. Adım: Yeni bir senaryo yüklemek için boş şablonu indirin, doldurun ve sisteme yükleyin.")
    ornek_senaryo_df = pd.DataFrame({
        "Soru No": [1, 2, 3, 4, 5],
        "Kazanım / Çıktı Kodu": ["MAT.6.2.1", "MAT.6.2.2", "MAT.6.4.1", "", ""],
        "Maksimum Puan": [20, 20, 20, 20, 20]
    })
    
    st.download_button(
        label="📥 Senaryo Şablonunu İndir (Excel)",
        data=df_to_excel(ornek_senaryo_df),
        file_name="senaryo_sablonu.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Senaryo Yükleme
    st.write("2. Adım: Doldurduğunuz senaryo şablonunu sisteme yükleyerek öğretmenlerin erişimine açın.")
    yuklenen_senaryo = st.file_uploader("Senaryo Excel Dosyasını Yükle", type=["xlsx"])
    
    if yuklenen_senaryo:
        okunan_senaryo = pd.read_excel(yuklenen_senaryo)
        st.success("Senaryo Başarıyla Okundu! Veritabanına kaydedildi.")
        st.dataframe(okunan_senaryo, use_container_width=True)

# ÖĞRETMEN MODÜLÜ
elif st.session_state.kullanici_rolu == "Öğretmen":
    st.header("📝 Sınav Uygulama ve Not Girişi")
    
    # Havuzdan Sınav Seçimi
    st.subheader("1. Havuzdan Sınav ve Senaryo Seç")
    col1, col2 = st.columns(2)
    with col1:
        secilen_sınav = st.selectbox("Tanımlı Sınavlar", ["Matematik - 2. Dönem 2. Ortak Yazılı", "Türkçe - 2. Dönem 1. Ortak Yazılı"])
    with col2:
        secilen_senaryo = st.selectbox("Uygulanacak Senaryo", ["Senaryo 1 (6 Soru)", "Senaryo 2 (8 Soru)", "Senaryo 3 (5 Soru)"])
        
    st.info(f"Seçilen senaryoda toplam 6 soru bulunmaktadır. Maksimum puan: 100")
    
    st.markdown("---")
    st.subheader("2. Öğrenci Not Listesi İşlemleri")
    
    # Otomatik Öğrenci Şablonu Üretme (Soru 1, Soru 2 kolonları ile)
    ogrenci_sablon_df = pd.DataFrame({
        "Öğrenci No": ["101", "102", "103"],
        "Adı": ["Ahmet", "Ayşe", "Fatma"],
        "Soyadı": ["Yılmaz", "Kaya", "Demir"],
        "Soru 1 (Max:20)": ["", "", ""],
        "Soru 2 (Max:15)": ["", "", ""],
        "Soru 3 (Max:15)": ["", "", ""],
        "Soru 4 (Max:25)": ["", "", ""],
        "Soru 5 (Max:25)": ["", "", ""]
    })
    
    col_indir, col_yukle = st.columns(2)
    with col_indir:
        st.write("Sınıfınızın boş not çizelgesini indirip sınav sonuçlarını Excel'e girin.")
        st.download_button(
            label="📥 Öğrenci Not Şablonunu İndir (Excel)",
            data=df_to_excel(ogrenci_sablon_df),
            file_name=f"not_cizelgesi_{secilen_senaryo}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    with col_yukle:
        st.write("Doldurduğunuz not çizelgesini sisteme yükleyin.")
        yuklenen_notlar = st.file_uploader("Doldurulmuş Not Excel'ini Yükle", type=["xlsx"])
        
    # Analiz ve Müfettiş Raporu (Yapay Zeka Çıktısı Simülasyonu)
    if yuklenen_notlar:
        df_notlar = pd.read_excel(yuklenen_notlar)
        st.success("Notlar Sisteme İşlendi!")
        st.dataframe(df_notlar, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🤖 Yapay Zeka Denetim ve Analiz Raporu (İdare / Müfettiş Ekranı)")
        
        # Grafik
        grafik_veri = pd.DataFrame({
            "Sorular": ["Soru 1 (MAT.6.2.1)", "Soru 2 (MAT.6.2.2)", "Soru 3", "Soru 4", "Soru 5"],
            "Sınıf Başarı Yüzdesi": [85, 42, 65, 70, 50]
        })
        fig = px.bar(grafik_veri, x="Sorular", y="Sınıf Başarı Yüzdesi", title="Kazanım Bazlı Sınıf Başarı Dağılımı", color="Sınıf Başarı Yüzdesi", color_continuous_scale="RdYlGn")
        st.plotly_chart(fig, use_container_width=True)
        
        # Gelişmiş AI Raporu Formatı
        st.error("**Sistem Analizi:** MAT.6.2.2 kodlu 'Sayı ve şekil örüntülerini yorumlayabilme' kazanımında başarı oranı %42'de kalarak kritik sınırın altına düşmüştür.")
        
        with st.expander("📄 Resmi Analiz Raporunu Görüntüle (Çıktı Alınabilir)"):
            st.write("""
            **Kurum:** Gazi Ortaokulu
            **Sınav:** Matematik 2. Dönem 2. Ortak Yazılı
            
            Öğrencilerin uygulanan açık uçlu sınavdaki süreç bileşenleri incelendiğinde; dört işlem algoritmalarını kullanmada yüksek performans gösterdikleri, ancak cebirsel ifadeler içeren durumlarda muhakeme yaparken zorlandıkları tespit edilmiştir. 
            
            **Eylem Planı Önerisi:** Zümre öğretmenleri tarafından problem çözme stratejilerini geliştirecek çalışma yapraklarının hazırlanması uygun görülmüştür.
            """)
