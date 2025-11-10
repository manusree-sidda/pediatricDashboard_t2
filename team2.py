# app.py
# run - 
# streamlit run team2.py
import streamlit as st
import datetime as dt
import math
import pandas as pd
import plotly.express as px

#__________________Loading the data set______________

df = pd.read_csv("MS_copy_DeID_Complete.csv")
df['PatID'] = df['PatID'].astype(str)
def get_patient_value(data, key, default="_"):
    val = data[key] 
    if pd.isna(val):
        return default
    return val
#__________________Data Preparation__________________

df['Gender_label'] = df['Gender'].map({0: "Girl", 1: "Boy"}).fillna("Unknown")
df['Premature_label'] = df['Premature'].map({0: "No", 1: "Yes"}).fillna("Unknown")

race_map = {1: 'White',2: 'Black',3: 'Asian', 4: 'American Indian', 5: 'Native Hawaiian', 6: 'Other Pacific Islander'}
df['Race_label'] = df['Race'].map(race_map).fillna('Other/Unknown')

ethnicity_map = { 0: 'Non-Hispanic', 1: 'Hispanic/Latino', 2: 'Other/Unknown' }
df['Ethnicity_label'] = df['Ethnicity'].map(ethnicity_map).fillna('Other/Unknown')

if 'SyndromeTerm' in df.columns:
    df['Syndrome_Present_bool'] = df['SyndromeTerm'] != "No syndromic abnormality identified"    
    df['Fetal_Drug_Exposure_label'] = df['SyndromeTerm'].apply(
        lambda x: "Yes" if x == "Fetal drug exposure" else "No")
else:
    st.warning("Warning: 'SyndromeTerm' column not found. Using default values.")
    df['SyndromeTerm'] = "Column Not Found"
    df['Syndrome_Present_bool'] = False
    df['Fetal_Drug_Exposure_label'] = "No"

st.set_page_config(page_title="Pediatric Dashboard", layout="wide")



# ----------------- THEME FUNCTION -----------------
def get_theme_css(sex):
    """Generate theme CSS based on gender selection"""
    if sex == "Boy":
        # Boy theme - Blue colors
        theme = {
            "bg": "#EFF4F8",
            "panel": "#E8F1FA",
            "border": "#B8D4E8",
            "ink": "#1b1e28",
            "pill": "#EAF3FF",
            "pillborder": "#C7DBFF",
            "hover": "#D6EBFF",
            "selected": "#C7E3FF",
            "card_shadow": "#d0e0f0",
            "panel_border": "#A8C8E0",
            "header_bg": "#A8C8E8",
            "header_border": "#8BB5D8",
            "iconbox1_border": "#7BB3D0",
            "iconbox1_bg": "#C8E3F5",
            "iconbox2_border": "#9DB8C8",
            "iconbox2_bg": "#D0E8F5",
            "iconbox3_border": "#6BA5C8",
            "iconbox3_bg": "#B8DDF5",
            "eventbox_shadow": "#d0e0f0"
        }
    else:
        # Girl theme - Pink colors (default)
        theme = {
            "bg": "#F6EFEF",
            "panel": "#FBECEC",
            "border": "#E1C1C3",
            "ink": "#1b1e28",
            "pill": "#EAF3FF",
            "pillborder": "#C7DBFF",
            "hover": "#EEF4FF",
            "selected": "#FFE7EC",
            "card_shadow": "#f6d8da",
            "panel_border": "#e8c7cf",
            "header_bg": "#f7c8d8",
            "header_border": "#eab2c6",
            "iconbox1_border": "#E7B6C0",
            "iconbox1_bg": "#FFD7E2",
            "iconbox2_border": "#F0C994",
            "iconbox2_bg": "#FFE8C6",
            "iconbox3_border": "#B6D7FF",
            "iconbox3_bg": "#D0E9FF",
            "eventbox_shadow": "#f6d8da"
        }
    
    return f"""
<style>
/* Remove Streamlit chrome + tighten spacing */
header[data-testid="stHeader"]{{display:none !important;}}
#MainMenu, footer{{visibility:hidden !important;}}
.block-container{{padding-top:6px !important; max-width:1320px;}}

/* Theme - {'Boy' if sex == 'Boy' else 'Girl'} */
:root{{
  --bg:{theme['bg']}; --panel:{theme['panel']}; --border:{theme['border']}; --ink:{theme['ink']};
  --pill:{theme['pill']}; --pillborder:{theme['pillborder']}; --hover:{theme['hover']}; --selected:{theme['selected']};
}}
[data-testid="stAppViewContainer"]{{background:var(--bg);}}
h1,h2,h3,h4,p,div,span{{color:var(--ink);}}

/* Cards & layout bits */
.card{{background:#fff;border:2px solid var(--border);border-radius:16px;padding:12px 14px;box-shadow:0 2px 0 {theme['card_shadow']} inset;margin-bottom:12px;}}
.pinkpanel{{background:var(--panel);border:2px solid {theme['panel_border']};border-radius:10px;overflow:hidden;}}
.headerpink{{background:{theme['header_bg']};border-bottom:2px solid {theme['header_border']};padding:10px 14px;font-weight:900;text-align:center;}}
.pill-blue{{display:inline-block;padding:6px 14px;border-radius:999px;background:#d6e7ff;border:1px solid #bcd6ff;font-weight:900;}}
.iconrow{{display:flex;gap:14px;justify-content:center;padding:12px 0 6px;}}
.iconbox, .iconbox2, .iconbox3{{
  width:70px;height:70px;display:flex;align-items:center;justify-content:center;border-radius:12px;font-size:36px;
}}
.iconbox{{border:2px solid {theme['iconbox1_border']};background:{theme['iconbox1_bg']};}}
.iconbox2{{border:2px solid {theme['iconbox2_border']};background:{theme['iconbox2_bg']};}}
.iconbox3{{border:2px solid {theme['iconbox3_border']};background:{theme['iconbox3_bg']};}}
.sel{{ outline:3px solid #3B82F6; box-shadow:0 0 0 2px #93C5FD inset; }}

.right{{text-align:right;}} .center{{text-align:center;}} .red{{color:#C6002A;font-weight:900;}}

/* Timeline */
.timelinewrap{{padding:12px;}}
.vert{{position:relative;height:520px;margin:0 24px;}}
.vert:before{{content:"";position:absolute;left:50%;top:18px;bottom:18px;width:2px;background:#111;transform:translateX(-50%);}}
.vert:after{{content:"";position:absolute;left:40px;right:40px;top:6px;height:2px;background:#111;}}
.hbot{{position:absolute;left:40px;right:40px;bottom:6px;height:2px;background:#111;}}
.tick{{position:absolute;left:50%;transform:translateX(-50%);}}
.tick .dot{{position:absolute;left:-4px;top:-4px;width:8px;height:8px;background:#111;border-radius:50%;}}
.tick .lbl{{position:absolute;left:20px;top:-10px;width:230px;font-weight:700;}}

/* Event-look boxes */
.eventbox{{border:2px solid var(--border);border-radius:16px;padding:12px;background:#fff;box-shadow:0 2px 0 {theme['eventbox_shadow']} inset;}}
.eventtitle{{font-weight:900;margin:10px 0 6px;}}
.addbtn{{display:inline-block;background:#fff;border:2px solid var(--border);border-radius:999px;padding:8px 20px;font-weight:900;box-shadow:0 2px 0 {theme['eventbox_shadow']} inset;}}

/* ===== DROPDOWN STYLES - HIGH CONTRAST WHITE BACKGROUND ===== */
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div{{
  background:#FFFFFF !important; 
  background-color:#FFFFFF !important; 
  color:#1B1E28 !important; 
  border-color:#C4C4C4 !important;
  min-height:44px; 
  font-weight:800; 
  border-width:2px !important;
}}
.stSelectbox svg, .stMultiSelect svg{{ 
  fill:#1B1E28 !important; 
  color:#1B1E28 !important; 
}}
div[data-baseweb="select"] input{{ 
  color:#1B1E28 !important; 
  font-weight:800; 
  background:#FFFFFF !important;
  background-color:#FFFFFF !important;
}}
div[data-baseweb="select"] input::placeholder{{ 
  color:#8A8A8A !important; 
}}

/* Dropdown menu popover - FORCE WHITE BACKGROUND */
div[data-baseweb="popover"]{{ 
  z-index: 9999 !important; 
  background:#FFFFFF !important;
  background-color:#FFFFFF !important;
}}
div[data-baseweb="popover"] > div{{
  background:#FFFFFF !important;
  background-color:#FFFFFF !important;
}}
div[data-baseweb="menu"]{{
  background:#FFFFFF !important; 
  background-color:#FFFFFF !important;
  color:#1B1E28 !important; 
  border:2px solid #C4C4C4 !important;
  border-radius:12px !important; 
  box-shadow:0 12px 30px rgba(0,0,0,0.25) !important;
}}
div[data-baseweb="menu"] ul{{ 
  background:#FFFFFF !important; 
  background-color:#FFFFFF !important;
  padding:6px !important; 
}}
div[data-baseweb="menu"] li, 
div[data-baseweb="menu"] [role="option"],
div[data-baseweb="menu"] > ul > li,
div[data-baseweb="menu"] ul li{{
  background:#FFFFFF !important; 
  background-color:#FFFFFF !important;
  color:#1B1E28 !important; 
  font-weight:900 !important;
  font-size:15px !important; 
  padding:10px 12px !important; 
  border-radius:8px !important;
}}
div[data-baseweb="menu"] li:hover, 
div[data-baseweb="menu"] [role="option"]:hover,
div[data-baseweb="menu"] > ul > li:hover,
div[data-baseweb="menu"] ul li:hover{{
  background:#E8E8E8 !important; 
  background-color:#E8E8E8 !important;
  color:#1B1E28 !important;
}}
div[data-baseweb="menu"] li[aria-selected="true"], 
div[data-baseweb="menu"] [role="option"][aria-selected="true"],
div[data-baseweb="menu"] > ul > li[aria-selected="true"],
div[data-baseweb="menu"] ul li[aria-selected="true"]{{
  background:#3B82F6 !important; 
  background-color:#3B82F6 !important;
  color:#FFFFFF !important; 
  box-shadow: inset 4px 0 0 #1E40AF;
}}

/* Force text color in dropdown options - override ALL nested elements */
div[data-baseweb="menu"] li *,
div[data-baseweb="menu"] [role="option"] *,
div[data-baseweb="menu"] span,
div[data-baseweb="menu"] div,
div[data-baseweb="menu"] p,
div[data-baseweb="menu"] li span,
div[data-baseweb="menu"] li div{{
  color:#1B1E28 !important;
}}

/* Override any dark theme styles on popover children - but preserve hover/selected */
div[data-baseweb="popover"] > div{{
  background-color:#FFFFFF !important;
}}
div[data-baseweb="popover"] ul{{
  background-color:#FFFFFF !important;
}}
div[data-baseweb="popover"] li:not(:hover):not([aria-selected="true"]){{
  background-color:#FFFFFF !important;
  color:#1B1E28 !important;
}}

/* Target BaseWeb select dropdown specifically */
[data-baseweb="select"] [role="listbox"],
[data-baseweb="select"] [role="option"]{{
  background:#FFFFFF !important;
  background-color:#FFFFFF !important;
  color:#1B1E28 !important;
}}

/* Multiselect tags */
.stMultiSelect [data-baseweb="tag"]{{
  background:#3B82F6 !important; 
  background-color:#3B82F6 !important;
  color:#FFFFFF !important; 
  border-radius:12px !important; 
  font-weight:900 !important;
}}

.stMultiSelect [data-baseweb="tag"]{{
  background:#3B82F6 !important; 
  background-color:#3B82F6 !important;
  color:#FFFFFF !important; 
  border-radius:12px !important; 
  font-weight:900 !important;
}}

/* ===== FIX FOR DISABLED TEXT BOXES (Dark/Light Mode) ===== */
[data-testid="stTextInput"] input:disabled {{
    background-color: #FFFFFF !important;
    color: #1B1E28 !important;
    -webkit-text-fill-color: #1B1E28 !important;
    font-weight: 800 !important;
    border-color: #C4C4C4 !important;
    border-width: 2px !important;
}}


/* ===== FIX FOR DISABLED TEXT AREA (Dark/Light Mode) ===== */
[data-testid="stTextArea"] textarea:disabled {{
    background-color: #FFFFFF !important;
    color: #1B1E28 !important;
    -webkit-text-fill-color: #1B1E28 !important;
    font-weight: 800 !important;
    border-color: #C4C4C4 !important;
    border-width: 2px !important;
}}
</style>
"""
# ----------------- INITIALIZE SEX SELECTION -----------------
# Get current sex from session state, default to "Girl"
current_sex = st.session_state.get("sex", "Girl")

# ----------------- APPLY THEME CSS -----------------
st.markdown(get_theme_css(current_sex), unsafe_allow_html=True)

# ----------------- TITLE -----------------
st.subheader("Pediatric Dashboard")
#__________________New Patient Selector__________________
patient_list = df['PatID'].unique()
selected_patient_id = st.selectbox("Select Patient ID", patient_list)

# __________________Get all data for the selected patient__________________
patient_data = df[df['PatID'] == selected_patient_id].iloc[0]

# ----------------- HELPERS -----------------
def gauge_svg(score_0_to_10: float) -> str:
    angle_deg = 180 - max(0, min(10, score_0_to_10)) * 18.0
    cx, cy, r = 130, 120, 65
    x2 = cx + r * math.cos(math.radians(angle_deg))
    y2 = cy - r * math.sin(math.radians(angle_deg))
    return f"""
    <svg width="260" height="140" viewBox="0 0 260 140">
      <path d="M20 120 A110 110 0 0 1 240 120" fill="none" stroke="#FFE0E0" stroke-width="26" />
      <path d="M20 120 A110 110 0 0 1 160 35" fill="none" stroke="#E15259" stroke-width="26" stroke-linecap="round"/>
      <path d="M160 35 A110 110 0 0 1 240 120" fill="none" stroke="#9DB7FF" stroke-width="26" stroke-linecap="round"/>
      <line x1="{cx}" y1="{cy}" x2="{x2}" y2="{y2}" stroke="#1B1E28" stroke-width="6" stroke-linecap="round"/>
      <circle cx="{cx}" cy="{cy}" r="10" fill="#1B1E28"/>
    </svg>
    """
# ----------------- COLUMNS -----------------
col_left, col_mid, col_right = st.columns([1.1, 1.2, 1.2])

# ================= LEFT COLUMN =================
with col_left:

    st.markdown('<div class="pinkpanel">', unsafe_allow_html=True)
    st.markdown('<div class="headerpink">Patient Info</div>', unsafe_allow_html=True)

    if get_patient_value(patient_data,"Premature_label") == "Yes":
        st.markdown('<div style="padding:6px 10px;"><span style="display:inline-block;padding:6px 12px;border-radius:999px;background:#EEF0F3;border:1px solid #D7DBE0;font-weight:800;font-size:12px;">Premature</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="height: 38px; padding:6px 10px;"></div>', unsafe_allow_html=True)
    
    # --- Sex selector (Girl/Boy) + highlight icon ---
    st.text_input("Sex", value=get_patient_value(patient_data, 'Gender_label'), disabled=True)

    sex = get_patient_value(patient_data, 'Gender_label')
    sel_girl = " sel" if sex == "Girl" else ""
    sel_boy  = " sel" if sex == "Boy" else ""

    st.markdown(f"""
    <div class="iconrow">
      <div class="iconbox{sel_girl}">♀️</div>
      <div class="iconbox2">👶</div>
      <div class="iconbox3{sel_boy}">♂️</div>
    </div>
    """, unsafe_allow_html=True)
    current_sex = sex
# ----------------- APPLY THEME CSS -----------------
    st.markdown(get_theme_css(current_sex), unsafe_allow_html=True)

    # Inner white card with ONLY the inputs
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)

#__________________Getting all the left colmun categories__________________
        st.text_input("Race", value=get_patient_value(patient_data, 'Race_label'), disabled=True)
        st.text_input("Ethnicity", value=get_patient_value(patient_data, 'Ethnicity_label'), disabled=True)
        st.text_input("Date of Birth", value=get_patient_value(patient_data, 'DOB'), disabled=True)
        st.text_input("Age at Surgery (days)", value=get_patient_value(patient_data, 'AgeAtSurgeryMonths'), disabled=True)

        shunt_size_val = get_patient_value(patient_data, 'Shunt Size', default="N/A")

        # Shunt size scale (visual)
        st.markdown(f"""
        <div style="margin-top:10px;">
          <div><b>Shunt Size</b></div>
          <div class="card" style="border-radius:14px;">
            <svg width="300" height="70" viewBox="0 0 300 70">
              <line x1="20" y1="45" x2="280" y2="45" stroke="#111" stroke-width="2"/>
              <g fill="#111" font-size="12" text-anchor="middle">
                <line x1="20" y1="38" x2="20" y2="52" stroke="#111" stroke-width="2"/><text x="20" y="65">0</text>
                <line x1="95" y1="38" x2="95" y2="52" stroke="#111" stroke-width="2"/><text x="95" y="65">1</text>
                <line x1="170" y1="38" x2="170" y2="52" stroke="#111" stroke-width="2"/><text x="170" y="65">2</text>
                <line x1="245" y1="38" x2="245" y2="52" stroke="#111" stroke-width="2"/><text x="245" y="65">3</text>
                <line x1="280" y1="38" x2="280" y2="52" stroke="#111" stroke-width="2"/><text x="280" y="65">4</text>
              </g>
              <polygon points="262,18 268,30 256,30" fill="#111"/>
              <line x1="262" y1="30" x2="262" y2="46" stroke="#111" stroke-width="2"/>
            </svg>
            <div class="center"><span class="red">{shunt_size_val} MM</span></div>
        
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # close white card
    st.markdown('</div>', unsafe_allow_html=True)      # close pinkpanel

# ================= MIDDLE COLUMN =================
with col_mid:
    
    cardiac_arrest_date = get_patient_value(patient_data, 'CardArrestDtTm', default="--")
    sepsis_date = get_patient_value(patient_data, 'CompSepsisDt', default="--")
    cardiac_details = get_patient_value(patient_data, "Cardiac Anatomy Notes", default = "--")
    
    st.markdown('<div class="eventtitle">Cardiac Event</div>', unsafe_allow_html=True)
    st.markdown((
        '<div class="eventbox">'
        f'<div class="right" style="font-size:20px;font-weight:900;">💔 &nbsp; {cardiac_arrest_date} </div>'
        '<div style="height:10px;"></div>'
        '<div style="height:1px;background:#111;margin:0 4px 8px;"></div>'
        f'<div class="center" style="font-style:italic;font-weight:700;">{cardiac_details}</div>'
        '</div>'), unsafe_allow_html=True)

    st.markdown('<div class="eventtitle">Septic Event</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="eventbox">'
       f'<div class="right" style="font-size:20px;font-weight:900;">🚩 &nbsp; {sepsis_date}</div>'
        '<div style="height:10px;"></div>'
        '<div style="height:1px;background:#111;margin:0 4px 8px;"></div>'
        '<div class="center" style="font-style:italic;font-weight:700;">*Details*</div>'
        '</div>', unsafe_allow_html=True)

    # Risk Factors box (dropdown directly above gauge)
    st.markdown('<div class="eventtitle">Risk Factors</div>', unsafe_allow_html=True)
    with st.container(border=True):
        risk_selection = st.multiselect(
            "Select risk factors",
            ["Premature","Low birth weight","Co-morbidity","Genetic syndrome","Recent infection","Post-op bleed"],
            default=[]
        )
        weights = {"Premature":2.5,"Low birth weight":2.0,"Co-morbidity":1.5,"Genetic syndrome":1.5,"Recent infection":1.0,"Post-op bleed":3.0}
        score = max(0.0, min(10.0, sum(weights.get(x,0) for x in risk_selection)))
        st.write(f"**Score:** {score:.1f} / 10")
        st.markdown('<div class="center" style="font-weight:900;margin:6px 0;">Risk Score</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(gauge_svg(score), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ================= RIGHT COLUMN =================
with col_right:

    surg_date_val = get_patient_value(patient_data, 'CardSurgDt', default="--")
    bleed_date_val = get_patient_value(patient_data, 'CompReopBleedDtTm', default="--")
    sepsis_date_val = get_patient_value(patient_data, 'CompSepsisDt', default="--")
    discharge_date_val = get_patient_value(patient_data, 'End of Interstage/BTTS Period/Admission', default="--")

    
    timeline_html = f"""
    <div class="card">
        <div class="center" style="font-weight:900;">Vertical<br>Timeline of<br>Events</div>
        <div class="timelinewrap">
            <div class="vert">
                <div class="hbot"></div>
                <div class="tick" style="top:40px;"><div class="dot"></div><div class="lbl"><b>Discharge</b><br>{discharge_date_val}</div></div>
                <div class="tick" style="top:170px;"><div class="dot"></div><div class="lbl"><b>Sepsis Found and Treated</b><br>{sepsis_date_val}</div></div>
                <div class="tick" style="top:300px;"><div class="dot"></div><div class="lbl"><b>Bleed Present</b><br>{bleed_date_val}</div></div>
                <div class="tick" style="top:420px;"><div class="dot"></div><div class="lbl"><b>Surgery Completion</b><br>{surg_date_val}</div></div>
            </div>
        </div>
    </div>
    """
    st.markdown(timeline_html, unsafe_allow_html=True)

    # --- FIX: Logic is now based on 'SyndromeTerm' column ---
    
    # 1. Syndrome Toggle
    # 1. Syndrome Present (Text Box)
    syn_val = get_patient_value(patient_data, 'Syndrome_Present_bool', default=False)
    syn_label = "Yes" if syn_val else "No"
    st.text_input("Syndrome Present", value=syn_label, disabled=True)

    # 2. Fetal Drug Selectbox
    fd_label = get_patient_value(patient_data, 'Fetal_Drug_Exposure_label', default='No')
    st.text_input("Fetal Drug Exposure", value=fd_label, disabled=True)


    # 3. Abnormalities Text Area
    ab_text = get_patient_value(patient_data, 'ChromAbTerm', default="—")
    ab = st.text_area("Abnormalities / Etc.", value=ab_text, height=80, disabled=True)
  
    st.markdown(
        f'<div class="card">'
        f'<div style="text-decoration:underline;font-weight:900;">Syndrome Present: {syn_val}</div>'
        f'Sex: {sex}<br>'
        f'Fetal Drug Exposure: {fd_label}<br>'
        f'Abnormalities: {ab_text}'
        f'</div>',
        unsafe_allow_html=True
    )