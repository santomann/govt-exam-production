import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from simulation_engines.scenerio_2 import ExamEcosystem
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Scenario 2: The Elite Era",
    page_icon="🚀",
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
        padding: 15px 20px;
        border-radius: 8px;
        margin: 15px 0;
        font-size: 0.95rem;
    }
    .analyst-note {
        background-color: #F9F9F9;
        border: 1px solid #E0E0E0;
        padding: 15px;
        border-radius: 8px;
        font-size: 0.9rem;
        color: #555;
        margin-top: 10px;
    }
    
    /* HIDE HEADER */
    [data-testid="stHeader"] {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- INJECT NAVBAR ---
st.markdown("""
    <div class="global-nav">
        <div class="nav-links">
            <a href="/" target="_self">← Return Home</a>
            <span style="opacity:0.3">|</span>
            <span style="color:white">Scenario 2: The Elite Era</span>
            <span style="opacity:0.3">|</span>
            <a href="pages/3_🌪️_The_Mass_Disruption.py" target="_self">Next Phase →</a>
        </div>
    </div>
""", unsafe_allow_html=True)


# --- NARRATIVE SECTION ---
st.title("Scenario 2: The Elite Era")

st.markdown("""
### Phase 2: Capital Meets Talent
In Phase 1, the world was fair (mostly). In Phase 2, we break that fairness by introducing the "Real World" constraints of **Biology** and **Economics**.

**The Dynamic Shift**
We introduce two major disruptions:
1.  **The Biological Clock:** Agents now age. They enter at ~22 and **must quit by 32**. No one stays forever, creating a "use it or lose it" pressure.
2.  **Population Inflation:** The population isn't static. It grows by **3% every year**, increasing the pressure on the same 50 seats.
""")

st.markdown("""
<div class="insight-box">
<b>The "Elite" Differentiator (The Coaching Multiplier):</b><br>
In real life, this corresponds to expensive coaching hubs like Kota or specialized residential programs.<br>
In this model, if an agent starts with <b>> 6 years of Runway</b> (High Net Worth), they automatically enroll in <b>Elite Coaching</b>.
This gives them a <b>3x faster learning rate</b> compared to self-study students. They don't just survive longer; they get smarter faster.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ System Parameters")
    num_agents = st.slider("Initial Population", 1000, 5000, 2000, step=100)
    top_n_seats = st.slider("Available Seats", 10, 200, 50, step=10)
    growth_rate = st.slider("Pop. Growth Rate", 0.0, 0.1, 0.03, step=0.01)
    steps = st.slider("Years to Simulate", 5, 30, 15)
    
    st.markdown("---")
    run_btn = st.button("🚀 Run Simulation", type="primary")

    # GLOBAL TIME TRAVEL (Appears after run)
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
    with st.spinner("Simulating the impact of capital..."):
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
    
    # FILTER DATA FOR SELECTED YEAR
    step_mapping = dict(zip(model_df["Year"], model_df.index))
    target_step = step_mapping.get(selected_year, 0)

    try:
        # Filter: Match Year AND Active Status
        year_data = agent_df[
            (agent_df["Step"] == target_step) & 
            (agent_df["Status"] == "active")
        ]
    except KeyError:
        st.error("Data Error: Please check model columns.")
        st.stop()
    
    cutoff_val = model_df.loc[target_step, "Cutoff Score"]

    # METRICS ROW
    final_cutoff = model_df["Cutoff Score"].iloc[-1]
    final_pop = model_df["Active Agents"].iloc[-1]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Cutoff", f"{cutoff_val:.1f}/300")
    c2.metric("Active Population", f"{int(len(year_data))}")
    c3.metric("Avg Competitor Age", f"{year_data['Age'].mean():.1f} yrs")
    c4.metric("Growth Factor", f"{(len(year_data)/num_agents):.2f}x")
    
    st.markdown("---")

    # === TABBED ANALYSIS ===
    tab1, tab2, tab3 = st.tabs(["🌌 3D Landscape", "📊 Micro-Distribution", "📈 Macro-Trends"])
    
    # TAB 1: 3D LANDSCAPE
    with tab1:
        st.subheader(f"The Battleground (Year {selected_year})")
        
        col_3d, col_explain = st.columns([3, 1])
        
        with col_3d:
            fig_3d = px.scatter_3d(
                year_data,
                x="Runway", y="Talent", z="Score",
                color="Coaching",
                hover_data=["Age", "Potential"],
                color_discrete_map={True: "#00CC96", False: "#EF553B"}, # Green=Elite, Red=Self
                opacity=0.6, template="plotly", height=600,
                labels={"Runway": "Capital (Years)", "Talent": "Innate Talent"}
            )
            fig_3d.update_traces(marker=dict(size=3)) # Smaller dots for clarity
            
            # Cutoff Plane
            x_range = [year_data["Runway"].min(), year_data["Runway"].max()]
            y_range = [year_data["Talent"].min(), year_data["Talent"].max()]
            
            fig_3d.add_trace(go.Surface(
                z=[[cutoff_val, cutoff_val], [cutoff_val, cutoff_val]],
                x=x_range, y=y_range,
                opacity=0.2, showscale=False,
                colorscale=[[0, 'black'], [1, 'black']], name="Cutoff Plane"
            ))
            st.plotly_chart(fig_3d, use_container_width=True)
            
        with col_explain:
            st.markdown("#### What are we looking at?")
            st.write("""
            **1. The Green Cloud (Elite):** Notice how the green points cluster *higher* on the Z-axis (Score). This is the multiplier effect of coaching. They don't need maximum talent to rise.
            
            **2. The Red Cloud (Self-Study):** These dots are suppressed. Unless they have extreme Talent (Y-axis > 0.8), they struggle to pierce the black Cutoff Plane.
            
            **3. The Ceiling:** Notice the hard stop at 300. As the simulation progresses, more students bunch up against this ceiling, making the cutoff difference decimal-thin.
            """)

    # TAB 2: DISTRIBUTIONS (RESTORED QUAD-GRID)
    with tab2:
        st.subheader(f"Demographic Breakdown (Year {selected_year})")
        st.caption("Analyzing the 4 Key Variables driving the simulation.")
        
        def plot_hist(data, x_col, title, color, vline=None):
            fig = px.histogram(
                data, x=x_col, nbins=40, title=title, 
                color_discrete_sequence=[color], template="plotly", 
                marginal="rug", opacity=0.75
            )
            fig.update_layout(bargap=0.1, height=250, margin=dict(l=20, r=20, t=40, b=20))
            if vline: fig.add_vline(x=vline, line_dash="dash", line_color="black")
            return fig

        # ROW 1
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.plotly_chart(plot_hist(year_data, "Potential", "1. Capped Talent Distribution", "#636EFA", 1.0), use_container_width=True)
            st.markdown("<div class='analyst-note'><b>Insight:</b> Notice the bulge on the right? That's the 'Experience Accumulation'.</div>", unsafe_allow_html=True)
            
        with r1c2:
            st.plotly_chart(plot_hist(year_data, "Age", "2. Age Distribution (The Cliff)", "#FFA15A", 32), use_container_width=True)
            st.markdown("<div class='analyst-note'><b>Insight:</b> The sharp drop at Age 32 represents the hard age limit. Veterans are forced out.</div>", unsafe_allow_html=True)
        
        # ROW 2
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            st.plotly_chart(plot_hist(year_data, "Runway", "3. Financial Runway (Wealth)", "#00CC96"), use_container_width=True)
            st.markdown("<div class='analyst-note'><b>Insight:</b> The 'Rich' (Runway > 6) are safe. The 'Poor' (Runway < 2) are in the danger zone.</div>", unsafe_allow_html=True)

        with r2c2:
            st.plotly_chart(plot_hist(year_data, "Score", "4. Final Score Distribution", "#AB63FA", cutoff_val), use_container_width=True)
            st.markdown(f"<div class='analyst-note'><b>Insight:</b> The Red Line is the Cutoff ({cutoff_val:.1f}). Notice how many people fail just barely?</div>", unsafe_allow_html=True)

    # TAB 3: TRENDS
    with tab3:
        st.subheader("System Evolution")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**📉 Cutoff Inflation**")
            fig_cutoff = px.line(
                model_df, x="Year", y="Cutoff Score", markers=True, 
                color_discrete_sequence=["#00CC96"], template="plotly"
            )
            fig_cutoff.add_vline(x=selected_year, line_dash="dash", line_color="black")
            st.plotly_chart(fig_cutoff, use_container_width=True)
            st.info("Why is it rising? Unlike Phase 1, the 'Elite' students have a learning multiplier. They push the bar higher every year.")
            
        with c2:
            st.markdown("**⚖️ The Inequality Gap**")
            fig_ineq = px.line(
                model_df, x="Year", y=["Rich_score", "Poor_score"], 
                title="Avg Score: Coached (Green) vs Uncoached (Red)",
                color_discrete_map={"Rich_score": "#00CC96", "Poor_score": "#EF553B"},
                template="plotly"
            )
            fig_ineq.add_vline(x=selected_year, line_dash="dash", line_color="black")
            st.plotly_chart(fig_ineq, use_container_width=True)
            st.info("The Gap: This chart visualizes 'Pay-to-Win'. The green line separates because money buys time AND efficiency.")

    # === HALL OF FAME ===
    st.markdown("---")
    st.subheader(f"🏆 Hall of Fame (Cumulative up to Year {selected_year})")
    
    # Dynamic Filtering
    cumulative_winners = agent_df[
        (agent_df["Status"] == "selected") & 
        (agent_df["Step"] <= target_step) # Use Step index for filtering
    ]
    unique_winners = cumulative_winners.drop_duplicates(subset=["AgentID"], keep="first")

    if unique_winners.empty:
        st.warning(f"No candidates have been selected yet by Year {selected_year}.")
    else:
        wc1, wc2, wc3, wc4 = st.columns(4)
        wc1.metric("Total Winners", len(unique_winners))
        wc2.metric("Avg Winner Talent", f"{unique_winners['Talent'].mean():.2f}")
        
        coached_count = unique_winners["Coaching"].sum()
        coached_percent = (coached_count / len(unique_winners)) * 100
        wc3.metric("Elite Coached %", f"{coached_percent:.1f}%")
        wc4.metric("Avg Winner Age", f"{unique_winners['Age'].mean():.1f} yrs")

        st.markdown(f"##### 🕵️ Winner Archetypes Analysis")
        st.write("This chart maps every single winner based on their starting conditions.")
        
        fig_cluster = px.scatter(
            unique_winners,
            x="Runway", y="Talent", color="Coaching", size="Score",
            hover_data=["Age", "AgentID"],
            title=f"Differentiation Map: The {len(unique_winners)} Winners",
            labels={"Runway": "Initial Capital", "Talent": "Innate Talent"},
            color_discrete_map={True: "#00CC96", False: "#EF553B"},
            template="plotly", height=500
        )
        # Add Quadrant Lines
        fig_cluster.add_hline(y=unique_winners['Talent'].mean(), line_dash="dot", line_color="gray", annotation_text="Avg Talent")
        fig_cluster.add_vline(x=unique_winners['Runway'].mean(), line_dash="dot", line_color="gray", annotation_text="Avg Capital")
        
        st.plotly_chart(fig_cluster, use_container_width=True)
        
        st.markdown("""
        <div class="insight-box">
        <b>The "Dead Zone" Analysis:</b><br>
        Look at the <b>Bottom-Left Quadrant</b> (Low Capital + Low Talent). It is likely empty.<br>
        This proves the hypothesis: <b>Without money, you MUST be a genius (Top-Left) to win.</b><br>
        However, if you have Money (Right side), you can win even with average talent (Bottom-Right green dots).
        </div>
        """, unsafe_allow_html=True)
    
    # === AGENT DATA EXPLORER (RESTORED) ===
    st.markdown("---")
    st.subheader(f"📋 Agent Data Explorer (Year {selected_year})")
    
    with st.expander("Show Raw Data Table", expanded=True):
        st.caption("Tip: Click on 'Exam Score' to sort by topper. Check 'Elite Coaching' column.")
        
        # Clean Dataframe for display
        display_df = year_data.drop(columns=["Step", "Status"]).rename(columns={"AgentID": "ID"})
        cols = ["ID", "Score", "Runway", "Age", "Talent", "Potential", "Coaching"]
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
                "Potential": st.column_config.NumberColumn("Potential", format="%.2f"),
                "Coaching": st.column_config.CheckboxColumn("Elite?"),
                "Age": st.column_config.NumberColumn("Age", format="%d")
            }
        )

else:
    st.info("👈 Set your parameters and click **Run Simulation** to see the Elite Era in action.")

# --- FOOTER ---
st.markdown("---")
col_prev, col_next = st.columns([1, 5])
with col_next:
    if st.button("Next: The Mass Disruption (Scenario 3) →", type="primary"):
        st.switch_page("pages/3_🌪️_The_Mass_Disruption.py")