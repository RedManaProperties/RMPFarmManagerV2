import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Farm Management App", layout="wide")
st.title("🌾 Farm Management Dashboard (Editable + Charts + Filters + Location)")

st.markdown("""
Manage and visualize your farm data by location.
- 📍 New "Location" column added
- ✏️ Edit directly in the table
- 🔍 Filter records by location, stage, water use
- 📊 Visualize per-location water and crop metrics
""")

# Define columns with "Location" first
COLUMNS = {
    "Location": str,
    "Crop": str,
    "Planting Date": str,
    "Growth Stage": str,
    "Nutrient Level (NPK)": str,
    "Water Used (gallons)": float,
    "Notes": str
}

GROWTH_STAGES = ["Seed", "Sprout", "Vegetative", "Flowering", "Harvest"]

# Upload section
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
        "Growth Stage": st.column_config.SelectboxColumn(
            "Growth Stage",
            help="Current stage of the crop",
            options=GROWTH_STAGES
        ),
        "Water Used (gallons)": st.column_config.NumberColumn(
            "Water Used (gallons)",
            min_value=0.0,
            step=0.1,
            format="%.1f"
        ),
        "Planting Date": st.column_config.TextColumn(
            "Planting Date (YYYY-MM-DD)",
            help="Format as YYYY-MM-DD"
        )
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
    (filtered_df["Water Used (gallons)"] <= max_water)
]

# Show filtered table
st.subheader("📄 Filtered Results")
st.dataframe(filtered_df, use_container_width=True)

# CHARTS
st.subheader("📊 Charts & Visualizations")

if not filtered_df.empty:
    # Convert planting date to datetime if valid
    try:
        filtered_df["Planting Date"] = pd.to_datetime(filtered_df["Planting Date"])
    except:
        pass

    # Chart: Water usage by location
    st.markdown("**💧 Total Water Usage per Location**")
    location_water = filtered_df.groupby("Location")["Water Used (gallons)"].sum()
    st.bar_chart(location_water)

    # Chart: Crop counts per location
    st.markdown("**🌽 Crop Count per Location**")
    location_crops = filtered_df.groupby("Location")["Crop"].nunique()
    st.bar_chart(location_crops)

    # Chart: Growth stage distribution
    st.markdown("**🌱 Growth Stage Distribution**")
    stage_counts = filtered_df["Growth Stage"].value_counts()
    st.pyplot(stage_counts.plot.pie(autopct='%1.1f%%', figsize=(5, 5), ylabel="").figure)

    # Line chart: Water use over time
    if pd.api.types.is_datetime64_any_dtype(filtered_df["Planting Date"]):
        st.markdown("**📈 Water Usage Over Time**")
        time_chart = filtered_df.groupby("Planting Date")["Water Used (gallons)"].sum()
        st.line_chart(time_chart)
else:
    st.info("No data matches the filters.")

# Download section
st.subheader("⬇️ Export Updated Data")
csv_buffer = io.StringIO()
edited_df.to_csv(csv_buffer, index=False)
st.download_button(
    label="Download CSV",
    data=csv_buffer.getvalue(),
    file_name="updated_farm_data.csv",
    mime="text/csv"
)
