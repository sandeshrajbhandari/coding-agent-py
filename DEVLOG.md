## ollama setup 

- follow the default ollama setup instructions for your windows go to their docs first
- you can open the ollama gui or use ollama serve to run the backend ollama server
- custom models location - you can set custom model locations in ollama from the gui or using env variables
    - `export OLLAMA_MODELS= \path\to\models`
    - check with `echo $OLLAMA_MODELS` to see if `ollama serve` is using the right model location.
- im using qwen3:8b model so use that.
- `ollama pull qwen3:8b`

### changing default context length of the model
- if the model card doesn't have num_ctx mentioned, ollama uses 4k, 4096 token context length which is very low for coding agents.
- so we increase that to 8192. 16k is ideal, but since we're running this in our own laptop, its gonna be slower. (not 100% sure, but pretty sure)
- get the modelfile, edit the model file and the create the same model again from that.
    - `ollama show --modelfile qwen3:8b > qwen3-Modelfile`
    - edit the Model file to add this line `PARAMETER num_ctx 8192`
    - `ollama create qwen3:8b -f 'qwen3-Modelfile'`
- now we have this model but with 8k context length.

### install ollama python
- `pip install ollama`

## Agent Code in Python
- heavily inspired by https://ampcode.com/how-to-build-an-agent and https://news.ycombinator.com/item?id=45001051
- see agent.py for basic tool use
- see agent2.py for actual implementation
- uses Client with configurable hosts, i was also using colab with local tunnel to expose an endpoint to run bigger models like gpt-oss:20b.
    - gpt-oss:20b is much better than qwen3:8b.
    - colab notebook link - https://colab.research.google.com/drive/1WIXa_VaujgNET_AJPl8PqhRyrf8vDCZL?usp=sharing
- at first I was using only one while True loop to get user input and call the api if there were tool_calls in the assitant response.
    - if there were no tool_call, the agent turn is finished
- Later I just added a another loop outside with user input to turn it into multi-turn conversation.

## tools.py
- i'm mostly using tools referenced from the article, and some from qwen-code tools list.
    - https://github.com/QwenLM/qwen-code/tree/main/packages/core/src/tools
- official list is: read_file, list_files, edit_file, run_command, todo_write_tool, grep_tool, glob_tool, read_many_files, write_file
- i should have tried to match the tool names from the qwen-code list but they are very minimally implemented so i didn't bother.
- another caveat is that these tools assume current dir ('.') as the base point, and I've not mentioned using absolute paths in my system prompts unlike most agents like claude code, qwen code, gemini cli and openai codex cli.

## System prompts
- latest system prompt is system_prompt_claude2 which is in system_prompt2.py.
- Main prompt references were from qwen-code
    - https://github.com/QwenLM/qwen-code/blob/main/packages/core/src/core/prompts.ts
- also found this opencode/crush cli prompt later which i've not tried to integrate into this system
    - Crush cli - https://github.com/charmbracelet/crush/blob/main/internal/llm/prompt/v2.md

- Learnings - 
    - i tried writing some of my own system prompts and didn't make sense.
    - I then fed qwencode system prompt to claude a bit and asked it to generate some examples.
        - https://claude.ai/share/1dfc2f26-c5b0-4576-9158-4e23742347ee
        - system_prompt_claude I called it. it worked upto a point. it was using following format in examples.
            -   <tool_call>
                <function={TodoWriteTool['Name']}>
                <parameter=todo_list>
                - [ ] Understand the requirements and the existing codebase using {CommandTool['Name']} tool.
                - [ ] If code exists, use the {ReadFileTool['Name']} tool to read the codebase and use {EditFileTool['Name']} to edit the files.
                - [ ] If no code exists, create a new file called main.py using {WriteFileTool['Name']} tool.
                - [ ] Use the {EditFileTool['Name']} tool to edit the main.py file.
                - [ ] Use the {CommandTool['Name']} tool to run the main.py file.
                - [ ] Test the app using the {CommandTool['Name']} tool.
                - Test the app using the {CommandTool['Name']} tool.
                </parameter>
                </function>
                </tool_call>
    - qwen code examples for tool call looked like this:
        -   <example>
            user: Where are all the 'app.config' files in this project? I need to check their settings.
            model:
            <tool_call>
            <function=glob>
            <parameter=pattern>
            ./**/app.config
            </parameter>
            </function>
            </tool_call>
            (Assuming GlobTool returns a list of paths like ['/path/to/moduleA/app.config', '/path/to/moduleB/app.config'])
            I found the following 'app.config' files:
            - /path/to/moduleA/app.config
            - /path/to/moduleB/app.config
            To help you check their settings, I can read their contents. Which one would you like to start with, or should I read all of them?
            </example>

    - i later used <tool_call> tags in system_prompt_claude, like in qwen code examples, but this was wrong. as a result when I did this tool calls weren't being parsed by ollama correctly. and the tool calls weren't happening
    - qwen-code and qwen agent lib has their own tool parser so the <tool_call> with <function=glob>..... style XML tags worked. but by adding them to my system prompt, it was interfering with the expected ollama tool format(https://ollama.com/library/qwen3:8b/blobs/ae370d884f10): 
        -   <tool_call>
            {"name": <function-name>, "arguments": <args-json-object>}
            </tool_call>
        - you can find this in the template part of the ollama model card.
    - I later removed most of the examples and the current version - 3rd commit is working properly.

    - I think if I want to add examples I have to either use another format for pseudocode tool-calls, or use the exact response the parser expects, which is the one I showed before.

## Current State and caveats
- the agent can't run background processes like running servers and installing packages or boilerplate code like npm create vite@latest to scaffold projects.(there's a 30s timeout, and just using npm create vite@latest expects multiple user inputs.)
- the agent needs confirmations from the users frequently. (like "ok", 'do step 3 in the todo list'), cursor and other agents are more independent.
- it needs a proper diff editing workflow to replace code or add new code.
    - trying it for a react app didn't work cause it was hallucinating small syntax corrections in old_str code to replace in App.jsx
- 


## Resources
- https://github.com/ollama/ollama-python
- https://github.com/awslabs/mcp/blob/main/VIBE_CODING_TIPS_TRICKS.md?utm_source=hackernewsletter&utm_medium=email&utm_term=code
- https://github.com/ollama/ollama/blob/main/docs/api.md#generate-request-with-options

- https://github.com/QwenLM/qwen-code/blob/main/packages/core/src/core/prompts.ts
- https://github.com/QwenLM/qwen-code/tree/main/packages/core/src/tools
- https://github.com/charmbracelet/crush/blob/main/internal/llm/prompt/v2.md