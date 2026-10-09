"""
Shade AI — Urban Heat & Tree Canopy Prioritization
Portfolio project: transparent, explainable decision support for urban greening.

Important:
- The default dataset is SYNTHETIC demo data, not measured city temperatures.
- Replace generate_demo_data() with verified geospatial/temperature/canopy data
  before using this for real planning decisions.
"""

from __future__ import annotations

from typing import Final

import folium
import numpy as np
import pandas as pd
import streamlit as st
from folium.plugins import HeatMap
from streamlit_folium import st_folium


# ----------------------------- App configuration -----------------------------
st.set_page_config(
    page_title="Shade AI | Urban Heat & Greening Planner",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded",
)

CITY_CENTER: Final[tuple[float, float]] = (13.0827, 80.2707)  # Chennai demo center
DATA_SEED: Final[int] = 42
STATUS_COLORS: Final[dict[str, str]] = {
    "Critical plantation priority": "#d62728",
    "Heat monitoring": "#ff8c00",
    "Lower current priority": "#2ca25f",
}


# -------------------------------- Data layer ---------------------------------
@st.cache_data(show_spinner=False)
def generate_demo_data(
    n_points: int = 250,
    seed: int = DATA_SEED,
) -> pd.DataFrame:
    """Create reproducible synthetic points for demonstration only."""
    rng = np.random.default_rng(seed)

    latitudes = CITY_CENTER[0] + rng.uniform(-0.035, 0.035, n_points)
    longitudes = CITY_CENTER[1] + rng.uniform(-0.035, 0.035, n_points)

    # Synthetic variables intentionally vary independently for a transparent demo.
    temperatures = rng.uniform(31.0, 44.0, n_points)
    canopy = rng.uniform(3.0, 85.0, n_points)

    return pd.DataFrame(
        {
            "Zone_ID": [f"CHN-{i:03d}" for i in range(1, n_points + 1)],
            "Latitude": latitudes,
            "Longitude": longitudes,
            "Temperature_C": temperatures.round(1),
            "Tree_Cover_Pct": canopy.round(1),
            "Data_Source": "Synthetic demo data",
        }
    )


def classify_zone(
    temperature: float,
    canopy_pct: float,
    temperature_threshold: float,
    canopy_threshold: float,
) -> str:
    """Apply a transparent rule-based classification; this is not an ML model."""
    if temperature >= temperature_threshold and canopy_pct < canopy_threshold:
        return "Critical plantation priority"
    if temperature >= temperature_threshold:
        return "Heat monitoring"
    return "Lower current priority"


def add_decision_support_columns(
    data: pd.DataFrame,
    temperature_threshold: float,
    canopy_threshold: float,
) -> pd.DataFrame:
    """Return a classified copy and a simple explainable priority score."""
    result = data.copy()
    result["Status"] = [
        classify_zone(t, c, temperature_threshold, canopy_threshold)
        for t, c in zip(result["Temperature_C"], result["Tree_Cover_Pct"])
    ]

    # Score is a heuristic for sorting, not a validated heat-risk model.
    heat_component = (
        (result["Temperature_C"] - temperature_threshold).clip(lower=0) / 6.0
    ).clip(upper=1)
    canopy_gap_component = (
        (canopy_threshold - result["Tree_Cover_Pct"]).clip(lower=0)
        / max(canopy_threshold, 1)
    ).clip(upper=1)
    result["Priority_Score"] = (
        100 * (0.55 * heat_component + 0.45 * canopy_gap_component)
    ).round(1)

    result["Recommended_Action"] = result["Status"].map(
        {
            "Critical plantation priority":
                "Assess planting feasibility; prioritize shade and native-canopy options",
            "Heat monitoring":
                "Validate temperature readings and inspect existing shade options",
            "Lower current priority":
                "Maintain canopy and monitor during hotter periods",
        }
    )
    return result


def build_map(
    data: pd.DataFrame,
    show_heat_layer: bool,
    show_only_priority: bool,
) -> folium.Map:
    """Build an interactive map with point details and optional heat layer."""
    city_map = folium.Map(
        location=CITY_CENTER,
        zoom_start=12,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    points = data.copy()
    if show_only_priority:
        points = points[
            points["Status"] == "Critical plantation priority"
        ]

    if show_heat_layer and not data.empty:
        HeatMap(
            data[["Latitude", "Longitude", "Temperature_C"]].values.tolist(),
            name="Temperature intensity (demo)",
            radius=20,
            blur=16,
            min_opacity=0.25,
        ).add_to(city_map)

    for _, row in points.iterrows():
        color = STATUS_COLORS[row["Status"]]
        popup_html = f"""
        <div style="font-family:Arial;min-width:230px">
          <h4 style="margin-bottom:8px">{row['Zone_ID']}</h4>
          <b>Status:</b> {row['Status']}<br>
          <b>Temperature:</b> {row['Temperature_C']:.1f} °C<br>
          <b>Tree canopy:</b> {row['Tree_Cover_Pct']:.1f}%<br>
          <b>Priority score:</b> {row['Priority_Score']:.1f}/100<br>
          <hr style="margin:6px 0">
          <b>Suggested next step:</b><br>{row['Recommended_Action']}
        </div>
        """
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=7 if row["Status"] == "Critical plantation priority" else 5,
            color=color,
            weight=1,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            tooltip=(
                f"{row['Zone_ID']} | {row['Status']} | "
                f"{row['Temperature_C']:.1f} °C"
            ),
            popup=folium.Popup(popup_html, max_width=360),
        ).add_to(city_map)

    folium.LayerControl(collapsed=True).add_to(city_map)
    return city_map


# ---------------------------------- UI ----------------------------------------
st.title("🌳 Shade AI")
st.subheader("Urban Heat & Tree Canopy Prioritization")
st.markdown(
    "An **explainable decision-support prototype** that combines temperature "
    "and tree-canopy indicators to help prioritize areas for further urban "
    "greening assessment."
)

st.info(
    "Demo mode: all point locations, temperatures, and canopy percentages are "
    "synthetic. The app demonstrates the workflow and must not be interpreted "
    "as a live Chennai heat map or used as the sole basis for planting decisions."
)

with st.sidebar:
    st.header("⚙️ Analysis settings")
    temperature_threshold = st.slider(
        "High-temperature threshold (°C)",
        min_value=32.0,
        max_value=43.0,
        value=38.0,
        step=0.5,
        help="A configurable demo threshold, not a universal safety standard.",
    )
    canopy_threshold = st.slider(
        "Low-canopy threshold (%)",
        min_value=10.0,
        max_value=50.0,
        value=25.0,
        step=5.0,
        help="Zones below this canopy percentage may be prioritized if hot.",
    )
    show_heat_layer = st.checkbox("Show temperature intensity layer", value=False)
    show_only_priority = st.checkbox("Show only critical priority zones", value=False)
    st.caption("Classification uses transparent rules, not a trained ML model.")

raw_data = generate_demo_data()
df = add_decision_support_columns(
    raw_data,
    temperature_threshold=temperature_threshold,
    canopy_threshold=canopy_threshold,
)

critical_count = int((df["Status"] == "Critical plantation priority").sum())
monitor_count = int((df["Status"] == "Heat monitoring").sum())
lower_count = int((df["Status"] == "Lower current priority").sum())
critical_share = critical_count / len(df) * 100 if len(df) else 0

st.markdown("### 📊 City snapshot")
metric_cols = st.columns(4)
metric_cols[0].metric("Demo zones analyzed", f"{len(df):,}")
metric_cols[1].metric("Critical priority zones", f"{critical_count:,}", f"{critical_share:.1f}% of demo")
metric_cols[2].metric("Heat monitoring zones", f"{monitor_count:,}")
metric_cols[3].metric("Mean demo temperature", f"{df['Temperature_C'].mean():.1f} °C")

st.caption(
    f"Thresholds in effect: temperature ≥ {temperature_threshold:.1f} °C; "
    f"canopy < {canopy_threshold:.0f}%. Counts update when thresholds change."
)

left, right = st.columns([1.7, 1], gap="large")

with left:
    st.markdown("### 🗺️ Interactive priority map")
    city_map = build_map(df, show_heat_layer, show_only_priority)
    st_folium(city_map, width=None, height=560, key="shade_ai_map", returned_objects=[])

    legend_cols = st.columns(3)
    for col, (label, color) in zip(legend_cols, STATUS_COLORS.items()):
        col.markdown(
            f'<div style="display:flex;align-items:center;gap:8px">'
            f'<span style="display:inline-block;width:12px;height:12px;'
            f'border-radius:50%;background:{color}"></span>'
            f'<span style="font-size:0.85rem">{label}</span></div>',
            unsafe_allow_html=True,
        )

with right:
    st.markdown("### 💡 Decision-support insights")
    if critical_count:
        critical_df = df[df["Status"] == "Critical plantation priority"]
        top_zones = critical_df.sort_values(
            "Priority_Score", ascending=False
        ).head(5)
        st.warning(
            f"**{critical_count} demo zones** meet both the high-temperature "
            f"and low-canopy rules. Validate these locations with real data "
            f"before proposing interventions."
        )
        st.markdown("**Highest-scoring demo zones**")
        st.dataframe(
            top_zones[
                ["Zone_ID", "Temperature_C", "Tree_Cover_Pct", "Priority_Score"]
            ].rename(
                columns={
                    "Zone_ID": "Zone",
                    "Temperature_C": "Temp (°C)",
                    "Tree_Cover_Pct": "Canopy (%)",
                    "Priority_Score": "Score / 100",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success(
            "No demo zones meet both selected criteria. Consider reviewing "
            "thresholds or validating the assumptions against local data."
        )

    st.markdown("**How the rules work**")
    st.markdown(
        "- **Critical plantation priority:** temperature meets/exceeds the "
        "selected threshold and canopy is below the selected threshold.\n"
        "- **Heat monitoring:** temperature is high, but canopy is not below "
        "the selected threshold.\n"
        "- **Lower current priority:** temperature is below the selected threshold."
    )
    st.caption(
        "Priority score is a simple, unvalidated heuristic used to sort "
        "demo zones. It is not a scientific heat-risk index."
    )

st.markdown("---")
st.markdown("### 🔎 Explore and export zone-level results")

status_options = ["All statuses", *STATUS_COLORS.keys()]
selected_status = st.selectbox("Filter by classification", status_options)
min_score = st.slider("Minimum priority score", 0.0, 100.0, 0.0, 5.0)

filtered = df.copy()
if selected_status != "All statuses":
    filtered = filtered[filtered["Status"] == selected_status]
filtered = filtered[filtered["Priority_Score"] >= min_score]

display_cols = [
    "Zone_ID",
    "Temperature_C",
    "Tree_Cover_Pct",
    "Status",
    "Priority_Score",
    "Recommended_Action",
]
st.dataframe(
    filtered[display_cols].rename(
        columns={
            "Zone_ID": "Zone ID",
            "Temperature_C": "Temperature (°C)",
            "Tree_Cover_Pct": "Tree canopy (%)",
            "Priority_Score": "Priority score (/100)",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download filtered results (CSV)",
    data=csv_bytes,
    file_name="shade_ai_zone_priorities.csv",
    mime="text/csv",
)

st.markdown("### 🌱 Suggested implementation roadmap")
roadmap_cols = st.columns(3)
roadmap_cols[0].markdown(
    "**1. Validate data**\n\n"
    "Replace synthetic values with documented temperature observations, "
    "satellite-derived land-surface temperature, canopy estimates, and "
    "verified coordinates."
)
roadmap_cols[1].markdown(
    "**2. Improve prioritization**\n\n"
    "Add population vulnerability, land ownership, water availability, "
    "native species suitability, utilities, and planting feasibility."
)
roadmap_cols[2].markdown(
    "**3. Measure outcomes**\n\n"
    "Track canopy growth, shade access, maintenance, and before/after "
    "temperature indicators with clear data provenance."
)

with st.expander("ℹ️ Methodology, limitations & responsible use"):
    st.markdown(
        "- This is a prototype using reproducible synthetic data.\n"
        "- The rule engine is explainable but is not machine learning and has "
        "not been scientifically validated.\n"
        "- Temperature and canopy thresholds are user-configurable assumptions, "
        "not official health or planning standards.\n"
        "- Real-world use requires data-quality checks, coordinate validation, "
        "local ecological expertise, community input, and human review.\n"
        "- A canopy percentage alone does not establish whether a location is "
        "safe, accessible, or suitable for tree planting."
    )

st.caption(
    "Shade AI | Portfolio prototype • SDG 11: Sustainable Cities and Communities "
    "• SDG 13: Climate Action • SDG 15: Life on Land"
)
