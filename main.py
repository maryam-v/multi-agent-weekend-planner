"""
main.py — Entry point for the Weekend Planner Agent Team

This script initializes the agent pipeline and runs sample queries.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Optional sanity check
if not os.environ.get("GOOGLE_API_KEY"):
    raise RuntimeError("GOOGLE_API_KEY not set. Please add it to your .env file.")

import asyncio
from runner import run_team_conversation

def main():
    """Run the weekend planner demo."""
    print("🚀 Starting Weekend Planner Agent Team...\n")
    asyncio.run(run_team_conversation())
    print("\n✅ Weekend Planner run complete.")

if __name__ == "__main__":
    main()
