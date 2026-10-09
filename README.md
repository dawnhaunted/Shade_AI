Shade AI — Urban Heat & Tree Canopy Prioritization
A Streamlit portfolio project demonstrating geospatial visualization, data analysis, transparent decision rules, and sustainability-oriented recommendations.

Features
Interactive Folium map centered on a Chennai demo area
Configurable temperature and tree-canopy thresholds
Explainable three-level zone classification
Heuristic priority score to rank demo zones
Summary metrics, filters, and CSV export
Optional temperature intensity layer
Methodology and responsible-use disclosure
Important data limitation
The app currently generates synthetic demonstration data. Coordinates are randomized around Chennai, and temperature/canopy values are simulated. They are not observations of actual streets or neighborhoods. Do not describe the output as a real-time heat map, a validated AI prediction, or evidence that a specific place needs planting.

Run locally
Python 3.10+ recommended.

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
Suggested next steps
Add a documented real dataset and data-source attribution.
Add input validation and data freshness metadata.
Compare the rule-based priority score against field observations.
Add population vulnerability, land suitability, water availability, native species, maintenance, and community consultation factors.
Add automated tests for classification and score behavior.
Consider a validated predictive model only if sufficient labeled data exists.
Technologies
Python, Streamlit, Pandas, NumPy, Folium, streamlit-folium.

Resume-ready description (adjust to reflect what you actually build)
Shade AI — Explainable Urban Greening Decision-Support Prototype

Built a Streamlit geospatial dashboard using Python, Pandas, NumPy, and Folium to explore temperature and tree-canopy indicators across synthetic urban zones.
Implemented configurable, explainable classification rules and a heuristic priority score to rank areas for further validation and greening assessment.
Added interactive map popups, filtering, summary metrics, CSV export, and explicit data-quality/responsible-use disclosures.
Do not claim real-world impact, production deployment, validated AI, or use of real satellite data unless you implement and verify those capabilities.
