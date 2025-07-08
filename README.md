# RMPFarmManagerV2
Version 2 of the Red Mana Properties Farm Manager

The new improved version of the Farm Manager provides a Steamlit web interface, and the ability to import and export data.

This app has only been tested with Python 3.13. Requirements are in requirements.txt

A live version is available for free at https://rmpfarmmanagerv2.streamlit.app/ without install.

NOTE: You must import your database each session, and export when you're finished. Unsaved changes will not be retained.

All data is exported as a .csv file, including historical data.

This app is still experimental. NO WARRANTY.

🛠️ How to Use the RMP Farm Manager App
1. 🚀 Launch the App

Visit https://rmpfarmmanagerv2.streamlit.app/ without install
OR Run locally:

Make sure you have Python installed (3.9 or higher recommended). Then:

bash

pip install -r requirements.txt

streamlit run app.py

2. 📥 Import Existing Data (Optional)
Use the "Import CSV" button at the top to upload your existing farm records.

The file should match the expected column structure (see example in repo).

If no file is imported, you’ll start with a blank database.

3. ➕ Add or Update a Crop Record
Choose between New Crop or Existing Crop mode.

Enter the location, crop name, planting date, growth stage, nutrient levels, water usage, pH, TDS, and any notes.

Submitting the form:

Archives previous active records for the same crop/location as “Historical.”

Saves the new entry as “Active.”

4. 🔍 Filter and Search
Use the filtering panel to narrow results by:

Crop name

Growth stage

Location

Water, pH, TDS ranges

Active vs Historical status

5. 📊 Generate Charts
Click “Generate Charts” to visualize:

Water usage by location

Crop variety and growth stage distribution

Average pH and TDS

Time-based pH and TDS trends

6. 📤 Export Your Data
Click the “Download Full CSV” button to export your data.

⚠️ After exporting, you'll be asked to reload the page to start a new session — this ensures no data is unintentionally retained.

✅ All data is kept local — no cloud storage or login required.
Perfect for small farms, greenhouse operators, or anyone managing planting cycles!


