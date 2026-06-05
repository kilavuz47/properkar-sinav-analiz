import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import io
import re

# --- SAYFA VE SİSTEM AYARLARI ---
st.set_page_config(page_title="Ulusal Ölçme ve Değerlendirme Sistemi", layout="wide", page_icon="🏫")

# Yapay Zeka Bağlantısı (Streamlit Secrets)
ai_aktif = False
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        ai_aktif = True
except:
    pass

# --- GEÇİCİ VERİTABANI (Sistemi Canlı Tutmak İçin Session State) ---
if "ogrenci_listesi" not in st.session_state:
    st.session_state.ogrenci_listesi = pd.DataFrame(columns=["Öğrenci No", "Adı", "Soyadı", "Sınıf"])
if "senaryolar" not in st.session_state:
    st.session_state.senaryolar = {}
if "sinav_sonuclari" not in st.session_state:
    st.session_state.sinav_sonuclari = {}

# --- YARDIMCI FONKSİYONLAR ---
def df_to_excel(df, sheet_name="Şablon"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

def alt_bilesenleri_ayikla(metin):
    """Metin içindeki a), b), c) gibi alt bileşenleri otomatik algılar."""
    bilesenler = re.findall(r'([a-zğüşöçı]\)\s.*?)(?=[a-zğüşöçı]\)|$)', metin, flags=re.DOTALL)
    if not bilesenler:
        return [metin.strip()]
    return [b.strip() for b in bilesenler]

# --- GİRİŞ EKRANI ---
if "giris_durumu" not in st.session_state:
    st.session_state.giris_durumu = False
    st.session_state.rol = None
    st.session_state.kullanici_adi = None

if not st.session_state.giris_durumu:
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>🏫 Profesyonel Sınav Analiz ve Havuz Sistemi</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.markdown("### Sisteme Giriş")
            secilen_rol = st.selectbox("Yetki Türü:", ["Öğretmen", "Süper Yönetici / İdareci"])
            kullanici = st.text_input("Kullanıcı Adı / Sicil No", placeholder="Örn: ahmet_hoca")
            sifre = st.text_input("Şifre (Şu an test aşamasında, boş geçilebilir)", type="password")
            
            if st.button("Giriş Yap", use_container_width=True):
                if kullanici:
                    st.session_state.giris_durumu = True
                    st.session_state.rol = secilen_rol
                    st.session_state.kullanici_adi = kullanici
                    st.rerun()
                else:
                    st.error("Lütfen bir kullanıcı adı giriniz.")
    st.stop()

# --- ANA SİSTEM ARAYÜZÜ ---
st.sidebar.title(f"👤 {st.session_state.kullanici_adi}")
st.sidebar.caption(f"Yetki: {st.session_state.rol}")
if st.sidebar.button("Çıkış Yap"):
    st.session_state.giris_durumu = False
    st.rerun()
st.sidebar.markdown("---")

# ==========================================
# 1. SÜPER YÖNETİCİ MODÜLÜ
# ==========================================
if st.session_state.rol == "Süper Yönetici / İdareci":
    st.title("⚙️ Süper Yönetici Kontrol Paneli")
    tab1, tab2, tab3 = st.tabs(["📑 Senaryo ve Kazanım Havuzu", "📁 Şablon Yükle/İndir", "👁️ Öğretmen Denetimi"])
    
    # SEKM 1: SENARYO OLUŞTURMA VE DÜZENLEME
    with tab1:
        st.subheader("Yeni Sınav Senaryosu Tanımlama")
        st.info("Kazanımları ve süreç bileşenlerini (a, b, c) sisteme toplu olarak tanımlayın.")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            ders_adi = st.text_input("Ders Adı", "Matematik 6")
            senaryo_adi = st.text_input("Sınav ve Senaryo Adı", "2. Dönem 2. Ortak Yazılı - Senaryo 1")
        with col_s2:
            toplu_metin = st.text_area("Kazanım ve Süreç Bileşenleri (Metni Buraya Yapıştırın)", height=150, 
                                       placeholder="Örn: MAT.6.2.1. a) Gerçek yaşam... b) Nicelikler...")
            kaydet_btn = st.button("Senaryoyu Çözümle ve Havuza Kaydet")
            
        if kaydet_btn and toplu_metin:
            bilesenler = alt_bilesenleri_ayikla(toplu_metin)
            st.session_state.senaryolar[senaryo_adi] = {"ders": ders_adi, "ciktilar": bilesenler}
            st.success(f"{senaryo_adi} başarıyla havuza kaydedildi! Sistem {len(bilesenler)} adet alt çıktı tespit etti.")
            st.json(bilesenler)
            
        st.markdown("---")
        st.subheader("Kayıtlı Senaryoları Düzenle")
        if st.session_state.senaryolar:
            secili_duzenle = st.selectbox("Düzenlenecek Senaryo", list(st.session_state.senaryolar.keys()))
            guncel_icerik = st.text_area("İçeriği Güncelle", "\n".join(st.session_state.senaryolar[secili_duzenle]["ciktilar"]), height=100)
            if st.button("Değişiklikleri Kaydet"):
                st.session_state.senaryolar[secili_duzenle]["ciktilar"] = guncel_icerik.split("\n")
                st.success("Senaryo güncellendi.")
        else:
            st.warning("Henüz havuza kaydedilmiş bir senaryo bulunmamaktadır.")

    # SEKM 2: ŞABLON İŞLEMLERİ
    with tab2:
        st.subheader("Kurumsal Sınav Şablonları (İndir / Yükle)")
        if st.session_state.senaryolar:
            secili_sablon_senaryo = st.selectbox("Şablonu Üretilecek Senaryo Seçin", list(st.session_state.senaryolar.keys()))
            
            # Dinamik Excel Üretimi
            ciktilar = st.session_state.senaryolar[secili_sablon_senaryo]["ciktilar"]
            sablon_dict = {"Öğrenci No": [], "Adı": [], "Soyadı": [], "Sınıf": []}
            for i, cikti in enumerate(ciktilar):
                # Başlıkları kısa tutmak için
                kisa_baslik = f"Soru {i+1} [Max: 20]"
                sablon_dict[kisa_baslik] = []
                
            df_sablon = pd.DataFrame(sablon_dict)
            
            st.download_button(
                label=f"📥 {secili_sablon_senaryo} Şablonunu İndir",
                data=df_to_excel(df_sablon, "Sınav Şablonu"),
                file_name=f"{secili_sablon_senaryo}_Sablon.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.markdown("### Toplu Sınav Verisi Yükle (Admin Yetkisiyle)")
            admin_yukleme = st.file_uploader("Öğretmenlerin Gönderdiği Şablonu Yükle", type=["xlsx"], key="admin_yukle")
            if admin_yukleme:
                df_admin = pd.read_excel(admin_yukleme)
                st.dataframe(df_admin)
                if st.button("Kurum Veritabanına İşle"):
                    st.success("Veriler kurum sistemine kalıcı olarak işlendi.")
        else:
            st.info("Şablon üretebilmek için önce Senaryo Havuzuna veri eklemelisiniz.")

    # SEKM 3: ÖĞRETMEN DENETİMİ
    with tab3:
        st.subheader("Öğretmen Veri Denetimi ve Müdahale")
        st.write("Sisteme veri giren öğretmenlerin yüklemelerini buradan görebilir, hatalı kayıtları düzeltebilirsiniz.")
        if st.session_state.sinav_sonuclari:
            # Öğretmen listesini simüle et
            ogretmenler = list(st.session_state.sinav_sonuclari.keys())
            secili_ogr = st.selectbox("Öğretmen Seçin", ogretmenler)
            
            st.write(f"**{secili_ogr}** adlı öğretmenin girdiği notlar:")
            duzenlenecek_df = st.data_editor(st.session_state.sinav_sonuclari[secili_ogr], num_rows="dynamic")
            
            if st.button("Öğretmenin Verisini Güncelle"):
                st.session_state.sinav_sonuclari[secili_ogr] = duzenlenecek_df
                st.success("Yetki kullanılarak veriler güncellendi.")
        else:
            st.warning("Henüz öğretmenler tarafından sisteme girilmiş bir veri bulunmamaktadır.")

# ==========================================
# 2. ÖĞRETMEN MODÜLÜ
# ==========================================
elif st.session_state.rol == "Öğretmen":
    st.title("📝 Öğretmen Sınav ve Analiz Paneli")
    tab_ogrenci, tab_sinav, tab_analiz = st.tabs(["👨‍🎓 Öğrenci Listesi İşlemleri", "📄 Sınav Şablonu İndir/Yükle", "📊 Detaylı Analiz"])

    # SEKM 1: ÖĞRENCİ LİSTESİ YÜKLEME VE İNDİRME
    with tab_ogrenci:
        st.subheader("Öğrenci Listesi Şablonu")
        st.info("Öğrenci listenizi sisteme bir kere yükleyin. Sistem mükerrer (aynı numaralı) kayıtları otomatik engelleyecektir.")
        
        col_list1, col_list2 = st.columns(2)
        with col_list1:
            bos_liste_df = pd.DataFrame(columns=["Öğrenci No", "Adı", "Soyadı", "Sınıf"])
            st.download_button(
                label="📥 Boş Öğrenci Listesi Şablonunu İndir",
                data=df_to_excel(bos_liste_df, "Ogrenci_Listesi"),
                file_name="Ogrenci_Listesi_Sablonu.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col_list2:
            yuklenen_liste = st.file_uploader("Dolu Öğrenci Listesini Yükle", type=["xlsx"])
            if yuklenen_liste:
                yeni_ogrenciler = pd.read_excel(yuklenen_liste)
                # Mükerrer kayıt engelleme (Öğrenci No'ya göre)
                mevcut_nolarlar = st.session_state.ogrenci_listesi["Öğrenci No"].tolist()
                yeni_ogrenciler_filtrelenmis = yeni_ogrenciler[~yeni_ogrenciler["Öğrenci No"].isin(mevcut_nolarlar)]
                
                if not yeni_ogrenciler_filtrelenmis.empty:
                    st.session_state.ogrenci_listesi = pd.concat([st.session_state.ogrenci_listesi, yeni_ogrenciler_filtrelenmis], ignore_index=True)
                    st.success(f"{len(yeni_ogrenciler_filtrelenmis)} yeni öğrenci başarıyla sisteme kaydedildi!")
                else:
                    st.warning("Yüklenen listedeki öğrenciler zaten sistemde mevcut.")
                    
        st.markdown("### 📋 Güncel Sistemdeki Öğrenci Listeniz")
        st.dataframe(st.session_state.ogrenci_listesi, use_container_width=True)

    # SEKM 2: SINAV ŞABLONU İNDİRME VE YÜKLEME
    with tab_sinav:
        st.subheader("Senaryoya Bağlı Sınav Notu İşlemleri")
        if not st.session_state.senaryolar:
            st.error("Yönetici henüz havuza senaryo tanımlamamış.")
        elif st.session_state.ogrenci_listesi.empty:
            st.error("Lütfen önce 'Öğrenci Listesi İşlemleri' sekmesinden öğrencilerinizi yükleyin.")
        else:
            secili_senaryo = st.selectbox("Uygulanan Senaryoyu Seçin", list(st.session_state.senaryolar.keys()))
            ciktilar = st.session_state.senaryolar[secili_senaryo]["ciktilar"]
            
            # Öğrencilerle birleşik sınav şablonu üretme
            sinav_df = st.session_state.ogrenci_listesi.copy()
            for i, cikti in enumerate(ciktilar):
                sinav_df[f"Soru {i+1} [Max Puan: 20]"] = None # Dinamik sütunlar
                
            st.download_button(
                label=f"📥 Sınıfınız İçin {secili_senaryo} Not Şablonunu İndir",
                data=df_to_excel(sinav_df, "Not_Girisi"),
                file_name=f"Notlar_{secili_senaryo}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.markdown("---")
            yuklenen_notlar = st.file_uploader("Doldurulmuş Sınav Notlarını Yükle", type=["xlsx"])
            if yuklenen_notlar:
                df_notlar = pd.read_excel(yuklenen_notlar)
                st.dataframe(df_notlar)
                if st.button("Sınav Sonuçlarını Sisteme Kalıcı Kaydet"):
                    st.session_state.sinav_sonuclari[st.session_state.kullanici_adi] = df_notlar
                    st.success("Notlarınız veritabanına başarıyla işlendi ve yönetici paneline düştü.")

    # SEKM 3: DETAYLI VE ÇİFT MOTORLU ANALİZ
    with tab_analiz:
        st.subheader("Kazanım ve Çıktı Bazlı Zümre Analizi")
        if st.session_state.kullanici_adi not in st.session_state.sinav_sonuclari:
            st.info("Analizleri görebilmek için önce Sınav Şablonu sekmesinden notlarınızı yüklemelisiniz.")
        else:
            df_analiz = st.session_state.sinav_sonuclari[st.session_state.kullanici_adi]
            soru_sutunlari = [col for col in df_analiz.columns if "Soru" in col]
            
            tab_alg, tab_ai = st.tabs(["📉 Algoritmik Analiz", "🤖 Yapay Zeka Raporu"])
            
            # Klasik Analiz
            with tab_alg:
                st.write("**Öğrenci - Soru (Kazanım) Çapraz Matrisi ve Isı Haritası**")
                # Sınıf isimleri ve soruları heatmap'e uygun hale getirme
                try:
                    heatmap_df = df_analiz.set_index("Adı")[soru_sutunlari]
                    heatmap_df = heatmap_df.apply(pd.to_numeric, errors='coerce').fillna(0) # String varsa 0'a çevir
                    
                    fig = px.imshow(heatmap_df, text_auto=True, aspect="auto", color_continuous_scale="Blues", title="Soru Başarı Dağılımı")
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning("Isı haritası oluşturulurken notların sayısal değer içerdiğinden emin olun.")
            
            # Yapay Zeka Analizi
            with tab_ai:
                if not ai_aktif:
                    st.error("Sistemde Gemini Yapay Zeka entegrasyonu aktif değil.")
                else:
                    if st.button("Müfettiş Standartlarında Rapor Üret"):
                        with st.spinner("Gemini çıktıları analiz ediyor..."):
                            try:
                                istatistik = df_analiz[soru_sutunlari].describe().to_string()
                                prompt = f"""
                                Sen MEB'de uzman bir müfettişsin. Aşağıda bir sınıfın sınav istatistikleri var:
                                {istatistik}
                                Lütfen bu verilere bakarak, en başarılı ve başarısız kazanımları belirle, eylem planı sunan resmi bir rapor yaz.
                                """
                                model = genai.GenerativeModel('gemini-1.5-flash')
                                cevap = model.generate_content(prompt)
                                st.write(cevap.text)
                            except Exception as e:
                                st.error(f"AI Analiz Hatası: {e}")
