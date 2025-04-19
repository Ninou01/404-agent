from llama_index.core.agent import ReActAgent
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI

from tools.json_query_engine import status_transitions_tool, order_lifecycle_tool
from tools.order_log_tool import order_log_tool
from tools.retriver_query_engine import WorkflowRetriever
from tools.time_line_builder import timeline_builder_tool


memory = ChatMemoryBuffer.from_defaults(token_limit=40000)

SYSTEM_PROMPT = """
You are Maystro Investigator, an AI agent specialized in tracing missing items in logistics workflows.

INVESTIGATION PROCESS:
1. First, retrieve the order timeline using build_order_timeline
2. Analyze the order's status transitions using status_transitions_tool
3. Check the expected workflow using order_lifecycle_tool and WorkflowRetriever
4. Identify gaps by comparing actual flow to expected flow
5. Generate a comprehensive investigation response
6. Store important findings in your memory for future reference

When investigating items:
- Use your memory of past investigations for similar issues or patterns
- Refer to previously found item locations for similar cases
- Apply knowledge from past solved cases to current investigations

Your final response MUST follow the InvestigationResponse format with:
- summary: Clear explanation of what happened to the order in plain language
- gaps_or_broken_steps: List specific workflow deviations found
- order_timeline: Include the complete timeline from the tool
- current_state: Include the current state information
"""
tools = [
    WorkflowRetriever,
    order_lifecycle_tool,
    status_transitions_tool,
    order_log_tool,
    timeline_builder_tool,
]

llm = OpenAI(model="gpt-4o")
agent = ReActAgent.from_tools(llm=llm, tools=tools, memory=memory, verbose=True, system_prompt=SYSTEM_PROMPT)

while (prompt := input("Enter a prompt (q to quit): ")) != "q":
    result = agent.chat(prompt)
    print(result)