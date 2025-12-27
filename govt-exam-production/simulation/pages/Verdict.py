import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="The Verdict: Key Takeaways",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS STYLING (Apple/Medium Style - Optimized for Reading) ---
st.markdown("""
    <style>
    /* 1. TYPOGRAPHY & LAYOUT */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1d1d1f; 
        background-color: #ffffff;
    }
    
    /* READABILITY CONTAINER */
    .block-container {
        max-width: 800px; /* Narrower width for reading focus */
        padding-top: 5rem;
        padding-bottom: 8rem;
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

    /* 3. HEADERS & TEXT */
    h1 { font-family: 'Inter', sans-serif; font-weight: 800; letter-spacing: -0.03em; font-size: 3rem; margin-bottom: 2rem; }
    h2 { font-family: 'Inter', sans-serif; font-weight: 700; font-size: 2rem; margin-top: 3rem; margin-bottom: 1rem; color: #111; }
    
    /* Use Serif font for body text to feel like an article */
    p, li { 
        font-family: 'Merriweather', serif; 
        font-size: 1.15rem; 
        line-height: 1.8; 
        color: #333; 
        margin-bottom: 1.5rem;
        font-weight: 300;
    }
    
    /* 4. HIGHLIGHT BOXES */
    .highlight-card {
        background-color: #F5F5F7;
        padding: 30px;
        border-radius: 12px;
        border-left: 5px solid #000;
        margin: 30px 0;
    }
    .highlight-title {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 10px;
        display: block;
    }
    
    /* 5. QUOTES */
    blockquote {
        border-left: 3px solid #0071e3;
        padding-left: 20px;
        margin-left: 0;
        font-style: italic;
        color: #555;
        font-size: 1.2rem;
    }
    
    /* HIDE HEADER */
    [data-testid="stHeader"] {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- INJECT NAVBAR ---
st.markdown("""
    <div class="global-nav">
        <div class="nav-links">
            <a href="Home" target="_self">← Restart Story</a>
            <span style="opacity:0.3">|</span>
            <span style="color:white">The Verdict</span>
        </div>
    </div>
""", unsafe_allow_html=True)


# --- HERO SECTION ---
st.title("The Verdict.")
st.markdown("""
We started with a simple question: **Who wins the Great Indian Exam Race?**

After simulating thousands of agents across three different realities—from the "Pure Merit" baseline to the "Mass Disruption" of today—the data has revealed a story that is both fascinating and uncomfortable.

Here are the three fundamental laws that govern this ecosystem.
""")

st.markdown("---")

# --- INSIGHT 1 ---
st.markdown("## 1. The Red Queen Effect")
st.markdown("""
In Lewis Carroll’s *Through the Looking-Glass*, the Red Queen tells Alice: *"Now, here, you see, it takes all the running you can do, to keep in the same place."*

Our simulation proves this mathematically. In **Phase 1**, as agents gained experience, the cutoff score didn't just stabilize; it inflated. An aspirant scoring 200/300 would have been a topper in Year 1, but by Year 10, they wouldn't even clear the cutoff.

**The Takeaway:** The system punishes "static competence." If you are not improving faster than the herd, you are technically falling backward. The exam stops testing intelligence and starts testing *endurance*.
""")

# --- INSIGHT 2 ---
st.markdown("## 2. Runway is the Invisible Hand")
st.markdown("""
We like to believe exams are about **Talent (IQ)** and **Hard Work (Grit)**. The simulation exposes a third, silent variable: **Runway (Capital)**.

In **Phase 2 (The Elite Era)**, we saw the "Dead Zone" appear in the bottom-left of the scatter plot. This zone represents high-potential candidates who simply ran out of money before they could peak.
""")

st.markdown("""
<div class="highlight-card">
<span class="highlight-title">The Capital Multiplier</span>
<p style="margin-bottom:0;">
Money doesn't just buy coaching; <b>money buys time.</b><br>
A rich student can afford to fail twice and succeed on the third try. A poor student has one shot. 
The simulation shows that <b>Mediocrity + High Capital</b> often defeats <b>Genius + Low Capital</b> because the former can survive long enough to "optimize" their score.
</p>
</div>
""", unsafe_allow_html=True)

# --- INSIGHT 3 ---
st.markdown("## 3. The Paradox of Access")
st.markdown("""
In **Phase 3**, we democratized education. We gave everyone cheap coaching. Logic suggests this should level the playing field. **It didn't.**

Instead, it created the **"Noise Trap."**
When information becomes abundant, the differentiator shifts from *access* to *discipline*. The "Mass Coaching" cohort in our model showed massive variance. While a few broke through, thousands were lost in the confusion of "too much content."

Meanwhile, the Elite cohort (Green Dots) maintained their dominance not because they had *better* books, but because they had *filtered* guidance.
""")

st.markdown("---")

# --- FINAL THOUGHTS ---
st.markdown("## The Final Conclusion")

st.markdown("""
The simulation suggests that the Government Exam system is no longer a test of just capability. It has evolved into a complex filter that selects for a specific archetype:

> **The Winner is rarely just the "Smartest."**
>
> The Winner is the one who possesses the **Financial Runway** to survive the Red Queen Effect, combined with the **Disciplined Guidance** to ignore the Noise of the mass market.

**What does this mean for you?**
If you are an aspirant, realize that "Time" is your most expensive asset.
If you are a policy maker, realize that "Free Content" is not the same as "Equal Opportunity."
""")

st.markdown("---")

# --- CALL TO ACTION ---
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("### Explore the model again?")
    st.write("Change the parameters. Break the system. See if you can find a scenario where talent wins every time.")
    if st.button("🔄 Restart Simulation (Go Home)", type="primary"):
        st.switch_page("Home.py")

with col2:
    st.markdown("### Read the Code")
    st.write("This simulation is open source. Check the logic behind the agents.")
    st.link_button("View on GitHub", "https://github.com/your-repo")