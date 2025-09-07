import ollama
def add_two_numbers(a: int, b: int) -> int:
    """
    Add two numbers
    Args:
        a: The first integer number
        b: The second integer number
    Returns:
        int: The sum of the two numbers
    """
    return a + b

response = ollama.chat(
    'gemma3-tools',
    messages=[{'role': 'user', 'content': 'What is 10 + 10?'}],
    tools=[add_two_numbers],
)
print(response)
