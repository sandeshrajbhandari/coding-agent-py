import inspect
import random
from typing import Dict, Any, List

def get_weather(city: str) -> str:
    """
    Get the current temperature for a city

    Args:
        city (str): The name of the city

    Returns:
        str: The current temperature
    """
    temperatures = list(range(-10, 35))
    temp = random.choice(temperatures)
    return f'The temperature in {city} is {temp}°C'

def get_weather_conditions(city: str) -> str:
    """
    Get the weather conditions for a city

    Args:
        city (str): The name of the city

    Returns:
        str: The current weather conditions
    """
    conditions = ['sunny', 'cloudy', 'rainy', 'snowy', 'foggy']
    return random.choice(conditions)

def search_gutenberg_books(search_terms: List[str]) -> str:
    """
    Search for books in the Project Gutenberg library

    Args:
        search_terms (List[str]): List of search terms to find books

    Returns:
        str: Search results
    """
    return f"Searching for books with terms: {', '.join(search_terms)}"

def create_tools_from_functions(available_tools: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Automatically create a tools list from available_tools dictionary
    
    Args:
        available_tools: Dictionary mapping function names to function objects
        
    Returns:
        List of tool definitions in the required format
    """
    tools = []
    
    for func_name, func_obj in available_tools.items():
        # Get function signature
        sig = inspect.signature(func_obj)
        
        # Get docstring and parse it
        docstring = func_obj.__doc__ or ""
        description = docstring.split('\n')[1].strip() if docstring else f"Function: {func_name}"
        
        # Build parameters schema
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            param_type = "string"  # default
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list or (hasattr(param.annotation, '__origin__') and param.annotation.__origin__ is list):
                    param_type = "array"
                    if hasattr(param.annotation, '__args__') and param.annotation.__args__:
                        items_type = "string"
                        if param.annotation.__args__[0] == int:
                            items_type = "integer"
                        elif param.annotation.__args__[0] == float:
                            items_type = "number"
                        elif param.annotation.__args__[0] == bool:
                            items_type = "boolean"
                    else:
                        items_type = "string"
                    properties[param_name] = {
                        "type": param_type,
                        "items": {"type": items_type},
                        "description": f"Parameter: {param_name}"
                    }
                else:
                    param_type = "string"
            
            if param_type != "array":
                properties[param_name] = {
                    "type": param_type,
                    "description": f"Parameter: {param_name}"
                }
            
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        tool_definition = {
            "type": "function",
            "function": {
                "name": func_name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
        
        tools.append(tool_definition)
    
    return tools

# Available tools dictionary
available_tools = {
    'get_weather': get_weather, 
    'get_weather_conditions': get_weather_conditions,
    'search_gutenberg_books': search_gutenberg_books
}

# Automatically generate tools list
tools = create_tools_from_functions(available_tools)
from pprint import pprint
pprint(tools)