import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Red Mana Properties Farm Manager", layout="wide")

# TITLE AND LINK
st.title("🌾 Red Mana Properties Farm Manager")
st.markdown("[Visit HoneypotAcres.com](https://HoneypotAcres.com)", unsafe_allow_html=True)

st.markdown("""
Manage and visualize your farm data by **location**, **pH**, and **TDS**.
- 🧪 `pH` and `TDS (ppm)` tracking
- 📍 Location-aware filtering
- 📊 Water, nutrient, and soil analytics
""")

# Define all columns
COLUMNS = {
    "Location": str,
    "Crop": str,
    "Planting Date": str,
    "Growth Stage": str,
    "Nutrient Level (NPK)": str,
    "Water Used (gallons)": float,
    "pH": float,
    "TDS (ppm)": float,
    "Notes": str
}

GROWTH_STAGES = ["Seed", "Sprout", "Vegetative", "Flowering", "Harvest"]

# Upload CSV
uploaded_file = st.file_uploader("Upload existing CSV (optional)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if set(COLUMNS.keys()).issubset(df.columns):
        st.success("CSV loaded.")
        df = df[list(COLUMNS.keys())].astype(COLUMNS)
    else:
        st.warning("CSV missing required columns. Starting blank.")
        df = pd.DataFrame(columns=COLUMNS.keys())
else:
    df = pd.DataFrame(columns=COLUMNS.keys())

# Editable table
st.subheader("📋 Edit Farm Records")
edited_df = st.data_editor(
    df,
    column_config={
        "Location": st.column_config.TextColumn("Location", help="Field or area (e.g., North Plot)"),
        "Growth Stage": st.column_config.SelectboxColumn("Growth Stage", options=GROWTH_STAGES),
        "Water Used (gallons)": st.column_config.NumberColumn("Water Used (gallons)", min_value=0.0, step=0.1),
        "pH": st.column_config.NumberColumn("pH", min_value=0.0, max_value=14.0, step=0.1),
        "TDS (ppm)": st.column_config.NumberColumn("TDS (ppm)", min_value=0.0, step=1.0),
        "Planting Date": st.column_config.TextColumn("Planting Date (YYYY-MM-DD)")
    },
    num_rows="dynamic",
    use_container_width=True
)

# FILTERS
st.subheader("🔍 Filter Your Data")
with st.expander("Filter Options", expanded=True):
    crop_filter = st.text_input("Search Crop Name")
    stage_filter = st.multiselect("Filter by Growth Stage", GROWTH_STAGES)
    location_filter = st.multiselect("Filter by Location", sorted(edited_df["Location"].dropna().unique()))
    min_water, max_water = st.slider("Water Usage (gallons)", 0.0, 500.0, (0.0, 500.0), step=0.5)
    min_ph, max_ph = st.slider("pH Range", 0.0, 14.0, (0.0, 14.0), step=0.1)
    min_tds, max_tds = st.slider("TDS Range (ppm)", 0, 2000, (0, 2000), step=10)

# Apply filters
filtered_df = edited_df.copy()

if crop_filter:
    filtered_df = filtered_df[filtered_df["Crop"].str.contains(crop_filter, case=False, na=False)]

if stage_filter:
    filtered_df = filtered_df[filtered_df["Growth Stage"].isin(stage_filter)]

if location_filter:
    filtered_df = filtered_df[filtered_df["Location"].isin(location_filter)]

filtered_df = filtered_df[
    (filtered_df["Water Used (gallons)"] >= min_water) &
    (filtered_df["Water Used (gallons)"] <= max_water) &
    (filtered_df["pH"] >= min_ph) &
    (filtered_df["pH"] <= max_ph) &
    (filtered_df["TDS (ppm)"] >= min_tds) &
    (filtered_df["TDS (ppm)"] <= max_tds)
]

# Show filtered table
st.subheader("📄 Filtered Results")
st.dataframe(filtered_df, use_container_width=True)

# CHARTS
st.subheader("📊 Charts & Visualizations")

if not filtered_df.empty:
    # Convert planting date if possible
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
        st.markdown("**📉 Average pH Over Time**")
        st.line_chart(filtered_df.groupby("Planting Date")["pH"].mean())

        st.markdown("**📉 TDS (ppm) Over Time**")
        st.line_chart(filtered_df.groupby("Planting Date")["TDS (ppm)"].mean())
else:
    st.info("No data matches the filters.")

# DOWNLOAD
st.subheader("⬇️ Export Updated Data")
csv_buffer = io.StringIO()
edited_df.to_csv(csv_buffer, index=False)
st.download_button(
    label="Download CSV",
    data=csv_buffer.getvalue(),
    file_name="updated_farm_data.csv",
    mime="text/csv"
)
