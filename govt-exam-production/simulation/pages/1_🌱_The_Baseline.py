import streamlit as st
import pandas as pd
import plotly.express as px
from simulation_engines.scenerio_1 import ExamEcosystem
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Scenario 1: Baseline",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS (Apple Style + Navbar) ----------------
st.markdown("""
    <style>
    /* 1. TYPOGRAPHY & LAYOUT */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1d1d1f; 
        background-color: #ffffff;
    }
    
    /* Center the main container text for readability */
    .block-container {
        max-width: 1100px; /* Slightly wider to accommodate sidebar + charts */
        padding-top: 4rem;
        padding-bottom: 5rem;
        margin: 0 auto;
    }

    /* 2. GLOBAL NAVBAR */
    .global-nav {
        position: fixed; top: 0; left: 0; width: 100vw; height: 50px;
        background-color: #000000; color: #f5f5f7; z-index: 99999;
        display: flex; align-items: center; justify-content: center;
        font-size: 14px; font-weight: 500;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .nav-links { display: flex; gap: 30px; }
    .nav-links a { color: #d1d1d1; text-decoration: none; transition: color 0.2s; }
    .nav-links a:hover { color: #ffffff; }

    /* 3. NARRATIVE STYLING */
    h1 { font-weight: 800; letter-spacing: -0.02em; font-size: 2.5rem; margin-bottom: 1rem; }
    h2 { font-weight: 700; font-size: 1.8rem; margin-top: 2rem; color: #1d1d1f; }
    h3 { font-weight: 600; font-size: 1.4rem; margin-top: 1.5rem; color: #333; }
    p, li { font-size: 1.05rem; line-height: 1.6; color: #333; }
    
    /* 4. CALLOUT BOXES */
    .analogy-box {
        background-color: #F5F5F7;
        border-left: 4px solid #0071e3;
        padding: 15px 20px;
        border-radius: 4px;
        margin: 20px 0;
        font-size: 0.95rem;
        color: #333;
    }
    .explainer-text {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 12px;
        font-size: 0.95rem;
        line-height: 1.6;
        border: 1px solid #eee;
    }
    
    /* HIDE DEFAULT HEADER LINE */
    [data-testid="stHeader"] {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---------------- INJECT NAVBAR ----------------
st.markdown("""
    <div class="global-nav">
        <div class="nav-links">
            <a href="/" target="_self">← Return Home</a>
            <span style="opacity:0.3">|</span>
            <span style="color:white">Scenario 1: Baseline</span>
            <span style="opacity:0.3">|</span>
            <a href="pages/2_🚀_The_Elite_Era.py" target="_self">Next Phase →</a>
        </div>
    </div>
""", unsafe_allow_html=True)


# ---------------- NARRATIVE SECTION ----------------
st.title("Scenario 1 - Baseline")

st.markdown("""
### Phase 1: The Baseline Model
**The Rules of the Game**

To understand a chaotic system, we must first look at it in a vacuum. Before we add complex policies or reservations, let’s look at the "Simple Case."

**The Setup**
Imagine a stadium with **2,000 aspirants** but only **50 seats**. The game is played annually. The rules are simple supply and demand. The supply of talent is endless, but the demand (seats) is rigid.
""")

st.info("💡 **Note:** You can change the number of seats and population in the sidebar to see what happens, but our standard observations are based on 2,000 population and 50 seats.")

st.markdown("---")

col_text1, col_text2 = st.columns(2, gap="large")

with col_text1:
    st.subheader("1. The Aspirant (Our Agent)")
    st.write("In this model, every student is defined by two invisible but decisive numbers:")
    
    st.markdown("""
    **🧠 Innate Talent (The Head Start):** Not everyone starts the race from the same line. In our code, this is modeled as a Normal Distribution (Bell Curve). Most are "Average." There are a few outliers who are brilliant (the "God-gifted") and a few who struggle.
    
    **⏳ Financial Runway (The Ticking Clock):** This is the brutal reality of exam preparation. How many years can you afford to sit at home and study without earning?
    * For some, this is 1 year (high pressure).
    * For others with generational wealth, this could be 5+ years.
    
    *The Logic: Every year you attempt the exam, your `financial_runway` decreases by 1. When it hits zero, you are forced to quit.*
    """)

with col_text2:
    st.subheader("2. The Mechanics of 'The Grind'")
    st.write("There is no attempt limit. You can take the exam as many times as you want, provided you can afford it.")
    
    st.markdown("""
    **The Learning Curve:** If you fail in Year 1, you don't reset to zero. You carry your knowledge to Year 2. In the simulation, retakers get a small `exp_boost` (Experience Boost).
    """)
    
    st.markdown("""
    <div class="analogy-box">
    <b>Real Life Analogy:</b><br>
    This is why a 3rd-year aspirant often scores higher than a fresher. They have "sharpened their axe" over three years.
    </div>
    """, unsafe_allow_html=True)

st.subheader("3. The Exit Doors")
st.write("How does an agent leave the system?")
st.markdown("""
* **Success:** They crack the top 50 ranks.
* **Financial Ruin:** Their runway hits 0. They must enter the workforce elsewhere.
* **Realization (The Soft Stop):** The code checks for "hopelessness." If an agent sees they are consistently failing to reach even the top 500 ranks for 3 years, they realize, "This isn't for me."
""")

st.markdown("---")


# ---------------- SIDEBAR (DYNAMIC CONTROLS) ----------------
st.sidebar.header("⚙️ System Parameters")
num_agents = st.sidebar.slider("Total Aspirants (Population)", 500, 5000, 2000, step=100)
top_n_seats = st.sidebar.slider("Available Seats", 10, 500, 50, step=10)
steps = st.sidebar.slider("Years to Simulate", 5, 50, 20)

st.sidebar.markdown("---")
st.sidebar.write("Last loaded:", time.strftime("%H:%M:%S"))


# ---------------- SIMULATION ENGINE ----------------
if st.button("▶️ Run Simulation", type="primary"):
    with st.spinner("Simulating ecosystem dynamics..."):

        model = ExamEcosystem(num_agents=num_agents, top_n_seats=top_n_seats)

        progress = st.progress(0)
        for i in range(steps):
            model.step()
            progress.progress((i + 1) / steps)

        # STORE RESULTS
        st.session_state["model"] = model
        st.session_state["model_df"] = model.datacollector.get_model_vars_dataframe()
        st.session_state["agent_df"] = (
            model.datacollector.get_agent_vars_dataframe().reset_index()
        )

# ---------------- GUARD: NO DATA ----------------
if "model_df" not in st.session_state:
    st.info("👈 Set your parameters and click **Run Simulation** to see the results.")
    st.stop()


# ---------------- VISUALIZATION & ANALYSIS ----------------
df = st.session_state["model_df"].copy()
agent_df = st.session_state["agent_df"].copy()
df["Year"] = df.index + 1

# 1. KPI CARDS
final_cutoff = df["Cutoff Score"].iloc[-1]
st.subheader(f"Final Cutoff Score: {final_cutoff:.2f} / 300")

# 2. CUTOFF TRAJECTORY (Side-by-Side with Explanation)
col_chart, col_explain = st.columns([2, 1], gap="medium")

with col_chart:
    st.markdown("**📈 The Rising Bar (Cutoff Scores)**")
    fig_cutoff = px.line(
        df, x="Year", y="Cutoff Score",
        markers=True,
        color_discrete_sequence=["#00CC96"]
    )
    fig_cutoff.add_hline(y=300, line_dash="dot", annotation_text="Max Score (300)")
    fig_cutoff.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_cutoff, use_container_width=True)

with col_explain:
    st.markdown("""
    <div class="explainer-text">
    <b>Why the flatline?</b><br><br>
    The graph shows a sharp spike followed by a plateau.<br><br>
    <b>Phase 1 (The Spike):</b> No one quits yet. Students who fail simply study harder. The group gets "smarter" together.<br><br>
    <b>Phase 2 (The Plateau):</b> A "revolving door" opens. Veterans who struggled too long finally exit, replaced by freshers. The experience leaving equals the new talent entering, creating a natural limit.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 3. MICRO ANALYSIS (Bell Curve)
st.subheader("🔬 Micro-Analysis: Talent Distribution")

max_year = int(agent_df["Step"].max()) + 1
selected_year = st.slider("Select Year to Inspect", 1, max_year, 1)

year_data = agent_df[agent_df["Step"] == selected_year]

if year_data.empty:
    st.error("No data for selected year.")
else:
    # Histogram
    fig_dist = px.histogram(
        year_data,
        x="Potential",
        nbins=50,
        title=f"Talent + Experience Distribution (Year {selected_year})",
        range_x=[0.0, 1.1],
        color_discrete_sequence=["#AB63FA"],
        opacity=0.75
    )
    fig_dist.add_vline(x=1.0, line_color="green", annotation_text="Max Cap")
    fig_dist.update_layout(height=400, template="simple_white")
    st.plotly_chart(fig_dist, use_container_width=True)

    # Explainer Text Below Chart
    st.markdown("""
    <div class="analogy-box">
    <b>What to look for:</b> Compare the purple graph of <b>Year 1</b> with <b>Year 20</b>.<br><br>
    Notice how the right side of the mountain isn't smooth anymore—it has developed a distinct "bulge."
    This represents the <b>Accumulation of Experience</b>. By Year 20, that crowded right side is filled with students who have spent 2-3 years refining their strategy.
    They aren't necessarily "smarter" than new students; they are just better prepared.
    </div>
    """, unsafe_allow_html=True)
    
    st.caption(f"Stats (Year {selected_year}) | Mean: {year_data['Potential'].mean():.2f} | Max: {year_data['Potential'].max():.2f}")

# 4. RAW DATA EXPANDER
with st.expander("🔍 View Raw Model Data"):
    st.dataframe(df)

st.markdown("---")

# 5. NAVIGATION FOOTER
col_prev, col_next = st.columns([1, 5])
with col_next:
    if st.button("Next: Enter the Elite Era (Scenario 2) 👉", type="primary"):
        st.switch_page("pages/2_🚀_The_Elite_Era.py")