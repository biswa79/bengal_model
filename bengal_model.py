import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Bengal 2026: Master War Room", layout="wide")
st.title("West Bengal 2026: Master War Room Dashboard")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    # Ensure this matches your filename exactly
    df = pd.read_csv('constituencies.csv')
    
    # Ensure numeric columns are clean
    numeric_cols = ['BJP_Votes_2021', 'TMC_Votes_2021', 'Muslim_Base_Score', 'Matua_Base_Score', 'Muslim_Base', 'Matua_Base']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Add defaults if missing
    if 'Muslim_Base_Score' not in df.columns: df['Muslim_Base_Score'] = 0.5
    if 'Matua_Base_Score' not in df.columns: df['Matua_Base_Score'] = 0.5
    if 'Muslim_Base' not in df.columns: df['Muslim_Base'] = 0.2
    if 'Matua_Base' not in df.columns: df['Matua_Base'] = 0.1
    return df

df = load_data()

# --- GLOBAL SIDEBAR (PERSISTENT ACROSS TABS) ---
st.sidebar.header("1. Demographic Weights (%)")
with st.sidebar.expander("Population Distribution"):
    weights_input = {
        "Muslim": st.number_input("Muslim %", 0, 100, 27),
        "Rural Remaining": st.number_input("Rural Remaining %", 0, 100, 18),
        "Rural Gen Z": st.number_input("Rural Gen Z %", 0, 100, 10),
        "Muni Urban": st.number_input("Municipality Urban %", 0, 100, 8),
        "Rural Unmar. Lady": st.number_input("Rural Unmarried Lady %", 0, 100, 7),
        "Unemp. Rural Youth": st.number_input("Unemp. Rural Youth %", 0, 100, 6),
        "Urban Gen Z": st.number_input("Urban Gen Z %", 0, 100, 5),
        "Kolkata": st.number_input("Kolkata %", 0, 100, 5),
        "UP/Bihar Non-Bengali": st.number_input("UP/Bihar Non-Bengali %", 0, 100, 4),
        "Unemp. Urban Youth": st.number_input("Unemp. Urban Youth %", 0, 100, 4),
        "Marwari": st.number_input("Marwari %", 0, 100, 3),
        "Sikh": st.number_input("Sikh %", 0, 100, 1),
        "Gujarati": st.number_input("Gujarati %", 0, 100, 1),
        "Rural Unmar. Lady 2": st.number_input("Remaining Rural Lady %", 0, 100, 1)
    }

total_w = sum(weights_input.values())
weights = {k: v / total_w for k, v in weights_input.items()}

st.sidebar.header("2. Sentiment & Identity")
with st.sidebar.expander("Sentiment (BJP Support %)"):
    sentiments = {
        "Muslim": st.slider("Muslim Support %", 0, 100, 5),
        "Rural Remaining": st.slider("Rural Remaining Support %", 0, 100, 30),
        "Rural Gen Z": st.slider("Rural Gen Z Support %", 0, 100, 45),
        "Muni Urban": st.slider("Muni Urban Support %", 0, 100, 60),
        "Rural Unmar. Lady": st.slider("Rural Unmar. Lady Support %", 0, 100, 30),
        "Unemp. Rural Youth": st.slider("Unemp. Rural Youth Support %", 0, 100, 50),
        "Urban Gen Z": st.slider("Urban Gen Z Support %", 0, 100, 75),
        "Kolkata": st.slider("Kolkata Support %", 0, 100, 40),
        "UP/Bihar Non-Bengali": st.slider("UP/Bihar Non-Bengali Support %", 0, 100, 75),
        "Unemp. Urban Youth": st.slider("Unemp. Urban Youth Support %", 0, 100, 70),
        "Marwari": st.slider("Marwari Support %", 0, 100, 80),
        "Sikh": st.slider("Sikh Support %", 0, 100, 70),
        "Gujarati": st.slider("Gujarati Support %", 0, 100, 85),
        "Rural Unmar. Lady 2": st.slider("Remaining Lady Support %", 0, 100, 25)
    }

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["Master Model (Global)", "2021 Historical Analysis", "Constituency War Room"])

# --- TAB 1: MASTER MODEL ---
with tab1:
    matua_swing = st.slider("Matua Community Swing (+/- %)", -15, 15, 0)
    rajbanshi_swing = st.slider("Rajbanshi Community Swing (+/- %)", -15, 15, 0)

    bjp_base_support = sum(sentiments[k] * weights[k] for k in weights)
    bjp_final_support = bjp_base_support + matua_swing + rajbanshi_swing
    
    seats_bjp = int(294 * (bjp_final_support / 100))
    seats_tmc = 294 - seats_bjp
    
    col1, col2 = st.columns(2)
    col1.metric("Projected BJP Seats", seats_bjp)
    col2.metric("Projected TMC Seats", seats_tmc)
    
    df_chart = pd.DataFrame({"Party": ["BJP", "TMC"], "Seats": [seats_bjp, seats_tmc]})
    fig = px.bar(df_chart, x="Party", y="Seats", color="Party", 
                 color_discrete_map={"BJP": "orange", "TMC": "green"}, text="Seats")
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: 2021 HISTORICAL ANALYSIS ---
with tab2:
    st.title("2021 Historical Reality")
    df['Winner_2021'] = df.apply(lambda x: 'BJP' if x['BJP_Votes_2021'] > x['TMC_Votes_2021'] else 'TMC', axis=1)
    
    seat_counts = df['Winner_2021'].value_counts().reset_index()
    seat_counts.columns = ['Party', 'Count']
    
    st.subheader("State-wide Seat Share (2021)")
    fig_pie = px.pie(seat_counts, values='Count', names='Party', title="2021 Seat Distribution",
                     color='Party', color_discrete_map={"BJP": "orange", "TMC": "green"})
    st.plotly_chart(fig_pie)

# --- TAB 3: CONSTITUENCY WAR ROOM ---
with tab3:
    st.subheader("Seat-Specific Tuning")
    selected_ac = st.selectbox("Select Seat to Fine-Tune", df['AC_Name'].unique())
    ac_row = df[df['AC_Name'] == selected_ac].iloc[0]
    
    col_a, col_b = st.columns(2)
    new_m = col_a.slider("Local Muslim Support Override", 0.0, 1.0, float(ac_row['Muslim_Base_Score']), key=f"m_{selected_ac}")
    new_ma = col_b.slider("Local Matua Support Override", 0.0, 1.0, float(ac_row['Matua_Base_Score']), key=f"ma_{selected_ac}")
    
    df_sim = df.copy()
    df_sim.loc[df_sim['AC_Name'] == selected_ac, 'Muslim_Base_Score'] = new_m
    df_sim.loc[df_sim['AC_Name'] == selected_ac, 'Matua_Base_Score'] = new_ma
    
    df_sim['BJP_Projected'] = ((df_sim['Muslim_Base'] * df_sim['Muslim_Base_Score']) + (df_sim['Matua_Base'] * df_sim['Matua_Base_Score'])) * 100
    df_sim['Winner'] = df_sim['BJP_Projected'].apply(lambda x: 'BJP' if x > 50 else 'TMC')
    
    # 1. Assembly Pie
    ac_val = df_sim[df_sim['AC_Name'] == selected_ac]['BJP_Projected'].iloc[0]
    fig_ac = px.pie(values=[ac_val, 100-ac_val], names=['BJP', 'TMC/Others'], title=f"Projection: {selected_ac}")
    st.plotly_chart(fig_ac)
    
    # 2. State Pie
    seat_tally = df_sim['Winner'].value_counts().reset_index()
    seat_tally.columns = ['Winner', 'Count']
    fig_state = px.pie(seat_tally, values='Count', names='Winner', title="Projected State Seat Distribution")
    st.plotly_chart(fig_state)
