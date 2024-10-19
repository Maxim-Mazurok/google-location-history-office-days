import json
import jsonschema
from genson import SchemaBuilder

# Install the necessary packages:
# pip install jsonschema genson

# Load a small sample of your large JSON file
with open('data/Records.json', 'r') as f:
    data = json.load(f)

# Initialize the schema builder
builder = SchemaBuilder()
builder.add_object(data)

# Print the schema
print(builder.to_schema())
