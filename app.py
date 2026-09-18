import base64
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# -------------------------------------------------------------------------
# 1. Page Configuration & Environment Setup
# -------------------------------------------------------------------------
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

st.set_page_config(
    page_title="NutriGuide Pro • Bio-Engine Modeling",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------------
# 2. Local Asset Loader: 45% Translucent Full-Screen Background
# -------------------------------------------------------------------------
def get_base64_image(image_path: Path) -> str:
    if image_path.exists():
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

assets_dir = Path(__file__).resolve().parent / "assets"
bg_image_path = assets_dir / "background.jpg"
bg_base64 = get_base64_image(bg_image_path)

if bg_base64:
    # Anchor the background image seamlessly behind both the main area and the sidebar
    st.markdown(
        f"""
        <style>
        .stApp, 
        [data-testid="stAppViewContainer"], 
        [data-testid="stMainBlockContainer"],
        section[data-testid="stSidebar"] {{
            background: 
                linear-gradient(rgba(254, 243, 199, 0.50), rgba(224, 242, 254, 0.50)),
                url("data:image/jpeg;base64,{bg_base64}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Load External Stylesheet
# Load External Stylesheet with Cache Busting
css_path = Path(__file__).resolve().parent / "style.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        # Appends file modification time to prevent browser caching
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# API Key Check
api_key = os.getenv("GEMINI_API_KEY")
if not api_key and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

if not api_key:
    st.error("Missing `GEMINI_API_KEY`. Please configure your .env file or Streamlit Secrets.")
    st.stop()

# -------------------------------------------------------------------------
# 3. Clinical System Instructions & Strict Negative Guardrails
# -------------------------------------------------------------------------
SYSTEM_INSTRUCTION = """
You are 'NutriGuide Pro', a clinical nutrition architect and diet planner.

CORE CAPABILITIES:
- Calculate daily caloric targets, macronutrient distributions (Protein, Carbs, Fats), and structure calibrated meal architectures.
- Structure meal recommendations clearly: Breakfast, Lunch, Dinner, and Snacks.
- Include estimated gram weights, portions, and macro targets for each meal.

STRICT BOUNDARY GUARDRAILS (ZERO TOLERANCE):
1. NO COOKING RECIPES OR STEP-BY-STEP PREPARATIONS:
   - You are a clinical diet planner, NOT a chef or recipe repository.
   - If a user asks 'how to cook', 'how to make [dish]', culinary preparations, pan temperatures, or step-by-step kitchen instructions (e.g., 'how to make chicken curry', 'how to bake protein bars'):
   - DECLINE IMMEDIATELY using this exact refusal:
     "I am your Clinical Diet Architect, not a culinary chef. I can calculate the caloric, macronutrient, and portion targets for chicken curry in your daily meal plan, but I do not provide cooking steps or recipes. Would you like me to calibrate its macros for your diet?"

2. CLINICAL SAFETY DISCLAIMER:
   - Include a brief medical disclaimer if the user mentions chronic conditions (e.g., diabetes, renal disease, hypertension, cardiovascular conditions, pregnancy).

3. TOPICAL FIREWALL:
   - Decline non-health queries (coding, homework, politics, general tech).
"""

# -------------------------------------------------------------------------
# 4. Sidebar: Biometric & Metabolic Calculation Engine
# -------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🧬 Bio-Engine Calibration")
    st.caption("Precision Mifflin-St Jeor Modeling")

    col_g, col_a = st.columns(2)
    with col_g:
        gender = st.selectbox("Biological Sex", ["Male", "Female"])
    with col_a:
        age = st.number_input("Age (yrs)", min_value=15, max_value=95, value=23)

    col_w, col_h = st.columns(2)
    with col_w:
        weight_kg = st.number_input("Weight (kg)", min_value=35.0, max_value=220.0, value=66.0, step=0.5)
    with col_h:
        height_cm = st.number_input("Height (cm)", min_value=120.0, max_value=230.0, value=170.0, step=1.0)

    activity = st.selectbox(
        "Activity Index",
        [
            "Sedentary (desk work, low exercise)",
            "Lightly Active (1-3 sessions/wk)",
            "Moderately Active (3-5 sessions/wk)",
            "Very Active (heavy exercise 6-7 days/wk)"
        ],
        index=3
    )

    primary_directive = st.selectbox(
        "Primary Goal",
        [
            "Lean Hypertrophy / Clean Surplus (+400 kcal)",
            "Aggressive Fat Loss / Deficit (-500 kcal)",
            "Moderate Fat Loss (-300 kcal)",
            "Metabolic Maintenance"
        ]
    )

    diet_tags = st.multiselect(
        "Dietary Tags & Exclusions",
        ["High-Protein", "Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Nut Allergy", "Halal"],
        default=["High-Protein"]
    )

    # Mifflin-St Jeor Arithmetic
    if gender == "Male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

    multipliers = {
        "Sedentary (desk work, low exercise)": 1.2,
        "Lightly Active (1-3 sessions/wk)": 1.375,
        "Moderately Active (3-5 sessions/wk)": 1.55,
        "Very Active (heavy exercise 6-7 days/wk)": 1.725
    }
    tdee = bmr * multipliers[activity]

    if "Surplus" in primary_directive:
        target_calories = int(tdee + 400)
    elif "Aggressive" in primary_directive:
        target_calories = int(tdee - 500)
    elif "Moderate" in primary_directive:
        target_calories = int(tdee - 300)
    else:
        target_calories = int(tdee)

    protein_target = int(weight_kg * 2.2)
    fat_target = int((target_calories * 0.25) / 9)
    carb_target = max(0, int((target_calories - (protein_target * 4 + fat_target * 9)) / 4))

    st.markdown("---")
    if st.button("🔄 Reset Consultation Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat = None
        st.rerun()

# -------------------------------------------------------------------------
# 5. Persistent Session State & Gemini Client
# -------------------------------------------------------------------------
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=api_key)

if "chat" not in st.session_state or st.session_state.chat is None:
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2
        )
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------------------------------------------------
# 6. Header & Frosted Metric Cards
# -------------------------------------------------------------------------
# Force-render the collapsed sidebar toggle as a floating white box
st.markdown(
    """
    <style>
    /* 1. CLOSED STATE (>>): Targets all active Streamlit collapsed toggle selectors */
    [data-testid="collapsedControl"],
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapsedControl"] button,
    header[data-testid="stHeader"] button[data-testid="baseButton-headerNoPadding"],
    header[data-testid="stHeader"] button[aria-label*="sidebar" i],
    header[data-testid="stHeader"] > div:first-child button {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 10px !important;
        width: 38px !important;
        height: 38px !important;
        min-width: 38px !important;
        min-height: 38px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35) !important;
        cursor: pointer !important;
        opacity: 1 !important;
        visibility: visible !important;
        z-index: 100000 !important;
        margin: 8px 0 0 12px !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    /* Dark chevron arrows inside the box */
    [data-testid="collapsedControl"] svg,
    [data-testid="collapsedControl"] button svg,
    header[data-testid="stHeader"] button[data-testid="baseButton-headerNoPadding"] svg,
    header[data-testid="stHeader"] button[aria-label*="sidebar" i] svg,
    header[data-testid="stHeader"] > div:first-child button svg,
    header[data-testid="stHeader"] > div:first-child button span {
        fill: #0f172a !important;
        stroke: #0f172a !important;
        color: #0f172a !important;
        width: 20px !important;
        height: 20px !important;
        font-size: 20px !important;
    }

    /* Hover effect */
    [data-testid="collapsedControl"]:hover button,
    header[data-testid="stHeader"] button[data-testid="baseButton-headerNoPadding"]:hover,
    header[data-testid="stHeader"] button[aria-label*="sidebar" i]:hover {
        background-color: #f8fafc !important;
        border-color: #0284c7 !important;
        box-shadow: 0 6px 20px rgba(2, 132, 199, 0.4) !important;
        transform: scale(1.05);
    }

    /* 2. OPEN STATE (<<): Ensure no white box appears inside the open sidebar */
    section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
    section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button,
    section[data-testid="stSidebar"] button[data-testid="baseButton-headerNoPadding"],
    section[data-testid="stSidebar"] button[aria-label*="sidebar" i] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        width: auto !important;
        height: auto !important;
        min-width: unset !important;
        min-height: unset !important;
        margin: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# 4-Column Metric Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">⚡ Daily Energy Target</div>
            <div class="metric-val">{target_calories} <span class="metric-unit">kcal</span></div>
            <div class="macro-progress"><div class="macro-progress-fill" style="width: 100%;"></div></div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">🥩 Protein Target</div>
            <div class="metric-val">{protein_target} <span class="metric-unit">g</span></div>
            <div class="macro-progress"><div class="macro-progress-fill" style="width: 75%; background: #0284c7;"></div></div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">🌾 Carbohydrates</div>
            <div class="metric-val">{carb_target} <span class="metric-unit">g</span></div>
            <div class="macro-progress"><div class="macro-progress-fill" style="width: 60%; background: #f59e0b;"></div></div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">🥑 Lipid Allowance</div>
            <div class="metric-val">{fat_target} <span class="metric-unit">g</span></div>
            <div class="macro-progress"><div class="macro-progress-fill" style="width: 45%; background: #10b981;"></div></div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
st.markdown("##### ⚡ Directives & Quick Protocols")

dcol1, dcol2, dcol3, dcol4 = st.columns(4)
active_directive = None
tags_str = ", ".join(diet_tags) if diet_tags else "Standard Whole Foods"

with dcol1:
    if st.button("🥦 1-Day Prep Blueprint", use_container_width=True):
        active_directive = f"Construct a complete 1-day meal architecture calibrated to ~{target_calories} kcal and {protein_target}g protein. Dietary tags: {tags_str}."
with dcol2:
    if st.button("⚡ High-Protein Distribution", use_container_width=True):
        active_directive = f"Outline a 4-meal distribution hitting ~{protein_target}g protein across the day within {target_calories} kcal. Tags: {tags_str}."
with dcol3:
    if st.button("🥑 Clean Mass Surplus", use_container_width=True):
        active_directive = f"Generate a high-density, clean mass-gain meal blueprint targeting {target_calories} kcal using whole foods. Tags: {tags_str}."
with dcol4:
    if st.button("🛒 Macro Grocery Manifest", use_container_width=True):
        active_directive = f"Generate a categorized weekly grocery shopping list structured around {target_calories} kcal and {protein_target}g protein targets. Tags: {tags_str}."

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# 7. Multi-Turn Conversation Feed
# -------------------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_query = st.chat_input("Inquire about meal distributions, macro adjustments, or portion weights...")
query_to_send = active_directive or user_query

if query_to_send:
    st.session_state.messages.append({"role": "user", "content": query_to_send})
    with st.chat_message("user"):
        st.markdown(query_to_send)

    with st.chat_message("assistant"):
        with st.spinner("Calibrating metabolic targets..."):
            try:
                response = st.session_state.chat.send_message(query_to_send)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Engine Exception: {e}")