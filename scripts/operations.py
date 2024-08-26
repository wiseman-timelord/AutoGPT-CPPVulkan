import json, datetime, os, subprocess
from config import Config
from utilities import LocalCache
import management as agents
from management import configure_logging, is_valid_url, sanitize_url, check_local_file_access, get_response, scrape_text, extract_hyperlinks, format_hyperlinks, scrape_links, scrape_links, create_message, summarize_text, evaluate_code, improve_code, write_tests, generate_image, ingest_directory, main, __name__
from operations import *
from json_parser import fix_and_parse_json
from playwright.sync_api import sync_playwright

WORKSPACE_FOLDER = ".\\workspace"
cfg = Config()

# Ensure workspace exists
os.makedirs(WORKSPACE_FOLDER, exist_ok=True)

def is_valid_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def get_command(response):
    try:
        res_json = fix_and_parse_json(response)
        cmd = res_json.get("command", {})
        return cmd.get("name", "Error: Missing 'name'"), cmd.get("args", {})
    except (json.JSONDecodeError, Exception) as e:
        return "Error:", str(e)

def execute_command(command_name, arguments):
    memory = LocalCache(cfg)
    try:
        if command_name == "web_search":
            return web_search(arguments["query"])
        if command_name == "browse_website":
            return browse_website(arguments["url"], arguments["question"])
        if command_name == "memory_add":
            return memory.add(arguments["string"])
        if command_name == "start_agent":
            return start_agent(arguments["name"], arguments["task"], arguments["prompt"])
        if command_name == "message_agent":
            return message_agent(arguments["key"], arguments["message"])
        if command_name == "list_agents":
            return list_agents()
        if command_name == "delete_agent":
            return delete_agent(arguments["key"])
        if command_name == "get_text_summary":
            return get_text_summary(arguments["url"], arguments["question"])
        if command_name == "get_hyperlinks":
            return get_hyperlinks(arguments["url"])
        if command_name == "read_file":
            return read_file(arguments["file"])
        if command_name == "write_to_file":
            return write_to_file(arguments["file"], arguments["text"])
        if command_name == "append_to_file":
            return append_to_file(arguments["file"], arguments["text"])
        if command_name == "delete_file":
            return delete_file(arguments["file"])
        if command_name == "search_files":
            return search_files(arguments["directory"])
        if command_name == "evaluate_code":
            return model.create_completion(arguments["code"], max_tokens=1500)
        if command_name == "improve_code":
            return model.create_completion(f"Improve the code:\n\n{arguments['code']}\n\nSuggestions:\n{arguments['suggestions']}", max_tokens=1500)
        if command_name == "write_tests":
            return model.create_completion(f"Write tests:\n\n{arguments['code']}\n\nFocus: {arguments.get('focus', 'all aspects')}", max_tokens=1500)
        if command_name == "execute_python_file":
            return execute_python_file(arguments["file"])
        if command_name == "execute_shell":
            return execute_shell(arguments["command_line"]) if cfg.execute_local_commands else "Not allowed to run local shell commands."
        if command_name == "generate_image":
            return generate_image(arguments["prompt"])
        if command_name == "do_nothing":
            return "No action performed."
        if command_name == "task_complete":
            shutdown()
        return f"Unknown command '{command_name}'."
    except Exception as e:
        return "Error: " + str(e)

def get_datetime():
    return "Current date/time: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def web_search(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=cfg.playwright_headless)
        page = browser.new_page()
        try:
            # Navigate to a search engine (e.g., DuckDuckGo)
            page.goto("https://duckduckgo.com/")
            
            # Type the query and submit
            page.fill('input[name="q"]', query)
            page.press('input[name="q"]', 'Enter')
            
            # Wait for results to load
            page.wait_for_selector('.result__body')
            
            # Extract search results
            results = page.evaluate("""
                () => Array.from(document.querySelectorAll('.result__body')).map(result => ({
                    title: result.querySelector('.result__title').innerText,
                    snippet: result.querySelector('.result__snippet').innerText,
                    url: result.querySelector('.result__url').href
                })).slice(0, 5)
            """)
            
            browser.close()
            return results
        except Exception as e:
            browser.close()
            return {"error": str(e)}

def browse_website(url, question):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=cfg.playwright_headless)
        page = browser.new_page()
        try:
            page.goto(url, timeout=cfg.playwright_timeout)
            page.wait_for_load_state("networkidle", timeout=cfg.playwright_timeout)
            
            # Extract the main content of the page
            content = page.evaluate("""
                () => {
                    const article = document.querySelector('article');
                    if (article) return article.innerText;
                    const main = document.querySelector('main');
                    if (main) return main.innerText;
                    return document.body.innerText;
                }
            """)
            
            # Extract links
            links = page.evaluate("""
                () => Array.from(document.links).map(link => ({
                    href: link.href,
                    text: link.textContent.trim()
                })).filter(link => link.text && link.href.startsWith('http'))
            """)
            
            browser.close()
            
            # Summarize content (you may want to use your existing summarization function)
            summary = summarize_text(content, question)
            
            return {
                "summary": summary,
                "links": links[:5]  # Return only top 5 links
            }
        except Exception as e:
            browser.close()
            return {"error": str(e)}

def get_text_summary(url, question):
    text = scrape_text(url)
    return "Result: " + summarize_text(url, text, question)

def get_hyperlinks(url):
    return scrape_links(url)

def commit_memory(string):
    mem.permanent_memory.append(string)
    return f"Memory committed: {string}"

def delete_memory(key):
    if 0 <= key < len(mem.permanent_memory):
        del mem.permanent_memory[key]
        return f"Memory {key} deleted."
    return "Invalid key."

def overwrite_memory(key, string):
    if is_valid_int(key) and 0 <= int(key) < len(mem.permanent_memory):
        mem.permanent_memory[int(key)] = string
        return f"Memory {key} overwritten with: {string}"
    elif isinstance(key, str):
        mem.permanent_memory[key] = string
        return f"Memory {key} overwritten with: {string}"
    return "Invalid key."

def shutdown():
    print("Shutting down...")
    quit()

def start_agent(name, task, prompt, model=cfg.fast_llm_model):
    key, ack = agents.create_agent(task, f"You are {name}. Acknowledged.", model)
    return f"Agent {name} created with key {key}. First response: {message_agent(key, prompt)}"

def message_agent(key, message):
    response = agents.message_agent(int(key) if is_valid_int(key) else key, message)
    return response

def list_agents():
    return agents.list_agents()

def delete_agent(key):
    return f"Agent {key} deleted." if agents.delete_agent(key) else f"Agent {key} does not exist."

def safe_join(base, *paths):
    """Safely join paths."""
    new_path = os.path.normpath(os.path.join(base, *paths))
    if os.path.commonprefix([base, new_path]) != base:
        raise ValueError("Path escape detected.")
    return new_path

def execute_shell(command_line):
    """Run shell command."""
    initial_dir = os.getcwd()
    os.chdir(WORKSPACE_FOLDER) if WORKSPACE_FOLDER not in initial_dir else None
    result = subprocess.run(command_line, capture_output=True, shell=True)
    os.chdir(initial_dir)
    return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

def execute_python_file(file):
    """Run a Python file."""
    if not file.endswith(".py"):
        return "Error: Only .py files."
    file_path = os.path.join(WORKSPACE_FOLDER, file)
    if not os.path.isfile(file_path):
        return f"Error: File '{file}' not found."
    try:
        result = subprocess.run(['python', file_path], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

def split_file(content, max_length=4000, overlap=0):
    """Split text into chunks."""
    for start in range(0, len(content), max_length - overlap):
        yield content[start:start + max_length]

def read_file(filename):
    """Read file contents."""
    try:
        with open(safe_join(WORKSPACE_FOLDER, filename), "r", encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"

def ingest_file(filename, memory, max_length=4000, overlap=200):
    """Ingest file into memory."""
    try:
        content = read_file(filename)
        for i, chunk in enumerate(split_file(content, max_length, overlap)):
            memory.add(f"File: {filename} | Part: {i + 1}\n{chunk}")
        return f"Ingested {filename}."
    except Exception as e:
        return f"Error ingesting '{filename}': {str(e)}"

def write_to_file(filename, text):
    """Write text to file."""
    try:
        filepath = safe_join(WORKSPACE_FOLDER, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding='utf-8') as f:
            f.write(text)
        return "File written."
    except Exception as e:
        return f"Error: {str(e)}"

def append_to_file(filename, text):
    """Append text to file."""
    try:
        with open(safe_join(WORKSPACE_FOLDER, filename), "a", encoding='utf-8') as f:
            f.write(text)
        return "Text appended."
    except Exception as e:
        return f"Error: {str(e)}"

def delete_file(filename):
    """Delete file."""
    try:
        os.remove(safe_join(WORKSPACE_FOLDER, filename))
        return "File deleted."
    except Exception as e:
        return f"Error: {str(e)}"

def search_files(directory):
    """Search files in directory."""
    found_files = []
    search_dir = safe_join(WORKSPACE_FOLDER, directory or "")
    for root, _, files in os.walk(search_dir):
        for file in files:
            if not file.startswith('.'):
                found_files.append(os.path.relpath(os.path.join(root, file), WORKSPACE_FOLDER))
    return found_files
