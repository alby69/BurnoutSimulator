import json
import jsonschema
import sys
import os

def validate_events(schema_path, events_path):
    if not os.path.exists(schema_path):
        print(f"Schema not found: {schema_path}")
        return False
    if not os.path.exists(events_path):
        print(f"Events not found: {events_path}")
        return False

    with open(schema_path, 'r') as f:
        schema = json.load(f)

    with open(events_path, 'r') as f:
        events = json.load(f)

    try:
        jsonschema.validate(instance=events, schema=schema)
        print("✅ Validation successful: events.json follows the schema.")
        return True
    except jsonschema.exceptions.ValidationError as err:
        print(f"❌ Validation error: {err.message}")
        print(f"At: {err.path}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    schema = "game/data/events.schema.json"
    events = "game/data/events.json"
    if not validate_events(schema, events):
        sys.exit(1)
