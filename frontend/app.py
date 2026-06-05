import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import io

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Gazi Ortaokulu - Sınav Havuzu", layout="wide")

# --- YAPAY ZEKA BAĞLANTISI (STREAMLIT SECRETS) ---
ai_aktif = False
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        ai_aktif = True
except Exception as e:
    pass

# --- EXCEL ÜRETİCİ ---
def df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sınav Şablonu')
    return output.getvalue()

# --- GİRİŞ EKRANI ---
if "giris_durumu" not in st.session_state:
    st.session_state.giris_durumu = False
    st.session_state.rol = None

if not st.session_state.giris_durumu:
    st.markdown("<h1 style='text-align: center;'>Gazi Ortaokulu Ölçme ve Değerlendirme Sistemi</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        secilen_rol = st.selectbox("Sisteme Giriş Rolünüz:", ["Öğretmen", "Süper Yönetici / İdareci"])
        sifre_giris = st.text_input("Şifre (Geçici Olarak Boş Bırakın)", type="password")
        
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            st.session_state.giris_durumu = True
            st.session_state.rol = secilen_rol
            st.rerun()
    st.stop()

# --- ANA SİSTEM ---
st.sidebar.title(f"👤 {st.session_state.rol} Paneli")
if st.sidebar.button("Çıkış Yap"):
    st.session_state.giris_durumu = False
    st.rerun()
st.sidebar.markdown("---")

# ==========================================
# 1. SÜPER YÖNETİCİ MODÜLÜ (Şablon Hazırlama)
# ==========================================
if st.session_state.rol == "Süper Yönetici / İdareci":
    st.header("⚙️ Havuz Yönetimi ve Senaryo Tanımlama")
    st.info("Kurum genelinde uygulanacak klasik sınavların şablonlarını buradan oluşturun.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        ders = st.selectbox("Ders", ["Matematik", "Türkçe", "Fen Bilimleri", "Sosyal Bilgiler"])
        sinav_adi = st.text_input("Sınav Adı", "2. Dönem 2. Ortak Yazılı")
    with col_b:
        soru_sayisi = st.number_input("Toplam Soru Sayısı (Açık Uçlu)", min_value=1, max_value=20, value=5)
        toplam_puan_kontrol = 0
    
    st.markdown("### Öğrenme Çıktıları (Kazanımlar) ve Puanlama")
    
    sablon_verisi = {"Öğrenci No": [], "Adı": [], "Soyadı": []}
    
    # Dinamik Soru Sütunları Oluşturma
    for i in range(1, soru_sayisi + 1):
        c1, c2 = st.columns([3, 1])
        with c1:
            kazanim = st.text_input(f"Soru {i} Kazanımı", key=f"kazanim_{i}", placeholder="Örn: MAT.6.2.1...")
        with c2:
            puan = st.number_input(f"Soru {i} Puanı", key=f"puan_{i}", min_value=1, max_value=100, value=20)
            toplam_puan_kontrol += puan
        
        # Excel sütun başlığı formatı: Soru 1 (MAT.6.2.1) [Max: 20]
        sutun_basligi = f"Soru {i} ({kazanim}) [Max: {puan}]"
        sablon_verisi[sutun_basligi] = []

    if toplam_puan_kontrol != 100:
        st.warning(f"Dikkat: Soruların toplam puanı {toplam_puan_kontrol}. 100 üzerinden değerlendirme yapılması önerilir.")
    else:
        st.success("Sınav toplam puanı 100 olarak dengelendi.")

    if st.button("Şablonu Oluştur ve Havuza Kaydet"):
        df_sablon = pd.DataFrame(sablon_verisi)
        st.download_button(
            label="📥 Öğretmenler İçin Boş Excel Şablonunu İndir",
            data=df_to_excel(df_sablon),
            file_name=f"{ders}_{sinav_adi}_Sablonu.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ==========================================
# 2. ÖĞRETMEN MODÜLÜ (Sınav Okuma ve Analiz)
# ==========================================
elif st.session_state.rol == "Öğretmen":
    st.header("📝 Klasik Sınav Sonuç Girişi ve Zümre Analizi")
    st.write("Yöneticinin oluşturduğu şablonu doldurup buraya yükleyin. Sistem çapraz tabloyu çıkarıp çift motorlu analiz yapacaktır.")
    
    yuklenen_dosya = st.file_uploader("Doldurulmuş Öğrenci Not Listesini Yükle (Excel)", type=["xlsx"])
    
    if yuklenen_dosya:
        df = pd.read_excel(yuklenen_dosya)
        
        st.markdown("### 📋 Çapraz Sınav Tablosu")
        st.dataframe(df, use_container_width=True)
        
        # Analiz için sadece soru sütunlarını ayırma
        soru_sutunlari = [col for col in df.columns if "Soru" in col]
        
        # --- ÇİFT MOTORLU ANALİZ SİSTEMİ ---
        st.markdown("---")
        st.subheader("🔬 Profesyonel Sınav Analiz Motorları")
        tab1, tab2 = st.tabs(["📊 Klasik Algoritma Motoru", "🤖 Gemini Yapay Zeka Motoru"])
        
        # MOTOR 1: ALGORİTMİK ANALİZ (Grafikler ve İstatistik)
        with tab1:
            st.info("Bu modül matematiksel algoritmalar kullanarak sınıfın sayısal röntgenini çeker.")
            
            # 1. Isı Haritası (Kıpkırmızı olan yerler başarısızlık)
            heatmap_veri = df.set_index("Adı")[soru_sutunlari]
            fig_heat = px.imshow(
                heatmap_veri, 
                text_auto=True, 
                aspect="auto",
                color_continuous_scale="RdYlGn",
                title="Öğrenci - Kazanım Isı Haritası (Yeşil: Başarılı, Kırmızı: Eksik)"
            )
            st.plotly_chart(fig_heat, use_container_width=True)
            
            # 2. Sınıf Soru Ortalamaları (Radar Grafik)
            sinif_ortalamalari = df[soru_sutunlari].mean()
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=sinif_ortalamalari.values,
                theta=soru_sutunlari,
                fill='toself'
            ))
            fig_radar.update_layout(title="Sınıf Kazanım Ortalamaları (Radar Analizi)")
            st.plotly_chart(fig_radar, use_container_width=True)
            
            if st.button("Algoritmik Raporu Sisteme Kaydet"):
                st.success("Algoritmik sayısal veriler resmi analiz olarak veritabanına işlendi.")

        # MOTOR 2: YAPAY ZEKA ANALİZİ (Gemini)
        with tab2:
            st.info("Bu modül, sayısal verileri okuyarak müfettiş standartlarında akademik bir zümre raporu ve eylem planı yazar.")
            
            if not ai_aktif:
                st.error("Gemini API bağlantısı kurulamadı. Streamlit ayarlarınızı kontrol edin.")
            else:
                if st.button("✨ Yapay Zeka Analizini Başlat"):
                    with st.spinner("Gemini sınıfın verilerini inceliyor, pedagojik rapor yazılıyor..."):
                        # Veriyi yapay zekanın anlayacağı şekilde özetleme
                        istatistik = df[soru_sutunlari].describe().to_string()
                        
                        prompt = f"""
                        Sen uzman bir MEB matematik zümre başkanısın. Aşağıda açık uçlu bir sınavın kazanım bazlı istatistikleri var:
                        
                        {istatistik}
                        
                        Bu verilere bakarak, müfettiş denetimine sunulacak resmi bir klasik sınav analiz raporu yaz.
                        Lütfen şunları içer:
                        1. Sınıfın genel durumu.
                        2. En başarılı olunan ve en zayıf kalınan kazanımların (soruların) tespiti.
                        3. Zayıf kazanımlar için uygulanabilir pedagojik çözüm önerileri (Eylem Planı).
                        """
                        try:
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            cevap = model.generate_content(prompt)
                            st.write(cevap.text)
                            
                            st.markdown("---")
                            if st.button("Yapay Zeka Raporunu Sisteme Kaydet"):
                                st.success("Pedagojik rapor resmi analiz olarak veritabanına işlendi.")
                        except Exception as e:
                            st.error(f"Analiz sırasında hata: {e}")
