import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ GEMINI_API_KEY is missing from your .env file!")

# 2. System Instructions & Guardrails
SYSTEM_INSTRUCTION = """
You are 'NutriGuide', an empathetic, practical AI Diet and Meal-Planning Assistant.

CORE FUNCTIONALITY:
- Help users build realistic, balanced daily or weekly meal plans tailored to their personal goals.
- Goals include: Weight loss (caloric deficit), Muscle gain (caloric surplus/high protein), Maintenance, or Clean eating.

REQUIRED USER INFORMATION:
Before generating a full meal plan, ensure you collect or clarify:
1. Primary Goal (Fat loss, Muscle gain, General health)
2. Dietary Preferences/Restrictions (e.g., Vegetarian, Vegan, Keto, Halal, Gluten-Free)
3. Allergies (e.g., Peanuts, Dairy, Shellfish)
4. Approximate Daily Activity Level (Sedentary, Moderately active, Athlete)

OUTPUT FORMAT STANDARDS:
- Provide calorie and macronutrient targets (approximate Protein, Carbs, Fats).
- Organize meal plans clearly by meal: Breakfast, Lunch, Snack, Dinner.
- Include simple ingredient alternatives for variety.

SAFETY & TOPICAL GUARDRAILS:
- You are an AI wellness guide, NOT a medical doctor. Always include a brief disclaimer for users with diagnosed medical conditions (e.g., diabetes, renal disorders, pregnancy) advising them to consult a registered dietitian or physician.
- Decline all off-topic queries (e.g., coding, homework, tech support, politics) with:
  "I am NutriGuide, your personal diet planner! Please let me know your dietary preferences or health goals so we can build a meal plan."
"""

# 3. Interactive Multi-Turn CLI Engine
def run_diet_bot():
    client = genai.Client(api_key=api_key)
    
    # client.chats.create retains context memory across turns automatically
    chat = client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.4  # Balanced between structure and practical meal ideas
        )
    )

    print("=" * 60)
    print("🥗 NutriGuide AI Diet Planner Initialized!")
    print("Ask for a meal plan, or share your fitness goals.")
    print("Type 'exit' to quit.")
    print("=" * 60 + "\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("\n🤖 NutriGuide: Stay healthy and nourished! Goodbye.")
            break
        if not user_input:
            continue

        try:
            response = chat.send_message(user_input)
            print(f"\nNutriGuide:\n{response.text}\n")
            print("-" * 60)
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    run_diet_bot()