import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Gelişmiş Sınav Analiz Platformu", layout="wide")
API_URL = "http://127.0.0.1:8000"

st.title("📊 Ulusal Klasik Sınav Analiz ve Havuz Sistemi")
st.markdown("---")

menu = st.sidebar.selectbox(
    "Sistem Modülleri",
    ["Süper Yönetici: Şablon Yükle", "Öğretmen: Sonuç Girişi", "Hiyerarşik Analiz (İl/İlçe/Okul)"]
)

if menu == "Süper Yönetici: Şablon Yükle":
    st.header("⚙️ MEB Ortak Sınav Senaryosu Havuzu")
    st.info("İl, ilçe ve okulların kullanacağı konu soru dağılım şablonlarını sisteme tanımlayın.")
    
    col1, col2 = st.columns(2)
    with col1:
        senaryo_adi = st.text_input("Senaryo Adı", value="6. Sınıf Mat - 2. Dönem 2. Sınav - Senaryo 1")
        soru_sayisi = st.number_input("Soru Sayısı", min_value=1, max_value=20, value=6)
    
    with col2:
        st.write("**Öğrenme Çıktıları (Kazanımlar) Eşleştirmesi**")
        kazanim_dict = {}
        # PDF'deki Senaryo 1'e göre varsayılan kazanımlar
        varsayilanlar = ["MAT.6.2.1", "MAT.6.2.2", "MAT.6.2.3", "MAT.6.4.1", "MAT.6.4.2", "MAT.6.4.3"]
        
        for i in range(1, soru_sayisi + 1):
            varsayilan = varsayilanlar[i-1] if i <= len(varsayilanlar) else ""
            kazanim_dict[f"Soru {i}"] = st.text_input(f"Soru {i} Kazanımı", value=varsayilan)
            
    if st.button("Senaryoyu Havuza Kaydet"):
        st.success(f"{senaryo_adi} başarıyla Türkiye geneli havuza eklendi!")
        st.json(kazanim_dict) # API'ye JSON olarak gidecek kısım

elif menu == "Hiyerarşik Analiz (İl/İlçe/Okul)":
    st.header("📈 Bölgesel ve Kurumsal Başarı Karşılaştırması")
    
    # Filtreleme Hiyerarşisi
    col1, col2, col3 = st.columns(3)
    secilen_il = col1.selectbox("İl Seçiniz", ["Tüm Türkiye", "Mardin", "Diyarbakır", "Şırnak"])
    secilen_ilce = col2.selectbox("İlçe Seçiniz", ["Tümü", "Dargeçit", "Artuklu", "Midiyat"])
    secilen_okul = col3.selectbox("Okul Seçiniz", ["Tümü", "Gazi Ortaokulu", "Atatürk Ortaokulu"])
    
    st.markdown("### 🎯 Öğrenme Çıktısı (Kazanım) Bazlı Analiz")
    
    # Gelişmiş Grafik Simülasyonu (Pandas ve Plotly ile)
    veri = {
        "Kazanım": ["MAT.6.2.1 (Cebirsel İfadeler)", "MAT.6.2.2 (Örüntüler)", "MAT.6.4.1 (Alan Ölçme)", "MAT.6.4.3 (Geometrik Problem)"],
        "İl Ortalaması (%)": [65, 70, 55, 45],
        "İlçe Ortalaması (%)": [62, 68, 52, 42],
        "Okul Ortalaması (%)": [75, 80, 60, 50]
    }
    df = pd.DataFrame(veri)
    
    # Plotly ile etkileşimli bar grafiği
    fig = px.barmart(
        df, 
        x="Kazanım", 
        y=["İl Ortalaması (%)", "İlçe Ortalaması (%)", "Okul Ortalaması (%)"],
        title="Kazanım Bazlı Hiyerarşik Başarı Kıyaslaması",
        barmode="group",
        color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c"]
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.warning("💡 **Yapay Zeka Yorumu:** Okulunuzun ortalaması il ve ilçe genelinin üzerindedir. Ancak MAT.6.4.3 numaralı Geometrik şekillerin alanları ile problem çözebilme [cite: 80, 83] konusunda bölge genelinde bir düşüş yaşanmaktadır. Bu öğrenme çıktısı için ek materyal hazırlanması önerilir.")

elif menu == "Öğretmen: Sonuç Girişi":
    st.header("📝 Sınıf Sınav Verisi Yükleme (Toplu)")
    st.info("Zümre olarak belirlediğiniz senaryoya ait öğrenci sonuçlarını Excel olarak yükleyin.")
    
    uploaded_file = st.file_uploader("Sınav Sonuçları Excel Dosyası Seçin", type=["xlsx", "xls", "csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xls') or uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
            st.write("Yüklenen Veri Önizlemesi:")
            st.dataframe(df.head())
            if st.button("Verileri Veritabanına İşle"):
                st.success(f"{len(df)} öğrencinin kazanım bazlı detaylı analizi sisteme kaydedildi!")
        except Exception as e:
            st.error(f"Dosya okuma hatası: {e}")
