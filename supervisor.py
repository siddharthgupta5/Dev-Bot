from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_perplexity import ChatPerplexity
from langchain_core.output_parsers import JsonOutputKeyToolsParser
import json

with open('config.json', 'r') as file:
    config = json.load(file)

llm = ChatPerplexity(
    model="gpt-4o",
    api_key=config['perplexity']['api_key']
)

members = ["CodeReview","UnitTest"]

system_prompt = f"""
You are a Dev-Bot who have two functionalities and your name is "Dev-Bot" You have to greet user first and introduce yourself
You have to ask user through the prompt to which functionality he wants to apply
The Functionalities are : 
1.CodeReview : you will have access of pull request url and access token depending on that you have to provide detailed codereview of the same.
2.UnitTest : Write Unit Test cases for the tests provided. Also format the response in string in proper format and Avoid repetitive response
Convert the dictionary response in MARKDOWN format 
As soon as one functionality is applied you have to end conversation with greetings message
"""

options = ["FINISH"] + members

function_def = {
    "name": "route",
    "description": "Select the next role.",
    "parameters": {
        "title": "routeSchema",
        "type": "object",
        "properties": {
            "next": {
                "title": "Next",
                "anyOf": [
                    {"enum": options},
                ],
            }
        },
        "required": ["next"],
    },
}

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            " Given the conversation above, who should act next?"
            "Ask user to choose between CodeReview or UnitTest"
            "Go further only after you get some response through the prompt"
            "Or should we FINISH? Select one of: {options}"
        ),
    ]
).partial(options=str(options), members=", ".join(members))

supervisor_chain = (
        prompt
        | llm
        | JsonOutputKeyToolsParser(key_name="route")
)

def should_end_conversation(state):
    try:
        last_message = state["messages"][-1]
        second_last_message = state["messages"][-2]
        if isinstance(last_message, HumanMessage) and isinstance(second_last_message, HumanMessage):
            return True
        return False
    except Exception as e:
        print("Error in should_end_conversation", e)
    return False

def supervisor_chain_with_termination(state):
    if should_end_conversation(state):
        return {"next": "FINISH"}
    result = supervisor_chain.invoke(state)
    return result