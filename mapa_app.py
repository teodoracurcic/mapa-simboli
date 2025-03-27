import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import os

# --- 📁 Putanje ---
xlsx_path = "simboli_koordinate_GPS.xlsx"
static_folder = "static"

# --- 📥 Učitaj podatke ---
df = pd.read_excel(xlsx_path)
df = df[df['lat'].notna() & df['lon'].notna()]

# 📅 Formatiranje datuma
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
        naziv_meseca = meseci_srpski.get(month, "nepoznato")
        return f"{day}. {naziv_meseca} {year}."
    except:
        return "Nepoznat datum"

df['Datum_fmt'] = df['Datum'].apply(parse_datum)

# 🎨 Stilovi
tip_naziv = {'G': 'Grafit', 'M': 'Mural', 'N': 'Nalepnica', 'P': 'Poster'}
tip_boja = {'G': 'gray', 'M': 'blue', 'N': 'orange', 'P': 'red'}
tip_ikonica = {'G': 'spray-can', 'M': 'paint-brush', 'N': 'sticky-note', 'P': 'file-image'}

# 🧠 Naslov
st.title("🗺 Desničarski simboli širom Beograda")
st.markdown("*Fotografije sa ulica nastale u periodu od 2019. do marta 2025. godine*")

# 🎛 Filteri
col1, col2 = st.columns(2)

with col1:
    tipovi = st.multiselect("🎨 Tip", sorted(df['Tip'].dropna().unique()), default=list(df['Tip'].dropna().unique()))
    velicine = st.multiselect("📏 Veličina", sorted(df['Relativna velicina?'].dropna().unique()), default=list(df['Relativna velicina?'].dropna().unique()))

with col2:
    kvaliteti = st.multiselect("📸 Kvalitet", sorted(df['Kvalitet'].dropna().unique()), default=list(df['Kvalitet'].dropna().unique()))
    autori = st.multiselect("✍ Autor", sorted(df['Autor'].dropna().unique()), default=list(df['Autor'].dropna().unique()))

# 🔎 Filtriranje
filtered = df[
    df['Tip'].isin(tipovi) &
    df['Relativna velicina?'].isin(velicine) &
    df['Kvalitet'].isin(kvaliteti) &
    df['Autor'].isin(autori)
]

# 🗺 Mapa
m = folium.Map(tiles="CartoDB positron", zoom_start=13, location=[44.8, 20.45])
marker_cluster = MarkerCluster().add_to(m)
bounds = []

for _, row in filtered.iterrows():
    lat, lon = row['lat'], row['lon']
    tip = row['Tip']
    autor = row['Autor']
    tekst = row.get('Tekst 1', '')
    datum = row.get('Datum_fmt', '')
    slika_file = f"{row['Slika']}.jpg"
    slika_url = f"https://mapa-simboli.streamlit.app/static/{slika_file}"

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
        icon=folium.Icon(color=tip_boja.get(tip, 'black'), icon=tip_ikonica.get(tip, 'info-sign'), prefix="fa")
    ).add_to(marker_cluster)

    bounds.append([lat, lon])

# Fit mapa na prikazane tačke
if bounds:
    m.fit_bounds(bounds)

# Prikaz mape
st_data = st_folium(m, width=1000, height=600)

# Napomena
st.markdown("---")
st.info("📬 Ako znate za neki simbol koji nedostaje, javite se na adresu: **primer@gmail.com**")
