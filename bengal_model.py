import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Bengal 2026 War Room", layout="wide")

st.title("West Bengal 2026: War Room Simulator")

# --- INITIALIZATION ---
if 'overrides' not in st.session_state:
    st.session_state.overrides = {}

# --- DATA LOADING ---
@st.cache_data
def load_data():
    if not os.path.exists('constituencies.csv'):
        st.error("Missing 'constituencies.csv'. Ensure it is in the same directory.")
        return None
    return pd.read_csv('constituencies.csv')

df = load_data()

if df is not None:
    # --- GLOBAL SENTIMENT ENGINE ---
    st.sidebar.header("Statewide sentiment")
    
    # Global Sliders
    muslim_swing = st.sidebar.slider("Muslim Segment Swing (+/- %)", -10.0, 10.0, 0.0, step=0.5)
    matua_swing = st.sidebar.slider("Matua Segment Swing (+/- %)", -10.0, 10.0, 0.0, step=0.5)
    
    # --- SEAT-SPECIFIC TUNING ---
    st.sidebar.divider()
    st.sidebar.subheader("Seat-Specific Tuning")
    selected_ac = st.sidebar.selectbox("Select Seat to Fine-Tune", df['AC_Name'].unique())
    
    # Override logic
    ac_row = df[df['AC_Name'] == selected_ac].iloc[0]
    
    st.sidebar.markdown(f"**Adjusting: {selected_ac}**")
    
    # Local Override Sliders
    new_m = st.sidebar.slider("Local Muslim Support Override", 0.0, 1.0, float(ac_row['Muslim_Base_Score']), key=f"m_{selected_ac}")
    new_ma = st.sidebar.slider("Local Matua Support Override", 0.0, 1.0, float(ac_row['Matua_Base_Score']), key=f"ma_{selected_ac}")
    
    # Apply overrides
    df.loc[df['AC_Name'] == selected_ac, 'Muslim_Base_Score'] = new_m
    df.loc[df['AC_Name'] == selected_ac, 'Matua_Base_Score'] = new_ma
    
    if st.sidebar.button("Reset All Overrides"):
        st.session_state.overrides = {}
        st.rerun()

    # --- CALCULATION ENGINE ---
    # Formula: (Base * BaseScore) + Global Swing
    df['BJP_Projected'] = (
        (df['Muslim_Base'] * (df['Muslim_Base_Score'] + (muslim_swing/100))) +
        (df['Matua_Base'] * (df['Matua_Base_Score'] + (matua_swing/100)))
    ) * 100 
    
    df['Winner'] = df['BJP_Projected'].apply(lambda x: 'BJP' if x > 50 else 'TMC')

    # --- DASHBOARD VIEW ---
    col1, col2, col3 = st.columns(3)
    col1.metric("BJP Projected Seats", (df['Winner'] == 'BJP').sum())
    col2.metric("TMC Projected Seats", (df['Winner'] == 'TMC').sum())
    col3.metric("Lead Margin", (df['Winner'] == 'BJP').sum() - (df['Winner'] == 'TMC').sum())

    # Visualization
    fig = px.bar(df, x="AC_Name", y="BJP_Projected", color="Winner", 
                 color_discrete_map={"BJP": "orange", "TMC": "green"},
                 title="Projected Vote Share by Constituency")
    st.plotly_chart(fig, use_container_width=True)

    # Table
    st.dataframe(df[['AC_No', 'AC_Name', 'BJP_Projected', 'Winner']])
