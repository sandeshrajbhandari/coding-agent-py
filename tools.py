import subprocess
import os
import glob
import re
from pathlib import Path

def read_file( path: str) -> str:
        """
        Read the contents of a given file path. Use this when you want to see what's inside a file.

        Args:
            path (str): The path of the file to read

        Returns:
            str: The contents of the file
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: File '{path}' not found"
        except Exception as e:
            return f"Error reading file '{path}': {str(e)}"

def read_many_files(file_paths: list) -> str:
    """
    Read the contents of multiple files at once. Useful for batch reading operations or when you need to examine several files together.

    Args:
        file_paths (list): List of file paths to read

    Returns:
        str: Contents of all files with clear separators and file headers
    """
    if not file_paths:
        return "Error: No file paths provided"
    
    if not isinstance(file_paths, list):
        return "Error: file_paths must be a list of file paths"
    
    results = []
    successful_reads = 0
    failed_reads = 0
    
    for i, file_path in enumerate(file_paths):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                results.append(f"=== FILE {i+1}: {file_path} ===\n{content}")
                successful_reads += 1
        except FileNotFoundError:
            results.append(f"=== FILE {i+1}: {file_path} ===\nError: File not found")
            failed_reads += 1
        except Exception as e:
            results.append(f"=== FILE {i+1}: {file_path} ===\nError: {str(e)}")
            failed_reads += 1
    
    # Add summary at the end
    summary = f"\n\n=== SUMMARY ===\nSuccessfully read: {successful_reads} files\nFailed to read: {failed_reads} files"
    results.append(summary)
    
    return "\n\n".join(results)
    
def list_files( path: str = ".") -> str:
        """
        List files and directories at a given path. If no path is provided, lists files in the current directory.

        Args:
            path (str): Optional path to list files from. Defaults to current directory if not provided.

        Returns:
            str: A newline-separated list of files and directories
        """
        try:
            files = []
            for item in Path(path).iterdir():
                if item.is_dir():
                    files.append(f"{item.name}/")
                else:
                    files.append(item.name)
            return "\n".join(sorted(files))
        except Exception as e:
            return f"Error listing files in '{path}': {str(e)}"
    
def edit_file( path: str, old_str: str, new_str: str) -> str:
        """
        Make edits to a text file. Replaces 'old_str' with 'new_str' in the given file. If the file doesn't exist, it will be created. use ./file_name or absolute path when necessary

        Args:
            path (str): The path to the file
            old_str (str): Text to search for - must match exactly
            new_str (str): Text to replace old_str with

        Returns:
            str: Success message or error description
        """
        try:
            # If old_str is empty, create a new file
            if not old_str:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_str)
                return f"Successfully created file '{path}'"
            
            # Read existing file
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except FileNotFoundError:
                return f"Error: File '{path}' not found"
            
            # Replace old_str with new_str
            if old_str not in content:
                return f"Error: Text '{old_str}' not found in file '{path}'"
            
            new_content = content.replace(old_str, new_str, 1)  # Replace only first occurrence
            
            # Write back to file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return "OK"
        except Exception as e:
            return f"Error editing file '{path}': {str(e)}"
    
def run_command( command: str, working_dir: str = ".") -> str:
        """
        Execute a terminal command and return the output. Use this to run scripts, compile code, or execute any command.

        Args:
            command (str): The command to execute
            working_dir (str): Optional working directory for the command. Defaults to current directory.

        Returns:
            str: The command output including exit code, stdout, and stderr
        """
        if working_dir == "":
            working_dir = "."
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = f"Exit code: {result.returncode}\n"
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            
            return output
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"

def todo_write_tool( todo_list: str, file_path: str = './TODO.md') -> str:
    """
    Write a todo list as a markdown to a file './TODO.md'
<example>
User: Help me rename the function getCwd to getCurrentWorkingDirectory across my project
Assistant: Let me first search through your codebase to find all occurrences of 'getCwd'.
*Uses grep or search tools to locate all instances of getCwd in the codebase*
Assistant: I've found 15 instances of 'getCwd' across 8 different files. Let me create a todo list to track these changes.
*Creates todo list with specific items for each file that needs updating*

<reasoning>
The assistant used the todo list because:
1. First, the assistant searched to understand the scope of the task
2. Upon finding multiple occurrences across different files, it determined this was a complex task with multiple steps
3. The todo list helps ensure every instance is tracked and updated systematically
4. This approach prevents missing any occurrences and maintains code consistency
</reasoning>
</example>

Skip using this tool when:
1. There is only a single, straightforward task
2. The task is trivial and tracking it provides no organizational benefit
3. The task can be completed in less than 3 trivial steps
4. The task is purely conversational or informational
    """
    with open(file_path, 'w') as f:
            f.write(todo_list + '\n')
    return f"Successfully wrote todo list to {file_path}"

def grep_tool(pattern: str, path: str = ".", case_sensitive: bool = True, file_pattern: str = "*") -> str:
    """
    Search for a pattern in files using regex. This is useful for finding specific text, function names, or code patterns across multiple files.

    Args:
        pattern (str): The regex pattern to search for
        path (str): Directory path to search in. Defaults to current directory
        case_sensitive (bool): Whether the search should be case sensitive. Defaults to True
        file_pattern (str): File pattern to match (e.g., "*.py", "*.js"). Defaults to "*" (all files)

    Returns:
        str: Search results showing file paths and matching lines with line numbers
    """
    try:
        results = []
        search_path = Path(path)
        
        if not search_path.exists():
            return f"Error: Path '{path}' does not exist"
        
        # Find files matching the pattern
        if search_path.is_file():
            files_to_search = [search_path]
        else:
            files_to_search = []
            for file_path in search_path.rglob(file_pattern):
                if file_path.is_file():
                    files_to_search.append(file_path)
        
        if not files_to_search:
            return f"No files found matching pattern '{file_pattern}' in '{path}'"
        
        # Compile regex pattern
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            return f"Error: Invalid regex pattern '{pattern}': {str(e)}"
        
        # Search in each file
        for file_path in files_to_search:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if regex.search(line):
                            relative_path = file_path.relative_to(search_path.parent if search_path.is_file() else search_path)
                            results.append(f"{relative_path}:{line_num}: {line.rstrip()}")
            except Exception as e:
                results.append(f"Error reading {file_path}: {str(e)}")
        
        if not results:
            return f"No matches found for pattern '{pattern}' in {len(files_to_search)} files"
        
        return f"Found {len(results)} matches:\n" + "\n".join(results)
    
    except Exception as e:
        return f"Error during grep search: {str(e)}"

def glob_tool(pattern: str, path: str = ".") -> str:
    """
    Find files and directories matching a glob pattern. Useful for finding files with specific extensions, names, or patterns.

    Args:
        pattern (str): Glob pattern to match (e.g., "*.py", "**/*.txt", "test_*")
        path (str): Base directory to search in. Defaults to current directory

    Returns:
        str: Newline-separated list of matching files and directories
    """
    try:
        search_path = Path(path)
        
        if not search_path.exists():
            return f"Error: Path '{path}' does not exist"
        
        # Use glob to find matches
        if search_path.is_file():
            # If path is a file, check if it matches the pattern
            if search_path.match(pattern):
                return str(search_path)
            else:
                return f"No files match pattern '{pattern}'"
        
        # Search in directory
        matches = []
        for match in search_path.rglob(pattern):
            try:
                # Get relative path from the search directory
                relative_path = match.relative_to(search_path)
                if match.is_dir():
                    matches.append(f"{relative_path}/")
                else:
                    matches.append(str(relative_path))
            except ValueError:
                # Handle cases where relative_to fails
                matches.append(str(match))
        
        if not matches:
            return f"No files or directories match pattern '{pattern}' in '{path}'"
        
        return "\n".join(sorted(matches))
    
    except Exception as e:
        return f"Error during glob search: {str(e)}"


def write_file( path: str, content: str) -> str:
    """
    Write content to a file.
    """
    with open(path, 'w') as f:
        f.write(content)
    return f"Successfully wrote to {path}"