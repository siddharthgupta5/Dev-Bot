import gradio as gr
import asyncio
from graph import graph
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from shared import set_unit_test_response, unit_test_event
from raisepr import send_pr_wrapper


async def async_wrap(generator):
    for item in generator:
        await asyncio.sleep(0)
        yield item


async def interact_with_langchain_agent(prompt, messages):
    global unit_test_response_global
    try:
        messages.append({"role": "user", "content": prompt})
        if "code review" in prompt.lower():
            function_choice = "CodeReview"
        elif "unit test" in prompt.lower():
            function_choice = "UnitTest"
        else:
            function_choice = None

        if function_choice:
            initial_messages = [
                SystemMessage(
                    content="Ask User which function he wants to implement? Depending upon the choice implement the thing."
                ),
                HumanMessage(
                    content=prompt
                ),
                AIMessage(
                    content=f"Hi I am Dev-Bot. You chose {function_choice}. I will now proceed with {function_choice}."
                ),
            ]

            response_generated = False
            unit_test_response = None

            async for s in async_wrap(graph.stream(
                    {
                        "messages": initial_messages,
                    },
                    {"recursion_limit": 150},
            )):
                if "__end__" not in s:
                    if isinstance(s, dict):
                        for key, value in s.items():
                            if 'messages' in value:
                                for message in value['messages']:
                                    if isinstance(message, SystemMessage):
                                        content = message.content
                                        messages.append({"role": "assistant", "content": content})
                                        response_generated = True
                                        # Check if the response contains "Unit Test"
                                        if "Unit Test" in content:
                                            unit_test_response = content
                                            print("Captured Unit Test Response:", unit_test_response)  # Debug print
                            else:
                                content = str(s)
                                messages.append({"role": "assistant", "content": content})
                                response_generated = True
                                # Check if the response contains "Unit Test"
                                if "Unit Test" in content:
                                    unit_test_response = content
                                    print("Captured Unit Test Response:", unit_test_response)  # Debug print
                    else:
                        content = str(s)
                        messages.append({"role": "assistant", "content": content})
                        response_generated = True
                        # Check if the response contains "Unit Test"
                        if "Unit Test" in content:
                            unit_test_response = content
                            print("Captured Unit Test Response:", unit_test_response)  # Debug print

            if not response_generated:
                messages.append(
                    {"role": "assistant", "content": "I'm sorry, I didn't understand that. Can you please clarify?"})

            if unit_test_response:
                print("Unit Test Response:", unit_test_response)
                await set_unit_test_response(unit_test_response)

                await send_pr_wrapper()

        else:
            messages.append({"role": "assistant",
                             "content": "Please choose a function to implement: Code Review or Unit Test Writing."})

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        messages.append({"role": "assistant", "content": error_message})

    return messages


async def submit_message(user_message, chat_history):
    messages = await interact_with_langchain_agent(user_message, chat_history)
    return messages


def run_gradio():
    with gr.Blocks() as demo:
        gr.Markdown("# Chat with a Dev-Bot. Lets Talk Dev!")
        chatbot = gr.Chatbot(

            type="messages",
            label="Agent",
            avatar_images=(
                None,
                "https://em-content.zobj.net/source/twitter/141/parrot_1f99c.png",
            ),
        )
        input_box = gr.Textbox(lines=1, label="Chat Message")

        input_box.submit(submit_message, [input_box, chatbot], [chatbot])

    demo.launch()


if __name__ == "__main__":
    run_gradio()
