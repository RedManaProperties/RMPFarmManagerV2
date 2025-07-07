import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Farm Management App", layout="wide")
st.title("🌾 Farm Management Dashboard")

st.markdown("Use this app to manage your farm activities without saving data to a server. Upload or download the entire database as a CSV.")

# Define the CSV schema
COLUMNS = [
    "Crop",
    "Planting Date",
    "Growth Stage",
    "Nutrient Level (NPK)",
    "Water Used (gallons)",
    "Notes"
]

# Load CSV
uploaded_file = st.file_uploader("Upload existing farm data (.csv)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if set(COLUMNS).issubset(df.columns):
        st.success("CSV loaded successfully.")
    else:
        st.error("Uploaded CSV is missing required columns.")
        df = pd.DataFrame(columns=COLUMNS)
else:
    df = pd.DataFrame(columns=COLUMNS)

# Add new entry
with st.expander("➕ Add New Crop Entry"):
    with st.form("new_entry"):
        crop = st.text_input("Crop")
        planting_date = st.date_input("Planting Date")
        growth_stage = st.selectbox("Growth Stage", ["Seed", "Sprout", "Vegetative", "Flowering", "Harvest"])
        nutrients = st.text_input("Nutrient Level (e.g., 10-10-10)")
        water_used = st.number_input("Water Used (gallons)", min_value=0.0, step=0.1)
        notes = st.text_area("Notes", height=100)
        submitted = st.form_submit_button("Add Entry")

        if submitted:
            new_data = {
                "Crop": crop,
                "Planting Date": planting_date.strftime("%Y-%m-%d"),
                "Growth Stage": growth_stage,
                "Nutrient Level (NPK)": nutrients,
                "Water Used (gallons)": water_used,
                "Notes": notes
            }
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            st.success("Entry added successfully.")

# Show current table
st.subheader("📋 Current Farm Data")
st.dataframe(df, use_container_width=True)

# Export CSV
st.subheader("⬇️ Download Data")
csv_buffer = io.StringIO()
df.to_csv(csv_buffer, index=False)
st.download_button(
    label="Download as CSV",
    data=csv_buffer.getvalue(),
    file_name="farm_data.csv",
    mime="text/csv"
)
