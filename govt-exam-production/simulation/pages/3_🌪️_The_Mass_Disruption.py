import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from simulation_engines.scenerio_3 import ExamEcosystem
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Scenario 3: Mass Disruption",
    page_icon="🌪️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS STYLING (Apple/Medium Style) ---
st.markdown("""
    <style>
    /* 1. TYPOGRAPHY & LAYOUT */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1d1d1f; 
        background-color: #ffffff;
    }
    
    .block-container {
        max-width: 1100px;
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
    h2 { font-weight: 700; font-size: 1.8rem; margin-top: 2rem; }
    h3 { font-weight: 600; font-size: 1.3rem; margin-top: 1.5rem; color: #333; }
    p, li { font-size: 1.05rem; line-height: 1.6; color: #333; }
    
    /* 4. CALLOUT BOXES */
    .insight-box {
        background-color: #f0f7ff;
        border-left: 4px solid #0071e3;
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        font-size: 1rem;
        line-height: 1.6;
    }
    .variance-box {
        background-color: #fff9f0;
        border-left: 4px solid #FFA15A;
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        font-size: 1rem;
        line-height: 1.6;
    }
    .deep-dive {
        background-color: #fafafa;
        border: 1px solid #e0e0e0;
        padding: 25px;
        border-radius: 12px;
        margin-top: 20px;
    }
    
    /* HIDE HEADER */
    [data-testid="stHeader"] {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- INJECT NAVBAR ---
st.markdown("""
    <div class="global-nav">
        <div class="nav-links">
            <a href="./" target="_self">← Return Home</a>
            <span style="opacity:0.3">|</span>
            <span style="color:white">Scenario 3: Mass Disruption</span>
            <span style="opacity:0.3">|</span>
            <a href="Verdict" target="_self">Finish Story 🏁</a>
        </div>
    </div>
""", unsafe_allow_html=True)


# --- NARRATIVE SECTION ---
st.title("Scenario 3: The Mass Disruption")

st.markdown("""
### Phase 3: The Chaos of Abundance
In Phase 2, the primary unfair advantage was **Access**. If you were rich, you got coaching. If you were poor, you didn't. The line was clear.

In Phase 3, we solve the Access problem. EdTech platforms, YouTube channels, and affordable online cohorts flood the market. Suddenly, **expert knowledge is cheap**. The secrets that were once locked in elite classrooms are now available for $10 or even free.

**But does this fix the inequality? Or does it create a new problem?**
""")

col_n1, col_n2 = st.columns(2, gap="large")

with col_n1:
    st.markdown("""
    <div class="insight-box">
    <b>📈 The "Floor Raising" Effect</b><br>
    When everyone has access to the "best strategies," the exam doesn't get easier—the <b>baseline competence explodes</b>.<br><br>
    A score of 200/300 was "Safe" in Phase 1. In Phase 3, 200 is the new average. The cutoff line moves up faster than the students improve, leaving many trapped in the "Good but not Good Enough" zone.
    </div>
    """, unsafe_allow_html=True)

with col_n2:
    st.markdown("""
    <div class="variance-box">
    <b>🎲 The "Noise" Problem</b><br>
    Cheap coaching comes with a hidden cost: <b>Lack of Discipline.</b><br><br>
    In our model, "Mass Coaching" provides a learning boost, but with <b>High Variance</b>.
    <ul>
    <li><b>Student A</b> uses it to crack the exam (The Success Story).</li>
    <li><b>Student B</b> gets lost in "Motivation Reels" and "Strategy Hopping" (The Distracted Majority).</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ System Parameters")
    num_agents = st.slider("Initial Population", 1000, 5000, 2000, step=100)
    top_n_seats = st.slider("Available Seats", 10, 200, 50, step=10)
    growth_rate = st.slider("Pop. Growth Rate", 0.0, 0.1, 0.05, step=0.01)
    steps = st.slider("Years to Simulate", 5, 30, 15)
    
    st.markdown("---")
    run_btn = st.button("🚀 Run Simulation", type="primary")
    
    # GLOBAL TIME TRAVEL
    selected_year = 1 
    if "simulation_done" in st.session_state and st.session_state.simulation_done:
        st.header("🕰️ Time Travel")
        valid_years = sorted(st.session_state.model_data["Year"].unique())
        selected_year = st.slider("Inspect Year", min_value=min(valid_years), max_value=max(valid_years), value=max(valid_years))

# --- SESSION STATE ---
if "model_data" not in st.session_state:
    st.session_state.model_data = None
if "agent_data" not in st.session_state:
    st.session_state.agent_data = None
if "simulation_done" not in st.session_state:
    st.session_state.simulation_done = False

# --- EXECUTION LOGIC ---
if run_btn:
    with st.spinner("Simulating the chaos of abundance..."):
        model = ExamEcosystem(
            num_agents=num_agents, 
            top_n_seats=top_n_seats, 
            growth_rate=growth_rate
        )
        
        progress_bar = st.progress(0)
        for i in range(steps):
            model.step()
            progress_bar.progress((i + 1) / steps)
        
        # Store Data
        m_df = model.datacollector.get_model_vars_dataframe()
        m_df["Year"] = m_df.index + 1 
        st.session_state.model_data = m_df
        
        a_df = model.datacollector.get_agent_vars_dataframe().reset_index()
        st.session_state.agent_data = a_df
        
        st.session_state.simulation_done = True
        st.rerun()

# --- DASHBOARD RENDER ---
if st.session_state.simulation_done:
    model_df = st.session_state.model_data
    agent_df = st.session_state.agent_data
    
    # 1. FILTERING
    step_mapping = dict(zip(model_df["Year"], model_df.index))
    target_step = step_mapping.get(selected_year, 0)

    try:
        year_data = agent_df[
            (agent_df["Step"] == target_step) & 
            (agent_df["Status"] == "active")
        ]
    except KeyError:
        st.error("Data Error: Please check model columns.")
        st.stop()
    
    cutoff_val = model_df.loc[target_step, "Cutoff Score"]

    # 2. METRICS
    final_cutoff = model_df["Cutoff Score"].iloc[-1]
    final_pop = model_df["Active Agents"].iloc[-1]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Cutoff", f"{cutoff_val:.1f}/300")
    c2.metric("Active Population", f"{int(len(year_data))}")
    c3.metric("Elite Avg Score", f"{model_df.loc[target_step, 'Elite_Score']:.1f}")
    c4.metric("Mass Avg Score", f"{model_df.loc[target_step, 'Mass_Score']:.1f}")
    
    st.markdown("---")

    # TABS
    tab1, tab2, tab3 = st.tabs(["🌌 3D Landscape", "📊 The 3-Hump Curve", "📈 Trends"])
    
    # COLOR MAP FOR THE 3 TIERS
    color_map = {"Elite": "#00CC96", "Mass": "#636EFA", "Self": "#EF553B"}
    
    # === TAB 1: 3D LANDSCAPE ===
    with tab1:
        st.subheader(f"The Battleground (Year {selected_year})")
        st.caption("Visualizing the 3 Tiers of Competition: Green (Elite), Blue (Mass), Red (Self-Study).")
        
        fig_3d = px.scatter_3d(
            year_data,
            x="Runway", 
            y="Talent", 
            z="Score",
            color="Coaching",
            hover_data=["Age", "Potential"],
            color_discrete_map=color_map,
            opacity=0.5,
            template="plotly", 
            height=700,
            labels={"Runway": "Capital", "Talent": "Innate Talent"}
        )
        fig_3d.update_traces(marker=dict(size=3))
        
        # Cutoff Plane
        x_range = [year_data["Runway"].min(), year_data["Runway"].max()]
        y_range = [year_data["Talent"].min(), year_data["Talent"].max()]
        
        fig_3d.add_trace(go.Surface(
            z=[[cutoff_val, cutoff_val], [cutoff_val, cutoff_val]],
            x=x_range, y=y_range,
            opacity=0.2, showscale=False,
            colorscale=[[0, 'black'], [1, 'black']],
            name="Cutoff Plane"
        ))
        st.plotly_chart(fig_3d, use_container_width=True)
        
        st.markdown("""
        <div class="deep-dive">
        <b>What am I looking at?</b><br>
        Notice the <b>Blue Cloud (Mass Coaching)</b>. It is massive, but it is "messy." 
        Unlike the Green Cloud (Elite) which is tightly packed at the top, the Blue Cloud is scattered all over the Z-axis (Score).
        <br><br>
        This visualizes the <b>High Variance</b> risk. Taking Mass Coaching doesn't guarantee you rise; it just creates volatility. 
        Some blue dots are piercing the ceiling, but many are sinking below the red dots.
        </div>
        """, unsafe_allow_html=True)

    # === TAB 2: DISTRIBUTIONS (THE 3 HUMPS) ===
    with tab2:
        st.subheader("Distribution Analysis")
        st.caption("How 'Mass Coaching' changes the shape of the competition.")
        
        col_dist1, col_dist2 = st.columns(2)
        
        with col_dist1:
            st.markdown("#### The 'Three-Hump' Camel")
            fig_hist = px.histogram(
                year_data, 
                x="Score", 
                color="Coaching",
                nbins=50,
                barmode="overlay", # Shows the overlap
                color_discrete_map=color_map,
                opacity=0.6,
                marginal="rug",
                title="Score Distribution Overlay"
            )
            fig_hist.add_vline(x=cutoff_val, line_dash="solid", line_color="black", annotation_text="Cutoff")
            st.plotly_chart(fig_hist, use_container_width=True)
            
            st.markdown("""
            **The Shift:** Notice how the **Red Curve (Self-Study)** is pushed to the left (Failure Zone). 
            The **Blue Curve (Mass)** dominates the middle but has a long tail of failures.
            The **Green Curve (Elite)** sits comfortably on the right.
            """)
            
        with col_dist2:
            st.markdown("#### Variance Analysis (Risk vs Reward)")
            fig_box = px.box(
                year_data,
                x="Coaching",
                y="Score",
                color="Coaching",
                color_discrete_map=color_map,
                title="Consistency Check: Which path is riskiest?"
            )
            st.plotly_chart(fig_box, use_container_width=True)
            
            st.markdown("""
            **The Consistency Problem:**
            Look at the size of the Blue Box. It is huge. This means Mass Coaching produces both 
            amazing toppers AND tragic failures. Elite coaching (Green) is tight—you pay for *reliability*.
            """)

    # === TAB 3: TRENDS ===
    with tab3:
        st.subheader("System Evolution")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**📉 Cutoff Inflation**")
            fig_cutoff = px.line(
                model_df, x="Year", y="Cutoff Score", 
                title="Cutoff Inflation", 
                markers=True, 
                color_discrete_sequence=["#00CC96"]
            )
            fig_cutoff.add_vline(x=selected_year, line_dash="dash", line_color="gray")
            st.plotly_chart(fig_cutoff, use_container_width=True)
            st.warning("The Cutoff rises sharply because 'Average' students are now scoring better due to cheap tools.")
            
        with c2:
            st.markdown("**⚖️ The 3-Tier Gap**")
            fig_ineq = px.line(
                model_df, x="Year", y=["Elite_Score", "Mass_Score", "Self_Score"], 
                title="Average Scores by Group",
                color_discrete_map={"Elite_Score": "#00CC96", "Mass_Score": "#636EFA", "Self_Score": "#EF553B"}
            )
            fig_ineq.add_vline(x=selected_year, line_dash="dash", line_color="gray")
            st.plotly_chart(fig_ineq, use_container_width=True)
            st.info("Notice that while Mass Coaching (Blue) is better than Self-Study (Red), it rarely catches up to Elite (Green).")

    # === SECTION 4: HALL OF FAME ===
    st.markdown("---")
    st.subheader(f"🏆 Hall of Fame (Years 1 - {selected_year})")
    
    history_df = agent_df[agent_df["Step"] <= (target_step)]
    all_winners = history_df[history_df["Status"] == "selected"]
    unique_winners = all_winners.drop_duplicates(subset=["AgentID"], keep="first")

    if not unique_winners.empty:
        # Cluster Map
        st.markdown("#### Winner Archetypes")
        fig_cluster = px.scatter(
            unique_winners,
            x="Runway",
            y="Talent",
            color="Coaching",
            size="Score",
            hover_data=["Age", "AgentID"],
            title=f"The {len(unique_winners)} Winners So Far",
            color_discrete_map=color_map,
            template="plotly",
            height=600,
            labels={"Runway": "Capital", "Talent": "Innate Talent"}
        )
        
        avg_t = unique_winners['Talent'].mean()
        avg_r = unique_winners['Runway'].mean()
        fig_cluster.add_hline(y=avg_t, line_dash="dot", line_color="gray", annotation_text="Avg Winner Talent")
        fig_cluster.add_vline(x=avg_r, line_dash="dot", line_color="gray", annotation_text="Avg Winner Capital")
        
        st.plotly_chart(fig_cluster, use_container_width=True)
        
        st.markdown("""
        <div class="insight-box">
        <b>The "Middle Class" Squeeze:</b><br>
        Look closely at the <b>Blue Dots (Mass Coaching)</b>. <br>
        They are struggling to compete with the Green Dots (Elite) on the right.<br>
        Even with coaching, the "Mass" students often need <b>Higher Talent (Y-axis)</b> than the "Elite" students to cross the finish line because their coaching is less efficient.
        </div>
        """, unsafe_allow_html=True)

    else:
        st.warning("No winners yet.")

    # === AGENT DATA EXPLORER ===
    st.markdown("---")
    st.subheader(f"📋 Agent Data Explorer (Year {selected_year})")
    
    with st.expander("Show Raw Data Table", expanded=True):
        st.caption("Filter by 'Coaching' to see the difference between Elite, Mass, and Self-study.")
        
        display_df = year_data.drop(columns=["Step", "Status"]).rename(columns={"AgentID": "ID"})
        cols = ["ID", "Score", "Runway", "Age", "Talent", "Coaching", "Potential"]
        display_cols = [c for c in cols if c in display_df.columns]
        
        st.dataframe(
            display_df[display_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", format="%d"),
                "Score": st.column_config.ProgressColumn("Exam Score", min_value=0, max_value=300, format="%.1f"),
                "Runway": st.column_config.NumberColumn("Runway", format="%d yrs"),
                "Talent": st.column_config.NumberColumn("Talent", format="%.2f"),
                "Coaching": st.column_config.TextColumn("Type"),
                "Age": st.column_config.NumberColumn("Age", format="%d")
            }
        )

else:
    st.info("👈 Click **Run Simulation** to initialize Phase 3.")