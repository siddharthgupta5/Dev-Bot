import re
import asyncio
from langchain_core.tools import Tool
from shared import get_unit_test_response

async def parse_res(*args):
    """
    This tool processes the unit test response and extracts runnable code for each file.
    Steps:
    1. Retrieve the unit test response asynchronously.
    2. Identify the programming language for each code block.
    3. Filter the response to extract only runnable code.
    4. Save the processed code in a dictionary format:
       - Key: test_[original_file_name].[appropriate_extension]
       - Value: The runnable code
    5. Print the filtered response to the console.
    6. Return the processed dictionary.

    Returns:
    dict: A dictionary containing filtered unit tests, where keys are file names
          and values are the corresponding runnable code.
    """
    try:
        unit_test_response = await get_unit_test_response()
        print("Unit test response received:", unit_test_response)  # Debugging statement
        filtered_response = {}
        pattern = r'####\s*File:\s*`([^`]+)`\s*```(\w+)?\n(.*?)```'
        matches = re.finditer(pattern, unit_test_response, re.DOTALL)
        match_count = 0
        for match in matches:
            match_count += 1
            file_name = match.group(1)
            language = match.group(2) or 'python'
            code = match.group(3).strip()
            extension = {
                'python': '.py',
                'java': '.java',
                'javascript': '.js',
                'typescript': '.ts',
                'c': '.c',
                'cpp': '.cpp',
                'csharp': '.cs',
                'go': '.go',
                'ruby': '.rb',
                'php': '.php'
            }.get(language.lower(), '.txt')
            test_file_name = f"test_{file_name}{extension}"
            filtered_response[test_file_name] = code
        print(f"Number of matches found: {match_count}")
        print("Filtered Response:")
        for file_name, code in filtered_response.items():
            print(f"\n{file_name} -> \n{code}\n{'='*50}")
        return filtered_response
    except Exception as e:
        print(f"An error occurred while parsing the unit test response: {str(e)}")
        return {}



async def send_wrapper(*args):
     await parse_res(*args)


prs_tool = Tool(
    name="request",
    func=send_wrapper,
    description="The tool will wait until the unit tests are generated. After that the tool will filter the response and will put it into dictionary"
)


if __name__ == "__main__":
    asyncio.run(send_wrapper())

