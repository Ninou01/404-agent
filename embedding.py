import json
from tqdm import tqdm

from env import TABLE_NAME
from openai_client import openai_client
from supabase_client import supabase_client as supabase

# --------- LOAD WORKFLOW FILE ---------
with open("Order Lifecycle Training.json", "r", encoding="utf-8") as f:
    lifecycle_data = json.load(f)

# --------- LOAD TRANSITIONS FILE ---------
with open("Order Status Transitions Guide.json", "r", encoding="utf-8") as f:
    transitions_data = json.load(f)

records = []

# --------- FLOW-LEVEL EMBEDDINGS ---------
for flow_name, flow_data in lifecycle_data["flows"].items():
    combined_steps = "\n".join([s["step"] for s in flow_data["steps"]])
    text = f"[FLOW: {flow_name.upper()}]\n{combined_steps}"
    embedding = openai_client.embeddings.create(input=[text], model="text-embedding-ada-002").data[0].embedding
    record = {
        "content": text,
        "embedding": embedding,
        "metadata": {
            "type": "flow",
            "flow_type": flow_name,
            "step_number": None,
            "related_statuses": [],
            "related_entities": json.dumps([])
        }
    }
    records.append(record)
    
print('finished FLOW-LEVEL')


# --------- STEP-LEVEL EMBEDDINGS ---------
for flow_name, flow_data in lifecycle_data["flows"].items():
    for i, step in enumerate(flow_data["steps"]):
        text = f"[{flow_name.upper()} - Step {i+1}] {step['step']}"
        embedding = openai_client.embeddings.create(input=[text], model="text-embedding-ada-002").data[0].embedding
        record = {
            "content": text,
            "embedding": embedding,
            "metadata": {
                "type": "step",
                "flow_type": flow_name,
                "step_number": i + 1,
                "related_statuses": step.get("order_status", []) + step.get("order_intra_status", []),
                "related_entities": json.dumps(step.get("related_entity", {}))
            }
        }
        records.append(record)
        
print('finished STEP-LEVEL')


# --------- STATUS AND INTRA-STATUS EMBEDDINGS ---------
for s in lifecycle_data["statuses"]:
    text = f"[STATUS: {s['name']}]\n{s['description']}\nContext: {s['context']}"
    embedding = openai_client.embeddings.create(input=[text], model="text-embedding-ada-002").data[0].embedding
    record = {
        "content": text,
        "embedding": embedding,
        "metadata": {
            "type": "status",
            "flow_type": None,
            "step_number": None,
            "related_statuses": [s['name']],
            "related_entities": json.dumps({})
        }
    }
    records.append(record)
    
print('finished STATUS embedding')

for s in lifecycle_data["order_intra_statuses"]:
    text = f"[INTRA-STATUS: {s['name']}]\n{s['description']}\nContext: {s['context']}"
    embedding = openai_client.embeddings.create(input=[text], model="text-embedding-ada-002").data[0].embedding
    record = {
        "content": text,
        "embedding": embedding,
        "metadata": {
            "type": "intra_status",
            "flow_type": None,
            "step_number": None,
            "related_statuses": [s['name']],
            "related_entities": json.dumps({})
        }
    }
    records.append(record)
    
print('finished INTRA-STATUS embedding')


# --------- TRANSITION RULE EMBEDDINGS ---------
for from_state, transitions in transitions_data.items():
    from_parts = from_state.split("::")
    from_status = from_parts[0]
    from_intra_status = from_parts[1] if len(from_parts) > 1 else None

    for t in transitions:
        to_parts = t["to"].split("::")
        to_status = to_parts[0]
        to_intra_status = to_parts[1] if len(to_parts) > 1 else None
        condition = t["condition"]

        text = f"TRANSITION RULE:\nFrom: {from_state}\nTo: {t['to']}\nCondition: {condition}"
        embedding = openai_client.embeddings.create(input=[text], model="text-embedding-ada-002").data[0].embedding
        record = {
            "content": text,
            "embedding": embedding,
            "metadata": {
                "type": "transition",
                "flow_type": None,
                "step_number": None,
                "related_statuses": [from_status, to_status],
                "related_entities": json.dumps({}),
            }
        }
        records.append(record)
        
print('finished TRANSITION RULE EMBEDDING')

# --------- INSERT INTO SUPABASE ---------
print("Inserting into Supabase...")
for record in tqdm(records):
    supabase.table(TABLE_NAME).insert(record).execute()

print("✅ All embeddings uploaded to Supabase with combined workflow and transition data!")
