
import streamlit as st
import pandas as pd
import os
from PIL import Image

# -------------------------
# MUST BE FIRST STREAMLIT CALL
# -------------------------
st.set_page_config(
    page_title="Guest Tracker",
    layout="centered"
)

# -------------------------
# PASSWORD LOGIN
# -------------------------
PASSWORD = "GuestList"

st.title("🔐 Guest App Login")

password = st.text_input("Enter password", type="password")

if password != PASSWORD:
    st.warning("Incorrect password or no access.")
    st.stop()

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_csv("guests.csv")
df.columns = df.columns.str.strip()

df["Guest"] = df["first name"].astype(str) + " " + df["last name"].astype(str)

# -------------------------
# STORAGE SETUP
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
# PROGRESS BAR
# -------------------------
done = state["Card_Written"].sum()
total = len(state)

st.progress(done / total if total else 0)
st.write(f" {done}/{total} cards written")

st.markdown("---")

updated_rows = []

# -------------------------
# MAIN LOOP
# -------------------------
for i, row in state.iterrows():

    st.subheader(f" {row['Guest']}")

    safe_key = str(row["Guest"]).replace(" ", "_").replace(".", "")

    # -------------------------
    # SAFE IMAGE PATH HANDLING
    # -------------------------
    image_path = row.get("Image_Path", "")
    if pd.isna(image_path):
        image_path = ""
    else:
        image_path = str(image_path)

    # -------------------------
    # CARD WRITTEN
    # -------------------------
    written = st.checkbox(
        "✍️ Card Written",
        value=row["Card_Written"],
        key=f"written_{safe_key}_{i}"
    )

    # -------------------------
    # APPROVED
    # -------------------------
    approved = st.checkbox(
        "✔ Approved",
        value=row["Approved"],
        key=f"approved_{safe_key}_{i}"
    )

    # -------------------------
    # IMAGE UPLOAD
    # -------------------------
    uploaded_file = st.file_uploader(
        "📸 Take / Upload Photo",
        type=["png", "jpg", "jpeg"],
        key=f"upload_{safe_key}_{i}"
    )

    if uploaded_file is not None:
        image_path = os.path.join(
            UPLOAD_DIR,
            f"{safe_key}_{uploaded_file.name}"
        )

        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    # -------------------------
    # VIEW + DELETE IMAGE
    # -------------------------
    if image_path and os.path.exists(image_path):

        col1, col2 = st.columns(2)

        if col1.button("👁 View", key=f"view_{safe_key}_{i}"):
            st.image(image_path, use_container_width=True)

        if col2.button("🗑 Delete", key=f"delete_{safe_key}_{i}"):

            try:
                os.remove(image_path)
            except:
                pass

            image_path = ""
            st.rerun()

    # -------------------------
    # SAVE ROW
    # -------------------------
    updated_rows.append({
        "Guest": row["Guest"],
        "Card_Written": written,
        "Approved": approved,
        "Image_Path": image_path
    })

    st.markdown("---")

# -------------------------
# SAVE STATE
# -------------------------
state = pd.DataFrame(updated_rows)
state.to_csv(STATE_FILE, index=False)
