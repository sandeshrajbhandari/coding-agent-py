import random
import json
# from rich import print
import typing
from litellm.types.llms.cohere import ToolCallObject
from ollama import Client
from ollama._types import ChatResponse
import ollama
from tools import read_file, list_files, edit_file, run_command, todo_write_tool, grep_tool, glob_tool, read_many_files, write_file
from system_prompt import system_prompt, system_prompt_claude, system_prompt_3
from system_prompt2 import system_prompt_claude2, sanitize_conversation
available_tools = {'read_file': read_file, 'list_files': list_files, 'edit_file': edit_file, 'run_command': run_command, 'todo_write_tool': todo_write_tool, 'grep_tool': grep_tool, 'glob_tool': glob_tool, 'read_many_files': read_many_files, 'write_file': write_file}
# first_input = input('User: ')
# initial_message = first_input if first_input else 'show me all the files in the current directory'
messages = [{
          "role": "system",
          # "content": system_prompt_3 + "/no_think"
          "content": system_prompt_claude2 + "/no_think"
        },
        # {
        #   'role': 'user', 'content': initial_message }
]

client = Client(
  # Ollama Turbo
  # host="https://ollama-host.loca.lt/", 
  host="http://localhost:11434",
  # headers={'Authorization': (os.getenv('OLLAMA_API_KEY'))}
)
# model = 'gpt-oss:20b'
# model = 'pielee/qwen3-4b-thinking-2507_q8:latest'
model = 'qwen3:8b'
# gpt-oss can call tools while "thinking"
# a loop is needed to call the tools and get the results
while True:
  user_input = input('User: ')
  messages.append({'role': 'user', 'content': user_input})
  if user_input == 'exit' or user_input == 'quit' or user_input == 'q':
    #store the messages to a file
    with open('messages.json', 'w', encoding='utf-8') as f:
      sanitized_messages = sanitize_conversation(messages)
      json.dump(sanitized_messages, f, indent=2, ensure_ascii=False)
    break
  while True:
    # Use streaming for real-time response
    stream = client.chat(model=model, messages=messages, 
      # options={
      #   "min_p": 0.001,
      #   "top_p": 0.9,
      #   "temperature": 0.4,
      #   "repeat_penalty": 1.2,
      #   "presence_penalty": 1.5,
      # },
      tools=[read_file, list_files, edit_file, run_command, todo_write_tool, grep_tool, glob_tool, read_many_files, write_file]
    , stream=True
    )
    
    # print (stream)
    # Collect the full response for message history
    full_content = ""
    full_thinking = ""
    tool_calls = []
    
    print('Content: ', end='', flush=True)
    # print (type(stream))  
    if isinstance(stream, typing.Generator):
      for chunk in stream:
        if chunk.message.content:
          print(chunk.message.content, end='', flush=True)
          full_content += chunk.message.content
        if chunk.message.thinking:
          full_thinking += chunk.message.thinking
        if chunk.message.tool_calls:
          print(f'{chunk.message.tool_calls}')
          tool_calls.extend(chunk.message.tool_calls)
    else:
      full_content = stream.message.content
      full_thinking = stream.message.thinking
      tool_calls = stream.message.tool_calls
      
    
    print('\n')  # New line after content
    
    if full_thinking:
      print('Thinking: ')
      print(full_thinking + '\n')
    
    # Create the complete message for history
    if tool_calls:
      for tool_call in tool_calls:
        # save to a file
        with open('tool_calls.txt', 'a') as f:
          f.write(str(tool_call) + '\n')
    complete_message = {
      'role': 'assistant',
      'content': full_content,
      'thinking': full_thinking if full_thinking else None,
      'tool_calls': tool_calls if tool_calls else None
    }
    # print ("Complete Message:", complete_message) 
    messages.append(complete_message)

    if tool_calls:
      print (f'Tool calls: {tool_calls}')
      for tool_call in tool_calls:
        function_to_call = available_tools.get(tool_call.function.name)
        if function_to_call:
          try: 
            # print(f'Calling {tool_call.function.name} with arguments: {tool_call.function.arguments}')
            result = function_to_call(**tool_call.function.arguments)
          except Exception as e:
            print(f'Error calling {tool_call.function.name}: {str(e)}')
            messages.append({'role': 'tool', 'content': f'Error calling {tool_call.function.name}: {str(e)}', 'tool_name': tool_call.function.name})
            continue

          tool_call_result = ('Result from tool call name: ' + tool_call.function.name + 'with arguments: ' + str(tool_call.function.arguments) + 'result: ' + str(result) + '\n')
          print(str(result))
          messages.append({'role': 'tool', 'content': tool_call_result, 'tool_name': tool_call.function.name})
        else:
          print(f'Tool {tool_call.function.name} not found')
          messages.append({'role': 'tool', 'content': f'Tool {tool_call.function.name} not found', 'tool_name': tool_call.function.name})
    else:
      # print (messages[-3])
      # print (messages[-2])
      # print (messages[-1])
      
      # no more tool calls, we can stop the loop
      break
      # Get user input and add to messages
      # user_input = input(">")
      # messages.append({'role': 'user', 'content': user_input})

      # create a tui python program with ascii art