import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Red Mana Properties Farm Manager", layout="wide")

# TITLE AND LINK
st.title("🌾 Red Mana Properties Farm Manager")
st.markdown("[Visit HoneypotAcres.com](https://HoneypotAcres.com)", unsafe_allow_html=True)

st.markdown("""
This version automatically keeps **historical records** by appending new versions of a crop entry instead of overwriting existing ones.
""")

# Updated column set
COLUMNS = {
    "Location": str,
    "Crop": str,
    "Planting Date": str,
    "Growth Stage": str,
    "Nutrient Level (NPK)": str,
    "Water Used (gallons)": float,
    "pH": float,
    "TDS (ppm)": float,
    "Notes": str,
    "Last Updated": str,
    "Status": str
}

GROWTH_STAGES = ["Seed", "Sprout", "Vegetative", "Flowering", "Harvest"]
STATUS_OPTIONS = ["Active", "Historical"]

# Load CSV
uploaded_file = st.file_uploader("Upload existing CSV (optional)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if set(COLUMNS.keys()).issubset(df.columns):
        st.success("CSV loaded.")
        df = df[list(COLUMNS.keys())].astype(COLUMNS)
    else:
        st.warning("CSV missing required columns. Starting with empty sheet.")
        df = pd.DataFrame(columns=COLUMNS.keys())
else:
    df = pd.DataFrame(columns=COLUMNS.keys())

# New entry form
st.subheader("➕ Add or Update Record")

with st.form("new_entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        location = st.text_input("Location")
        crop = st.text_input("Crop")
        planting_date = st.date_input("Planting Date")
        growth_stage = st.selectbox("Growth Stage", GROWTH_STAGES)
        npk = st.text_input("Nutrient Level (NPK)", value="10-10-10")
    with col2:
        water = st.number_input("Water Used (gallons)", min_value=0.0, step=0.1)
        ph = st.number_input("pH", min_value=0.0, max_value=14.0, step=0.1)
        tds = st.number_input("TDS (ppm)", min_value=0.0, step=1.0)
        notes = st.text_area("Notes", height=80)

    submitted = st.form_submit_button("Submit Entry")

if submitted:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = {
        "Location": location,
        "Crop": crop,
        "Planting Date": planting_date.strftime("%Y-%m-%d"),
        "Growth Stage": growth_stage,
        "Nutrient Level (NPK)": npk,
        "Water Used (gallons)": water,
        "pH": ph,
        "TDS (ppm)": tds,
        "Notes": notes,
        "Last Updated": now,
        "Status": "Active"
    }

    # Mark existing active rows with same Crop + Location as historical
    df.loc[
        (df["Crop"] == crop) &
        (df["Location"] == location) &
        (df["Status"] == "Active"),
        "Status"
    ] = "Historical"

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    st.success("Entry added. Historical record preserved.")

# Filter options
st.subheader("🔍 Filter Records")

with st.expander("Filter Options", expanded=True):
    crop_filter = st.text_input("Search Crop Name")
    stage_filter = st.multiselect("Growth Stage", GROWTH_STAGES)
    location_filter = st.multiselect("Location", sorted(df["Location"].dropna().unique()))
    status_filter = st.multiselect("Status", STATUS_OPTIONS, default=["Active"])
    min_water, max_water = st.slider("Water (gallons)", 0.0, 500.0, (0.0, 500.0), step=0.5)
    min_ph, max_ph = st.slider("pH", 0.0, 14.0, (0.0, 14.0), step=0.1)
    min_tds, max_tds = st.slider("TDS (ppm)", 0, 2000, (0, 2000), step=10)

# Apply filters
filtered_df = df.copy()

if crop_filter:
    filtered_df = filtered_df[filtered_df["Crop"].str.contains(crop_filter, case=False, na=False)]

if stage_filter:
    filtered_df = filtered_df[filtered_df["Growth Stage"].isin(stage_filter)]

if location_filter:
    filtered_df = filtered_df[filtered_df["Location"].isin(location_filter)]

if status_filter:
    filtered_df = filtered_df[filtered_df["Status"].isin(status_filter)]

filtered_df = filtered_df[
    (filtered_df["Water Used (gallons)"] >= min_water) &
    (filtered_df["Water Used (gallons)"] <= max_water) &
    (filtered_df["pH"] >= min_ph) &
    (filtered_df["pH"] <= max_ph) &
    (filtered_df["TDS (ppm)"] >= min_tds) &
    (filtered_df["TDS (ppm)"] <= max_tds)
]

# Show filtered records
st.subheader("📄 Filtered Records")
st.dataframe(filtered_df, use_container_width=True)

# Charts
st.subheader("📊 Visualizations")

if not filtered_df.empty:
    try:
        filtered_df["Planting Date"] = pd.to_datetime(filtered_df["Planting Date"])
    except:
        pass

    st.markdown("**💧 Water Usage per Location**")
    st.bar_chart(filtered_df.groupby("Location")["Water Used (gallons)"].sum())

    st.markdown("**🌽 Crop Variety per Location**")
    st.bar_chart(filtered_df.groupby("Location")["Crop"].nunique())

    st.markdown("**🌱 Growth Stage Distribution**")
    st.pyplot(filtered_df["Growth Stage"].value_counts().plot.pie(autopct="%1.1f%%", ylabel="", figsize=(5,5)).figure)

    st.markdown("**🧪 Average pH per Location**")
    st.bar_chart(filtered_df.groupby("Location")["pH"].mean())

    st.markdown("**💧 Average TDS (ppm) per Location**")
    st.bar_chart(filtered_df.groupby("Location")["TDS (ppm)"].mean())

    if pd.api.types.is_datetime64_any_dtype(filtered_df["Planting Date"]):
        st.markdown("**📉 pH Over Time**")
        st.line_chart(filtered_df.groupby("Planting Date")["pH"].mean())

        st.markdown("**📉 TDS (ppm) Over Time**")
        st.line_chart(filtered_df.groupby("Planting Date")["TDS (ppm)"].mean())
else:
    st.info("No matching records.")

# Download section
st.subheader("⬇️ Download Full History")
csv_buffer = io.StringIO()
df.to_csv(csv_buffer, index=False)
st.download_button("Download CSV", data=csv_buffer.getvalue(), file_name="farm_history.csv", mime="text/csv")
