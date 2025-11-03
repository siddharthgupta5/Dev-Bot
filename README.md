# DevBot

An AI-powered development assistant that performs code reviews and generates unit tests with automatic GitHub integration.

## Features

- 🤖 **Code Review**: Analyze GitHub PRs and provide detailed feedback
- 🧪 **Unit Test Generation**: Auto-generate and deploy unit tests
- 🔄 **GitHub Integration**: Create branches, files, and PRs automatically
- 💬 **Chat Interface**: Simple web UI for interaction
- 🔌 **Flexible LLM**: Use Perplexity, OpenAI, or other LangChain-compatible models

## Quick Start

### 1. Install
```bash
git clone https://github.com/De2nim/dev-bot-final.git
cd dev-bot-final
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure
```bash
cp config.template.json config.json
# Edit config.json with your GitHub token and LLM API key
```

### 3. Run
```bash
python ui.py
```

## Setup

**GitHub Token**: Go to Settings → Developer settings → Personal access tokens

**LLM Options**:
- **Perplexity**: Sign up at [perplexity.ai](https://www.perplexity.ai/)
- **OpenAI**: Get API key from [platform.openai.com](https://platform.openai.com/)
- **Anthropic**: Get API key from [console.anthropic.com](https://console.anthropic.com/)
- **Other**: Any LangChain-compatible model

## Usage

- **Code Review**: "I want to review a pull request" + PR URL
- **Unit Tests**: "I want to generate unit tests"

## Security

⚠️ Never commit `config.json` - it contains your API keys!

---

Built with LangChain, LangGraph, and flexible LLM support