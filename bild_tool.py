import streamlit as st
from PIL import Image, ImageDraw
import io
import numpy as np

# --- Seiteneinstellungen ---
st.set_page_config(page_title="Bild anpassen & komprimieren", layout="centered")

st.title("🛠️ Bild zuschneiden, skalieren & komprimieren")
st.write("Lade ein Bild hoch, wähle Größe, steuere den Bildausschnitt und komprimiere für Web oder Social Media.")

# --- Bild-Upload ---
bilddatei = st.file_uploader("📤 Bild auswählen (JPG/PNG)", type=["jpg", "jpeg", "png"])

# --- Formatauswahl ---
formate = {
    "Web (1200x800)": (1200, 800),
    "Instagram Post (1080x1080)": (1080, 1080),
    "Instagram Story (1080x1920)": (1080, 1920),
    "YouTube Thumbnail (1280x720)": (1280, 720),
    "Facebook Cover (1200x630)": (1200, 630)
}

wahl = st.selectbox("🖼️ Zielgröße auswählen", list(formate.keys()))
custom = st.checkbox("Oder eigene Größe eingeben")

if custom:
    z_breite = st.number_input("📐 Breite (px)", min_value=100, max_value=5000, value=1200)
    z_hoehe = st.number_input("📐 Höhe (px)", min_value=100, max_value=5000, value=800)
else:
    z_breite, z_hoehe = formate[wahl]

if bilddatei:
    original = Image.open(bilddatei).convert("RGB")

    # --- Skalieren proportional ---
    original_ratio = original.width / original.height
    ziel_ratio = z_breite / z_hoehe

    if original_ratio > ziel_ratio:
        new_height = z_hoehe
        new_width = int(original_ratio * new_height)
    else:
        new_width = z_breite
        new_height = int(new_width / original_ratio)

    resized = original.resize((new_width, new_height))

    # --- Slider für Zuschneideposition ---
    max_x = max(0, new_width - z_breite)
    max_y = max(0, new_height - z_hoehe)

    if max_x > 0:
        x_offset = st.slider("📍 Linker Rand", 0, max_x, 0)
    else:
        x_offset = 0

    if max_y > 0:
        y_offset = st.slider("📍 Oberer Rand", 0, max_y, 0)
    else:
        y_offset = 0

    # --- Zuschneiden ---
    left = x_offset
    top = y_offset
    right = left + z_breite
    bottom = top + z_hoehe
    cropped = resized.crop((left, top, right, bottom))

    # --- Komprimierungsqualität ---
    st.subheader("⚙️ Komprimierung")
    qualitaet = st.slider("🧬 JPEG-Qualität", 10, 100, 85)

    # --- Vorschau mit Zielrahmen ---
    st.subheader("🔍 Vorschau")
    show_frame = st.checkbox("🔲 Zielrahmen im Originalbild anzeigen")

    if show_frame:
        rahmenbild = resized.copy()
        draw = ImageDraw.Draw(rahmenbild)
        draw.rectangle([(x_offset, y_offset), (x_offset + z_breite, y_offset + z_hoehe)], outline="red", width=3)
        st.image(rahmenbild, caption="🔲 Zielausschnitt im Originalbild")

    st.image(cropped, caption=f"{z_breite}×{z_hoehe}px, Qualität: {qualitaet}%")

    # --- Komprimieren und speichern ---
    buffer = io.BytesIO()
    cropped.save(buffer, format="JPEG", quality=qualitaet)
    size_kb = len(buffer.getvalue()) / 1024
    st.markdown(f"📦 Geschätzte Dateigröße: **{size_kb:.1f} KB**")

    st.download_button(
        label="⬇️ Bild herunterladen",
        data=buffer.getvalue(),
        file_name=f"bild_{z_breite}x{z_hoehe}_q{qualitaet}.jpg",
        mime="image/jpeg"
    )

# --- Nutzeranleitung ---
st.sidebar.title("📘 Anleitung")
st.sidebar.markdown(\"\"\"
1. **Bild hochladen** (JPG oder PNG)  
2. **Zielgröße auswählen** oder eigene Maße eingeben  
3. **Ausschnitt verschieben**, falls gewünscht  
4. **Zielrahmen anzeigen** zur besseren Vorschau  
5. **Qualität wählen** für optimale Komprimierung  
6. **Herunterladen** – fertig fürs Web oder Social Media!
\"\"\")
