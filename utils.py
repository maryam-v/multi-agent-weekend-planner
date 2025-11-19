import json

def pretty_print_itinerary(json_str: str):
    """Format the final itinerary JSON into a human-friendly schedule."""
    try:
        data = json.loads(json_str)
        print(f"\nWeekend in {data['city']} — {data['theme']}")
        for day, activities in data["itinerary"].items():
            print(f"\n{day}:")
            for act in activities:
                print(f"  {act['time']} - {act['activity']}: {act['details']}")
        print(f"\nNotes: {data['notes']}\n")
    except Exception as e:
        print(f"⚠️ Could not parse itinerary JSON: {e}")
        print(json_str)
