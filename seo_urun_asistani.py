import streamlit as st
import pandas as pd
import openai
client = openai.OpenAI()
st.set_page_config(page_title="SEO Ürün Açıklama Asistanı", layout="wide")

st.title("🦾 Katia & Bony - SEO Ürün Başlık & Açıklama Asistanı")

st.markdown("""
Kullanım:
1. Ürünlerinizin olduğu Excel dosyasını yükleyin.
2. Her ürün için otomatik olarak SEO uyumlu başlık ve açıklama oluşturulsun.
3. Sonucu Excel olarak indirin!
---
**Excel’de olması gereken başlıklar:**  
- `Ürün Adı`  
- `Ürün Açıklaması` (varsa)  
- `Kategori` (varsa)  
""")

uploaded_file = st.file_uploader("Excel dosyanızı yükleyin", type=["xlsx"])

def gpt_urun_aciklama_baslik(urun_adi, urun_aciklama, kategori):
    prompt = f"""
Aşağıdaki bilgileri kullanarak SEO uyumlu, özgün ve etkili bir ürün başlığı ve açıklaması oluştur:

Ürün Adı: {urun_adi}
Ürün Açıklaması: {urun_aciklama}
Kategori: {kategori}

Kurallar:
- Başlık 70 karakteri aşmasın, anahtar kelime ile başlasın.
- Açıklama 100-200 kelime arasında, ürünün öne çıkan özellikleri ve faydalarını içersin.
- Cümleler sade, açık ve ikna edici olsun.
- Özgün ve kopya olmayan bir metin üret.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600
        )
        content = response.choices[0].message.content.strip().split("\n", 1)
        baslik = content[0].replace("Başlık:", "").strip() if len(content) > 0 else ""
        aciklama = content[1].replace("Açıklama:", "").strip() if len(content) > 1 else ""
        return baslik, aciklama
    except Exception as e:
        return "", f"HATA: {e}"

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    # Gerekli kolon kontrolü
    for col in ['Ürün Adı']:
        if col not in df.columns:
            st.error(f"Excel dosyasında '{col}' kolonu eksik!")
            st.stop()
    if 'Ürün Açıklaması' not in df.columns:
        df['Ürün Açıklaması'] = ""
    if 'Kategori' not in df.columns:
        df['Kategori'] = ""

    st.write("İlk 5 ürün örnek veri:", df.head())

    if st.button("SEO İçerikleri Oluştur ve Ekle"):
        seo_basliklar = []
        seo_aciklamalar = []
        with st.spinner("Ürünler işleniyor..."):
            for idx, row in df.iterrows():
                baslik, aciklama = gpt_urun_aciklama_baslik(
                    str(row['Ürün Adı']),
                    str(row.get('Ürün Açıklaması', '')),
                    str(row.get('Kategori', ''))
                )
                seo_basliklar.append(baslik)
                seo_aciklamalar.append(aciklama)
        df['SEO Başlık'] = seo_basliklar
        df['SEO Açıklama'] = seo_aciklamalar

        st.success("Ürünler başarıyla işlendi! Sonuçları aşağıda inceleyebilir ve Excel olarak indirebilirsin.")
        st.dataframe(df[['Ürün Adı', 'SEO Başlık', 'SEO Açıklama']])

        # Excel indirme linki
        from io import BytesIO
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        st.download_button("Sonuçları Excel olarak indir", data=output, file_name="seo_urunler.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
