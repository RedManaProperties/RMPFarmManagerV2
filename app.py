import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Farm Management App", layout="wide")
st.title("🌾 Farm Management Dashboard (Editable)")

st.markdown("""
Manage your farm records directly in an editable table.
- Upload a `.csv` to get started or work from a blank slate
- All edits stay local until you download the updated file
""")

# Define the expected column names and types
COLUMNS = {
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
        st.success("CSV loaded successfully.")
        df = df[list(COLUMNS.keys())].astype(COLUMNS)
    else:
        st.warning("CSV missing required columns. Starting with a blank table.")
        df = pd.DataFrame(columns=COLUMNS.keys())
else:
    df = pd.DataFrame(columns=COLUMNS.keys())

# Display editable data editor
st.subheader("📋 Edit Farm Records")
edited_df = st.data_editor(
    df,
    column_config={
        "Growth Stage": st.column_config.SelectboxColumn(
            "Growth Stage",
            help="Current growth stage of the crop",
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
    num_rows="dynamic",  # allows adding new rows
    use_container_width=True
)

# Download section
st.subheader("⬇️ Export Updated Data")
csv_buffer = io.StringIO()
edited_df.to_csv(csv_buffer, index=False)
st.download_button(
    label="Download Edited CSV",
    data=csv_buffer.getvalue(),
    file_name="updated_farm_data.csv",
    mime="text/csv"
)
