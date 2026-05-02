import streamlit as st
import pandas as pd
import plotly.express as px

# Set up the page
st.set_page_config(page_title="Bengal Election 2026: Friction Model", layout="wide")
st.title("West Bengal 2026: 'Ground Reality' Friction Model")
st.markdown("Adjust the variables below to simulate how the 'Urban Aspiration' vs 'Rural Anchor' affects the final seat tally.")

# --- SIDEBAR: INPUT CONTROLS ---
st.sidebar.header("Model Variables")

gen_z_bjp = st.sidebar.slider(
    "Urban Gen Z Vote for BJP (%)", 
    min_value=40, max_value=90, value=80, step=5,
    help="Default is 80%. Higher values lower the friction in urban seats."
)

rural_friction = st.sidebar.slider(
    "TMC Rural Firewall / 'Anti-SIR' Factor (%)", 
    min_value=40, max_value=90, value=60, step=5,
    help="Default is 60%. Represents the % of rural seats impenetrable by BJP swings."
)

left_leakage = st.sidebar.slider(
    "Left/Congress Vote Recovery (%)", 
    min_value=0, max_value=15, value=5, step=1,
    help="Votes returning to the Left, mostly draining from the BJP's 2021 pool."
)

bjp_swing = st.sidebar.slider(
    "Baseline BJP Vote Swing from 2021 (%)", 
    min_value=-5.0, max_value=12.0, value=3.5, step=0.5
)

# --- MATHEMATICAL ENGINE ---
TOTAL_URBAN_SEATS = 110
TOTAL_RURAL_SEATS = 184

base_bjp_urban = 35
base_tmc_urban = 75
base_bjp_rural = 42
base_tmc_rural = 140
others_base_seats = 2

# Calculate Urban
urban_shift = max(0, (gen_z_bjp - 50) / 5) * 4
bjp_urban_final = min(TOTAL_URBAN_SEATS, base_bjp_urban + urban_shift)
tmc_urban_final = TOTAL_URBAN_SEATS - bjp_urban_final

# Calculate Rural
rural_swing_impact = (bjp_swing * 3) * ((100 - rural_friction) / 100)
bjp_rural_final = base_bjp_rural + rural_swing_impact

# Apply Left Leakage
bjp_rural_final -= (left_leakage / 2) * 3
tmc_rural_final = TOTAL_RURAL_SEATS - bjp_rural_final - others_base_seats

bjp_final = max(0, int(bjp_urban_final + bjp_rural_final))
tmc_final = max(0, int(tmc_urban_final + tmc_rural_final))
others_final = 294 - bjp_final - tmc_final

bjp_vote_share = 38.1 + bjp_swing - (left_leakage * 0.7)
tmc_vote_share = 47.9 - (bjp_swing * 0.5) - (left_leakage * 0.3)
others_vote_share = 100 - bjp_vote_share - tmc_vote_share

# --- MAIN DASHBOARD DISPLAY ---
col1, col2, col3 = st.columns(3)
col1.metric("TMC Projected Seats", tmc_final, f"{tmc_final - 213} from 2021")
col2.metric("BJP Projected Seats", bjp_final, f"+{bjp_final - 77} from 2021")
col3.metric("Others Projected Seats", others_final)

st.divider()

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Seat Distribution")
    df_seats = pd.DataFrame({
        "Party": ["TMC", "BJP", "Others"],
        "Seats": [tmc_final, bjp_final, others_final]
    })
    fig_seats = px.bar(df_seats, x="Party", y="Seats", color="Party", 
                       color_discrete_map={"TMC": "green", "BJP": "orange", "Others": "red"},
                       text="Seats")
    fig_seats.add_hline(y=148, line_dash="dash", line_color="black", annotation_text="Majority Mark (148)")
    st.plotly_chart(fig_seats, use_container_width=True)

with col_chart2:
    st.subheader("Projected Vote Share (%)")
    df_votes = pd.DataFrame({
        "Party": ["TMC", "BJP", "Others"],
        "Vote Share": [tmc_vote_share, bjp_vote_share, others_vote_share]
    })
    fig_votes = px.pie(df_votes, values="Vote Share", names="Party", 
                       color="Party", color_discrete_map={"TMC": "green", "BJP": "orange", "Others": "red"})
    st.plotly_chart(fig_votes, use_container_width=True)

st.markdown("### Analysis")
if bjp_final >= 148:
    st.success("Verdict: The 'Saffron Wave' overcomes the friction. BJP secures a majority.")
elif tmc_final >= 148:
    st.info("Verdict: The 'Ground Reality' model holds. TMC's rural firewall secures the state despite urban losses.")
else:
    st.warning("Verdict: Hung Assembly. The 'Left Leakage' has acted as a spoiler for both major parties.")
