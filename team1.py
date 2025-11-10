# ==============================================
# DASHBOARD 1
# ==============================================
import uuid
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# from streamlit_extras.row import row  # <--- CHANGED (1/7): This line is deleted
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.avatar import avatar

# ---------- Page config ----------
st.set_page_config(page_title="Risk Dashboard", layout="wide")

# =========================================================
# 1. REAL DATA LOADING
# =========================================================

def get_patient_value(data, key, default="_"):                  
    val = data.get(key) 
    if pd.isna(val):
        return default
    return val

# @st.cache_data ensures this only runs once
@st.cache_data
def load_all_data():
    try:
        df = pd.read_csv("MS_copy_DeID_Complete.csv")
        df['PatID'] = df['PatID'].astype(str)
        df['Gender_label'] = df['Gender'].map({0: "Girl", 1: "Boy"}).fillna("Unknown")
        df['Premature_label'] = df['Premature'].map({0: "Normal", 1: "Early"}).fillna("Unknown")
        race_map = {1: 'White', 2: 'Black', 3: 'Asian', 4: 'American Indian', 5: 'Native Hawaiian', 6: 'Other Pacific Islander'}
        df['Race_label'] = df['Race'].map(race_map).fillna('Other/Unknown')

        ethnicity_map = {0: 'Non-Hispanic', 1: 'Hispanic/Latino', 2: 'Other/Unknown'}
        df['Ethnicity_label'] = df['Ethnicity'].map(ethnicity_map).fillna('Other/Unknown')

        if 'SyndromeTerm' in df.columns:
            df['Syndrome_Present_bool'] = df['SyndromeTerm'] != "No syndromic abnormality identified"
            df['Fetal_Drug_Exposure_label'] = df['SyndromeTerm'].apply(
                lambda x: "Yes" if x == "Fetal drug exposure" else "No")
        else:
            print("Warning: 'SyndromeTerm' column not found. Using default values.")
            df['SyndromeTerm'] = "Column Not Found"
            df['Syndrome_Present_bool'] = False
            df['Fetal_Drug_Exposure_label'] = "No"
                    
        return df
        
    except FileNotFoundError:
        st.error("Data file 'MS_copy_DeID_Complete.csv' not found.")
        return None
    except KeyError as e:
        st.error(f"Data mapping error: Column {e} not found in the CSV. Please check your column names.")
        return None
    
# =========================================================
# 2. DATA TRANSFORMATION FUNCTION (THE "BRIDGE")
# =========================================================





# =========================================================
# 2. DATA TRANSFORMATION FUNCTION (THE "BRIDGE")
# =========================================================

def build_patient_data(patient_id, df):
    """
    Finds data for the selected patient in the DataFrame
    and builds the dictionary that dashboard_app expects.
    """
    
    # --- 1. GET PATIENT ROW ---
    try:
        patient_row = df[df["PatID"] == patient_id].to_dict('records')[0]
    except IndexError:
        st.error(f"Patient ID {patient_id} not found.")
        return None # Return None to stop the app

    # --- 2. DEFINE COLUMN MAPPINGS ---
    csv_col_map = {
        "id": "PatID",
        "age_display": "AgeAtSurgeryMonths",
        "birth_weight_display": "BirthWtKg",
        "sex": "Gender_label",
        "race": "Race_label",
        "ethnicity": "Ethnicity_label",
        "birth_status": "Premature_label", 
        "shunt_size_mm": "Shunt Size",
        "surgical_weight_kg": "SurgWtKg",
        "surgery_date": "CardSurgDt",
    }

    # --- 3. CALCULATE VALUES ---
    surg_weight = get_patient_value(patient_row, csv_col_map["surgical_weight_kg"], 0)
    birth_weight = get_patient_value(patient_row, csv_col_map["birth_weight_display"], 0)
    weight_gain_kg = round(surg_weight - birth_weight, 1)

    # --- 4. BUILD NOTIFICATION LISTS (NOW WITH DYNAMIC DETAILS) ---
    
    complications_list = []
    comorbidities_list = []
    other_list = []

    # --- Complications ---
    if get_patient_value(patient_row, "CompCardArrest", 0) == 1:
        details = f"**Date/Time:** {get_patient_value(patient_row, 'CardArrestDtTm', 'N/A')}"
        complications_list.append({"title": "Cardiac Arrest", "subtext": "Patient experienced cardiac arrest.", "risk": "High", "details": details})

    if get_patient_value(patient_row, "MechCircSupp", 0) == 1:
        details = (f"**Type:** {get_patient_value(patient_row, 'MechCircSuppType', 'N/A')}\n\n"
                   f"**Reason:** {get_patient_value(patient_row, 'MechCircSuppReason', 'N/A')}\n\n"
                   f"**Date:** {get_patient_value(patient_row, 'MechCircSuppInitDtTm', 'N/A')}")
        complications_list.append({"title": "Mechanical Support", "subtext": "Mechanical circulatory support was required.", "risk": "High", "details": details})
    
    if get_patient_value(patient_row, "CompLCOS2", 0) == 1:
        details = f"**Date/Time:** {get_patient_value(patient_row, 'CompLCOSDtTime', 'N/A')}"
        complications_list.append({"title": "Low Cardiac Output", "subtext": "Patient experienced Low Cardiac Output Syndrome.", "risk": "High", "details": details})

    if get_patient_value(patient_row, "CompReopBleed", 0) == 1:
        details = f"**Date/Time:** {get_patient_value(patient_row, 'CompReopBleedDtTm', 'N/A')}"
        complications_list.append({"title": "Reoperation for Bleeding", "subtext": "Patient required reoperation for bleeding.", "risk": "Medium", "details": details})

    if get_patient_value(patient_row, "CompChyloIntv", 0) == 1:
        details = f"**Date/Time:** {get_patient_value(patient_row, 'CompChyloIntvDtTm', 'N/A')}"
        complications_list.append({"title": "Chylothorax", "subtext": "Intervention required for chylothorax.", "risk": "Medium", "details": details})

    if get_patient_value(patient_row, "CompSepsis", 0) == 1:
        details = f"**Date:** {get_patient_value(patient_row, 'CompSepsisDt', 'N/A')}"
        complications_list.append({"title": "Sepsis", "subtext": "Patient developed sepsis.", "risk": "High", "details": details})
    
    if get_patient_value(patient_row, "CompSupWoundInf", 0) == 1:
        details = f"**Date:** {get_patient_value(patient_row, 'CompSupWoundInfDt', 'N/A')}"
        complications_list.append({"title": "Superficial Wound Infection", "subtext": "Post-operative superficial wound infection.", "risk": "Medium", "details": details})

    if get_patient_value(patient_row, "CompWoundInf", 0) == 1:
        details = "No additional details available." # No matching 'Dt' column in the list
        complications_list.append({"title": "Deep Wound Infection", "subtext": "Post-operative deep wound infection.", "risk": "High", "details": details})

    if get_patient_value(patient_row, "CompCLABSI", 0) == 1:
        details = f"**Date:** {get_patient_value(patient_row, 'CompCLABSIDt', 'N/A')}"
        complications_list.append({"title": "CLABSI", "subtext": "Central line-associated bloodstream infection.", "risk": "High", "details": details})

    if get_patient_value(patient_row, "CompStroke", 0) == 1:
        details = (f"**Date/Time:** {get_patient_value(patient_row, 'StrokeDtTm', 'N/A')}\n\n"
                   f"**Hemorrhage:** {'Yes' if get_patient_value(patient_row, 'StrokeHemorrhage', 0) == 1 else 'No'}")
        complications_list.append({"title": "Stroke", "subtext": "Patient experienced a stroke.", "risk": "High", "details": details})

    if get_patient_value(patient_row, "CompIVH", 0) == 1:
        details = f"**Date/Time:** {get_patient_value(patient_row, 'CompIVHDtTm', 'N/A')}"
        complications_list.append({"title": "IVH (Intraventricular Hemorrhage)", "subtext": "Patient developed an IVH.", "risk": "High", "details": details})

    if get_patient_value(patient_row, "CompNECBell", 0) == 1:
        details = f"**Date:** {get_patient_value(patient_row, 'NECbellDt', 'N/A')}"
        complications_list.append({"title": "NEC (Necrotizing Enterocolitis)", "subtext": "Patient developed NEC.", "risk": "High", "details": details})

    if get_patient_value(patient_row, "Concurrent TAPVR Repair", 0) == 1:
        details = "TAPVR repair was performed during the primary surgery."
        complications_list.append({"title": "Concurrent TAPVR Repair", "subtext": "TAPVR repair performed during surgery.", "risk": "Medium", "details": details})

    # --- Comorbidities ---
    if get_patient_value(patient_row, "Syndrome_Present_bool", False) == True:
        details = f"**Syndrome Term:** {get_patient_value(patient_row, 'SyndromeTerm', 'N/A')}"
        comorbidities_list.append({"title": "Genetic Syndrome", "subtext": "Genetic syndrome identified.", "risk": "Medium", "details": details})

    if get_patient_value(patient_row, "ChromAb", 0) == 1:
        details = f"**Abnormality:** {get_patient_value(patient_row, 'ChromAbTerm', 'N/A')}"
        comorbidities_list.append({"title": "Chromosomal Abnormality", "subtext": "Chromosomal abnormality present.", "risk": "Medium", "details": details})

    # --- Other ---
    if get_patient_value(patient_row, "Fetal_Drug_Exposure_label", "No") == "Yes":
        details = "Patient noted as having fetal drug exposure."
        other_list.append({"title": "Fetal Drug Exposure", "subtext": "Patient had fetal drug exposure.", "risk": "Medium", "details": details})

    # --- 5. BUILD FINAL DICTIONARY ---
    
    # --- CHANGED: Create real scatter data ---
    # Get the relevant columns for *all* patients and drop any with missing data
    scatter_df = df[['PatID', 'SurgWtKg', 'Shunt Size']].dropna()
    
    data_dict = {
        "patient": {
            "id": get_patient_value(patient_row, csv_col_map["id"], patient_id),
            "age_display": f"{get_patient_value(patient_row, csv_col_map['age_display'], 0)} months",
            "birth_weight_display": f"{birth_weight} kg",
            "avatar_url": "https://picsum.photos/id/237/300/300", # Static for now
            "sex": get_patient_value(patient_row, csv_col_map["sex"]),
            "race": get_patient_value(patient_row, csv_col_map["race"]),
            "ethnicity": get_patient_value(patient_row, csv_col_map["ethnicity"]),
            "birth_status": get_patient_value(patient_row, csv_col_map["birth_status"]),
            "shunt_size_mm": get_patient_value(patient_row, csv_col_map["shunt_size_mm"], 0),
            "surgical_weight_kg": surg_weight,
            "surgery_date": get_patient_value(patient_row, csv_col_map["surgery_date"], "N/A"),
            "weight_gain_kg": weight_gain_kg,
        },
        "overall_risk_percent": 28, # Static value for now
        
        "procedure_times": {
            "cpb_time": get_patient_value(patient_row, "CPBTm", 0),
            "cross_clamp_time": get_patient_value(patient_row, "XClampTm", 0),
        },
        
        "risk_breakdown": [
            ("Age", 20),
            ("Surgical Complexity", 35),
            ("Cardiac Function", 30),
            ("Procedure Duration", 10),
            ("Comorbidities", 5),
        ],
        
        "notifs_complications": complications_list,
        "notifs_comorbidities": comorbidities_list,
        "notifs_other": other_list,
        
        # --- CHANGED: Use real data for the shunt scatter plot ---
        "shunt_scatter": {
            "patient_ids": scatter_df['PatID'].tolist(),
            "weight_kg": scatter_df['SurgWtKg'].tolist(),
            "shunt_mm":   scatter_df['Shunt Size'].tolist(),
            "current_patient_id": patient_id, # Use the currently selected patient ID
        },
    }
    
    return data_dict





# =========================
# THEME / COLOR UTILITIES
# =========================
RISK_COLORS = {
    "Low":    {"band": "#22c55f", "bg": "#cff4db", "card": "#f1fdf4", "border": "#22c55f"},
    "Medium": {"band": "#ebb30b", "bg": "#ffdeb7", "card": "#fff8ed", "border": "#ebb30b"},
    "High":   {"band": "#ef4444", "bg": "#e1767a", "card": "#fef3f3", "border": "#ef4444"},
}

def band_color(risk: str) -> str: return RISK_COLORS[risk]["band"]

def bg_color(risk: str)  -> str: return RISK_COLORS[risk]["bg"]

def riskLevelStyle(risk: str) -> str:
    c = RISK_COLORS[risk]
    return f"{{background-color:{c['card']};border:1px solid {c['border']};border-radius:12px;padding:18px 18px 24px 18px;}}"


def compute_risk_label(score_0_100: int) -> str:
    if score_0_100 <= 30: return "Low"
    if score_0_100 <= 70: return "Medium"
    return "High"

# ======================
# SVG / HTML ICON HELPERS
# ======================

def alert_markdown(risk: str) -> str:
    card = RISK_COLORS[risk]["card"]; band = RISK_COLORS[risk]["band"]
    return f"""<div style=\"display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:8px;background-color:{card};color:{band};\">\n   <svg xmlns=\"http://www.w3.org/2000/svg\" width=\"20\" height=\"20\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\">\n    <path d=\"m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3\"></path>\n    <path d=\"M12 9v4\"></path><path d=\"M12 17h.01\"></path>\n   </svg></div>"""


def check_markdown(risk: str) -> str:
    card = RISK_COLORS[risk]["card"]; band = RISK_COLORS[risk]["band"]
    return f"""<div style=\"display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:8px;background-color:{card};color:{band};\">\n   <svg xmlns=\"http://www.w3.org/2000/svg\" width=\"20\" height=\"20\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">\n    <circle cx=\"12\" cy=\"12\" r=\"10\"></circle><path d=\"m9 12 2 2 4-4\"></path>\n   </svg></div>"""


def scale_markdown(risk: str) -> str:
    color = band_color("Low") if risk == "Low" else band_color("High")
    return ("""
    <div style=\"display:inline-flex;align-items:center;gap:8px;padding:8px 12px;border-radius:10px;"""
            + f"background:{color};background-color:{color};"
            + """color:#ffffff;\">\n       <svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\"\n           viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"\n           stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\">\n        <path d=\"m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z\"></path>\n        <path d=\"m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z\"></path>\n        <path d=\"M7 21h10\"></path><path d=\"M12 3v18\"></path><path d=\"M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2\"></path>\n       </svg>\n    </div>""")


def get_icon(icon: str, text: str):
    icons = {
        "calendar": """<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"20\" height=\"20\"\nviewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M8 2v4\"></path><path d=\"M16 2v4\"></path><rect width=\"18\" height=\"18\" x=\"3\" y=\"4\" rx=\"2\"></rect><path d=\"M3 10h18\"></path></svg>""",
        "baby": """<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"20\" height=\"20\"\nviewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M10 16c.5.3 1.2.5 2 .5s1.5-.2 2-.5\"></path><path d=\"M15 12h.01\"></path><path d=\"M19.38 6.813A9 9 0 0 1 20.8 10.2a2 2 0 0 1 0 3.6 9 9 0 0 1-17.6 0 2 2 0 0 1 0-3.6A9 9 0 0 1 12 3c2 0 3.5 1.1 3.5 2.5s-.9 2.5-2 2.5c-.8 0-1.5-.4-1.5-1\"></path><path d=\"M9 12h.01\"></path></svg>""",
        "activity": """<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"20\" height=\"20\"\nviewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0L6.41 10.54A2 2 0 0 1 4.49 12H2\"></path></svg>""",
        "user": """<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"20\" height=\"20\"\nviewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2\"></path><circle cx=\"12\" cy=\"7\" r=\"4\"></circle></svg>""",
    }
    svg = icons.get(icon, "")
    st.markdown(f"""<div style=\"display:flex;align-items:center;padding:6px 0;gap:10px;font-size:0.9rem;\">\n        <span>{svg}</span><span>{text}</span></div>""", unsafe_allow_html=True)


def notification_text(text: str, risk: str):
    color = band_color(risk); bg = f"{color}26"
    st.markdown(f"""<span style=\"display:inline-block;padding:4px 10px;border-radius:9999px;\n        font-size:0.85rem;font-weight:500;border:1px solid {color};background:{bg};color:{color};white-space:nowrap;\">\n        {text}</span>""", unsafe_allow_html=True)


# ======================
# DASHBOARD LAYOUT (App 1)
# ======================

def dashboard_app(data: dict):
    patient = data["patient"]
    risk_value = int(data["overall_risk_percent"])
    risk = compute_risk_label(risk_value)

    riskGaugeContainer, infantIDContainer_col = st.columns([.35, .65], gap="medium")

   # ---- Left: Overall Risk Gauge ----
    with riskGaugeContainer:
        with stylable_container(
            key="riskGaugeContainer",
            css_styles=f"{{background-color: {RISK_COLORS[risk]['card']}; border:1px solid {RISK_COLORS[risk]['border']}; border-radius:12px; padding: 24px 18px 18px 18px;}}"
        ):
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = risk_value,
                number = {"font": {"size": 60, "color": "#111"}}, # Changed size, removed "%"
                gauge = {
                    "axis": {"range": [0, 100], "visible": False},
                    "bar": {"color": band_color(risk), "thickness": 0.8}, # Made bar thicker
                    
                    "steps": [
                        {"range": [0, 30], "color": RISK_COLORS["Low"]["bg"]},
                        {"range": [30, 70], "color": RISK_COLORS["Medium"]["bg"]},
                        {"range": [70, 100], "color": RISK_COLORS["High"]["bg"]}
                    ],
                },
                domain = {"x": [0, 1], "y": [0, 1]}
            ))
            
            fig.update_layout(
                height=195, # Made chart shorter
                margin=dict(l=20, r=20, t=0, b=0), # Adjusted margins
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            st.plotly_chart(fig, config={'displayModeBar': False, 'scrollZoom': False}, use_container_width=True, key=f"p2-gauge-{uuid.uuid4()}")

            st.markdown(
                f"""
                <div style='text-align:center; margin-top: -30px;'>
                    <div style='font-size: 1rem; color: #555;'>Risk Score</div>
                    <span style="display:inline-block; padding: 4px 12px; border-radius: 9999px; font-weight: 600;
                                background:{bg_color(risk)}; color:{band_color(risk)}; font-size: 0.6rem; margin-top: 8px;">
                        {risk} Risk
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(f"""
                <style>
                    [data-testid=\"stProgress\"] {{ margin-top: 20px !important; }}
                    /* Background of progress bar */
                    .stProgress > div > div > div {{ background-color: {bg_color(risk)} !important; }}
                    /* The actual bar itself */
                    .stProgress > div > div > div > div {{ background-color: {band_color(risk)} !important; }}
                </style>""", unsafe_allow_html=True)

            with st.expander("View Risk Factor Breakdown", expanded=False): # Set to False
                st.write("The following factors contribute to the total score:")
                for label, pct in data["risk_breakdown"]:
                    st.progress(int(pct), text=f"{label}: {pct}%")


    # ---- Right: Patient Header & Status ----
    with infantIDContainer_col:
        with st.container(border=True, key="infantIDContainer"):
            header_col1, header_col2 = st.columns((0.8, 0.2))
            with header_col1:
                avatar([{"url": patient["avatar_url"], "size": 60,
                         "caption": patient["id"], "key": "avatar1"}])
            with header_col2:
                st.markdown("<div style='display:flex; justify-content:flex-end; margin-right:4px;'>", unsafe_allow_html=True)
                notification_text("Stable", "Low")
                st.markdown("</div>", unsafe_allow_html=True)

            info1_col1, info1_col2, info1_col3 = st.columns(3)
            with info1_col1: get_icon("calendar", f"Age: {patient['age_display']}")
            with info1_col2: get_icon("baby", f"Birth Status: {patient['birth_status']}")
            with info1_col3: get_icon("activity", f"Shunt Size: {patient['shunt_size_mm']} mm")

            info2_col1, info2_col2, info2_col3 = st.columns(3)
            with info2_col1: get_icon("user", f"Race: {patient['race']}")
            with info2_col2: get_icon("user", f"Ethnicity: {patient['ethnicity']}")
            with info2_col3: get_icon("user", f"Sex: {patient['sex']}")

            st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)

# ---"Weight at Surgery" Card  ---
            
            # 1. Get all the data from the patient dict
            surg_weight = patient['surgical_weight_kg']
            surg_date = patient['surgery_date']
            gain_kg = patient['weight_gain_kg']
            
            # 2. Determine risk level for card color (based on weight)
            # !! You can change this logic !!
            weight_risk = "Low"
            if surg_weight < 3.0: # Example: High risk if under 3kg
                weight_risk = "High"
            elif surg_weight < 3.5: # Example: Medium risk if 3.0-3.5kg
                weight_risk = "Medium"

            # 3. Build the card
            with stylable_container(key="infantStatusContainer", css_styles=riskLevelStyle(weight_risk)):
                
                # --- Top part of the card ---
                cols_top = st.columns([0.08, 0.92])
                with cols_top[0]:
                    st.markdown(scale_markdown(weight_risk), unsafe_allow_html=True); st.text("")
                
                with cols_top[1]:
                    st.markdown(f"""
                        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                            <div>
                                <strong>Weight at Surgery</strong><br>
                                <span style="font-size:1.1rem;font-weight:600;">{surg_weight} kg</span>
                                </div>
                            <div style="text-align:right;color:#555;font-size:0.9rem;white-space:nowrap;">
                                <span style="margin-right:20px;">Weight Gain: <b>{gain_kg} kg</b></span>
                                <span>Surgery: <b>{surg_date}</b></span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                # --- Bottom part of the card ---
                st.markdown("<hr style='margin:10px 0;border-color:#e5e7eb;opacity:0.7;'>", unsafe_allow_html=True)
                st.markdown(f"<span style='color:#555;font-size:0.9rem;'>Below healthy range</span>",
                            unsafe_allow_html=True)

    # ---- Row: Notifications ----
    notif_col1, notif_col2, notif_col3 = st.columns(3, gap="medium")

    def render_notifications(title: str, items: list, icon="alert"):
        with stylable_container(key=f"notif-wrap-{title}-{uuid.uuid4()}",
                                css_styles="{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:12px;}"):
            
            # --- Using st.markdown for font size control ---
            st.markdown(f"<h3 style='font-size: 1.2rem; margin-bottom: 8px;'>{title}</h3>", unsafe_allow_html=True)
            
            active_count = len(items)
            count_risk = "Low"
            if active_count > 2: count_risk = "High"
            elif active_count > 0: count_risk = "Medium"
            notification_text(f"{active_count} active", count_risk)
            
            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            
            if not items:
                st.write("No active items to report.")

            for notif in items:
                risk = notif.get("risk", "Low")
                with stylable_container(key=f"notif-{notif['title']}-{uuid.uuid4()}",
                                        css_styles=riskLevelStyle(risk)):
                    
                    top_row = st.columns([0.08, 0.92])
                    with top_row[0]:
                        html = alert_markdown(risk) if icon == "alert" else check_markdown(risk)
                        st.markdown(html, unsafe_allow_html=True)
                    with top_row[1]:
                        st.markdown(f"**{notif['title']}** \n"
                                    f"<span style='color:#555;font-size:0.9rem;'>{notif['subtext']}</span>",
                                    unsafe_allow_html=True)
                    
                    with st.expander("View Details", expanded=False):
                        details_text = notif.get("details", f"This notification is **{risk} risk**. No additional details found.")
                        st.markdown(details_text, unsafe_allow_html=True)



    # Place the render_notifications calls inside bordered containers within their columns
    with notif_col1:
        with st.container(border=True):
            render_notifications("Complications & Concurrent Repairs",  data["notifs_complications"], icon="alert")
    with notif_col2:
        with st.container(border=True):
            render_notifications("Comorbidities",  data["notifs_comorbidities"], icon="check")
    with notif_col3:
        with st.container(border=True):
            render_notifications("Other",          data["notifs_other"],       icon="check")

    # ---- Row: Procedure durations & Shunt analysis ----
    left_col, right_col = st.columns((.5, .5), gap="medium")
    
    # The original code created `left` and `right` variables for the containers
    left = left_col.container(border=True)
    right = right_col.container(border=True)


    with left:
        st.subheader("Duration of Surgical Procedures")
        # --- CHANGED: Use real data from the dictionary ---
        cross_clamp_time = int(data["procedure_times"]["cross_clamp_time"])
        cpb_time = int(data["procedure_times"]["cpb_time"])
        # --- END CHANGE ---
        
        def risk_bg(val):
            if val <= 30: return RISK_COLORS["Low"]["bg"]
            if val <= 70: return RISK_COLORS["Medium"]["bg"]
            return RISK_COLORS["High"]["bg"]
        st.markdown("""
        <style>
        .progress-container{border:1px solid #e5e7eb;border-radius:10px;padding:8px 12px;background:#fff;margin-bottom:14px;box-shadow:0 1px 2px rgba(0,0,0,0.04)}
        .progress-bar{height:10px;width:100%;border-radius:5px;overflow:hidden;position:relative}
        .legend{display:flex;justify-content:center;gap:16px;margin-top:10px}
        .legend-item{display:flex;align-items:center;gap:6px;font-size:.85rem;color:#374151}
        .legend-swatch{width:14px;height:14px;border-radius:3px;border:1px solid #d1d5db}
        </style>
        """, unsafe_allow_html=True)



        def styled_progress(value, title):
            st.markdown(f"""
                <div class="progress-container">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                        <strong>{title}</strong>
                        <span style="font-size:0.85rem;color:#6b7280;">Time: {value} minutes</span>
                    </div>
                    <div class="progress-bar" style="background-color:{risk_bg(value)};">
                        <div style="width:{value}%;background-color:black;height:100%;border-radius:5px 0 0 5px;transition:width .4s;"></div>
                    </div>
                </div>""", unsafe_allow_html=True)
        styled_progress(cross_clamp_time, "Cross Clamp Duration")
        styled_progress(cpb_time, "CPB (Cardiopulmonary Bypass) Duration")
        st.markdown(f"""
            <div class="legend">
                <div class="legend-item"><div class="legend-swatch" style="background:{RISK_COLORS['Low']['bg']};"></div>Low Risk</div>
                <div classs="legend-item"><div class="legend-swatch" style="background:{RISK_COLORS['Medium']['bg']};"></div>Medium Risk</div>
                <div class="legend-item"><div class="legend-swatch" style="background:{RISK_COLORS['High']['bg']};"></div>High Risk</div>
            </div>""", unsafe_allow_html=True)
        
    with right:
        st.subheader("Shunt Analysis")
        mode = st.radio("Select Visualization", ["Shunt-to-Weight Ratio", "Shunt Size"], horizontal=True, label_visibility="collapsed")
        sc = data["shunt_scatter"]
        df = pd.DataFrame({"patient_id": sc["patient_ids"], "weight": sc["weight_kg"], "shunt_size": sc["shunt_mm"]})
        df["ratio"] = df["shunt_size"] / df["weight"]
        df["x"] = np.arange(1, len(df) + 1)
        current_id = sc["current_patient_id"]
        if mode == "Shunt-to-Weight Ratio":
            y_label = "Shunt-to-Weight (mm/kg)"; y_data = df["ratio"]
        else:
            y_label = "Shunt Size (mm)"; y_data = df["shunt_size"]
        m, b = np.polyfit(df["x"], y_data, 1)
        xfit = np.array([df["x"].min(), df["x"].max()])
        yfit = m * xfit + b
        fig = go.Figure()
        others = df[df["patient_id"] != current_id]
        fig.add_scatter(x=others["x"], y=y_data[df["patient_id"] != current_id], mode="markers",
                        name="Other Patients", hovertext=others["patient_id"], hoverinfo="text+y")
        me = df[df["patient_id"] == current_id]
        fig.add_scatter(x=me["x"], y=y_data[df["patient_id"] == current_id], mode="markers",
                        marker=dict(size=12, color="black"),
                        name=f"Current Patient ({current_id})", hovertext=me["patient_id"], hoverinfo="text+y")
        fig.add_scatter(x=xfit, y=yfit, mode="lines", name="Trendline")
        fig.update_layout(margin=dict(l=20, r=20, t=10, b=10),
                          xaxis=dict(title="Patient ID", tickmode="array", tickvals=df["x"], ticktext=df["patient_id"]),
                          yaxis=dict(title=y_label), height=300)
        fig.add_hrect(y0=y_data.min(), y1=y_data.max(), opacity=0.08, line_width=0)
        st.plotly_chart(fig, use_container_width=True, key=f"p2-shunt-{uuid.uuid4()}")


# =========================================================
# 4. MAIN APP EXECUTION
# =========================================================

# Load the main dataframe
main_df = load_all_data()

if main_df is not None:
    # Get the list of all unique patient IDs for the selector
    patient_list = main_df["PatID"].unique()
    # Create the patient selector in the sidebar
    selected_patient_id = st.sidebar.selectbox(
        "Select Patient ID:",
        patient_list
    )
    dashboard_data = build_patient_data(selected_patient_id, main_df)    
    if dashboard_data:
        dashboard_app(dashboard_data)
else:
    st.error("Dashboard cannot be loaded. Please check data file.")

#streamlit run team1.py