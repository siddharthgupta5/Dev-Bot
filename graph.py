import operator
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, END
from supervisor import members, supervisor_chain_with_termination
from agent import code_review_agent, unit_test_agent

import functools

def agent_node(state, agent, name):
    try:
        result = agent.invoke(state)
        if isinstance(result, dict):
            if "output" in result:
                content = result["output"]
            elif "messages" in result:
                content = str(result["messages"])
            else:
                content = str(result)
        else:
            content = str(result)
            
        return {"messages": [SystemMessage(content=content, name=name)]}
    except Exception as e:
        print(f"Error in agent_node {name}: {e}")
        return {"messages": [SystemMessage(content=f"Error: {str(e)}", name=name)]}

class AgentState(TypedDict):

    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str

code_review_node = functools.partial(agent_node, agent=code_review_agent, name="CodeReview")
unit_test_node = functools.partial(agent_node, agent=unit_test_agent, name="UnitTest")

workflow = StateGraph(AgentState)
workflow.add_node("CodeReview", code_review_node)
workflow.add_node("UnitTest", unit_test_node)

workflow.add_node("supervisor", supervisor_chain_with_termination)

for member in members:
    workflow.add_edge(member, "supervisor")

conditional_map = {k: k for k in members}
conditional_map["FINISH"] = END

workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
workflow.set_entry_point("supervisor")

graph = workflow.compile()
