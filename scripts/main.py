import json, random, time, traceback, yaml, argparse, logging
from memory import get_memory
from spinner import Spinner
from config import Config
from models import create_chat_completion, fix_json
from ai_config import AIConfig
from utils import logger, say_text, clean_input
from prompt import get_prompt, generate_context, chat_with_ai
import commands as cmd
from llm_utils import initialize_model

cfg = Config()

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process args.')
    parser.add_argument('-c', '--continuous', action='store_true', help='Enable Continuous Mode')
    parser.add_argument('-l', '--continuous-limit', type=int, help='Set continuous run limit')
    parser.add_argument('--speak', action='store_true', help='Enable Speak Mode')
    parser.add_argument('--debug', action='store_true', help='Enable Debug Mode')
    parser.add_argument('-y', '--skip-reprompt', action='store_true', help='Skip reprompt messages')
    parser.add_argument('-C', '--ai-settings', help="Specify ai_settings.yaml")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    if args.continuous:
        cfg.set_continuous_mode(True)
        cfg.set_continuous_limit(args.continuous_limit)
    if args.speak:
        cfg.set_speak_mode(True)
    if args.ai_settings:
        cfg.ai_settings_file = args.ai_settings
        cfg.skip_reprompt = True

def main():
    parse_arguments()
    logger.set_level(logging.DEBUG if cfg.debug_mode else logging.INFO)
    
    initialize_model()
    
    prompt = construct_prompt()
    full_message_history, next_action_count = [], 0
    user_input = "Determine next command:"

    memory = get_memory(cfg, init=True)
    print(f'Using memory: {memory.__class__.__name__}')

    agent = Agent("", memory, full_message_history, next_action_count, prompt, user_input)
    agent.start_interaction_loop()

class Agent:
    def __init__(self, ai_name, memory, full_message_history, next_action_count, prompt, user_input):
        self.ai_name = ai_name
        self.memory = memory
        self.full_message_history = full_message_history
        self.next_action_count = next_action_count
        self.prompt = prompt
        self.user_input = user_input

    def start_interaction_loop(self):
        loop_count = 0
        while True:
            loop_count += 1
            if cfg.continuous_mode and cfg.continuous_limit > 0 and loop_count > cfg.continuous_limit:
                logger.typewriter_log("Limit Reached: ", "", f"{cfg.continuous_limit}")
                break

            with Spinner("Thinking..."):
                assistant_reply = create_chat_completion(
                    messages=[{"role": "user", "content": self.prompt + "\n" + self.user_input}],
                    max_tokens=cfg.max_tokens
                )

            print_assistant_thoughts(assistant_reply)

            try:
                command_name, arguments = cmd.get_command(fix_and_parse_json(assistant_reply))
                if cfg.speak_mode:
                    say_text(f"Executing {command_name}")
            except Exception as e:
                logger.error("Command error: ", str(e))

            if not cfg.continuous_mode and self.next_action_count == 0:
                self.user_input = handle_user_input(command_name, arguments)
                if self.user_input == "EXIT":
                    print("Exiting...", flush=True)
                    break
            else:
                log_command(command_name, arguments)

            if command_name.lower() != "human_feedback":
                result = f"Command {command_name} returned: {cmd.execute_command(command_name, arguments)}"
                if self.next_action_count > 0:
                    self.next_action_count -= 1
            else:
                result = f"Human feedback: {self.user_input}"

            self.memory.add(f"Assistant Reply: {assistant_reply}\nResult: {result}\nFeedback: {self.user_input}")
            if result:
                self.full_message_history.append(result)

def handle_user_input(command_name, arguments):
    print(f"Authorize command: {command_name} {arguments}? (y/n)", flush=True)
    while True:
        console_input = clean_input("Input: ").lower().strip()
        if console_input == "y":
            return "GENERATE NEXT COMMAND JSON"
        elif console_input.startswith("y -"):
            try:
                self.next_action_count = abs(int(console_input.split(" ")[1]))
                return "GENERATE NEXT COMMAND JSON"
            except ValueError:
                print("Invalid input. Use 'y -n' for continuous.")
        elif console_input == "n":
            return "EXIT"
        else:
            return console_input

def log_command(command_name, arguments):
    logger.typewriter_log("NEXT ACTION: ", "", f"COMMAND = {command_name} ARGUMENTS = {arguments}")

def print_assistant_thoughts(assistant_reply):
    logger.typewriter_log("Assistant Thoughts: ", "", assistant_reply)
