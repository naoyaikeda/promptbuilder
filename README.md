# Prompt Builder

A Streamlit application for building and managing character prompts for AI image generation. This tool allows you to combine characters, clothing, modifiers, stages, and styles stored as Markdown files to generate complex prompts using Jinja2 templates.

## Features

- **Character Management**: Load character definitions from Markdown files.
- **Asset Assembly**: Combine characters with various assets:
  - Clothing
  - Modifiers
  - Stages
  - Styles
- **Template-based Generation**: Use Jinja2 templates to format the final prompt.
- **Export to Vault**: Save generated scenes back to your Markdown vault with metadata.

## Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) (recommended for dependency management)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd promptbuilder
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

## Configuration

Create a `.env` file in the root directory to configure your vault paths. You can use the following variables:

```env
# Required: The root path of your Obsidian vault or markdown storage
VAULT_PATH=/path/to/your/vault

# Optional: Relative paths within the vault (defaults shown)
CHARACTERS_DIR=Characters
CLOTHES_DIR=Clothing
MODIFIERS_DIR=Modification
STAGE_DIR=Stage
STYLE_DIR=Styles
EXPORTS_DIR=Scenes
TEMPLATES_DIR=templates
```

## Usage

To start the application, run:

```bash
uv run streamlit run main.py
```

Or on Windows, you can use the provided batch file:

```batch
run.bat
```

Open your browser to the URL shown in the terminal (usually `http://localhost:8501`).

## Data Structure

The application expects Markdown files with frontmatter metadata in your vault directories.

### Character Example
```markdown
---
tags: [character]
Series: "Original"
Subtype: "Human"
prompts:
  default:
    base_model: "pony"
    lora: "<lora:character_lora:1>"
    positive: "1girl, solo"
---
```

### Asset Example (Clothing/Stage/etc.)
```markdown
---
tags: [clothing]
Model: "pony"
Base: "white dress, frills"
LoRA: "<lora:dress_lora:1>"
---
```

## License

See `license.txt` for details.
