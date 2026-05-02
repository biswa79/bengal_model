import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Bengal 2026: Pro Model", layout="wide")
st.title("West Bengal 2026: Dynamic Segmentation Model")

# --- SIDEBAR: DEMOGRAPHIC CALIBRATION ---
st.sidebar.header("Step 1: Demographic Weights")
st.sidebar.caption("Define the % of the total electorate for each group.")

with st.sidebar.expander("Configure Population Weights", expanded=True):
    w_u_genz = st.number_input("Urban Gen Z %", 0, 100, 8)
    w_r_genz = st.number_input("Rural Gen Z %", 0, 100, 10)
    w_u_youth_unemp = st.number_input("Unemp. Urban Youth %", 0, 100, 5)
    w_r_youth_unemp = st.number_input("Unemp. Rural Youth %", 0, 100, 7)
    w_u_lady_unmar = st.number_input("Urban Unmarried Lady %", 0, 100, 4)
    w_r_lady_unmar = st.number_input("Rural Unmarried Lady %", 0, 100, 8)
    w_r_lady_rem = st.number_input("Rural Remaining Lady %", 0, 100, 15)
    w_u_muni = st.number_input("Municipality Urban %", 0, 100, 8)
    w_kolkata = st.number_input("Kolkata %", 0, 100, 5)
    w_muslim = st.number_input("Muslim %", 0, 100, 20)
    w_sikh = st.number_input("Sikh %", 0, 100, 2)
    w_gujarati = st.number_input("Gujarati %", 0, 100, 2)
    w_marwari = st.number_input("Marwari %", 0, 100, 3)
    w_up_bihar = st.number_input("UP/Bihar Non-Bengali %", 0, 100, 3)

# Normalize weights
raw_weights = {
    "u_genz": w_u_genz, "r_genz": w_r_genz, "u_youth_unemp": w_u_youth_unemp, 
    "r_youth_unemp": w_r_youth_unemp, "u_lady_unmar": w_u_lady_unmar, 
    "r_lady_unmar": w_r_lady_unmar, "r_lady_rem": w_r_lady_rem, 
    "u_muni": w_u_muni, "kolkata": w_kolkata, "muslim": w_muslim, 
    "sikh": w_sikh, "gujarati": w_gujarati, "marwari": w_marwari, "up_bihar": w_up_bihar
}
total_weight = sum(raw_weights.values())
weights = {k: v / total_weight for k, v in raw_weights.items()}

# --- SIDEBAR: SENTIMENT INPUTS ---
st.sidebar.divider()
st.sidebar.header("Step 2: Sentiment (BJP Support %)")

with st.sidebar.expander("Sentiment Sliders"):
    u_genz = st.slider("Urban Gen Z Support %", 0, 100, 75)
    r_genz = st.slider("Rural Gen Z Support %", 0, 100, 45)
    u_youth_unemp = st.slider("Unemp. Urban Youth %", 0, 100, 70)
    r_youth_unemp = st.slider("Unemp. Rural Youth %", 0, 100, 50)
    u_lady_unmar = st.slider("Urban Unmarried Lady %", 0, 100, 40)
    r_lady_unmar = st.slider("Rural Unmarried Lady %", 0, 100, 30)
    r_lady_rem = st.slider("Rural Remaining Lady %", 0, 100, 25)
    u_muni = st.slider("Municipality Urban %", 0, 100, 60)
    kolkata = st.slider("Kolkata %", 0, 100, 40)
    muslim = st.slider("Muslim %", 0, 100, 5)
    sikh = st.slider("Sikh %", 0, 100, 70)
    gujarati = st.slider("Gujarati %", 0, 100, 85)
    marwari = st.slider("Marwari %", 0, 100, 80)
    up_bihar = st.slider("UP/Bihar Non-Bengali %", 0, 100, 75)

# --- ENGINE: CALCULATION ---
inputs = {
    "u_genz": u_genz, "r_genz": r_genz, "u_youth_unemp": u_youth_unemp, 
    "r_youth_unemp": r_youth_unemp, "u_lady_unmar": u_lady_unmar, 
    "r_lady_unmar": r_lady_unmar, "r_lady_rem": r_lady_rem, 
    "u_muni": u_muni, "kolkata": kolkata, "muslim": muslim, 
    "sikh": sikh, "gujarati": gujarati, "marwari": marwari, "up_bihar": up_bihar
}

bjp_support = sum(inputs[k] * weights[k] for k in weights)
seats_bjp = int(294 * (bjp_support / 100))
seats_tmc = 294 - seats_bjp

# --- DISPLAY ---
col1, col2 = st.columns(2)
col1.metric("Projected BJP Seats", seats_bjp)
col2.metric("Projected TMC Seats", seats_tmc)

df = pd.DataFrame({"Party": ["BJP", "TMC"], "Seats": [seats_bjp, seats_tmc]})
fig = px.bar(df, x="Party", y="Seats", color="Party", 
             color_discrete_map={"BJP": "orange", "TMC": "green"}, text="Seats")
st.plotly_chart(fig, use_container_width=True)

st.write(f"**Total Weight Check:** {total_weight}% (The model automatically normalizes this to 100%)")
