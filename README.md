# AutoGPT-CPPVulkan: A Fork and Remake of AutoGPT 1.3, the Autonomous LLM Experiment

# DEVELOPMENT:
- Check and update code relating to the .ENV.
- SKim over other scripts, checking compatibility with updates, and possibility of streamlining.
- Installer works, however, Launcer requires, run and debug. 

## DESCRIPTION:
Auto-GPT is an experimental open-source application showcasing the capabilities of the GPT-4 language model. This program, driven by GPT-4, chains together LLM "thoughts", to autonomously achieve whatever goal you set. As one of the first examples of GPT-4 running fully autonomously, Auto-GPT pushes the boundaries of what is possible with AI. This forf "AutoGPT=CPPVulkan", is a remake of an early version of Auto-GPT, that has been streamlined to basic windows non-wsl operation, and will be designed to run of local models, such as "qwencode 1.5". Auto-GPT is currently at v5.1, so dont expect that level of operation, however, we will be finding better alternates to things such as huggingface and google websearch.

### PREVIEW:
- The Env gives a better idea of where its going...
```
################################################################################
### AUTO-GPT - GENERAL SETTINGS
################################################################################
# EXECUTE_LOCAL_COMMANDS - Allow local command execution (Example: False)
EXECUTE_LOCAL_COMMANDS=Allow
# BROWSE_CHUNK_MAX_LENGTH - When browsing website, define the length of chunk stored in memory
BROWSE_CHUNK_MAX_LENGTH=8192
# BROWSE_SUMMARY_MAX_TOKEN - Define the maximum length of the summary generated by GPT agent when browsing website
BROWSE_SUMMARY_MAX_TOKEN=300
# USER_AGENT - Define the user-agent used by the requests library to browse website (string)
# USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
# AI_SETTINGS_FILE - Specifies which AI Settings file to use (defaults to ai_settings.yaml)
AI_SETTINGS_FILE=ai_settings.yaml
################################################################################
### LLM MODELS
################################################################################
# SMART_LLM_MODEL - Smart language model (Default: gpt-4)
SMART_LLM_MODEL=.\models\L3-8B-Stheno-v3.2-IQ3_M-imat.gguf
### LLM MODEL SETTINGS
# SMART_TOKEN_LIMIT - Smart token limit for OpenAI (Default: 8000)
# TEMPERATURE - Sets temperature in OpenAI (Default: 1)
SMART_TOKEN_LIMIT=8000
TEMPERATURE=1
################################################################################
### MEMORY
################################################################################
# MEMORY_BACKEND - Memory backend type (Default: local)
MEMORY_BACKEND=local
################################################################################
### IMAGE GENERATION PROVIDER
################################################################################
### HUGGINGFACE
# HUGGINGFACE_API_TOKEN - HuggingFace API token (Example: my-huggingface-api-token)
HUGGINGFACE_API_TOKEN=your-huggingface-api-token
################################################################################
### SEARCH PROVIDER
################################################################################
### GOOGLE
# GOOGLE_API_KEY - Google API key (Example: my-google-api-key)
# CUSTOM_SEARCH_ENGINE_ID - Custom search engine ID (Example: my-custom-search-engine-id)
GOOGLE_API_KEY=your-google-api-key
CUSTOM_SEARCH_ENGINE_ID=your-custom-search-engine-id
```

### REQUIREMENTS:
- HuggingFace - For now, AutoGPT-CCPVulkan uses Stable Diffusion, get a [HuggingFace API Token](https://huggingface.co/settings/tokens) , then see ENV section.

### INSTALL AND USAGE:
1. Run the `.\Installer.Bat`, ensure firewall is off temprarely, or allow through.
2. Ensure to insert a `*.GGUF` model into ".\models` folder, only one.
2. Configure the `.\.ENV` file, its now cut down, and should be simple enough.
3. Run the `.\Launcher.Bat`, and use as you would normally, within the limitations.

# DISCLAIMER
This fork AutoGPT-CPPVulkan, is a experimental application, and is provided "as-is" without any warranty, express or implied. By using this software, you agree to assume all risks associated with its use, including but not limited to data loss, system failure, or any other issues that may arise. But be safe in knowing, you will not incur any more GPT fees. Continuous mode is not recommendedm It is potentially dangerous and may cause your AI to run forever or carry out actions you would not usually authorise.
