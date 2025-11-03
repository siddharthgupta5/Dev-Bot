from graph import graph
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


for s in graph.stream(
    {
        "messages": [
            SystemMessage(
                content="Ask User which function he wants to implement? Depending upon the choice implement the thing."
            ),
            # HumanMessage(
            #     content="Provide Unit Test cases."
            # ),
            AIMessage(
               content="Hi I am Dev-Bot. I can do the following things:"
                       "1.Code-Review"
                       "2.Unit Test Writing"
                       "How can I assist you?"
            ),
        ],
    },
    {"recursion_limit": 150},
):
    if "__end__" not in s:
        print(s)
        # op_ph.text(s)
        print("---")
