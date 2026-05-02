import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Bengal 2026: Master War Room", layout="wide")
st.title("West Bengal 2026: Master War Room Dashboard")

# --- 1. ROBUST DATA LOADING ---
@st.cache_data
def load_data():
    df = pd.read_csv('constituencies.csv')
    
    # Define required columns and default values to prevent KeyErrors
    required_cols = {
        'Muslim_Base': 0.2,
        'Matua_Base': 0.1,
        'Muslim_Base_Score': 0.5,
        'Matua_Base_Score': 0.5,
        'BJP_Votes_2021': 0,
        'TMC_Votes_2021': 0
    }
    
    # Automatically add missing columns
    for col, default_val in required_cols.items():
        if col not in df.columns:
            df[col] = default_val
            
    # Ensure numeric types
    for col in required_cols.keys():
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(required_cols[col])
        
    return df

# Initialize Session State
if 'df_sim' not in st.session_state:
    st.session_state.df_sim = load_data()
else:
    # Check if session state is stale/missing columns
    if 'Muslim_Base' not in st.session_state.df_sim.columns:
        st.session_state.df_sim = load_data()

# Simulation Logic
def calculate_simulation(df):
    df['BJP_Projected'] = ((df['Muslim_Base'] * df['Muslim_Base_Score']) + 
                           (df['Matua_Base'] * df['Matua_Base_Score'])) * 100
    df['Winner'] = df['BJP_Projected'].apply(lambda x: 'BJP' if x > 50 else 'TMC')
    return df

# Ensure current state is calculated
st.session_state.df_sim = calculate_simulation(st.session_state.df_sim)

# --- 2. SIDEBAR (GLOBAL INPUTS) ---
st.sidebar.header("Global Calibration")
with st.sidebar.expander("Population Distribution"):
    weights_input = {
        "Muslim": st.number_input("Muslim %", 0, 100, 27),
        "Rural Remaining": st.number_input("Rural Remaining %", 0, 100, 18),
        "Muni Urban": st.number_input("Municipality Urban %", 0, 100, 8),
        # ... Add other fields as needed ...
    }

st.sidebar.header("Sentiment & Identity")
with st.sidebar.expander("Sentiment (BJP Support %)"):
    # Note: These sentiments can be integrated into your calculate_simulation if needed
    st.slider("Muslim Support %", 0, 100, 5)
    st.slider("Rural Remaining Support %", 0, 100, 30)

# --- 3. TABS ---
tab1, tab2, tab3 = st.tabs(["War Room (Aggregate)", "Constituency (Input/Sim)", "District-wise Breakdown"])

# --- TAB 1: WAR ROOM ---
with tab1:
    st.header("Aggregate 2026 Projection")
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
    st.header("Constituency-Level Tuning")
    selected_ac = st.selectbox("Select Seat to Simulate", st.session_state.df_sim['AC_Name'].unique())
    
    idx = st.session_state.df_sim[st.session_state.df_sim['AC_Name'] == selected_ac].index[0]
    
    col_a, col_b = st.columns(2)
    new_m = col_a.slider("Muslim Support Override", 0.0, 1.0, float(st.session_state.df_sim.at[idx, 'Muslim_Base_Score']))
    new_ma = col_b.slider("Matua Support Override", 0.0, 1.0, float(st.session_state.df_sim.at[idx, 'Matua_Base_Score']))
    
    # Update state immediately
    st.session_state.df_sim.at[idx, 'Muslim_Base_Score'] = new_m
    st.session_state.df_sim.at[idx, 'Matua_Base_Score'] = new_ma
    st.session_state.df_sim = calculate_simulation(st.session_state.df_sim)
    
    st.subheader(f"Projection for {selected_ac}")
    ac_val = st.session_state.df_sim.at[idx, 'BJP_Projected']
    fig_ac = px.pie(values=[ac_val, 100-ac_val], names=['BJP', 'TMC/Others'], 
                    title=f"Vote Share: {selected_ac}", color_discrete_map={'BJP': 'orange', 'TMC/Others': 'green'})
    st.plotly_chart(fig_ac)

# --- TAB 3: DISTRICT-WISE BREAKDOWN ---
with tab3:
    st.header("District-wise Projections (2026)")
    
    districts = sorted(st.session_state.df_sim['District'].unique())
    cols = st.columns(3)
    
    for i, district in enumerate(districts):
        dist_df = st.session_state.df_sim[st.session_state.df_sim['District'] == district]
        winner_counts = dist_df['Winner'].value_counts().reset_index()
        winner_counts.columns = ['Winner', 'Count']
        
        fig = px.pie(winner_counts, values='Count', names='Winner', title=f"{district}",
                     color='Winner', color_discrete_map={"BJP": "orange", "TMC": "green"})
        fig.update_layout(showlegend=False)
        
        with cols[i % 3]:
            st.plotly_chart(fig, use_container_width=True)
