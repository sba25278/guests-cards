
import streamlit as st
import pandas as pd
import os
from PIL import Image

# -------------------------
# MOBILE CONFIG
# -------------------------
st.set_page_config(
    page_title="Guest Tracker",
    layout="centered"
)

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_csv("guests.csv")
df.columns = df.columns.str.strip()

df["Guest"] = df["first name"].astype(str) + " " + df["last name"].astype(str)

# -------------------------
# STORAGE
# -------------------------
STATE_FILE = "guests_state.csv"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------------
# LOAD OR INIT STATE
# -------------------------
if os.path.exists(STATE_FILE):
    state = pd.read_csv(STATE_FILE)
else:
    state = df[["Guest"]].copy()
    state["Card_Written"] = False
    state["Approved"] = False
    state["Image_Path"] = ""
    state.to_csv(STATE_FILE, index=False)

st.title("📋 Guest Tracker")

# -------------------------
# PROGRESS (BASED ON WRITTEN)
# -------------------------
done = state["Card_Written"].sum()
total = len(state)

st.progress(done / total if total else 0)
st.write(f"✍️ {done}/{total} written")

st.markdown("---")

updated_rows = []

# -------------------------
# MOBILE CARD LIST (NO SWIPE BUTTONS)
# -------------------------
for i, row in state.iterrows():

    st.subheader(f"👤 {row['Guest']}")

    safe_key = str(row["Guest"]).replace(" ", "_").replace(".", "")

    # -------------------------
    # IMAGE PATH SAFE
    # -------------------------
    image_path = row.get("Image_Path", "")
    if pd.isna(image_path):
        image_path = ""
    else:
        image_path = str(image_path)

    # -------------------------
    # WRITTEN (drives progress)
    # -------------------------
    written = st.checkbox(
        "✍️ Card Written",
        value=row["Card_Written"],
        key=f"written_{i}_{safe_key}"
    )

    # -------------------------
    # UPLOAD (camera enabled on mobile)
    # -------------------------
    uploaded_file = st.file_uploader(
        "📸 Take / Upload Photo",
        type=["png", "jpg", "jpeg"],
        key=f"upload_{i}_{safe_key}"
    )

    if uploaded_file is not None:
        image_path = os.path.join(
            UPLOAD_DIR,
            f"{i}_{safe_key}_{uploaded_file.name}"
        )

        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    # -------------------------
    # IMAGE PREVIEW (FULL WIDTH)
    # -------------------------
    if image_path and os.path.exists(image_path):
        st.image(Image.open(image_path), use_container_width=True)

    # -------------------------
    # APPROVED (UNDER PHOTO)
    # -------------------------
    approved = st.checkbox(
        "✔ Approved",
        value=row["Approved"],
        key=f"approved_{i}_{safe_key}"
    )

    # -------------------------
    # SAVE STATE (AUTO)
    # -------------------------
    updated_rows.append({
        "Guest": row["Guest"],
        "Card_Written": written,
        "Approved": approved,
        "Image_Path": image_path
    })

    st.markdown("---")

# -------------------------
# WRITE BACK (AUTO SAVE)
# -------------------------
state = pd.DataFrame(updated_rows)
state.to_csv(STATE_FILE, index=False)
