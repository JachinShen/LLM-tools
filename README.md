# Personal Tools Collection

This repository contains a collection of personal tools powered by Large Language Models (LLMs).

## Prerequisites

Before using the tools, you need to set up the environment and provide the necessary API keys.

### API Keys

Place your API keys in the `secrets/` directory:

- `glm_api_key.txt`: Your GLM API key.
- `langsmith_api_key.txt`: Your LangSmith API key.

See `devenv.nix` for more details on how these keys are used.

### Environment Setup

The environment is powered by NixOS's devenv. To set up the environment and enter the shell, run:

```bash
devenv shell
```

### Manual Installation (Without Nix)
Setup python3.12 virtual environment. To install the required dependencies, run the following command:

```
pip install -r requirements.txt
```

### Usage
To use the tool, navigate to the directory and run the script (for example):

```
cd accounting
python accounting.py
```