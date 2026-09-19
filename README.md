# DietBot: Bio-Engine Clinical Diet Architect

[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit%201.37%2B-FF4B4B.svg)](https://streamlit.io/)
[![LLM Engine](https://img.shields.io/badge/LLM-Gemini%203.5%20Flash%20Lite-4285F4.svg)](https://ai.google.dev/)
[![SDK](https://img.shields.io/badge/SDK-google--genai-00A67E.svg)](https://github.com/googleapis/python-genai)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)

DietBot is a Streamlit nutrition-planning application that combines deterministic metabolic calculations with Google Gemini meal-planning assistance. It is intended for nutrition education and planning, not diagnosis or medical treatment.

## Features

- **Metabolic engine:** Calculates BMR with Mifflin-St Jeor and derives TDEE from activity and goal settings.
- **Clinical calorie floor:** Enforces 1,200 kcal minimum for female profiles and 1,500 kcal minimum for male profiles, with an in-app warning when applied.
- **Condition-aware macros:** The `Renal / Low Sodium` tag changes protein to 0.8 g/kg; other profiles use 2.2 g/kg.
- **Interactive metric cards:** Energy, protein, carbohydrates, and fats are clickable cards that open `st.dialog` breakdowns with calculations and interpretation.
- **Deterministic guardrails:** Culinary recipe and off-topic requests are refused before a Gemini call.
- **Dark-mode UI:** Supports Streamlit dark mode, system dark mode, readable frosted surfaces, and a visible darkened background image.
- **Persistent consultation:** Gemini chat history and displayed messages persist through `st.session_state`.

## Metabolic Formulas

### Basal Metabolic Rate

$$\text{BMR}_{\text{Male}} = (10 \times \text{weight}_{\text{kg}}) + (6.25 \times \text{height}_{\text{cm}}) - (5 \times \text{age}_{\text{yrs}}) + 5$$

$$\text{BMR}_{\text{Female}} = (10 \times \text{weight}_{\text{kg}}) + (6.25 \times \text{height}_{\text{cm}}) - (5 \times \text{age}_{\text{yrs}}) - 161$$

### Total Daily Energy Expenditure

$$\text{TDEE} = \text{BMR} \times \text{Activity Multiplier}$$

### Macronutrients

$$\text{Target Calories} = \text{TDEE} \pm \Delta_{\text{Protocol}}$$

- Standard protein: $\text{weight}_{\text{kg}} \times 2.2$ g
- Renal / Low Sodium protein: $\text{weight}_{\text{kg}} \times 0.8$ g
- Fat: $\frac{\text{Target Calories} \times 0.25}{9}$ g
- Carbohydrates: remaining calories after protein and fat, divided by 4

Macro card progress bars use 4 kcal/g for protein and carbohydrates and 9 kcal/g for fat.

## Project Structure

```text
Diet Bot/
├── app.py                  # Streamlit application and Gemini chat flow
├── style.css               # Glass UI, responsive layout, and theme overrides
├── requirements.txt        # Runtime dependencies
├── cli_test.py             # Optional CLI smoke-test client
├── assets/
│   └── background.jpg      # Dashboard background image
├── .env                    # Local Gemini API key, ignored by Git
└── .streamlit/
    └── secrets.toml        # Optional Streamlit secret, ignored by Git
```

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configure Gemini

Create `.env` in the project root:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

Or use `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your_actual_gemini_api_key_here"
```

Never commit either credentials file.

## Run

```bash
streamlit run app.py
```

Open `http://localhost:8501` if the browser does not open automatically.

## Testing

Run the optional CLI smoke test with:

```bash
python cli_test.py
```

## Safety

DietBot provides estimates and educational guidance. Users with renal disease, diabetes, cardiovascular disease, pregnancy, eating disorders, severe underweight, or other medical concerns should consult a qualified physician or registered dietitian before changing their diet.
