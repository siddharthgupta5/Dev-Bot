from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from parseresponse import prs_tool
from supervisor import llm, system_prompt
from getpr import get_pr
from langchain_perplexity import ChatPerplexity
from repofetch import implementation
from langchain.agents import AgentExecutor, create_openai_tools_agent# from ui import  get_unit_test_response
# unit_test_resp = get_unit_test_response()

def create_agent(llm: ChatPerplexity, tools: list, system_prompt: str):
    # Each worker node will be given a name and some tools.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),

        ]
    )
    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor



from raisepr import pr_tool

code_review_tool = [get_pr]

code_review_agent = create_agent(llm, code_review_tool,
                                 " You are a code review agent. You will have the changes made in a pull request in JSON format"
                                 " You will analyze the pull request changes and provide reviews for it"
                                 )

test_tool = [implementation,pr_tool]



unit_test_agent = create_agent(llm,test_tool,
" You are a unit test writer agent"
"You have to generate DETAILED Unit Test cases from the JSON file"
"Also format the response in MARKDOWN format."
"You have to first execute the implementation tool then only you can go to the pr_tool tool"
"After generating the unit tests you have to create a branch and create files using send_pr tool."
"ensure to create a branch and a folder in the branch before uploading the files."
"After generating unit test cases, pass the generated unit test cases to send_pr tool inorder to create files."
"once files have been created, automatically raise a pull request"
"ensure to display the unit test cases to the user."
"After writing this things in new branch you have to send pull request of the test files generated."
"Also it will return the parsed response as well which we have obtained."
"This agent is not for generating test cases for pull request"
"Note that the unit test response received should be filter properly"
"Once the Unit Tests are generated filter them such that the code and filename must be separated"  
"The filename and respective code should be added no extra things and prompts should be added in the code"
)



