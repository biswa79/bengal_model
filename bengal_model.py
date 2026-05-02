import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Bengal 2026 War Room", layout="wide")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    df = pd.read_csv('constituencies.csv')
    
    # 1. Ensure numeric data for calculations
    cols_to_numeric = ['BJP_Votes_2021', 'TMC_Votes_2021', 'BJP_Vote_Share_2021']
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # 2. Ensure simulation columns exist
    if 'Muslim_Base_Score' not in df.columns: df['Muslim_Base_Score'] = 0.5
    if 'Matua_Base_Score' not in df.columns: df['Matua_Base_Score'] = 0.5
    if 'Muslim_Base' not in df.columns: df['Muslim_Base'] = 0.2
    if 'Matua_Base' not in df.columns: df['Matua_Base'] = 0.1
    return df

df = load_data()

# --- SIDEBAR: CONTROLS ---
st.sidebar.header("Navigation & Settings")
tab_selection = st.sidebar.radio("View", ["2021 Historical Analysis", "2026 Simulation"])

# --- TAB 1: 2021 HISTORICAL ANALYSIS ---
if tab_selection == "2021 Historical Analysis":
    st.title("2021 Historical Reality")
    
    dist_summary = df.groupby('District').agg({
        'BJP_Votes_2021': 'sum',
        'TMC_Votes_2021': 'sum'
    }).reset_index()
    
    dist_summary['Winner'] = dist_summary.apply(
        lambda x: 'BJP' if x['BJP_Votes_2021'] > x['TMC_Votes_2021'] else 'TMC', axis=1
    )
    
    st.subheader("District-wise Tally (2021)")
    st.table(dist_summary)
    
    st.subheader("BJP Vote Share Distribution (2021)")
    # Create copy for brackets to avoid SettingWithCopyWarning
    df_plot = df.copy()
    df_plot['BJP_Bracket'] = pd.cut(df_plot['BJP_Vote_Share_2021'] * 100, bins=[0, 20, 30, 40, 50, 100])
    
    # Process for plotting
    bracket_counts = df_plot['BJP_Bracket'].value_counts().sort_index().reset_index()
    bracket_counts.columns = ['Bracket', 'Count']
    
    fig = px.bar(bracket_counts, x='Bracket', y='Count', title="BJP Vote Share Brackets (2021)")
    st.plotly_chart(fig)

# --- TAB 2: 2026 SIMULATION ---
else:
    st.title("2026 War Room Simulation")
    
    # Sidebar Sliders
    st.sidebar.header("Global Sentiment")
    muslim_swing = st.sidebar.slider("Muslim Segment Swing (+/- %)", -10.0, 10.0, 0.0, step=0.5)
    matua_swing = st.sidebar.slider("Matua Segment Swing (+/- %)", -10.0, 10.0, 0.0, step=0.5)
    
    st.sidebar.divider()
    selected_ac = st.sidebar.selectbox("Select Seat to Fine-Tune", df['AC_Name'].unique())
    ac_row = df[df['AC_Name'] == selected_ac].iloc[0]
    
    new_m = st.sidebar.slider("Local Muslim Support Override", 0.0, 1.0, float(ac_row['Muslim_Base_Score']), key=f"m_{selected_ac}")
    new_ma = st.sidebar.slider("Local Matua Support Override", 0.0, 1.0, float(ac_row['Matua_Base_Score']), key=f"ma_{selected_ac}")
    
    # Calculate Projection
    df_sim = df.copy()
    df_sim.loc[df_sim['AC_Name'] == selected_ac, 'Muslim_Base_Score'] = new_m
    df_sim.loc[df_sim['AC_Name'] == selected_ac, 'Matua_Base_Score'] = new_ma
    
    df_sim['BJP_Projected'] = ((df_sim['Muslim_Base'] * (df_sim['Muslim_Base_Score'] + (muslim_swing/100))) +
                               (df_sim['Matua_Base'] * (df_sim['Matua_Base_Score'] + (matua_swing/100)))) * 100 
    df_sim['Winner'] = df_sim['BJP_Projected'].apply(lambda x: 'BJP' if x > 50 else 'TMC')

    # DASHBOARD VIEW
    # 1. ASSEMBLY PIE CHART
    st.subheader(f"Assembly View: {selected_ac}")
    ac_val = df_sim[df_sim['AC_Name'] == selected_ac]['BJP_Projected'].iloc[0]
    ac_pie_df = pd.DataFrame({'Party': ['BJP', 'TMC/Others'], 'Votes': [ac_val, 100-ac_val]})
    
    fig_ac = px.pie(ac_pie_df, values='Votes', names='Party', title=f"Vote Share Projection: {selected_ac}",
                    color='Party', color_discrete_map={'BJP': 'orange', 'TMC/Others': 'green'})
    st.plotly_chart(fig_ac)

    st.markdown("---")
    
    # 2. STATE AGGREGATE VIEW
    st.subheader("State-Wide Aggregate (294 Seats)")
    col1, col2, col3 = st.columns(3)
    col1.metric("BJP Seats", int((df_sim['Winner'] == 'BJP').sum()))
    col2.metric("TMC Seats", int((df_sim['Winner'] == 'TMC').sum()))
    
    seat_tally = df_sim['Winner'].value_counts().reset_index()
    seat_tally.columns = ['Winner', 'Count']
    
    fig_state = px.pie(seat_tally, values='Count', names='Winner', title="Projected Seat Tally (294 Seats)",
                       color='Winner', color_discrete_map={"BJP": "orange", "TMC": "green"})
    st.plotly_chart(fig_state)
