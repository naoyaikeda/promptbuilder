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
            character['subtype'] = post.metadata.get('Subtype', '')
            character['tags'] = post.metadata.get('tags', [])
            character['prompts'] = post.metadata.get('prompts', {})
            characters.append(character)
    
    df_characters = pl.DataFrame(characters, schema_overrides={"prompts": pl.Object})

    return df_characters

def load_clothes(vault_path: str, clothes_dir:str):
    clothes_path = os.path.join(vault_path, clothes_dir)

    clothes = [{'name': 'empty', 'tags': [], 'base_model': 'common', 'positive': '', 'lora': ''}]
    for filepath in glob.glob(os.path.join(clothes_path, "*.md"), recursive=True):
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            cloth_name = os.path.basename(filepath).replace('.md', '')
            cloth = {}
            cloth['name'] = cloth_name
            cloth['tags'] = post.metadata.get('tags', [])
            base_model = post.metadata.get('Model', 'unknown')

            try:
                cloth['base_model'] = base_model.lower()
            except Exception:
                cloth['base_model'] = 'unknown'            

            cloth['positive'] = post.metadata.get('Base', '')
            cloth['lora'] = post.metadata.get('LoRA', '')
            clothes.append(cloth)
    
    df_clothes = pl.DataFrame(clothes)

    return df_clothes

def load_modifiers(vault_path: str, modifiers_dir:str):
    modifiers_path = os.path.join(vault_path, modifiers_dir)

    modifiers = [{'name': 'empty', 'tags': [], 'base_model': 'common', 'positive': '', 'lora': ''}]
    for filepath in glob.glob(os.path.join(modifiers_path, "*.md"), recursive=True):
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            modifier_name = os.path.basename(filepath).replace('.md', '')
            modifier = {}
            modifier['name'] = modifier_name
            modifier['tags'] = post.metadata.get('tags', [])
            base_model = post.metadata.get('Model', 'unknown')

            try:
                modifier['base_model'] = base_model.lower()
            except Exception:
                modifier['base_model'] = 'unknown'            

            modifier['positive'] = post.metadata.get('Base', '')
            modifier['lora'] = post.metadata.get('LoRA', '')
            modifiers.append(modifier)
    
    df_modifiers = pl.DataFrame(modifiers)

    return df_modifiers

def load_templates():
    templates = {}

    templates_dir = os.path.join(os.getenv("TEMPLATES_DIR", "templates"), "advanced-character")

    for filepath in glob.glob(os.path.join(templates_dir, "*.txt")):
        with open(filepath, 'r', encoding='utf-8') as f:
            template_name = os.path.basename(filepath).replace('.txt', '')
            template_content = f.read()
            
            templates[template_name] = template_content

    return templates

def main():
    env = Environment(
        trim_blocks=True,           # タグの後の最初の改行を削除
        lstrip_blocks=True,         # タグの前のタブやスペースを削除
        keep_trailing_newline=False # ファイル末尾の改行を維持するかどうか
    )
    load_dotenv()

    templates = load_templates()

    vault_path = os.getenv("VAULT_PATH")
    characters_dir = os.getenv("CHARACTERS_DIR", "Characters")

    characters = load_characters(vault_path, characters_dir)
    clothes = load_clothes(vault_path, os.getenv("CLOTHES_DIR", "Clothing"))
    modifiers = load_modifiers(vault_path, os.getenv("MODIFIERS_DIR", "Modification"))

    serieses = characters['series'].unique().sort().to_list()

    st.title("Character Prompt Builder")

    st.set_page_config(page_title="Prompt Builder", layout="wide")
    st.title("Prompt Builder")
    selected_series = st.sidebar.selectbox("Select Series", options=serieses)
    filtered_characters = characters.filter(pl.col('series') == selected_series)['name'].sort().to_list()
    selected_character = st.sidebar.selectbox("Select Character", options=filtered_characters)
    subtype = characters.filter(pl.col('name') == selected_character)['subtype'][0]
    prompts = characters.filter(pl.col('name') == selected_character)['prompts'][0]
    selected_prompt_key = st.sidebar.selectbox("Select Prompt", options=list(prompts.keys()))

    prompt = prompts[selected_prompt_key]
    base_model = prompt.get("base_model", "unknown")

    fitted_modifiers = modifiers.filter(pl.col('base_model').is_in([base_model.lower(),'common']))
    selected_modifier = st.sidebar.selectbox("Select Modifier", options=fitted_modifiers['name'].to_list())
    selected_template_name = st.sidebar.selectbox("Select Template", options=list(templates.keys()))

    temlpate = env.from_string(templates[selected_template_name])

    fitted_clothes = clothes.filter(pl.col('base_model').is_in([base_model.lower(),'common']))

    if "clothes_count" not in st.session_state:
        st.session_state.clothes_count = 1

    col1, col2 = st.columns(2)
    with col1:
        if st.button("追加"):
            st.session_state.clothes_count += 1
    with col2:
        if st.button("削除") and st.session_state.options_count > 1:
            st.session_state.clothes_count -= 1

    selected_clothes_values = []
    for i in range(st.session_state.clothes_count):
        val = st.selectbox(
            f"選択項目 {i+1}",
            options=fitted_clothes['name'].to_list(),
            key=f"selectbox_{i}" # 重要: keyをユニークにする
        )
        selected_clothes_values.append(val)
    
    clothing = []
    for selected_cloth in selected_clothes_values:
        selected_cloth_data = fitted_clothes.filter(pl.col('name') == selected_cloth).to_dicts()[0]
        clothing.append({
            "lora": selected_cloth_data.get("lora", ""),
            "positive": selected_cloth_data.get("positive", ""),
        })
    
    modifier = fitted_modifiers.filter(pl.col('name') == selected_modifier).to_dicts()[0]
    data = {
        "subtype": subtype,
        "modifier": modifier,
        "lora": prompt.get("lora", ""),
        "positive": prompt.get("positive", ""),
        "clothes": clothing,
    }

    rendered_prompt = temlpate.render(data)
    clean_output = "".join(rendered_prompt.splitlines()).strip()

    st.subheader("Generated Prompt")
    st.text_area("Prompt", value=clean_output, height=400)

if __name__ == "__main__":
    main()
