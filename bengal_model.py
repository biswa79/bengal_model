import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Bengal 2026: Micro-Segmentation Model", layout="wide")
st.title("West Bengal 2026: Micro-Segmentation Dashboard")

# --- SIDEBAR: CATEGORIZED INPUTS ---
st.sidebar.header("Micro-Segmentation")

with st.sidebar.expander("Youth & Employment"):
    u_genz = st.slider("Urban Gen Z Support for BJP (%)", 0, 100, 75)
    r_genz = st.slider("Rural Gen Z Support for BJP (%)", 0, 100, 45)
    u_youth_unemp = st.slider("Unemployed Urban Youth Support (%)", 0, 100, 70)
    r_youth_unemp = st.slider("Unemployed Rural Youth Support (%)", 0, 100, 50)

with st.sidebar.expander("Gender & Welfare"):
    u_lady_unmar = st.slider("Urban Unmarried Lady Support (%)", 0, 100, 40)
    r_lady_unmar = st.slider("Rural Unmarried Lady Support (%)", 0, 100, 30)
    r_lady_rem = st.slider("Rural Remaining Lady Support (%)", 0, 100, 25)

with st.sidebar.expander("Geography & Demographics"):
    u_muni = st.slider("Municipality Urban Support (%)", 0, 100, 60)
    kolkata = st.slider("Kolkata Support (%)", 0, 100, 40)
    muslim = st.slider("Muslim Segment Support (%)", 0, 100, 5)
    sikh = st.slider("Sikh Segment Support (%)", 0, 100, 70)
    gujarati = st.slider("Gujarati Segment Support (%)", 0, 100, 85)
    marwari = st.slider("Marwari Segment Support (%)", 0, 100, 80)
    up_bihar = st.slider("UP/Bihar Non-Bengali Support (%)", 0, 100, 75)

# --- ENGINE: WEIGHTED SUM CALCULATOR ---
# We assign arbitrary weights (importance) to each segment
weights = {
    "u_genz": 0.08, "r_genz": 0.10, "u_youth_unemp": 0.05, "r_youth_unemp": 0.07,
    "u_lady_unmar": 0.04, "r_lady_unmar": 0.08, "r_lady_rem": 0.15,
    "u_muni": 0.08, "kolkata": 0.05, "muslim": 0.20, "sikh": 0.01,
    "gujarati": 0.01, "marwari": 0.03, "up_bihar": 0.05
}

# Calculate final BJP Support % (Weighted Average)
bjp_support = (
    (u_genz * weights["u_genz"]) + (r_genz * weights["r_genz"]) + 
    (u_youth_unemp * weights["u_youth_unemp"]) + (r_youth_unemp * weights["r_youth_unemp"]) +
    (u_lady_unmar * weights["u_lady_unmar"]) + (r_lady_unmar * weights["r_lady_unmar"]) +
    (r_lady_rem * weights["r_lady_rem"]) + (u_muni * weights["u_muni"]) +
    (kolkata * weights["kolkata"]) + (muslim * weights["muslim"]) +
    (sikh * weights["sikh"]) + (gujarati * weights["gujarati"]) +
    (marwari * weights["marwari"]) + (up_bihar * weights["up_bihar"])
)

# Predict Seats (Simplified linear scaling)
# Base: 40% support = 148 seats.
seats_bjp = int(148 * (bjp_support / 40))
seats_tmc = 294 - seats_bjp

# --- DASHBOARD UI ---
col1, col2 = st.columns(2)
col1.metric("Projected BJP Seats", seats_bjp)
col2.metric("Projected TMC Seats", seats_tmc)

df = pd.DataFrame({"Party": ["BJP", "TMC"], "Seats": [seats_bjp, seats_tmc]})
fig = px.bar(df, x="Party", y="Seats", color="Party", color_discrete_map={"BJP": "orange", "TMC": "green"})
st.plotly_chart(fig, use_container_width=True)
