import base64
import os
import re
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
    page_title="DietBot • Bio-Engine Clinical Diet Architect",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------------
# 2. Local Asset Loader: Full-Screen Background
# -------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_base64_image(image_path: Path) -> str:
    if image_path.exists():
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

assets_dir = Path(__file__).resolve().parent / "assets"
bg_image_path = assets_dir / "background.jpg"
bg_base64 = get_base64_image(bg_image_path)

if bg_base64:
    st.markdown(
        f"""
        <style>
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMainBlockContainer"],
        section[data-testid="stSidebar"] {{
            background-image: linear-gradient(rgba(254, 243, 199, 0.50), rgba(224, 242, 254, 0.50)), url("data:image/png;base64,{bg_base64}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}
        [data-theme="dark"] .stApp,
        [data-theme="dark"] [data-testid="stAppViewContainer"],
        [data-theme="dark"] [data-testid="stMainBlockContainer"],
        [data-theme="dark"] section[data-testid="stSidebar"],
        .stApp[data-theme="dark"],
        .stApp[class*="st-emotion-cache-13k62yr"],
        body:has(.stApp[class*="st-emotion-cache-13k62yr"]) [data-testid="stAppViewContainer"],
        body:has(.stApp[class*="st-emotion-cache-13k62yr"]) [data-testid="stMainBlockContainer"],
        body:has(.stApp[class*="st-emotion-cache-13k62yr"]) section[data-testid="stSidebar"] {{
            background-image: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)), url("data:image/png;base64,{bg_base64}") !important;
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
css_path = Path(__file__).resolve().parent / "style.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
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
You are 'DietBot', a clinical nutrition architect and precision metabolic diet planner.

CORE CAPABILITIES:
- Calculate daily caloric targets, macronutrient distributions (Protein, Carbs, Fats), and structure calibrated meal architectures.
- Structure meal recommendations clearly: Breakfast, Lunch, Dinner, and Snacks.
- Include estimated gram weights, portions, and macro targets for each meal based on user biometrics.

STRICT BOUNDARY GUARDRAILS (ZERO TOLERANCE):
1. NO COOKING RECIPES OR STEP-BY-STEP PREPARATIONS:
   - You are a clinical diet planner, NOT a chef or recipe repository.
   - If a user asks 'how to cook', 'how to make [dish]', culinary preparations, pan temperatures, or step-by-step kitchen instructions (e.g., 'how to make chicken curry', 'how to bake protein bars'):
   - DECLINE IMMEDIATELY using this exact refusal:
     "I am DietBot, your Clinical Diet Architect, not a culinary chef. I can calculate the caloric, macronutrient, and portion targets for this item in your calibrated meal plan, but I do not provide cooking steps or recipes. Would you like me to calibrate its macros for your diet?"

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
        gender = st.selectbox("Biological Sex", ["Male", "Female"], index=0)
    with col_a:
        age = st.number_input("Age (yrs)", min_value=18, max_value=95, value=18)

    col_w, col_h = st.columns(2)
    with col_w:
        weight_kg = st.number_input("Weight (kg)", min_value=35.0, max_value=220.0, value=35.0, step=0.5)
    with col_h:
        height_cm = st.number_input("Height (cm)", min_value=120.0, max_value=230.0, value=120.0, step=1.0)

    activity = st.selectbox(
        "Activity Index",
        [
            "Basal Metabolic Rate Only (Bed rest / Comatose)",
            "Sedentary (desk work, minimal movement)",
            "Lightly Active (light exercise / sports 1-3 days/wk)",
            "Moderately Active (moderate exercise / sports 3-5 days/wk)",
            "Very Active (heavy exercise / hard sports 6-7 days/wk)",
            "Extremely Active (hard daily training / physical labor)"
        ],
        index=0
    )

    primary_directive = st.selectbox(
        "Primary Goal",
        [
            "Aggressive Fat Loss / Steep Deficit (-500 kcal)",
            "Moderate Fat Loss / Steady Cut (-350 kcal)",
            "Conservative Fat Loss / Gentle Cut (-200 kcal)",
            "Metabolic Maintenance & Body Recomposition (±0 kcal)",
            "Lean Hypertrophy / Clean Surplus (+250 kcal)",
            "Accelerated Mass Gain / Bulking Phase (+450 kcal)",
            "Endurance Performance Fueling (+300 kcal)"
        ],
        index=0
    )

    diet_tags = st.multiselect(
        "Dietary Tags & Exclusions",
        [
            "High-Protein",
            "Low-Carb / Ketogenic",
            "Vegetarian",
            "Vegan (Plant-Based)",
            "Pescatarian",
            "Gluten-Free (Celiac)",
            "Dairy-Free (Lactose-Free)",
            "Nut Allergy (Peanut & Tree Nut)",
            "Egg-Free",
            "Soy-Free",
            "Shellfish-Free",
            "Halal",
            "Kosher",
            "Low-FODMAP (IBS Protocol)",
            "Diabetic-Friendly (Low Glycemic)",
            "Renal / Low Sodium",
            "Heart-Healthy (Low Saturated Fat)",
            "Intermittent Fasting (16/8 Structure)"
        ],
        default=[]
    )

    default_profile = {
        "gender": "Male",
        "age": 18,
        "weight_kg": 35.0,
        "height_cm": 120.0,
        "activity": "Basal Metabolic Rate Only (Bed rest / Comatose)",
        "primary_directive": "Aggressive Fat Loss / Steep Deficit (-500 kcal)",
        "diet_tags": [],
    }
    current_profile = {
        "gender": gender,
        "age": age,
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "activity": activity,
        "primary_directive": primary_directive,
        "diet_tags": diet_tags,
    }
    profile_touched = current_profile != default_profile

    # Mifflin-St Jeor Arithmetic
    if gender == "Male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

    multipliers = {
        "Basal Metabolic Rate Only (Bed rest / Comatose)": 1.0,
        "Sedentary (desk work, minimal movement)": 1.2,
        "Lightly Active (light exercise / sports 1-3 days/wk)": 1.375,
        "Moderately Active (moderate exercise / sports 3-5 days/wk)": 1.55,
        "Very Active (heavy exercise / hard sports 6-7 days/wk)": 1.725,
        "Extremely Active (hard daily training / physical labor)": 1.9
    }
    tdee = bmr * multipliers[activity]

    if "Steep Deficit" in primary_directive:
        target_calories = int(tdee - 500)
    elif "Steady Cut" in primary_directive:
        target_calories = int(tdee - 350)
    elif "Gentle Cut" in primary_directive:
        target_calories = int(tdee - 200)
    elif "Clean Surplus" in primary_directive:
        target_calories = int(tdee + 250)
    elif "Accelerated Mass" in primary_directive:
        target_calories = int(tdee + 450)
    elif "Endurance Performance" in primary_directive:
        target_calories = int(tdee + 300)
    else:
        target_calories = int(tdee)

    calorie_floor = 1200 if gender == "Female" else 1500
    calorie_floor_applied = target_calories < calorie_floor
    if calorie_floor_applied:
        target_calories = calorie_floor
        st.warning(
            f"Clinical calorie floor applied: targets below {calorie_floor} kcal are not permitted for this profile."
        )

    protein_multiplier = 0.8 if "Renal / Low Sodium" in diet_tags else 2.2
    protein_target = int(weight_kg * protein_multiplier)
    fat_target = int((target_calories * 0.25) / 9)
    carb_target = max(0, int((target_calories - (protein_target * 4 + fat_target * 9)) / 4))

    st.markdown("---")
    if st.button("🔄 Reset Consultation Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat = None
        st.session_state.profile_touched = False
        st.rerun()

# -------------------------------------------------------------------------
# 5. Persistent Session State & Gemini Client
# -------------------------------------------------------------------------
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=api_key)

if "chat" not in st.session_state or st.session_state.chat is None:
    st.session_state.chat = st.session_state.client.chats.create(
        model="gemini-3.5-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2
        )
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------------------------------------------------
# 6. Prominent Brand Tagline & Frosted Metric Cards
# -------------------------------------------------------------------------
# Enhanced, larger, full-width tagline banner
st.markdown(
    """
    <div style="display: flex; align-items: center; justify-content: flex-start; margin-bottom: 14px; width: 100%;">
        <div class="tagline-shell">
            <span class="tagline-copy">
                Precision Bio-Engine Architecture Powered by 
                <span class="tagline-brand">DIET BOT</span>
                — Fuel Your Biology with Exact Science.
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

def render_metric_card(container_key, label, value, unit, percentage, fill_color=""):
    with st.container(key=container_key):
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-val">{value} <span class="metric-unit">{unit}</span></div>
                <div class="macro-progress"><div class="macro-progress-fill" style="width: {percentage:.1f}%; {fill_color}"></div></div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return st.button(" ", key=f"{container_key}-button")


protein_calorie_pct = (protein_target * 4 / target_calories) * 100 if target_calories else 0
carb_calorie_pct = (carb_target * 4 / target_calories) * 100 if target_calories else 0
fat_calorie_pct = (fat_target * 9 / target_calories) * 100 if target_calories else 0

# 4-Column Metric Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    energy_clicked = render_metric_card("metric-energy", "⚡ Daily Energy Target", target_calories, "kcal", 100)
with col2:
    protein_clicked = render_metric_card("metric-protein", "🥩 Protein Target", protein_target, "g", protein_calorie_pct, "background: #0284c7;")
with col3:
    carb_clicked = render_metric_card("metric-carbs", "🌾 Carbohydrates", carb_target, "g", carb_calorie_pct, "background: #f59e0b;")
with col4:
    fat_clicked = render_metric_card("metric-fats", "🥑 Lipid Allowance", fat_target, "g", fat_calorie_pct, "background: #10b981;")


@st.dialog("Daily Energy Target")
def show_energy_breakdown():
    st.metric("Daily target", f"{target_calories} kcal")
    energy_change = target_calories - int(tdee)
    change_label = "surplus" if energy_change > 0 else "deficit" if energy_change < 0 else "maintenance"
    st.write(f"Your estimated resting need is **{int(bmr)} kcal** and your activity-adjusted TDEE is **{int(tdee)} kcal**.")
    st.write(f"This plan uses a **{abs(energy_change)} kcal {change_label}** relative to TDEE.")
    st.progress(min(target_calories / max(int(tdee), 1), 1.0), text="Target relative to TDEE")
    if calorie_floor_applied:
        st.info(f"The calculated target fell below the {calorie_floor} kcal clinical floor, so the floor was applied for safety.")
    st.caption(f"Based on {gender.lower()} profile, age {age}, {weight_kg:g} kg, {height_cm:g} cm, and {activity.lower()}.")


@st.dialog("Protein Target")
def show_protein_breakdown():
    protein_calories = protein_target * 4
    st.metric("Daily target", f"{protein_target} g")
    st.write(f"Protein is set at **{protein_multiplier:g} g/kg x {weight_kg:g} kg**.")
    st.write(f"That provides approximately **{protein_calories} kcal**, or **{protein_calorie_pct:.1f}%** of the daily energy target.")
    st.progress(min(protein_calorie_pct / 100, 1.0), text="Protein share of calories")
    if "Renal / Low Sodium" in diet_tags:
        st.info("Renal / Low Sodium guidance is active: protein is capped at 0.8 g/kg rather than the standard 2.2 g/kg setting.")
    else:
        st.caption("The standard target supports satiety, lean-mass retention, and recovery within the selected calorie plan.")


@st.dialog("Carbohydrate Target")
def show_carb_breakdown():
    carb_calories = carb_target * 4
    st.metric("Daily target", f"{carb_target} g")
    st.write(f"Carbohydrates provide approximately **{carb_calories} kcal**, or **{carb_calorie_pct:.1f}%** of the daily energy target.")
    st.write("This is the remaining energy allocation after protein and the 25% fat allocation are accounted for.")
    st.progress(min(carb_calorie_pct / 100, 1.0), text="Carbohydrate share of calories")
    st.caption("Use higher-fiber carbohydrate sources when possible, especially around activity and training.")


@st.dialog("Lipid Allowance")
def show_fat_breakdown():
    fat_calories = fat_target * 9
    st.metric("Daily target", f"{fat_target} g")
    st.write(f"Fat provides approximately **{fat_calories} kcal**, or **{fat_calorie_pct:.1f}%** of the daily energy target.")
    st.write("The baseline allocation is calculated at 25% of target calories, then converted using 9 kcal per gram.")
    st.progress(min(fat_calorie_pct / 100, 1.0), text="Fat share of calories")
    st.caption("Prioritize unsaturated fat sources and keep saturated fat within your clinician’s guidance.")


if energy_clicked:
    show_energy_breakdown()
if protein_clicked:
    show_protein_breakdown()
if carb_clicked:
    show_carb_breakdown()
if fat_clicked:
    show_fat_breakdown()

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
st.markdown('<h5 class="directive-heading">⚡ Directives &amp; Quick Protocols</h5>', unsafe_allow_html=True)

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
# 7. Multi-Turn Conversation Feed & Biometric State Injection
# -------------------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_query = st.chat_input("Inquire about meal distributions, macro adjustments, or portion weights...")
query_to_send = active_directive or user_query

CULINARY_REFUSAL = (
    "I am DietBot, your Clinical Diet Architect, not a culinary chef. I can calculate the caloric, "
    "macronutrient, and portion targets for this item in your calibrated meal plan, but I do not provide "
    "cooking steps or recipes. Would you like me to calibrate its macros for your diet?"
)
OFF_TOPIC_REFUSAL = (
    "I am DietBot, your Clinical Diet Architect. I can help with nutrition targets, meal distributions, "
    "and portion guidance, but I cannot help with coding or other off-topic requests."
)
PERSONAL_QUERY_PATTERN = re.compile(
    r"\b(my|i am|i'm|for me|should i|can i|what should i|personal|my diet|my calories|my macros|how many calories|calorie target|meal plan for me|diet plan|macro target|protein target)\b",
    re.IGNORECASE,
)
CULINARY_PATTERN = re.compile(
    r"\b(how to (bake|cook|make|prepare)|how do i (bake|cook|make|prepare)|pan temperature|oven temperature|recipe|step[- ]by[- ]step)\b",
    re.IGNORECASE,
)
OFF_TOPIC_PATTERN = re.compile(r"\b(python code|write code|coding|javascript|homework|politics|debug my app)\b", re.IGNORECASE)


def deterministic_guardrail(query: str) -> str | None:
    if CULINARY_PATTERN.search(query):
        return CULINARY_REFUSAL
    if OFF_TOPIC_PATTERN.search(query):
        return OFF_TOPIC_REFUSAL
    if PERSONAL_QUERY_PATTERN.search(query) and not profile_touched:
        return "Please update at least one biometric or goal field in the sidebar before I personalize your diet targets."
    return None


if query_to_send:
    # 1. Display only the user's clean message in the UI
    st.session_state.messages.append({"role": "user", "content": query_to_send})
    with st.chat_message("user"):
        st.markdown(query_to_send)

    # 2. Bundle current sidebar parameters into an internal context wrapper
    biometric_context = (
        f"[CURRENT USER BIOMETRICS & METABOLIC CALIBRATION]\n"
        f"- Sex: {gender}\n"
        f"- Age: {age} yrs\n"
        f"- Weight: {weight_kg} kg\n"
        f"- Height: {height_cm} cm\n"
        f"- Activity Index: {activity}\n"
        f"- Primary Directives: {primary_directive}\n"
        f"- Dietary Tags & Exclusions: {tags_str}\n"
        f"- Computed BMR: {int(bmr)} kcal\n"
        f"- Computed TDEE: {int(tdee)} kcal\n"
        f"- Daily Caloric Target: {target_calories} kcal\n"
        f"- Target Macros: Protein {protein_target}g, Fats {fat_target}g, Carbs {carb_target}g\n"
        f"--------------------------------------------------\n"
        f"USER REQUEST: {query_to_send}"
    )

    with st.chat_message("assistant"):
        with st.spinner("Calibrating metabolic targets..."):
            try:
                guardrail_response = deterministic_guardrail(query_to_send)
                if guardrail_response:
                    st.markdown(guardrail_response)
                    st.session_state.messages.append({"role": "assistant", "content": guardrail_response})
                else:
                    # Dispatch the context-enriched prompt to Gemini only after local guardrails pass.
                    response = st.session_state.chat.send_message(biometric_context)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Engine Exception: {e}")