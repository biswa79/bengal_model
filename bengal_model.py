import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Bengal 2026 War Room", layout="wide")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    # Ensure 'constituencies.csv' exists in the folder
    df = pd.read_csv('constituencies.csv')
    
    # 1. Ensure columns exist for the simulation math
    # We initialize these with defaults so the app doesn't crash if they are missing
    required_cols = {
        'Muslim_Base_Score': 0.5,
        'Matua_Base_Score': 0.5,
        'Muslim_Base': 0.2,  # Default % if not in data
        'Matua_Base': 0.1    # Default % if not in data
    }
    
    for col, default_val in required_cols.items():
        if col not in df.columns:
            df[col] = default_val
            
    return df

df = load_data()

# --- SIDEBAR: CONTROLS ---
st.sidebar.header("Navigation & Settings")
tab_selection = st.sidebar.radio("View", ["2021 Historical Analysis", "2026 Simulation"])

# --- TAB 1: 2021 HISTORICAL ANALYSIS ---
if tab_selection == "2021 Historical Analysis":
    st.title("2021 Historical Reality")
    
    # District-wise aggregation
    dist_summary = df.groupby('District').agg({
        'BJP_Votes_2021': 'sum',
        'TMC_Votes_2021': 'sum'
    }).reset_index()
    
    dist_summary['Winner'] = dist_summary.apply(
        lambda x: 'BJP' if x['BJP_Votes_2021'] > x['TMC_Votes_2021'] else 'TMC', axis=1
    )
    
    st.subheader("District-wise Tally (2021)")
    st.table(dist_summary)
    
    st.subheader("Vote Share Distribution (2021)")
    # Basic check to avoid errors if column is missing or empty
    if 'BJP_Vote_Share_2021' in df.columns:
        df['BJP_Bracket'] = pd.cut(df['BJP_Vote_Share_2021'] * 100, bins=[0, 20, 30, 40, 50, 100])
        fig = px.bar(df['BJP_Bracket'].value_counts().sort_index(), title="BJP Vote Share Brackets (2021)")
        st.plotly_chart(fig)

# --- TAB 2: 2026 SIMULATION ---
else:
    st.title("2026 War Room Simulation")
    
    # Global Sentiment Overrides
    st.sidebar.header("Global Sentiment")
    muslim_swing = st.sidebar.slider("Muslim Segment Swing (+/- %)", -10.0, 10.0, 0.0, step=0.5)
    matua_swing = st.sidebar.slider("Matua Segment Swing (+/- %)", -10.0, 10.0, 0.0, step=0.5)
    
    st.sidebar.divider()
    st.sidebar.subheader("Seat-Specific Tuning")
    selected_ac = st.sidebar.selectbox("Select Seat to Fine-Tune", df['AC_Name'].unique())
    
    ac_row = df[df['AC_Name'] == selected_ac].iloc[0]
    
    st.sidebar.markdown(f"**Adjusting: {selected_ac}**")
    
    # Sliders bound to the specific constituency
    new_m = st.sidebar.slider(
        "Local Muslim Support Override", 0.0, 1.0, 
        float(ac_row['Muslim_Base_Score']), key=f"m_{selected_ac}"
    )
    new_ma = st.sidebar.slider(
        "Local Matua Support Override", 0.0, 1.0, 
        float(ac_row['Matua_Base_Score']), key=f"ma_{selected_ac}"
    )
    
    # Calculation Logic
    df_sim = df.copy()
    
    # Apply the overrides from the sliders
    df_sim.loc[df_sim['AC_Name'] == selected_ac, 'Muslim_Base_Score'] = new_m
    df_sim.loc[df_sim['AC_Name'] == selected_ac, 'Matua_Base_Score'] = new_ma
    
    # Apply calculation
    df_sim['BJP_Projected'] = (
        (df_sim['Muslim_Base'] * (df_sim['Muslim_Base_Score'] + (muslim_swing/100))) +
        (df_sim['Matua_Base'] * (df_sim['Matua_Base_Score'] + (matua_swing/100)))
    ) * 100 
    
    df_sim['Winner'] = df_sim['BJP_Projected'].apply(lambda x: 'BJP' if x > 50 else 'TMC')

    # Dashboard View
    col1, col2, col3 = st.columns(3)
    col1.metric("BJP Seats", int((df_sim['Winner'] == 'BJP').sum()))
    col2.metric("TMC Seats", int((df_sim['Winner'] == 'TMC').sum()))
    col3.metric("Lead Margin", int((df_sim['Winner'] == 'BJP').sum() - (df_sim['Winner'] == 'TMC').sum()))

    fig = px.bar(df_sim, x="AC_Name", y="BJP_Projected", color="Winner", 
                 color_discrete_map={"BJP": "orange", "TMC": "green"},
                 title="Projected Vote Share by Constituency")
    st.plotly_chart(fig, use_container_width=True)
