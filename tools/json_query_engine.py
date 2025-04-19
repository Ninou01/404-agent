import json
from llama_index.llms.openai import OpenAI
from llama_index.core.indices.struct_store import JSONQueryEngine
from llama_index.core.tools.query_engine import QueryEngineTool

llm = OpenAI(model="gpt-4")

with open("Order Lifecycle Training.json", "r") as f:
    status_transitions_value = json.load(f)

status_transitions_schema = {
  "type": "object",
  "description": "Defines all possible transitions from each order status, including target statuses and the conditions under which transitions occur.",
  "patternProperties": {
    "^.*$": {
      "type": "array",
      "description": "List of transition rules from the current status",
      "items": {
        "type": "object",
        "properties": {
          "to": {
            "type": "string",
            "description": "The target status the order transitions to"
          },
          "condition": {
            "type": "string",
            "description": "The condition that must be met for the transition to occur"
          }
        },
        "required": ["to", "condition"]
      }
    }
  },
  "additionalProperties": False
}


with open("Order Status Transitions Guide.json", "r") as f:
    order_lifecycle_value = json.load(f)

order_lifecycle_schema = {
  "type": "object",
  "properties": {
    "flows": {
      "type": "object",
      "description": "Describes various operational flows, each composed of multiple sequential steps.",
      "patternProperties": {
        "^.*$": {
          "type": "object",
          "properties": {
            "steps": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "step": { "type": "string" },
                  "order_status": {
                    "type": "array",
                    "items": { "type": "string" }
                  },
                  "order_intra_status": {
                    "type": "array",
                    "items": { "type": "string" }
                  },
                  "related_entity": {
                    "type": "object",
                    "properties": {
                      "entity": { "type": "string" },
                      "status": { "type": "string" },
                      "intra_status": { "type": "string" }
                    },
                    "additionalProperties": False
                  }
                },
                "required": ["step"]
              }
            }
          },
          "required": ["steps"]
        }
      }
    },
    "statuses": {
      "type": "array",
      "description": "List of top-level order statuses with descriptions and context.",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "description": { "type": "string" },
          "context": { "type": "string" }
        },
        "required": ["name", "description"]
      }
    },
    "order_intra_statuses": {
      "type": "array",
      "description": "List of intra-statuses representing detailed sub-states of an order.",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "description": { "type": "string" },
          "context": { "type": "string" }
        },
        "required": ["name", "description"]
      }
    },
    "related_entities": {
      "type": "object",
      "description": "Status descriptions of related entities such as vouchers or bags.",
      "patternProperties": {
        "^.*$": {
          "type": "object",
          "properties": {
            "statuses": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "name": { "type": "string" },
                  "description": { "type": "string" },
                  "context": { "type": "string" }
                },
                "required": ["name", "description"]
              }
            }
          },
          "required": ["statuses"]
        }
      }
    }
  },
  "required": ["flows", "statuses", "order_intra_statuses", "related_entities"]
}



status_transitions_query_engine = JSONQueryEngine(
  json_value=status_transitions_value,
  json_schema=status_transitions_schema,
  synthesize_response=False,
)


order_lifecycle_query_engine = JSONQueryEngine(
  json_value=order_lifecycle_value,
  json_schema=order_lifecycle_schema,
  synthesize_response=False,
)

status_transitions_tool = QueryEngineTool.from_defaults(
  query_engine=status_transitions_query_engine,
  name="status_transitions_tool",
  description="Provides valid status transitions for orders based on the current status."
)

order_lifecycle_tool = QueryEngineTool.from_defaults(
  query_engine=order_lifecycle_query_engine,
  name="order_lifecycle_tool",
  description="Provides detailed information about order lifecycle steps, statuses, and related entities."
)