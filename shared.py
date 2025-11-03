

import asyncio

unit_test_response_global = ""
unit_test_event = asyncio.Event() 
 # Event to signal when the response is ready

async def set_unit_test_response(response):
    global unit_test_response_global
    unit_test_response_global = response
    print("Unit test response set.")
    print("Generated unit test cases: ", unit_test_response_global)
    unit_test_event.set()  

async def get_unit_test_response():
    print("Waiting for event to be set...")
    await unit_test_event.wait()  
    print("Event set, returning response.")
    return unit_test_response_global
