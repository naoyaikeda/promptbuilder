import glob
import os
import streamlit as st
import polars as pl
from dotenv import load_dotenv
import frontmatter
import jinja2 as j2
from jinja2 import Environment

def load_characters(vault_path: str, characters_dir:str):
    characters_path = os.path.join(vault_path, characters_dir)

    characters = []
    for filepath in glob.glob(os.path.join(characters_path, "**/*.md"), recursive=True):
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            character_name = os.path.basename(filepath).replace('.md', '')
            character = {}
            character['name'] = character_name
            character['series'] = post.metadata.get('Series', 'Unknown')
            character['tags'] = post.metadata.get('tags', [])
            character['prompts'] = post.metadata.get('prompts', {})
            characters.append(character)
    
    df_characters = pl.DataFrame(characters, schema_overrides={"prompts": pl.Object})

    return df_characters

def load_templates():
    templates = {}

    templates_dir = os.path.join(os.getenv("TEMPLATES_DIR", "templates"), "character")

    for filepath in glob.glob(os.path.join(templates_dir, "*.txt")):
        with open(filepath, 'r', encoding='utf-8') as f:
            template_name = os.path.basename(filepath).replace('.txt', '')
            template_content = f.read()
            
            templates[template_name] = template_content

    return templates

def main():
    env = Environment()
    load_dotenv()

    templates = load_templates()

    vaulth_path = os.getenv("VAULT_PATH")
    characters_dir = os.getenv("CHARACTERS_DIR", "Characters")

    characters = load_characters(vaulth_path, characters_dir)

    serieses = characters['series'].unique().sort().to_list()

    st.set_page_config(page_title="Prompt Builder", layout="wide")
    st.title("Prompt Builder")
    selected_series = st.sidebar.selectbox("Select Series", options=serieses)
    filtered_characters = characters.filter(pl.col('series') == selected_series)['name'].sort().to_list()
    selected_character = st.sidebar.selectbox("Select Character", options=filtered_characters)
    prompts = characters.filter(pl.col('name') == selected_character)['prompts'][0]
    selected_prompt_key = st.sidebar.selectbox("Select Prompt", options=list(prompts.keys()))
    selected_template_name = st.sidebar.selectbox("Select Template", options=list(templates.keys()))

    temlpate = env.from_string(templates[selected_template_name])
    prompt = prompts[selected_prompt_key]
    data = {
        "lora": prompt.get("lora", ""),
        "positive": prompt.get("positive", ""),
    }
    rendered_prompt = temlpate.render(data)
    st.subheader("Generated Prompt")
    st.text_area("Prompt", value=rendered_prompt, height=400)

if __name__ == "__main__":
    main()
