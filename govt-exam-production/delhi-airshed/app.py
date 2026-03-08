import streamlit as st
import pandas as pd
import altair as alt
import folium
from streamlit_folium import st_folium
from folium import plugins
from model import DelhiAirshed
import plotly.graph_objects as go
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Delhi Airshed Simulator",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Global styling */
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .dashboard-header h1.dashboard-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .dashboard-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f7fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
        border: 1px solid #cbd5e0;
    }
        
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.5);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
        color: #e2e8f0;
    }
    
    .metric-label {
        color: #a0aec0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Chart containers */
    .chart-container {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        color: white;
    }
    
    .chart-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 1rem;
    }
    
    /* Modal styling */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.85);
        z-index: 9998;
        backdrop-filter: blur(8px);
    }
    
    .modal-content {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        border-radius: 20px;
        padding: 2rem;
        max-width: 90vw;
        max-height: 85vh;
        overflow-y: auto;
        z-index: 9999;
        box-shadow: 0 20px 60px rgba(0,0,0,0.6);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Control button */
    .control-btn {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(66,153,225,0.4);
        transition: all 0.3s ease;
    }
    
    .control-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(66,153,225,0.6);
    }
    
    /* Run button */
    .run-btn {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 1.2rem 3rem;
        border-radius: 50px;
        font-size: 1.2rem;
        font-weight: 700;
        border: none;
        cursor: pointer;
        box-shadow: 0 6px 20px rgba(72,187,120,0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .run-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(72,187,120,0.6);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 1.1rem;
        color: #a0aec0;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #63b3ed;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #2d374815 0%, #4a556815 100%);
        border-left: 4px solid #4299e1;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: black;
    
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-left: 1rem;
    }
    
    .status-default {
        background: #2c5282;
        color: #90cdf4;
    }
    
    .status-custom {
        background: #744210;
        color: #fbd38d;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def calculate_aqi(pm25):
    if pm25 <= 30: return pm25 * (50/30)
    elif pm25 <= 60: return 50 + (pm25 - 30) * (50/30)
    elif pm25 <= 90: return 100 + (pm25 - 60) * (100/30)
    elif pm25 <= 120: return 200 + (pm25 - 90) * (100/30)
    elif pm25 <= 250: return 300 + (pm25 - 120) * (100/130)
    else: return 400 + (pm25 - 250) * (100/130)

def get_aqi_color(aqi):
    if aqi <= 50: return "#00B050"
    elif aqi <= 100: return "#92D050"
    elif aqi <= 200: return "#FFFF00"
    elif aqi <= 300: return "#FF9900"
    elif aqi <= 400: return "#FF0000"
    else: return "#C00000"

def get_aqi_category(aqi):
    if aqi <= 50: return "Good"
    elif aqi <= 100: return "Satisfactory"
    elif aqi <= 200: return "Moderate"
    elif aqi <= 300: return "Poor"
    elif aqi <= 400: return "Very Poor"
    else: return "Severe"

def create_premium_map(zone_locs):
    """Create a premium, non-scrollable map with advanced features"""
    m = folium.Map(
        location=[28.61, 77.20],
        zoom_start=10,
        tiles=None,
        zoom_control=True,
        scrollWheelZoom=False,
        dragging=True,
        max_bounds=True
    )
    
    # Add premium tile layer
    folium.TileLayer(
        tiles='https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png',
        attr='Stadia Maps',
        name='Premium Base',
        overlay=False,
        control=False
    ).add_to(m)
    
    # Add AQI gradient circles with glow effect
    for loc in zone_locs:
        color = get_aqi_color(loc['aqi'])
        
        # Outer glow
        folium.CircleMarker(
            location=[loc['lat'], loc['lon']],
            radius=25 + (loc['aqi'] / 20),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.15,
            weight=0
        ).add_to(m)
        
        # Main circle
        folium.CircleMarker(
            location=[loc['lat'], loc['lon']],
            radius=18 + (loc['aqi'] / 25),
            popup=folium.Popup(f"""
                <div style='font-family: Arial; min-width: 200px;'>
                    <h4 style='margin:0; color: {color};'>{loc['name']}</h4>
                    <hr style='margin: 5px 0;'>
                    <p style='margin:5px 0;'><b>AQI:</b> {loc['aqi']:.0f}</p>
                    <p style='margin:5px 0;'><b>PM2.5:</b> {loc['pm25']:.1f} µg/m³</p>
                    <p style='margin:5px 0;'><b>Category:</b> {get_aqi_category(loc['aqi'])}</p>
                    <p style='margin:5px 0; color: #666;'><i>{loc['desc']}</i></p>
                </div>
            """, max_width=300),
            tooltip=f"<b>{loc['name']}</b><br>AQI: {loc['aqi']:.0f}",
            color='white',
            weight=3,
            fill=True,
            fillColor=color,
            fillOpacity=0.85
        ).add_to(m)
        
        # Zone label
        folium.Marker(
            location=[loc['lat'], loc['lon']],
            icon=folium.DivIcon(html=f"""
                <div style='
                    font-size: 11px;
                    font-weight: bold;
                    color: white;
                    text-align: center;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
                    white-space: nowrap;
                '>
                    {int(loc['aqi'])}
                </div>
            """)
        ).add_to(m)
    
    # Add legend
    legend_html = f'''
    <div style="
        position: fixed;
        bottom: 50px;
        right: 50px;
        background: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 9999;
        font-family: Arial;
        min-width: 160px;
    ">
        <h4 style="margin: 0 0 10px 0; font-size: 14px; font-weight: 600;">AQI Scale</h4>
        <div style="margin: 5px 0; display: flex; align-items: center;">
            <div style="width: 20px; height: 20px; background: #00B050; border-radius: 50%; margin-right: 8px;"></div>
            <span style="font-size: 12px;">0-50 Good</span>
        </div>
        <div style="margin: 5px 0; display: flex; align-items: center;">
            <div style="width: 20px; height: 20px; background: #92D050; border-radius: 50%; margin-right: 8px;"></div>
            <span style="font-size: 12px;">51-100 Satisfactory</span>
        </div>
        <div style="margin: 5px 0; display: flex; align-items: center;">
            <div style="width: 20px; height: 20px; background: #FFFF00; border-radius: 50%; margin-right: 8px;"></div>
            <span style="font-size: 12px;">101-200 Moderate</span>
        </div>
        <div style="margin: 5px 0; display: flex; align-items: center;">
            <div style="width: 20px; height: 20px; background: #FF9900; border-radius: 50%; margin-right: 8px;"></div>
            <span style="font-size: 12px;">201-300 Poor</span>
        </div>
        <div style="margin: 5px 0; display: flex; align-items: center;">
            <div style="width: 20px; height: 20px; background: #FF0000; border-radius: 50%; margin-right: 8px;"></div>
            <span style="font-size: 12px;">301-400 V.Poor</span>
        </div>
        <div style="margin: 5px 0; display: flex; align-items: center;">
            <div style="width: 20px; height: 20px; background: #C00000; border-radius: 50%; margin-right: 8px;"></div>
            <span style="font-size: 12px;">400+ Severe</span>
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def create_atmospheric_heatmap(df_global):
    """Create premium 3D-style atmospheric risk heatmap using Plotly"""
    
    # Prepare data
    data_matrix = []
    factors = ['Stubble Fires', 'Ventilation', 'Rain Event']
    
    for factor in factors:
        if factor == 'Stubble Fires':
            values = df_global['Stubble Fires'].tolist()
            # Normalize to 0-1 (higher = worse)
            max_val = max(values) if max(values) > 0 else 1
            normalized = [v / max_val for v in values]
        elif factor == 'Ventilation':
            values = df_global['Ventilation Index'].tolist()
            # Normalize and invert (lower ventilation = worse)
            max_val = max(values) if max(values) > 0 else 1
            normalized = [1 - (v / max_val) for v in values]
        else:  # Rain
            normalized = [0 if v == 0 else -0.5 for v in df_global['Rain Occurred'].tolist()]
        
        data_matrix.append(normalized)
    
    fig = go.Figure(data=go.Heatmap(
        z=data_matrix,
        x=list(range(1, len(df_global) + 1)),
        y=factors,
        colorscale=[
            [0, '#4facfe'],      # Blue - Good
            [0.3, '#00f2fe'],    # Cyan
            [0.5, '#ffd93d'],    # Yellow - Moderate
            [0.7, '#ff6b6b'],    # Orange - Bad
            [1, '#c92a2a']       # Red - Severe
        ],
        showscale=False,
        hovertemplate='Day %{x}<br>%{y}<br>Risk: %{z:.2f}<extra></extra>',
        zmin=-0.5,
        zmax=1
    ))
    
    fig.update_layout(
        title=dict(
            text='',
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='Day',
            showgrid=False,
            zeroline=False,
            tickmode='linear',
            tick0=1,
            dtick=5,
            color='#a0aec0'
        ),
        yaxis=dict(
            title='',
            showgrid=False,
            zeroline=False,
            color='#a0aec0'
        ),
        plot_bgcolor='#1a202c',
        paper_bgcolor='#1a202c',
        height=200,
        margin=dict(l=120, r=20, t=20, b=50),
        font=dict(size=12, family='Arial', color='#e2e8f0')
    )
    
    return fig

def create_pollution_trends_chart(df_zones):
    """Create premium interactive pollution trends using Plotly"""
    
    fig = go.Figure()
    
    zones = df_zones['Zone'].unique()
    colors = px.colors.qualitative.Set2
    
    for i, zone in enumerate(zones):
        zone_data = df_zones[df_zones['Zone'] == zone]
        
        fig.add_trace(go.Scatter(
            x=zone_data['Day'],
            y=zone_data['AQI'],
            mode='lines+markers',
            name=zone,
            line=dict(width=3, color=colors[i % len(colors)]),
            marker=dict(size=6),
            hovertemplate='<b>%{fullData.name}</b><br>Day %{x}<br>AQI: %{y:.0f}<extra></extra>'
        ))
    
    fig.update_layout(
        title='',
        xaxis=dict(
            title='Day',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            zeroline=False,
            color='#a0aec0'
        ),
        yaxis=dict(
            title='Air Quality Index (AQI)',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            zeroline=False,
            color='#a0aec0'
        ),
        plot_bgcolor='#1a202c',
        paper_bgcolor='#1a202c',
        height=400,
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(color='#e2e8f0')
        ),
        margin=dict(l=60, r=20, t=40, b=60),
        font=dict(size=12, family='Arial', color='#e2e8f0')
    )
    
    # Add AQI category bands
    fig.add_hrect(y0=0, y1=50, fillcolor="#00B050", opacity=0.1, line_width=0)
    fig.add_hrect(y0=50, y1=100, fillcolor="#92D050", opacity=0.1, line_width=0)
    fig.add_hrect(y0=100, y1=200, fillcolor="#FFFF00", opacity=0.1, line_width=0)
    fig.add_hrect(y0=200, y1=300, fillcolor="#FF9900", opacity=0.1, line_width=0)
    fig.add_hrect(y0=300, y1=400, fillcolor="#FF0000", opacity=0.1, line_width=0)
    
    return fig

# --- SESSION STATE INITIALIZATION ---
if 'custom_params' not in st.session_state:
    st.session_state.custom_params = None
if 'show_modal' not in st.session_state:
    st.session_state.show_modal = False
if 'df_zones' not in st.session_state:
    st.session_state.df_zones = None
    st.session_state.df_global = None
    st.session_state.zone_locs = None
if 'start_month' not in st.session_state:
    st.session_state.start_month = 'Nov'
if 'sim_days' not in st.session_state:
    st.session_state.sim_days = 30

# --- MAIN SIMULATION FUNCTION ---
def run_simulation(month, days, custom_params=None):
    model = DelhiAirshed(start_month=month, start_day=1, custom_params=custom_params)
    
    global_stats = []
    zone_stats = []
    zone_locations = []

    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(days):
        model.step()
        
        if i % 3 == 0 or i == days - 1:
            status_text.markdown(f"**Simulating Day {i+1}/{days}** ({model.month}-{model.current_day})")
        
        ventilation_index = model.regional_wind_speed * model.base_mixing_height
        
        global_stats.append({
            "Day": i + 1,
            "DateLabel": f"{model.month}-{model.current_day}",
            "Wind Speed (km/h)": round(model.regional_wind_speed, 1),
            "Wind Direction": model.regional_wind_direction,
            "Stubble Fires": model.stubble_fire_count,
            "Rain Occurred": 100 if model.rain_occurred else 0, 
            "Mixing Height (m)": model.base_mixing_height,
            "Ventilation Index": round(ventilation_index, 0)
        })
        
        for agent in model.agents:
            aqi_val = calculate_aqi(agent.pm25_concentration)
            
            if i == days - 1: 
                zone_locations.append({
                    "name": agent.name,
                    "lat": agent.location['lat'],
                    "lon": agent.location['lon'],
                    "aqi": aqi_val,
                    "pm25": agent.pm25_concentration,
                    "desc": agent.zone_type
                })

            garbage_kg = agent.breakdown.get("Garbage", 0.0)
            transport_kg = agent.breakdown.get("Transport", 0.0)
            dust_kg = agent.breakdown.get("Dust", 0.0)
            industry_kg = agent.breakdown.get("Industry", 0.0)
            construction_kg = agent.breakdown.get("Construction", 0.0)
            secondary_kg = agent.breakdown.get("Secondary", 0.0)

            local_load_kg = agent.breakdown.get("Total_Local_Load_kg", 1.0)
            local_conc = agent.breakdown.get("Local_Concentration", 0.0)
            stubble_conc = agent.breakdown.get("Stubble_Concentration", 0.0)
            
            if local_load_kg == 0: local_load_kg = 1.0
            
            def get_conc(kg_val):
                return (kg_val / local_load_kg) * local_conc

            row = {
                "Day": i + 1,
                "DateLabel": f"{model.month}-{model.current_day}",
                "Zone": agent.name,
                "PM2.5": round(agent.pm25_concentration, 1),
                "AQI": round(aqi_val, 0),
                "Category": get_aqi_category(aqi_val),
                
                "Transport_Conc": get_conc(transport_kg),
                "Dust_Conc": get_conc(dust_kg),
                "Industry_Conc": get_conc(industry_kg),
                "Garbage_Conc": get_conc(garbage_kg),
                "Construction_Conc": get_conc(construction_kg),
                "Secondary_Conc": get_conc(secondary_kg),
                "Stubble_Conc": stubble_conc,

                "Garbage_Load_kg": garbage_kg,
                "Transport_Load_kg": transport_kg,
                "Dust_Load_kg": dust_kg,
                "Industry_Load_kg": industry_kg,
                "Construction_Load_kg": construction_kg,
                "Secondary_Load_kg": secondary_kg,

                "Stubble_Fires_Count": model.stubble_fire_count,
                "Rain_Event": "Yes" if model.rain_occurred else "No",
                "Regional_Wind_Speed": round(model.regional_wind_speed, 1),
                "Zone_Wind_Speed": round(agent.wind_speed, 1),
                "Wind_Direction": model.regional_wind_direction,
                "Regional_Mixing_Height": model.base_mixing_height,
                "Zone_Mixing_Height": round(agent.mixing_height, 1),
                "Fog_Occurred": "Yes" if agent.is_foggy else "No",
            }
            zone_stats.append(row)
        
        progress_bar.progress((i + 1) / days)
    
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(global_stats), pd.DataFrame(zone_stats), zone_locations

# --- HEADER ---
st.markdown("""
<div class='dashboard-header'>
    <h1 class='dashboard-title'>🌫️ Delhi Airshed Simulator</h1>
    <p class='dashboard-subtitle'>Physics-based air quality modeling with interactive parameter control</p>
</div>
""", unsafe_allow_html=True)

# --- CONTROL BAR ---
col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns([2, 2, 2, 1])

with col_ctrl1:
    start_month = st.selectbox("📅 Start Month", 
        ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        index=["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"].index(st.session_state.start_month),
        key='month_select')
    st.session_state.start_month = start_month

with col_ctrl2:
    sim_days = st.slider("⏱️ Duration (Days)", 7, 180, st.session_state.sim_days, key='days_select')
    st.session_state.sim_days = sim_days

with col_ctrl3:
    status_mode = "Custom Parameters" if st.session_state.custom_params else "Default Parameters"
    status_class = "status-custom" if st.session_state.custom_params else "status-default"
    st.markdown(f"<div style='margin-top:25px;'><span class='status-badge {status_class}'>{status_mode}</span></div>", 
                unsafe_allow_html=True)

with col_ctrl4:
    if st.button("⚙️ Configure", key='config_btn', use_container_width=True):
        st.session_state.show_modal = True
        st.rerun()

# --- RUN BUTTON (PROMINENT) ---
st.markdown("<div style='margin: 2rem 0;'>", unsafe_allow_html=True)
if st.button("🚀 RUN SIMULATION", key='run_btn', use_container_width=True):
    with st.spinner("🔄 Running simulation..."):
        g, z, l = run_simulation(start_month, sim_days, st.session_state.custom_params)
        st.session_state.df_global = g
        st.session_state.df_zones = z
        st.session_state.zone_locs = l
    st.success("✅ Simulation Complete!", icon="✅")
st.markdown("</div>", unsafe_allow_html=True)

# --- CONFIGURATION MODAL ---
if st.session_state.show_modal:
    # Create modal using dialog (Streamlit native)
    @st.dialog("⚙️ Advanced Parameter Configuration", width="large")
    def show_configuration_modal():
        st.markdown("### Configure Model Parameters")
        st.info("💡 Customize any parameter below. Leave unchecked sections will use validated defaults.")
        
        tabs = st.tabs(["🏙️ Zones", "🌦️ Meteorology", "💨 Emissions"])
        
        # Initialize temp storage
        if 'temp_params' not in st.session_state:
            st.session_state.temp_params = {}
        
        with tabs[0]:
            st.markdown("#### Zone Configurations")
            st.info("💡 Configure vehicle profiles and zone characteristics for each of the 5 zones.")
            
            # Anand Vihar
            with st.expander("📍 Anand Vihar (Industrial Edge)", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**🚛 Vehicle Counts**")
                    av_trucks = st.number_input("Trucks", 0, 50000, 14000, 1000, key="av_trucks")
                    av_buses = st.number_input("Buses", 0, 50000, 15000, 1000, key="av_buses")
                    av_cars = st.number_input("Cars", 0, 150000, 50000, 5000, key="av_cars")
                    av_2w = st.number_input("Two Wheelers", 0, 150000, 60000, 5000, key="av_2w")
                    av_autos = st.number_input("Autos", 0, 50000, 20000, 1000, key="av_autos")
                
                with col2:
                    st.markdown("**⏱️ Average Hours**")
                    av_truck_hrs = st.number_input("Truck Hours", 0.1, 5.0, 1.0, 0.1, key="av_truck_hrs")
                    av_bus_hrs = st.number_input("Bus Hours", 0.1, 5.0, 1.0, 0.1, key="av_bus_hrs")
                    av_car_hrs = st.number_input("Car Hours", 0.1, 5.0, 1.4, 0.1, key="av_car_hrs")
                    av_2w_hrs = st.number_input("2W Hours", 0.1, 5.0, 1.2, 0.1, key="av_2w_hrs")
                    av_auto_hrs = st.number_input("Auto Hours", 0.1, 5.0, 1.5, 0.1, key="av_auto_hrs")
                
                with col3:
                    st.markdown("**🏙️ Zone Characteristics**")
                    av_congestion = st.slider("Congestion Level", 1.0, 5.0, 2.8, 0.1, key="av_cong")
                    av_silt = st.slider("Road Silt Factor", 0.0, 10.0, 6.0, 0.5, key="av_silt")
                    av_ind_dist = st.number_input("Industry Distance (km)", 1, 50, 3, 1, key="av_ind")
                    av_const = st.number_input("Construction Sites", 0, 500, 150, 10, key="av_const")
                    av_fires = st.number_input("Garbage Fires", 0, 2000, 500, 50, key="av_fires")
            
            # Lutyens Delhi
            with st.expander("📍 Lutyens Delhi (VIP Zone)", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**🚛 Vehicle Counts**")
                    ld_trucks = st.number_input("Trucks", 0, 50000, 1500, 100, key="ld_trucks")
                    ld_buses = st.number_input("Buses", 0, 50000, 6000, 500, key="ld_buses")
                    ld_cars = st.number_input("Cars", 0, 150000, 80000, 5000, key="ld_cars")
                    ld_2w = st.number_input("Two Wheelers", 0, 150000, 40000, 5000, key="ld_2w")
                    ld_autos = st.number_input("Autos", 0, 50000, 9000, 500, key="ld_autos")
                
                with col2:
                    st.markdown("**⏱️ Average Hours**")
                    ld_truck_hrs = st.number_input("Truck Hours", 0.1, 5.0, 0.8, 0.1, key="ld_truck_hrs")
                    ld_bus_hrs = st.number_input("Bus Hours", 0.1, 5.0, 0.8, 0.1, key="ld_bus_hrs")
                    ld_car_hrs = st.number_input("Car Hours", 0.1, 5.0, 1.2, 0.1, key="ld_car_hrs")
                    ld_2w_hrs = st.number_input("2W Hours", 0.1, 5.0, 0.8, 0.1, key="ld_2w_hrs")
                    ld_auto_hrs = st.number_input("Auto Hours", 0.1, 5.0, 0.8, 0.1, key="ld_auto_hrs")
                
                with col3:
                    st.markdown("**🏙️ Zone Characteristics**")
                    ld_congestion = st.slider("Congestion Level", 1.0, 5.0, 2.0, 0.1, key="ld_cong")
                    ld_silt = st.slider("Road Silt Factor", 0.0, 10.0, 2.0, 0.5, key="ld_silt")
                    ld_ind_dist = st.number_input("Industry Distance (km)", 1, 50, 30, 1, key="ld_ind")
                    ld_const = st.number_input("Construction Sites", 0, 500, 50, 10, key="ld_const")
                    ld_fires = st.number_input("Garbage Fires", 0, 2000, 50, 10, key="ld_fires")
            
            # Okhla
            with st.expander("📍 Okhla (Industrial Core)", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**🚛 Vehicle Counts**")
                    ok_trucks = st.number_input("Trucks", 0, 50000, 18000, 1000, key="ok_trucks")
                    ok_buses = st.number_input("Buses", 0, 50000, 10000, 1000, key="ok_buses")
                    ok_cars = st.number_input("Cars", 0, 150000, 35000, 5000, key="ok_cars")
                    ok_2w = st.number_input("Two Wheelers", 0, 150000, 70000, 5000, key="ok_2w")
                    ok_autos = st.number_input("Autos", 0, 50000, 18000, 1000, key="ok_autos")
                
                with col2:
                    st.markdown("**⏱️ Average Hours**")
                    ok_truck_hrs = st.number_input("Truck Hours", 0.1, 5.0, 2.0, 0.1, key="ok_truck_hrs")
                    ok_bus_hrs = st.number_input("Bus Hours", 0.1, 5.0, 0.6, 0.1, key="ok_bus_hrs")
                    ok_car_hrs = st.number_input("Car Hours", 0.1, 5.0, 1.5, 0.1, key="ok_car_hrs")
                    ok_2w_hrs = st.number_input("2W Hours", 0.1, 5.0, 2.0, 0.1, key="ok_2w_hrs")
                    ok_auto_hrs = st.number_input("Auto Hours", 0.1, 5.0, 1.5, 0.1, key="ok_auto_hrs")
                
                with col3:
                    st.markdown("**🏙️ Zone Characteristics**")
                    ok_congestion = st.slider("Congestion Level", 1.0, 5.0, 2.5, 0.1, key="ok_cong")
                    ok_silt = st.slider("Road Silt Factor", 0.0, 10.0, 4.5, 0.5, key="ok_silt")
                    ok_ind_dist = st.number_input("Industry Distance (km)", 1, 50, 2, 1, key="ok_ind")
                    ok_const = st.number_input("Construction Sites", 0, 500, 200, 10, key="ok_const")
                    ok_fires = st.number_input("Garbage Fires", 0, 2000, 700, 50, key="ok_fires")
            
            # Uttam Nagar
            with st.expander("📍 Uttam Nagar (Dense Residential)", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**🚛 Vehicle Counts**")
                    un_trucks = st.number_input("Trucks", 0, 50000, 10000, 1000, key="un_trucks")
                    un_buses = st.number_input("Buses", 0, 50000, 40000, 5000, key="un_buses")
                    un_cars = st.number_input("Cars", 0, 150000, 30000, 5000, key="un_cars")
                    un_2w = st.number_input("Two Wheelers", 0, 150000, 100000, 5000, key="un_2w")
                    un_autos = st.number_input("Autos", 0, 50000, 25000, 1000, key="un_autos")
                
                with col2:
                    st.markdown("**⏱️ Average Hours**")
                    un_truck_hrs = st.number_input("Truck Hours", 0.1, 5.0, 1.0, 0.1, key="un_truck_hrs")
                    un_bus_hrs = st.number_input("Bus Hours", 0.1, 5.0, 1.5, 0.1, key="un_bus_hrs")
                    un_car_hrs = st.number_input("Car Hours", 0.1, 5.0, 2.0, 0.1, key="un_car_hrs")
                    un_2w_hrs = st.number_input("2W Hours", 0.1, 5.0, 2.5, 0.1, key="un_2w_hrs")
                    un_auto_hrs = st.number_input("Auto Hours", 0.1, 5.0, 2.0, 0.1, key="un_auto_hrs")
                
                with col3:
                    st.markdown("**🏙️ Zone Characteristics**")
                    un_congestion = st.slider("Congestion Level", 1.0, 5.0, 3.0, 0.1, key="un_cong")
                    un_silt = st.slider("Road Silt Factor", 0.0, 10.0, 5.5, 0.5, key="un_silt")
                    un_ind_dist = st.number_input("Industry Distance (km)", 1, 50, 15, 1, key="un_ind")
                    un_const = st.number_input("Construction Sites", 0, 500, 180, 10, key="un_const")
                    un_fires = st.number_input("Garbage Fires", 0, 2000, 1000, 50, key="un_fires")
            
            # Bahadurgarh
            with st.expander("📍 Bahadurgarh (Peri-Urban)", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**🚛 Vehicle Counts**")
                    bg_trucks = st.number_input("Trucks", 0, 50000, 15000, 1000, key="bg_trucks")
                    bg_buses = st.number_input("Buses", 0, 50000, 18000, 1000, key="bg_buses")
                    bg_cars = st.number_input("Cars", 0, 150000, 40000, 5000, key="bg_cars")
                    bg_2w = st.number_input("Two Wheelers", 0, 150000, 55000, 5000, key="bg_2w")
                    bg_autos = st.number_input("Autos", 0, 50000, 15000, 1000, key="bg_autos")
                
                with col2:
                    st.markdown("**⏱️ Average Hours**")
                    bg_truck_hrs = st.number_input("Truck Hours", 0.1, 5.0, 1.5, 0.1, key="bg_truck_hrs")
                    bg_bus_hrs = st.number_input("Bus Hours", 0.1, 5.0, 0.6, 0.1, key="bg_bus_hrs")
                    bg_car_hrs = st.number_input("Car Hours", 0.1, 5.0, 1.8, 0.1, key="bg_car_hrs")
                    bg_2w_hrs = st.number_input("2W Hours", 0.1, 5.0, 1.2, 0.1, key="bg_2w_hrs")
                    bg_auto_hrs = st.number_input("Auto Hours", 0.1, 5.0, 1.2, 0.1, key="bg_auto_hrs")
                
                with col3:
                    st.markdown("**🏙️ Zone Characteristics**")
                    bg_congestion = st.slider("Congestion Level", 1.0, 5.0, 2.5, 0.1, key="bg_cong")
                    bg_silt = st.slider("Road Silt Factor", 0.0, 10.0, 7.0, 0.5, key="bg_silt")
                    bg_ind_dist = st.number_input("Industry Distance (km)", 1, 50, 1, 1, key="bg_ind")
                    bg_const = st.number_input("Construction Sites", 0, 500, 250, 10, key="bg_const")
                    bg_fires = st.number_input("Garbage Fires", 0, 2000, 400, 50, key="bg_fires")
        
        with tabs[1]:
            st.markdown("#### Meteorology Parameters")
            st.info("💡 Configure seasonal mixing heights, wind patterns, fog probabilities, and event controls.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🌡️ Seasonal Mixing Heights (m)**")
                mix_jan = st.number_input("January", 100, 2000, 300, 50, key="mix_jan")
                mix_feb = st.number_input("February", 100, 2000, 400, 50, key="mix_feb")
                mix_mar = st.number_input("March", 100, 2000, 800, 50, key="mix_mar")
                mix_apr = st.number_input("April", 100, 2000, 1200, 50, key="mix_apr")
                mix_may = st.number_input("May", 100, 2000, 1500, 50, key="mix_may")
                mix_jun = st.number_input("June", 100, 2000, 1000, 50, key="mix_jun")
            
            with col2:
                st.markdown("**🌡️ Seasonal Mixing Heights (m)**")
                mix_jul = st.number_input("July", 100, 2000, 800, 50, key="mix_jul")
                mix_aug = st.number_input("August", 100, 2000, 800, 50, key="mix_aug")
                mix_sep = st.number_input("September", 100, 2000, 900, 50, key="mix_sep")
                mix_oct = st.number_input("October", 100, 2000, 700, 50, key="mix_oct")
                mix_nov = st.number_input("November", 100, 2000, 400, 50, key="mix_nov")
                mix_dec = st.number_input("December", 100, 2000, 250, 50, key="mix_dec")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**💨 Initial Wind Conditions**")
                init_wind_speed = st.slider("Wind Speed (km/h)", 0.5, 15.0, 3.0, 0.5, key="init_wind_speed")
                init_wind_dir = st.selectbox("Wind Direction", 
                    ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], index=7, key="init_wind_dir")
            
            with col2:
                st.markdown("**🌫️ Fog Probability by Month**")
                fog_jan = st.slider("January", 0.0, 1.0, 0.7, 0.05, key="fog_jan")
                fog_dec = st.slider("December", 0.0, 1.0, 0.8, 0.05, key="fog_dec")
                fog_nov = st.slider("November", 0.0, 1.0, 0.6, 0.05, key="fog_nov")
                fog_feb = st.slider("February", 0.0, 1.0, 0.5, 0.05, key="fog_feb")
                fog_oct = st.slider("October", 0.0, 1.0, 0.2, 0.05, key="fog_oct")
                fog_mar = st.slider("March", 0.0, 1.0, 0.1, 0.05, key="fog_mar")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🔥 Stubble Fire Controls**")
                enable_stubble = st.checkbox("Enable Stubble Burning Events", True, key="enable_stubble")
                stubble_mult = st.slider("Stubble Fire Intensity Multiplier", 0.0, 2.0, 1.0, 0.1, key="stubble_mult",
                    help="Multiplies base fire counts (1.0 = normal, 1.5 = 50% more intense)")
            
            with col2:
                st.markdown("**🌧️ Rain Controls**")
                enable_rain = st.checkbox("Enable Rain Events", True, key="enable_rain")
                rain_mult = st.slider("Rain Probability Multiplier", 0.0, 3.0, 1.0, 0.1, key="rain_mult",
                    help="Adjusts seasonal rain probabilities (1.0 = normal)")
        
        with tabs[2]:
            st.markdown("#### Emission Parameters")
            st.info("💡 Configure vehicle emission factors, dust formula, chemistry parameters, and industrial loads.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🚗 Vehicle Emission Factors (g/hr)**")
                ef_trucks = st.number_input("Trucks", 5.0, 100.0, 30.0, 1.0, key="ef_trucks")
                ef_buses = st.number_input("Buses", 5.0, 50.0, 12.0, 1.0, key="ef_buses")
                ef_cars = st.number_input("Cars", 0.5, 10.0, 2.0, 0.1, key="ef_cars")
                ef_2w = st.number_input("Two Wheelers", 0.5, 10.0, 2.0, 0.1, key="ef_2w")
                ef_autos = st.number_input("Autos", 0.5, 10.0, 1.5, 0.1, key="ef_autos")
                
                st.markdown("**🏭 Industrial Emissions (kg/day)**")
                cluster_e = st.number_input("Cluster E (Small Industry)", 5000, 50000, 15000, 1000, key="cluster_e")
                cluster_s = st.number_input("Cluster S (Engineering)", 5000, 50000, 12000, 1000, key="cluster_s")
                cluster_nw = st.number_input("Cluster NW (Thermal)", 10000, 100000, 45000, 5000, key="cluster_nw")
                cluster_brick = st.number_input("Cluster Brick (Kilns)", 5000, 50000, 25000, 2000, key="cluster_brick")
            
            with col2:
                st.markdown("**⚗️ Secondary PM Formation**")
                nox_mult = st.slider("NOx Multiplier", 1.0, 15.0, 6.0, 0.5, key="nox_mult")
                fog_conv = st.slider("Fog Conversion Rate", 0.01, 0.5, 0.15, 0.01, key="fog_conv")
                clear_conv = st.slider("Clear Conversion Rate", 0.001, 0.15, 0.03, 0.005, key="clear_conv")
                
                st.markdown("**🏗️ Dust Formula (AP-42)**")
                dust_k = st.number_input("k factor", 0.05, 0.5, 0.15, 0.01, format="%.3f", key="dust_k")
                dust_silt_exp = st.number_input("Silt exponent", 0.5, 1.5, 0.91, 0.01, format="%.2f", key="dust_silt_exp")
                dust_weight_exp = st.number_input("Weight exponent", 0.5, 1.5, 1.02, 0.01, format="%.2f", key="dust_weight_exp")
                
                st.markdown("**🗑️ Garbage & Construction**")
                garbage_ef = st.number_input("Garbage Fire Emission (g/fire)", 100.0, 1000.0, 300.0, 10.0, key="garbage_ef")
                construction_ef = st.number_input("Construction Emission (kg/site/day)", 0.5, 10.0, 2.0, 0.1, key="construction_ef")
        
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("💾 Apply Configuration", use_container_width=True):
                # Save comprehensive configuration
                st.session_state.custom_params = {
                    'zones': {
                        'Anand Vihar': {
                            'vehicles': {
                                'trucks': {'count': av_trucks, 'avg_stay_hrs': av_truck_hrs},
                                'buses': {'count': av_buses, 'avg_stay_hrs': av_bus_hrs},
                                'cars': {'count': av_cars, 'avg_stay_hrs': av_car_hrs},
                                'two_wheelers': {'count': av_2w, 'avg_stay_hrs': av_2w_hrs},
                                'autos': {'count': av_autos, 'avg_stay_hrs': av_auto_hrs}
                            },
                            'congestion': av_congestion, 'silt': av_silt, 'ind_dist': av_ind_dist,
                            'const': av_const, 'fires': av_fires
                        },
                        'Lutyens Delhi': {
                            'vehicles': {
                                'trucks': {'count': ld_trucks, 'avg_stay_hrs': ld_truck_hrs},
                                'buses': {'count': ld_buses, 'avg_stay_hrs': ld_bus_hrs},
                                'cars': {'count': ld_cars, 'avg_stay_hrs': ld_car_hrs},
                                'two_wheelers': {'count': ld_2w, 'avg_stay_hrs': ld_2w_hrs},
                                'autos': {'count': ld_autos, 'avg_stay_hrs': ld_auto_hrs}
                            },
                            'congestion': ld_congestion, 'silt': ld_silt, 'ind_dist': ld_ind_dist,
                            'const': ld_const, 'fires': ld_fires
                        },
                        'Okhla': {
                            'vehicles': {
                                'trucks': {'count': ok_trucks, 'avg_stay_hrs': ok_truck_hrs},
                                'buses': {'count': ok_buses, 'avg_stay_hrs': ok_bus_hrs},
                                'cars': {'count': ok_cars, 'avg_stay_hrs': ok_car_hrs},
                                'two_wheelers': {'count': ok_2w, 'avg_stay_hrs': ok_2w_hrs},
                                'autos': {'count': ok_autos, 'avg_stay_hrs': ok_auto_hrs}
                            },
                            'congestion': ok_congestion, 'silt': ok_silt, 'ind_dist': ok_ind_dist,
                            'const': ok_const, 'fires': ok_fires
                        },
                        'Uttam Nagar': {
                            'vehicles': {
                                'trucks': {'count': un_trucks, 'avg_stay_hrs': un_truck_hrs},
                                'buses': {'count': un_buses, 'avg_stay_hrs': un_bus_hrs},
                                'cars': {'count': un_cars, 'avg_stay_hrs': un_car_hrs},
                                'two_wheelers': {'count': un_2w, 'avg_stay_hrs': un_2w_hrs},
                                'autos': {'count': un_autos, 'avg_stay_hrs': un_auto_hrs}
                            },
                            'congestion': un_congestion, 'silt': un_silt, 'ind_dist': un_ind_dist,
                            'const': un_const, 'fires': un_fires
                        },
                        'Bahadurgarh': {
                            'vehicles': {
                                'trucks': {'count': bg_trucks, 'avg_stay_hrs': bg_truck_hrs},
                                'buses': {'count': bg_buses, 'avg_stay_hrs': bg_bus_hrs},
                                'cars': {'count': bg_cars, 'avg_stay_hrs': bg_car_hrs},
                                'two_wheelers': {'count': bg_2w, 'avg_stay_hrs': bg_2w_hrs},
                                'autos': {'count': bg_autos, 'avg_stay_hrs': bg_auto_hrs}
                            },
                            'congestion': bg_congestion, 'silt': bg_silt, 'ind_dist': bg_ind_dist,
                            'const': bg_const, 'fires': bg_fires
                        }
                    },
                    'mixing_heights': {
                        'Jan': mix_jan, 'Feb': mix_feb, 'Mar': mix_mar, 'Apr': mix_apr,
                        'May': mix_may, 'Jun': mix_jun, 'Jul': mix_jul, 'Aug': mix_aug,
                        'Sep': mix_sep, 'Oct': mix_oct, 'Nov': mix_nov, 'Dec': mix_dec
                    },
                    'init_wind_speed': init_wind_speed,
                    'init_wind_dir': init_wind_dir,
                    'fog_probs': {
                        'Jan': fog_jan, 'Dec': fog_dec, 'Nov': fog_nov,
                        'Feb': fog_feb, 'Oct': fog_oct, 'Mar': fog_mar
                    },
                    'enable_stubble': enable_stubble,
                    'stubble_multiplier': stubble_mult,
                    'enable_rain': enable_rain,
                    'rain_multiplier': rain_mult,
                    'emission_factors': {
                        'trucks': ef_trucks, 'buses': ef_buses, 'cars': ef_cars,
                        'two_wheelers': ef_2w, 'autos': ef_autos
                    },
                    'dust_k': dust_k,
                    'dust_silt_exp': dust_silt_exp,
                    'dust_weight_exp': dust_weight_exp,
                    'nox_multiplier': nox_mult,
                    'fog_conversion': fog_conv,
                    'clear_conversion': clear_conv,
                    'industrial_loads': {
                        'Cluster_E': cluster_e,
                        'Cluster_S': cluster_s,
                        'Cluster_NW': cluster_nw,
                        'Cluster_Brick': cluster_brick
                    },
                    'garbage_emission': garbage_ef,
                    'construction_emission': construction_ef
                }
                st.session_state.show_modal = False
                st.success("✅ Configuration saved!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset to Defaults", use_container_width=True):
                st.session_state.custom_params = None
                st.success("✅ Reset to defaults!")
        
        with col3:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.show_modal = False
                st.rerun()
    
    show_configuration_modal()

# --- RESULTS DASHBOARD ---
if st.session_state.df_zones is not None:
    df_global = st.session_state.df_global
    df_zones = st.session_state.df_zones
    zone_locs = st.session_state.zone_locs
    st.session_state.last_sim_days = sim_days

    # --- KEY METRICS ---
    st.markdown("### 📊 Key Performance Indicators")
    
    last_day_df = df_zones[df_zones["Day"] == st.session_state.get("last_sim_days", df_zones["Day"].max())]
    avg_aqi = last_day_df["AQI"].mean()
    worst_zone = last_day_df.loc[last_day_df["AQI"].idxmax()]
    best_zone = last_day_df.loc[last_day_df["AQI"].idxmin()]
    avg_pm25 = last_day_df["PM2.5"].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Average AQI</div>
            <div class='metric-value' style='color: {get_aqi_color(avg_aqi)};'>{avg_aqi:.0f}</div>
            <div style='color: #666; font-size: 0.9rem;'>{get_aqi_category(avg_aqi)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Worst Zone</div>
            <div class='metric-value' style='color: {get_aqi_color(worst_zone["AQI"])}; font-size: 1.8rem;'>{worst_zone['Zone']}</div>
            <div style='color: #666; font-size: 0.9rem;'>AQI: {worst_zone['AQI']:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Best Zone</div>
            <div class='metric-value' style='color: {get_aqi_color(best_zone["AQI"])}; font-size: 1.8rem;'>{best_zone['Zone']}</div>
            <div style='color: #666; font-size: 0.9rem;'>AQI: {best_zone['AQI']:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        rain_events = df_global[df_global['Rain Occurred'] > 0].shape[0]
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Rain Events</div>
            <div class='metric-value' style='color: #4299e1;'>{rain_events}</div>
            <div style='color: #666; font-size: 0.9rem;'>{(rain_events/sim_days*100):.1f}% of days</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- MAIN VISUALIZATIONS ---
    col_map, col_trend = st.columns([1, 2])
    
    with col_map:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h3 class='chart-title'>🗺️ Spatial Distribution</h3>", unsafe_allow_html=True)
        premium_map = create_premium_map(zone_locs)
        st_folium(premium_map, height=500, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_trend:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h3 class='chart-title'>📈 Pollution Trends</h3>", unsafe_allow_html=True)
        trend_chart = create_pollution_trends_chart(df_zones)
        st.plotly_chart(trend_chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # --- ATMOSPHERIC RISK MATRIX ---
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("<h3 class='chart-title'>🌪️ Atmospheric Risk Matrix</h3>", unsafe_allow_html=True)
    risk_heatmap = create_atmospheric_heatmap(df_global)
    st.plotly_chart(risk_heatmap, use_container_width=True)
    st.markdown("<p style='color: #666; font-size: 0.9rem; margin-top: -10px;'>🔴 Red = High Risk | 🔵 Blue = Low Risk | ⚪ White = Rain Event (Beneficial)</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # --- ANALYSIS TABS ---
    st.markdown("### 🔬 Detailed Analysis")
    
    tab1, tab2, tab3 = st.tabs(["📊 Source Apportionment", "📍 Zone Deep Dive", "💾 Export Data"])
    
    with tab1:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        
        col_zone, col_view = st.columns([2, 1])
        with col_zone:
            selected_zone = st.selectbox("Select Zone for Analysis:", df_zones["Zone"].unique(), key='source_zone')
        with col_view:
            view_type = st.radio("View Type:", ["Area Chart", "Pie Chart"], horizontal=True, key='source_view')
        
        zone_data = df_zones[df_zones["Zone"] == selected_zone]
        
        if view_type == "Area Chart":
            source_cols = ["Transport_Conc", "Dust_Conc", "Industry_Conc", 
                          "Stubble_Conc", "Garbage_Conc", "Construction_Conc", "Secondary_Conc"]
            
            fig = go.Figure()
            
            for col in source_cols:
                source_name = col.replace("_Conc", "")
                fig.add_trace(go.Scatter(
                    x=zone_data['Day'],
                    y=zone_data[col],
                    mode='lines',
                    name=source_name,
                    stackgroup='one',
                    fillcolor=px.colors.qualitative.Set2[source_cols.index(col) % len(px.colors.qualitative.Set2)]
                ))
            
            fig.update_layout(
                xaxis=dict(title='Day'),
                yaxis=dict(title='PM2.5 Contribution (µg/m³)'),
                hovermode='x unified',
                height=400,
                showlegend=True,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:  # Pie Chart
            final_day = zone_data[zone_data["Day"] == sim_days].iloc[0]
            
            pie_data = {
                'Transport': final_day['Transport_Conc'],
                'Dust': final_day['Dust_Conc'],
                'Industry': final_day['Industry_Conc'],
                'Stubble': final_day['Stubble_Conc'],
                'Garbage': final_day['Garbage_Conc'],
                'Construction': final_day['Construction_Conc'],
                'Secondary': final_day['Secondary_Conc']
            }
            
            fig = go.Figure(data=[go.Pie(
                labels=list(pie_data.keys()),
                values=list(pie_data.values()),
                hole=0.4,
                marker=dict(colors=px.colors.qualitative.Set2)
            )])
            
            fig.update_layout(
                title=f"Final Day Source Distribution - {selected_zone}",
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        
        zone_select = st.selectbox("Choose Zone:", df_zones["Zone"].unique(), key='deep_zone')
        zone_detail = df_zones[df_zones["Zone"] == zone_select]
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Avg AQI", f"{zone_detail['AQI'].mean():.0f}")
        col2.metric("Max AQI", f"{zone_detail['AQI'].max():.0f}")
        col3.metric("Min AQI", f"{zone_detail['AQI'].min():.0f}")
        col4.metric("Avg PM2.5", f"{zone_detail['PM2.5'].mean():.1f} µg/m³")
        
        # Time series
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=zone_detail['Day'],
            y=zone_detail['PM2.5'],
            mode='lines+markers',
            name='PM2.5',
            line=dict(color='#f5576c', width=3),
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=zone_detail['Day'],
            y=zone_detail['Zone_Mixing_Height'],
            mode='lines',
            name='Mixing Height',
            line=dict(color='#4facfe', width=2, dash='dash'),
            yaxis='y2'
        ))
        
        fig.update_layout(
            xaxis=dict(title='Day'),
            yaxis=dict(title='PM2.5 (µg/m³)', side='left'),
            yaxis2=dict(title='Mixing Height (m)', side='right', overlaying='y'),
            hovermode='x unified',
            height=350,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("#### 📥 Download Simulation Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv_zones = df_zones.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📊 Download Zone Data (CSV)",
                data=csv_zones,
                file_name=f"delhi_zones_{start_month}_{sim_days}days.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            csv_global = df_global.to_csv(index=False).encode('utf-8')
            st.download_button(
                "🌦️ Download Weather Data (CSV)",
                data=csv_global,
                file_name=f"delhi_weather_{start_month}_{sim_days}days.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with st.expander("📋 Data Preview"):
            st.dataframe(df_zones.head(20), use_container_width=True, height=300)
        
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- WELCOME SCREEN ---
    st.markdown("""
    <div class='info-box'>
        <h3 style='margin-top: 0;'>👋 Welcome to Delhi Airshed Simulator</h3>
        <p>A physics-based air quality model for understanding Delhi's pollution dynamics.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='chart-container'>
            <h4>✨ Features</h4>
            <ul style='line-height: 1.8;'>
                <li><b>Box Model Physics:</b> Ventilation-based dilution</li>
                <li><b>Source Apportionment:</b> 7 emission categories</li>
                <li><b>Daily Timestep:</b> 24-hour pollution cycles</li>
                <li><b>5 Representative Zones:</b> Spatial variation</li>
                <li><b>Full Parameter Control:</b> Customize everything</li>
                <li><b>Premium Visualizations:</b> Interactive charts & maps</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='chart-container'>
            <h4>🚀 Quick Start</h4>
            <ol style='line-height: 1.8;'>
                <li>Select <b>start month</b> and <b>duration</b> above</li>
                <li>Click <b>"RUN SIMULATION"</b> (uses validated defaults)</li>
                <li>Explore results: maps, trends, source analysis</li>
                <li><i>Optional:</i> Click <b>"⚙️ Configure"</b> to customize parameters</li>
            </ol>
            <p style='margin-top: 1.5rem; color: orange;'>
                <i>💡 Tip: Start with default parameters to see baseline behavior, 
                then customize to test scenarios.</i>
            </p>
        </div>
        """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p style='margin: 0;'>🌫️ <b>Delhi Airshed Simulator v3.0</b> | Physics-Based Air Quality Modeling</p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Educational tool for research and policy exploration</p>
</div>
""", unsafe_allow_html=True)