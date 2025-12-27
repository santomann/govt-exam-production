import streamlit as st
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="The Great Indian Exam Race",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (APPLE STYLE + BLACK NAVBAR) ---
st.markdown("""
    <style>
    /* 1. HIDE DEFAULT STREAMLIT ELEMENTS */
    [data-testid="stSidebarNav"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {visibility: hidden;} /* Hides the thin top bar */

    /* 2. TYPOGRAPHY & LAYOUT */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1d1d1f; 
        background-color: #ffffff;
    }
    
    /* Center the main container */
    .block-container {
        max-width: 900px;
        padding-top: 5.5rem; /* Push content down so navbar doesn't cover it */
        padding-bottom: 5rem;
        margin: 0 auto;
    }

    /* 3. GLOBAL BLACK NAVBAR (Fixed Top) */
    .global-nav {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 70px;
        background-color: #000000;
        color: #f5f5f7;
        z-index: 99999; /* Force on top of everything */
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: 500;
        letter-spacing: 0.02em;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .nav-links {
        display: flex;
        gap: 30px;
    }

    .nav-links a {
        color: #d1d1d1;
        text-decoration: none;
        transition: color 0.2s ease;
    }
    .nav-links a:hover {
        color: #ffffff;
    }
    
    /* 4. CARD STYLING */
    .nav-card {
        background-color: #f5f5f7;
        border-radius: 18px;
        padding: 25px;
        text-align: left;
        height: 100%;
        border: 1px solid #ffffff;
        transition: all 0.3s ease;
    }
    .nav-card:hover {
        transform: translateY(-5px);
        background-color: #ffffff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
    }
    
    /* 5. BUTTON STYLING */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        font-weight: 600;
        height: 3rem;
        border: none;
        background-color: #0071e3; /* Apple Blue */
        color: white;
    }
    div.stButton > button:hover {
        background-color: #0077ed;
    }

    .small-img img {
        width: 10px;
        height: 10px;
        object-fit: contain;
        margin: auto;
        display: block;
    }


    </style>
""", unsafe_allow_html=True)

# --- INJECT NAVBAR HTML ---
st.markdown("""
    <div class="global-nav">
        <div class="nav-links">
            <a href="#" target="_self"> ExamSim</a>
            <a href="#" target="_blank">All Models</a>
            <a href="#" target="_blank">About Author</a>
            <a href="#" target="_blank">Source Code</a>
            <a href="#" target="_blank">Contact</a>
        </div>
    </div>
""", unsafe_allow_html=True)


# --- HERO SECTION ---
st.title("Welcome.")

st.markdown("""
So, what are we solving for in this model? What is the complex system at play, and what is the baseline reality we are trying to highlight?

It comes down to this: We see a disproportionate number of young people in India preparing for government exams. The reasoning is straightforward—it remains the cleanest mechanism to jump social classes, build career security, and insulate one’s life from economic volatility. A government job launches you onto a distinct trajectory, one that minimizes life's inherent risks.
""")

# --- VISUALS (HOW TO LINK LOCAL IMAGES) ---
# Create a folder named "assets" in your project and put your images there.
# Example: project_folder/assets/trajectory.png

col_img, col_cap = st.columns([4, 1])

with col_img:
    # Check if file exists to prevent errors
    if os.path.exists("assets/trajectory.png"): 
        st.image("assets/trajectory.png", use_container_width=True)
    elif os.path.exists("assets/trajectory.gif"):
        st.image("assets/trajectory.gif", use_container_width=True)
    else:
        st.info("ℹ️ To see the image, create a folder named `assets` and place `trajectory.png` inside it.")

st.markdown("""
### The Ask
The requirement is deceptively simple: **Just crack the exam.** Grind for 12, 14, or 16 hours a day. Create strategies to optimize your score. Do this, and voilà—you cross over to the other side of society’s frame. The task is hard, but it is not complex; the path is visible and linear.

### The Goal
If the path is so clear, **who wins this race?** What are the ground rules in play? 

Our goal here is to understand this social system and model it in a way that makes sense—creating a simulation that accurately replicates the results we see in real life.
""")

st.markdown('<div class="small-img">', unsafe_allow_html=True)
st.image("assets/trajectory.gif", use_container_width=False)
st.markdown('</div>', unsafe_allow_html=True)


st.divider()

# --- NAVIGATION SECTION ---
st.subheader("How to Navigate")
st.write("Below is an attempt to model this reality. The project is divided into three phases covering key definitions, the tools used, and the final analysis.")
st.write("") 

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown("""
    <div class="nav-card">
        <h4>🌱 Phase 1</h4>
        <p><b>The Baseline Reality.</b><br>Pure merit, no coaching.</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    if st.button("Explore Phase 1"):
        st.switch_page("pages/1_🌱_The_Baseline.py")

with col2:
    st.markdown("""
    <div class="nav-card">
        <h4>🚀 Phase 2</h4>
        <p><b>The Elite Era.</b><br>Capital meets Talent.</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    if st.button("Explore Phase 2"):
        st.switch_page("pages/2_🚀_The_Elite_Era.py")

with col3:
    st.markdown("""
    <div class="nav-card">
        <h4>🌪️ Phase 3</h4>
        <p><b>Mass Disruption.</b><br>The chaos of abundance.</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    if st.button("Explore Phase 3"):
        st.switch_page("pages/3_🌪️_The_Mass_Disruption.py")

st.markdown("---")
st.caption("© 2025 ExamSim Project. Built with Mesa & Streamlit.")