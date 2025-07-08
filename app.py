import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import datetime

st.set_page_config(page_title="Red Mana Properties Farm Manager", layout="wide")

# TITLE AND LINK
st.title("🌾 Red Mana Properties Farm Manager")
st.markdown("[Visit HoneypotAcres.com](https://HoneypotAcres.com)", unsafe_allow_html=True)

# COLUMN DEFINITIONS
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

# IMPORT
uploaded_file = st.file_uploader("📥 Import CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if set(COLUMNS.keys()).issubset(df.columns):
        df = df[list(COLUMNS.keys())].astype(COLUMNS)
        st.success("✅ Imported data loaded.")
    else:
        st.warning("⚠️ Uploaded file is missing required columns. Starting blank.")
        df = pd.DataFrame(columns=COLUMNS.keys())
else:
    df = pd.DataFrame(columns=COLUMNS.keys())
    st.warning("⚠️ No data imported yet. You’re starting with a blank database.")

# NEW ENTRY FORM
st.subheader("➕ Add or Update Record")

existing_locations = sorted(df["Location"].dropna().unique())
location = st.text_input("Location", placeholder="Type new or match existing")
if location:
    matching_locations = [loc for loc in existing_locations if loc.lower().startswith(location.lower())]
    if matching_locations:
        st.markdown("**Suggestions:** " + ", ".join(matching_locations))

filtered_by_location = df[df["Location"] == location] if location else df
existing_crops = sorted(filtered_by_location["Crop"].dropna().unique())

crop = st.text_input("Crop", placeholder="Type new or match existing")
if crop:
    matching_crops = [c for c in existing_crops if c.lower().startswith(crop.lower())]
    if matching_crops:
        st.markdown("**Suggestions:** " + ", ".join(matching_crops))

# LOAD LAST RECORD FOR PREFILL
prefill = {}
if location and crop:
    match = df[(df["Location"] == location) & (df["Crop"] == crop) & (df["Status"] == "Active")]
    if not match.empty:
        prefill = match.sort_values("Last Updated", ascending=False).iloc[-1].to_dict()

# FORM INPUTS
with st.form("new_entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        planting_date = st.date_input(
            "Planting Date",
            value=pd.to_datetime(prefill.get("Planting Date", pd.Timestamp.today()))
        )
        growth_stage = st.selectbox(
            "Growth Stage",
            GROWTH_STAGES,
            index=GROWTH_STAGES.index(prefill.get("Growth Stage", GROWTH_STAGES[0]))
            if prefill.get("Growth Stage") in GROWTH_STAGES else 0
        )
        npk = st.text_input("Nutrient Level (NPK)", value=prefill.get("Nutrient Level (NPK)", "10-10-10"))
    with col2:
        water = st.number_input("Water Used (gallons)", min_value=0.0, step=0.1,
                                value=float(prefill.get("Water Used (gallons)", 0.0)))
        ph = st.number_input("pH", min_value=0.0, max_value=14.0, step=0.1,
                             value=float(prefill.get("pH", 7.0)))
        tds = st.number_input("TDS (ppm)", min_value=0.0, step=1.0,
                              value=float(prefill.get("TDS (ppm)", 0.0)))
        notes = st.text_area("Notes", height=80, value=prefill.get("Notes", ""))

    submitted = st.form_submit_button("Submit Entry")

# HANDLE SUBMISSION
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

    df.loc[
        (df["Crop"] == crop) &
        (df["Location"] == location) &
        (df["Status"] == "Active"),
        "Status"
    ] = "Historical"

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    st.success("✅ Entry added. Historical record preserved.")

# FILTERS
st.subheader("🔍 Filter Records")

with st.expander("Filter Options", expanded=True):
    crop_filter = st.text_input("Search Crop")
    stage_filter = st.multiselect("Growth Stage", GROWTH_STAGES)
    location_filter = st.multiselect("Location", sorted(df["Location"].dropna().unique()))
    status_filter = st.multiselect("Status", STATUS_OPTIONS, default=["Active"])
    min_water, max_water = st.slider("Water (gallons)", 0.0, 500.0, (0.0, 500.0), step=0.5)
    min_ph, max_ph = st.slider("pH", 0.0, 14.0, (0.0, 14.0), step=0.1)
    min_tds, max_tds = st.slider("TDS (ppm)", 0, 2000, (0, 2000), step=10)

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

# DISPLAY FILTERED DATA
st.subheader("📄 Filtered Records")
st.dataframe(filtered_df, use_container_width=True)

# CHARTS ON DEMAND
if st.button("📊 Generate Charts"):
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
        fig, ax = plt.subplots()
        filtered_df["Growth Stage"].value_counts().plot.pie(
            autopct="%1.1f%%", ylabel="", figsize=(5, 5), ax=ax
        )
        st.pyplot(fig)

        st.markdown("**🧪 Average pH per Location**")
        st.bar_chart(filtered_df.groupby("Location")["pH"].mean())

        st.markdown("**💧 Average TDS per Location**")
        st.bar_chart(filtered_df.groupby("Location")["TDS (ppm)"].mean())

        if pd.api.types.is_datetime64_any_dtype(filtered_df["Planting Date"]):
            st.markdown("**📉 pH Over Time**")
            st.line_chart(filtered_df.groupby("Planting Date")["pH"].mean())

            st.markdown("**📉 TDS Over Time**")
            st.line_chart(filtered_df.groupby("Planting Date")["TDS (ppm)"].mean())
    else:
        st.info("No data available for charting.")

# EXPORT BUTTON (BOTTOM)
st.subheader("📤 Export Data")
export_buffer = io.StringIO()
df.to_csv(export_buffer, index=False)
st.download_button(
    label="Download Full CSV",
    data=export_buffer.getvalue(),
    file_name="farm_data.csv",
    mime="text/csv"
)
