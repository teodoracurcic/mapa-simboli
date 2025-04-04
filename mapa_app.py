import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# ⚠️ Ovo mora biti PRVA Streamlit komanda
st.set_page_config(page_title="Mapa simbola", layout="wide")

# 📁 Putanja do fajla sa podacima
xlsx_path = "simboli_koordinate_GPS.xlsx"

# 📅 Pretvaranje datuma u čitljiv format
meseci_srpski = {
    1: 'januar', 2: 'februar', 3: 'mart', 4: 'april', 5: 'maj', 6: 'jun',
    7: 'jul', 8: 'avgust', 9: 'septembar', 10: 'oktobar', 11: 'novembar', 12: 'decembar'
}

def parse_datum(raw):
    try:
        raw_str = str(int(raw)).zfill(5)
        month = int(raw_str[0])
        day = int(raw_str[1:3])
        year = 2000 + int(raw_str[3:])
        return f"{day}. {meseci_srpski.get(month, 'nepoznato')} {year}."
    except:
        return "Nepoznat datum"

@st.cache_data
def ucitaj_podatke():
    df = pd.read_excel(xlsx_path)
    df = df[df['lat'].notna() & df['lon'].notna()]
    df["Datum_fmt"] = df["Datum"].apply(parse_datum)
    return df

df = ucitaj_podatke()

# 🌈 Stilovi za mapu
tip_naziv = {'G': 'Grafit', 'M': 'Mural', 'N': 'Nalepnica', 'P': 'Poster'}
tip_boja = {'G': 'gray', 'M': 'blue', 'N': 'orange', 'P': 'red'}
tip_ikonica = {'G': 'spray-can', 'M': 'paint-brush', 'N': 'sticky-note', 'P': 'file-image'}

# 🧭 Naslov
st.markdown("<h3 style='margin-bottom:0'>🗺 Desničarski simboli širom Beograda</h3>", unsafe_allow_html=True)
st.caption("Fotografije sa ulica nastale u periodu od 2019. do marta 2025. godine")

# 🎛 Filteri
with st.expander("🎛 Prikaži / sakrij filtere", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        tipovi = st.multiselect("🎨 Tip", sorted(df['Tip'].dropna().unique()), default=[], placeholder="izberi")
        velicine = st.multiselect("📏 Veličina", sorted(df['Relativna velicina?'].dropna().unique()), default=[], placeholder="izberi")
    with col2:
        kvaliteti = st.multiselect("📸 Kvalitet", sorted(df['Kvalitet'].dropna().unique()), default=[], placeholder="izberi")
        autori = st.multiselect("✍ Autor", sorted(df['Autor'].dropna().unique()), default=[], placeholder="izberi")

if st.button("🔄 Resetuj filtere"):
    st.experimental_rerun()

# 🔍 Filtriranje
filtered = df.copy()
if tipovi:
    filtered = filtered[filtered['Tip'].isin(tipovi)]
if velicine:
    filtered = filtered[filtered['Relativna velicina?'].isin(velicine)]
if kvaliteti:
    filtered = filtered[filtered['Kvalitet'].isin(kvaliteti)]
if autori:
    filtered = filtered[filtered['Autor'].isin(autori)]

st.markdown(f"🔎 <small><b>Pronađeno simbola: {len(filtered)}</b></small>", unsafe_allow_html=True)

# 🗺 Kreiranje mape
if not filtered.empty:
    m = folium.Map(tiles="CartoDB positron", zoom_start=13, location=[44.8, 20.45])
    marker_cluster = MarkerCluster(spiderfyOnMaxZoom=True, zoomToBoundsOnClick=True).add_to(m)
    bounds = []

    for _, row in filtered.iterrows():
        lat, lon = row['lat'], row['lon']
        tip = row['Tip']
        autor = row['Autor']
        tekst = row.get('Tekst 1', '')
        datum = row.get('Datum_fmt', '')
        slika_file = f"{row['Slika']}.jpg"
        slika_url = f"https://teodoracurcic-mapa-simboli.streamlit.app/static/{slika_file}"

        img_tag = f"""
        <div style="margin-bottom:8px">
            <img src="{slika_url}" width="200px"
                 style="border-radius:10px; box-shadow:0 2px 6px rgba(0,0,0,0.25);">
        </div>
        """

        popup_html = f"""
        <div style="font-family:sans-serif; font-size:13px; line-height:1.5">
            {img_tag}
            <div><b>🖍 Tip:</b> {tip_naziv.get(tip, tip)}</div>
            <div><b>✍ Tekst:</b> {tekst}</div>
            <div><b>🧑 Autor:</b> {autor}</div>
            <div><b>📷 Slikano:</b> {datum}</div>
        </div>
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=tekst,
            icon=folium.Icon(color=tip_boja.get(tip, 'black'),
                             icon=tip_ikonica.get(tip, 'info-sign'),
                             prefix="fa")
        ).add_to(marker_cluster)

        bounds.append([lat, lon])

    if bounds:
        m.fit_bounds(bounds)

    # 🧭 Legenda
    legend_html = """
    <div style='position: fixed; bottom: 20px; right: 20px; background: white; padding: 10px;
                border-radius: 8px; border:1px solid #ccc; font-size: 13px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1); z-index: 9999;'>
    <b>Legenda</b><br>
    <div><span style='background:gray; width:12px; height:12px; display:inline-block; margin-right:5px'></span>Grafit</div>
    <div><span style='background:blue; width:12px; height:12px; display:inline-block; margin-right:5px'></span>Mural</div>
    <div><span style='background:orange; width:12px; height:12px; display:inline-block; margin-right:5px'></span>Nalepnica</div>
    <div><span style='background:red; width:12px; height:12px; display:inline-block; margin-right:5px'></span>Poster</div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=None, height=700)

else:
    st.info("⛔ Nema rezultata za zadate filtere.")

# 📥 CSV za preuzimanje
st.divider()
st.download_button("⬇️ Preuzmi CSV trenutnog prikaza", filtered.to_csv(index=False), "simboli_filtrirani.csv")

# 📬 Prijava
st.markdown("---")
st.markdown("📩 **Ako ste videli neki grafit, nalepnicu, mural ili poster** možete poslati detalje na **mejl@mejl.rs**")
