import asyncio
import json
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agents import weekend_planner_root_agent

console = Console()

# -------------------------------
# Helper: Pretty-print itinerary
# -------------------------------
def pretty_print_itinerary(json_str: str):
    """Format the final itinerary JSON into a human-friendly schedule with colors."""
    try:
        data = json.loads(json_str)
        console.print(Panel.fit(f"Weekend in {data['city']} — {data['theme']}", style="bold green"))
        for day, activities in data["itinerary"].items():
            console.print(Text(day, style="bold cyan"))
            for act in activities:
                console.print(f"[yellow]{act['time']}[/yellow] - [bold]{act['activity']}[/bold]: {act['details']}")
        console.print(f"\n[italic magenta]Notes:[/italic magenta] {data['notes']}\n")
    except Exception as e:
        console.print(f"[red]⚠️ Could not parse itinerary JSON: {e}[/red]")
        console.print(json_str)

# -------------------------------
# Agent Interaction Function
# -------------------------------
async def call_agent_async(query: str, runner, user_id: str, session_id: str):
    """Send a query to the agent team and print each agent's step output with clear headers and colors."""
    console.print(Panel.fit(f">>> User Query: {query}", style="bold blue"))
    content = types.Content(role="user", parts=[types.Part(text=query)])

    step_counter = 1
    async for event in runner.run_async(user_id=user_id,
                                        session_id=session_id,
                                        new_message=content):
        if event.content and event.content.parts:
            text = event.content.parts[0].text

            if event.is_final_response():
                try:
                    data = json.loads(text)
                    if "city" in data and "itinerary" in data:
                        console.print(Panel.fit(f"Step {step_counter}: Build Itinerary (plan_itinerary_agent)", style="bold green"))
                        pretty_print_itinerary(text)
                    else:
                        console.print(Panel.fit(f"Step {step_counter}: Final JSON Output", style="bold yellow"))
                        console.print(text)
                except Exception:
                    console.print(Panel.fit(f"Step {step_counter}: Final Raw Output", style="bold red"))
                    console.print(text)
            else:
                console.print(Panel.fit(f"Step {step_counter}: Intermediate from {event.author}", style="bold cyan"))
                console.print(text)

            step_counter += 1

        elif event.actions and event.actions.escalate:
            console.print(f"[red]⚠️ Agent escalated: {event.error_message or 'No specific message.'}[/red]")

# -------------------------------
# Team Conversation Runner
# -------------------------------
async def run_team_conversation():
    """Create session, runner, and execute multiple queries with colored logging."""
    console.print(Panel.fit("--- Testing Agent Team Delegation ---", style="bold magenta"))

    APP_NAME = "weekend_planner_agent_team"
    USER_ID = "user_1_agent_team"
    SESSION_ID = "session_001_agent_team"

    # Create session once
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    console.print(f"[green]Session created:[/green] App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

    # Create runner bound to the same session service
    runner_agent_team = Runner(
        agent=weekend_planner_root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    console.print(f"[green]Runner created for agent:[/green] '{weekend_planner_root_agent.name}'")

    # Queries to test
    queries = [
        "Plan a two-day weekend in Montreal, Canada focused on hiking trails, scenic outdoor spots, and nature activities.",
        "Plan a cultural weekend in Toronto, Canada with visits to museums, art galleries, and architectural landmarks.",
        "Plan a weekend in London, UK centered on movies, film history, and entertainment venues.",
        "Plan a weekend in Tokyo, Japan focused on shopping districts, street markets, and nightlife entertainment."
    ]

    # Run each query through the pipeline
    for q in queries:
        await call_agent_async(query=q,
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)
