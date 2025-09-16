
client = Client(
  # Ollama Turbo
  # host="https://ollama-host.loca.lt/", 
  host="http://localhost:11434",
  # headers={'Authorization': (os.getenv('OLLAMA_API_KEY'))}
)

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

## functioncalling
available_tools = {'read_file': read_file, 'list_files': list_files, 'edit_file': edit_file, 'run_command': run_command, 'todo_write_tool': todo_write_tool, 'grep_tool': grep_tool, 'glob_tool': glob_tool, 'read_many_files': read_many_files, 'write_file': write_file}
function_to_call = available_tools.get(tool_call.function.name)
## we get a tool_calls list with different tool_call objects.
result = function_to_call(**tool_call.function.arguments)