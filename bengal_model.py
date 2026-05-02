import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Bengal 2026: Master War Room", layout="wide")

# --- 1. DATA INITIALIZATION ---
@st.cache_data
def load_data():
    df = pd.read_csv('constituencies.csv')
    # Ensure numeric columns
    cols = ['Muslim_Base_Score', 'Matua_Base_Score', 'Muslim_Base', 'Matua_Base']
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

# Initialize Session State
if 'df_sim' not in st.session_state:
    st.session_state.df_sim = load_data()

# Helper: Simulation Logic
def calculate_simulation(df):
    # Logic: Projected BJP Vote Share
    df['BJP_Projected'] = ((df['Muslim_Base'] * df['Muslim_Base_Score']) + 
                           (df['Matua_Base'] * df['Matua_Base_Score'])) * 100
    df['Winner'] = df['BJP_Projected'].apply(lambda x: 'BJP' if x > 50 else 'TMC')
    return df

# Ensure current state is calculated
st.session_state.df_sim = calculate_simulation(st.session_state.df_sim)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["War Room (Aggregate 2026)", "Constituency (Input/Sim)", "District-wise Breakdown (2026)"])

# --- TAB 1: WAR ROOM ---
with tab1:
    st.title("Aggregate 2026 Projection")
    df_agg = st.session_state.df_sim
    
    col1, col2, col3 = st.columns(3)
    bjp_seats = int((df_agg['Winner'] == 'BJP').sum())
    tmc_seats = int((df_agg['Winner'] == 'TMC').sum())
    
    col1.metric("Projected BJP Seats", bjp_seats)
    col2.metric("Projected TMC Seats", tmc_seats)
    col3.metric("Lead Margin", bjp_seats - tmc_seats)
    
    fig_state = px.pie(df_agg['Winner'].value_counts().reset_index(), 
                       values='count', names='Winner', title="State-wide Seat Share",
                       color='Winner', color_discrete_map={"BJP": "orange", "TMC": "green"})
    st.plotly_chart(fig_state, use_container_width=True)

# --- TAB 2: CONSTITUENCY SIMULATION ---
with tab2:
    st.title("Constituency-Level Tuning")
    selected_ac = st.selectbox("Select Seat to Simulate", st.session_state.df_sim['AC_Name'].unique())
    
    # Get index
    idx = st.session_state.df_sim[st.session_state.df_sim['AC_Name'] == selected_ac].index[0]
    
    # Sliders
    col_a, col_b = st.columns(2)
    new_m = col_a.slider("Muslim Support Override", 0.0, 1.0, float(st.session_state.df_sim.at[idx, 'Muslim_Base_Score']))
    new_ma = col_b.slider("Matua Support Override", 0.0, 1.0, float(st.session_state.df_sim.at[idx, 'Matua_Base_Score']))
    
    # Update state immediately
    st.session_state.df_sim.at[idx, 'Muslim_Base_Score'] = new_m
    st.session_state.df_sim.at[idx, 'Matua_Base_Score'] = new_ma
    st.session_state.df_sim = calculate_simulation(st.session_state.df_sim)
    
    # Local Visualization
    st.subheader(f"Projection for {selected_ac}")
    ac_val = st.session_state.df_sim.at[idx, 'BJP_Projected']
    fig_ac = px.pie(values=[ac_val, 100-ac_val], names=['BJP', 'TMC/Others'], 
                    title=f"Vote Share: {selected_ac}", color_discrete_map={'BJP': 'orange', 'TMC/Others': 'green'})
    st.plotly_chart(fig_ac)

# --- TAB 3: DISTRICT-WISE BREAKDOWN ---
with tab3:
    st.title("District-wise Projections (2026)")
    
    districts = sorted(st.session_state.df_sim['District'].unique())
    
    # Layout logic: 3 pie charts per row
    cols = st.columns(3)
    for i, district in enumerate(districts):
        dist_df = st.session_state.df_sim[st.session_state.df_sim['District'] == district]
        winner_counts = dist_df['Winner'].value_counts().reset_index()
        winner_counts.columns = ['Winner', 'Count']
        
        fig = px.pie(winner_counts, values='Count', names='Winner', title=f"{district}",
                     color='Winner', color_discrete_map={"BJP": "orange", "TMC": "green"})
        fig.update_layout(showlegend=False) # Keep clean
        
        with cols[i % 3]:
            st.plotly_chart(fig, use_container_width=True)
