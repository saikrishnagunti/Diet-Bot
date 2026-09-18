# 🥗 Diet Bot • Bio-Engine Clinical Diet Architect

[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit%201.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![LLM Engine](https://img.shields.io/badge/LLM-Gemini%203.6%20Flash-4285F4.svg)](https://ai.google.dev/)
[![SDK](https://img.shields.io/badge/SDK-google--genai-00A67E.svg)](https://github.com/googleapis/python-genai)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Diet Bot is an AI-powered clinical nutritional architecture and metabolic modeling platform. Designed as a high-fidelity alternative to generic recipe generators, it combines the **Mifflin-St Jeor metabolic equations** with **Google Gemini 3.5 Flash lite** to compute individualized caloric, macronutrient, and daily meal targets under strict domain-level non-culinary guardrails.

---

## 🌟 Key Features & Engineering Highlights

* **🧬 Real-Time Mifflin-St Jeor Metabolic Engine:** Calculates Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE) dynamically across biological sex, age, height, weight, activity indices, and surplus/deficit protocols.
* **🛡️ Zero-Tolerance Non-Culinary Guardrail:** Operates under a clinical firewall that explicitly refuses step-by-step cooking recipes, pan temperatures, or kitchen instructions, redirecting the user back to macronutrient distributions.
* **💎 Glassmorphic Clinical UI:** Custom translucent styling (`style.css`), dynamic macro ratio progress bars, a smoke-grey tinted sidebar, and a floating chat input capsule with boundary separation.
* **🖼️ Full-Screen Base64 Asset Injection:** Reads local imagery from an `assets/` directory and injects it across all layout containers with a calibrated translucent tint to guarantee contrast and legibility.
* **⚡ Persistent Multi-Turn Client Lifecycle:** Integrates the official `google-genai` SDK (`client.chats.create`) with Streamlit's `st.session_state` to retain multi-turn context memory across consultations.

---

## 📐 Mathematical Formulation (Mifflin-St Jeor Equations)

### 1. Basal Metabolic Rate (BMR)

$$\text{BMR}_{\text{Male}} = (10 \times \text{weight}_{\text{kg}}) + (6.25 \times \text{height}_{\text{cm}}) - (5 \times \text{age}_{\text{yrs}}) + 5$$

$$\text{BMR}_{\text{Female}} = (10 \times \text{weight}_{\text{kg}}) + (6.25 \times \text{height}_{\text{cm}}) - (5 \times \text{age}_{\text{yrs}}) - 161$$

### 2. Total Daily Energy Expenditure (TDEE)

$$\text{TDEE} = \text{BMR} \times \text{Activity Multiplier}$$

* **Sedentary:** $1.2$
* **Lightly Active (1–3 sessions/wk):** $1.375$
* **Moderately Active (3–5 sessions/wk):** $1.55$
* **Very Active (6–7 sessions/wk):** $1.725$

### 3. Macronutrient Targets

$$\text{Target Calories} = \text{TDEE} \pm \Delta_{\text{Protocol}}$$

* **Protein:** $\text{Target (g)} = \text{weight}_{\text{kg}} \times 2.2$
* **Lipids (Fats):** $\text{Target (g)} = \frac{\text{Target Calories} \times 0.25}{9}$
* **Carbohydrates:** $\text{Target (g)} = \max\left(0, \frac{\text{Target Calories} - (\text{Protein}_{\text{g}} \times 4 + \text{Fat}_{\text{g}} \times 9)}{4}\right)$

---

## 🗂️ Project Structure

```text
diet-planner/
│
├── assets/
│   └── background.jpg      # High-resolution local UI background image
├── .env                    # Private Google Gemini API key (Git-ignored)
├── .gitignore              # Git exclusion rules for secrets and environments
├── requirements.txt        # Production dependency specifications
├── README.md               # Technical documentation & setup guide
├── style.css               # Frosted glassmorphism, capsule input & layout CSS
└── app.py                  # Streamlit dashboard, bio-engine, and Gemini chat

```

---

## 🛠️ Installation & Local Setup

### 1. Clone the Repository

```bash
git clone [https://github.com/saikrishnagunti/Diet-Bot-.git](https://github.com/saikrishnagunti/Diet-Bot-.git)
cd YOUR_REPOSITORY

```

### 2. Configure Virtual Environment & Install Dependencies

```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

```

### 3. Environment Variable Configuration

Create a `.env` file in the root project folder:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here

```

### 4. Background Image Setup

Place your desired background image in the `assets/` directory:

```bash
assets/background.jpg

```

### 5. Launch the Application

```bash
streamlit run app.py

```

*Opens automatically in your default browser at `http://localhost:8501`.*

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE&utm_source=gemini) file for details.