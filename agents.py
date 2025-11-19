from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.genai import types
from google.adk.tools import google_search

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Agent 1: Extract user interest
retrieve_user_interest_agent = LlmAgent(
    name="retrieve_user_interest_agent",
    description="Extracts target city and maps interest to predefined categories.",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction=""" You are the **Location/Interest Extraction Agent**.
                    Your job is to convert a user's free-form travel request into a strict JSON object.

                    ------------------------------------------------
                    REQUIRED OUTPUT FORMAT (NO TEXT OUTSIDE JSON):
                    {"target_city": "...", "interest_category": "..."}
                    ------------------------------------------------

                    TARGET_CITY RULES:
                    - Extract the city (e.g., "San Diego", "Rome, Italy", "Montreal").
                    - Use the most explicit version possible.

                    INTEREST CATEGORY RULES:
                    Map the user’s interest to EXACTLY ONE of the following five categories,
                    returned UPPERCASE:
                    - NATURE_OUTDOORS
                    - CULTURE_ARTS
                    - FOOD_DRINK
                    - NIGHTLIFE_ENTERTAINMENT
                    - SHOPPING_MARKETS

                    STRICT RULES:
                    - Only output raw JSON.
                    - No markdown.
                    - No explanation.
                    - No commentary.
                    """,
    tools=[],
    output_key="user_location_and_interests",
)

# Agent 2: Discover POIs
discovery_agent = LlmAgent(
    name="discovery_agent",
    description="Finds 3–5 relevant POIs using Google Search.",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction=""" You are the **Discovery Agent**.

                    Here is the structured input from the previous agent:
                    {user_location_and_interests}

                    ------------------------------------------------
                    REQUIRED TASKS
                    ------------------------------------------------
                    1. Parse the JSON:
                    {"target_city": "...", "interest_category": "..."}

                    2. Use the google_search tool to find 3–5 relevant POIs in the target city.

                    3. Extract:
                    - name
                    - address
                    - rating (if available)
                    - type (category inferred from search)

                    4. Output ONLY a JSON array of POIs:
                    [
                        {"name": "...", "address": "...", "rating": "...", "type": "..."},
                        ...
                    ]

                    STRICT RULES:
                    - No text outside the JSON array.
                    - No markdown.
                    - Include 3–5 items.
                    """,
    tools=[google_search],
    output_key="suggested_places",
)

# Agent 3: Plan itinerary
plan_itinerary_agent = LlmAgent(
    name="plan_itinerary_agent",
    description="Creates a structured weekend itinerary using POIs.",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction=""" You are the **Itinerary Agent**.

                    Here is the list of suggested POIs:
                    {suggested_places}

                    ------------------------------------------------
                    REQUIRED TASK
                    ------------------------------------------------
                    Create a 2-day weekend itinerary (Saturday and Sunday) that:
                    - Uses the provided POIs
                    - Orders activities logically
                    - Assigns realistic times
                    - Includes lunch/dinner suggestions
                    - Minimizes travel distances
                    - Includes a theme for the trip
                    - Ends with a helpful note

                    ------------------------------------------------
                    STRICT OUTPUT FORMAT (NO TEXT OUTSIDE JSON):
                    {
                    "city": "...",
                    "theme": "...",
                    "itinerary": {
                        "Saturday": [
                        {"time": "...", "activity": "...", "details": "..."},
                        ...
                        ],
                        "Sunday": [
                        {"time": "...", "activity": "...", "details": "..."},
                        ...
                        ]
                    },
                    "notes": "..."
                    }
                    ------------------------------------------------

                    RULES:
                    - Only output raw JSON.
                    - No markdown.
                    - No commentary.
                    """,
    tools=[],
    output_key="final_itinerary",
)

# Root agent
weekend_planner_root_agent = SequentialAgent(
    name="WeekendPlanner",
    sub_agents=[
        retrieve_user_interest_agent,
        discovery_agent,
        plan_itinerary_agent,
    ],
)
