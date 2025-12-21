import pathlib
import glob
import os
import uuid
import streamlit as st
import polars as pl
from dotenv import load_dotenv
import frontmatter
import jinja2 as j2
from jinja2 import Environment

def compose_prompt(vault_path: str, sources:dict, output:str) -> str:
    print(vault_path)

    character = sources.get('character', {})
    clothes = sources.get('clothes', [])
    modifiers = sources.get('modifiers', [])
    stages = sources.get('stages', [])
    styles = sources.get('styles', []) 

    scene = ""

    scene += "# Character\n"
    character_path = pathlib.Path(character.get('path', '')).relative_to(vault_path).as_posix()
    scene += f"- [{character.get('name', '')}](<{character_path}>)\n"
    scene += "\n# Clothing\n"
    for cloth in clothes:
        cloth_absolute_path = cloth.get('path', '')
        if cloth_absolute_path:
            cloth_path = pathlib.Path(cloth_absolute_path).relative_to(vault_path).as_posix()
            scene += f"- [{cloth.get('name', '')}](<{cloth_path}>)\n"

    scene += "\n# Modifiers\n"    
    for modifier in modifiers:
        modifier_absolute_path = modifier.get('path', '')
        if modifier_absolute_path:
            modifier_path = pathlib.Path(modifier_absolute_path).relative_to(vault_path).as_posix()
            scene += f"- [{modifier.get('name', '')}](<{modifier_path}>)\n"

    scene += "\n# Stage\n"
    for stage in stages:
        stage_absolute_path = stage.get('path', '')
        if stage_absolute_path:
            stage_path = pathlib.Path(stage_absolute_path).relative_to(vault_path).as_posix()
            scene += f"- [{stage.get('name', '')}](<{stage_path}>)\n"

    scene += "\n# Style\n"
    for style in styles:
        style_absolute_path = style.get('path', '')
        if style_absolute_path:
            style_path = pathlib.Path(style_absolute_path).relative_to(vault_path).as_posix()
            scene += f"- [{style.get('name', '')}](<{style_path}>)\n"
    
    scene += "\n# Generated Prompt\n"
    scene += output + "\n"
    
    post = frontmatter.Post(scene)
    post.metadata = {
        "title": f"Scene - {character.get('name', '')}",
        "Character": character.get('name', ''),
        "Clothing": [cloth.get('name', '') for cloth in clothes],
        "Modifiers": [modifier.get('name', '') for modifier in modifiers],
        "Stage": [stage.get('name', '') for stage in stages],
        "Style": [style.get('name', '') for style in styles],
    }

    return frontmatter.dumps(post)
   


def load_characters(vault_path: str, characters_dir:str):
    characters_path = os.path.join(vault_path, characters_dir)

    characters = []
    for filepath in glob.glob(os.path.join(characters_path, "**/*.md"), recursive=True):
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            character_name = os.path.basename(filepath).replace('.md', '')
            character = {}
            character['path'] = filepath
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
            cloth['path'] = filepath
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
            modifier['path'] = filepath
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

def load_stages(vault_path: str, stage_dir:str):
    stages_path = os.path.join(vault_path, stage_dir)

    stages = [{'name': 'empty', 'tags': [], 'base_model': 'common', 'positive': '', 'lora': ''}]
    for filepath in glob.glob(os.path.join(stages_path, "*.md"), recursive=True):
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            stage_name = os.path.basename(filepath).replace('.md', '')
            stage = {}
            stage['path'] = filepath
            stage['name'] = stage_name
            stage['tags'] = post.metadata.get('tags', [])
            base_model = post.metadata.get('Model', 'unknown')

            try:
                stage['base_model'] = base_model.lower()
            except Exception:
                stage['base_model'] = 'unknown'            

            stage['positive'] = post.metadata.get('Base', '')
            stage['lora'] = post.metadata.get('LoRA', '')
            stages.append(stage)
    
    df_stages = pl.DataFrame(stages)

    return df_stages

def load_styles(vault_path: str, style_dir:str):
    style_path = os.path.join(vault_path, style_dir)

    styles = [{'name': 'empty', 'tags': [], 'base_model': 'common', 'positive': '', 'lora': ''}]
    for filepath in glob.glob(os.path.join(style_path, "*.md"), recursive=True):
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
            style_name = os.path.basename(filepath).replace('.md', '')
            style = {}
            style['path'] = filepath
            style['name'] = style_name
            style['tags'] = post.metadata.get('tags', [])
            base_model = post.metadata.get('Model', 'unknown')

            try:
                style['base_model'] = base_model.lower()
            except Exception:
                style['base_model'] = 'unknown'            

            style['positive'] = post.metadata.get('Base', '')
            style['lora'] = post.metadata.get('LoRA', '')
            styles.append(style)
    
    df_styles = pl.DataFrame(styles)

    return df_styles

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
    exports_dir = os.getenv("EXPORTS_DIR", "Scenes")

    characters = load_characters(vault_path, characters_dir)
    clothes = load_clothes(vault_path, os.getenv("CLOTHES_DIR", "Clothing"))
    modifiers = load_modifiers(vault_path, os.getenv("MODIFIERS_DIR", "Modification"))
    stages = load_stages(vault_path, os.getenv("STAGE_DIR", "Stage"))
    styles = load_styles(vault_path, os.getenv("STYLE_DIR", "Styles"))

    serieses = characters['series'].unique().sort().to_list()

    st.set_page_config(page_title="Character Prompt Builder", layout="wide")
    selected_series = st.sidebar.selectbox("Select Series", options=serieses)
    filtered_characters = characters.filter(pl.col('series') == selected_series)['name'].sort().to_list()
    selected_character = st.sidebar.selectbox("Select Character", options=filtered_characters)

    sources = {}
    sources['character'] = characters.filter(pl.col('name') == selected_character).to_dicts()[0]
    subtype = characters.filter(pl.col('name') == selected_character)['subtype'][0]
    prompts = characters.filter(pl.col('name') == selected_character)['prompts'][0]
    selected_prompt_key = st.sidebar.selectbox("Select Prompt", options=list(prompts.keys()))

    prompt = prompts[selected_prompt_key]
    base_model = prompt.get("base_model", "unknown")

    fitted_modifiers = modifiers.filter(pl.col('base_model').is_in([base_model.lower(),'common']))
    selected_template_name = st.sidebar.selectbox("Select Template", options=list(templates.keys()))

    temlpate = env.from_string(templates[selected_template_name])

    fitted_clothes = clothes.filter(pl.col('base_model').is_in([base_model.lower(),'common']))
    fitted_stages = stages.filter(pl.col('base_model').is_in([base_model.lower(),'common']))
    fitted_styles = styles.filter(pl.col('base_model').is_in([base_model.lower(),'common']))

    if "clothes_count" not in st.session_state:
        st.session_state.clothes_count = 1
    
    if "stages_count" not in st.session_state:
        st.session_state.stages_count = 1

    if "modifiers_count" not in st.session_state:
        st.session_state.modifiers_count = 1

    if "styles_count" not in st.session_state:
        st.session_state.styles_count = 1

    col1, col2 = st.columns(2)
    with col1:
        if st.button("追加", key="btn_add_clothes"):
            st.session_state.clothes_count += 1
    with col2:
        if st.button("削除", key="btn_del_clothes") and st.session_state.clothes_count > 1:
            st.session_state.clothes_count -= 1

    selected_clothes_values = []
    for i in range(st.session_state.clothes_count):
        val = st.selectbox(
            f"衣装項目 {i+1}",
            options=fitted_clothes['name'].to_list(),
            key=f"sb_clothes_{i}" # 重要: keyをユニークにする
        )
        selected_clothes_values.append(val)
    
    clothing = []
    sources['clothes'] = []
    for selected_cloth in selected_clothes_values:
        selected_cloth_data = fitted_clothes.filter(pl.col('name') == selected_cloth).to_dicts()[0]
        sources['clothes'].append(selected_cloth_data)
        clothing.append({
            "lora": selected_cloth_data.get("lora", ""),
            "positive": selected_cloth_data.get("positive", ""),
        })

    mcol1, mcol2 = st.columns(2)
    with mcol1:
        if st.button("追加", key="btn_add_modifiers"):
            st.session_state.modifiers_count += 1
    with mcol2:
        if st.button("削除", key="btn_del_modifiers") and st.session_state.modifiers_count > 1:
            st.session_state.modifiers_count -= 1

    sources['modifiers'] = []
    selected_modifiers_values = []
    for i in range(st.session_state.modifiers_count):
        val = st.selectbox(
            f"モディファイア項目 {i+1}",
            options=fitted_modifiers['name'].to_list(),
            key=f"sb_modifiers_{i}" # keyをより具体的に
        )
        selected_modifiers_values.append(val)
    
    mods = []
    for selected_modifier in selected_modifiers_values:
        selected_modifier_data = fitted_modifiers.filter(pl.col('name') == selected_modifier).to_dicts()[0]
        sources['modifiers'].append(selected_modifier_data)
        mods.append({
            "lora": selected_modifier_data.get("lora", ""),
            "positive": selected_modifier_data.get("positive", ""),
        })

    scol1, scol2 = st.columns(2)
    with scol1:
        if st.button("追加", key="btn_add_stages"):
            st.session_state.stages_count += 1
    with scol2:
        if st.button("削除", key="btn_del_stages") and st.session_state.stages_count > 1:
            st.session_state.stages_count -= 1

    selected_stages_values = []
    for i in range(st.session_state.stages_count):
        val = st.selectbox(
            f"ステージ項目 {i+1}",
            options=fitted_stages['name'].to_list(),
            key=f"sb_stages_{i}" # keyをより具体的に
        )
        selected_stages_values.append(val)
    
    sources['stages'] = []
    stg = []
    for selected_stage in selected_stages_values:
        selected_stage_data = fitted_stages.filter(pl.col('name') == selected_stage).to_dicts()[0]
        sources['stages'].append(selected_stage_data)
        stg.append({
            "lora": selected_stage_data.get("lora", ""),
            "positive": selected_stage_data.get("positive", ""),
        })

    ycol1, ycol2 = st.columns(2)
    with ycol1:
        if st.button("追加", key="btn_add_styles"):
            st.session_state.styles_count += 1
    with ycol2:
        if st.button("削除", key="btn_del_styles") and st.session_state.styles_count > 1:
            st.session_state.styles_count -= 1

    selected_styles_values = []
    for i in range(st.session_state.styles_count):
        val = st.selectbox(
            f"スタイル項目 {i+1}",
            options=fitted_styles['name'].to_list(),
            key=f"sb_styles_{i}" # keyをより具体的に
        )
        selected_styles_values.append(val)
    
    sources['styles'] = []
    sty = []
    for selected_style in selected_styles_values:
        selected_style_data = fitted_styles.filter(pl.col('name') == selected_style).to_dicts()[0]
        sources['styles'].append(selected_style_data)
        sty.append({
            "lora": selected_style_data.get("lora", ""),
            "positive": selected_style_data.get("positive", ""),
        })

    data = {
        "styles": sty,
        "stages": stg,
        "subtype": subtype,
        "mods": mods,
        "lora": prompt.get("lora", ""),
        "positive": prompt.get("positive", ""),
        "clothes": clothing,
    }

    print(sources)
    rendered_prompt = temlpate.render(data)
    clean_output = "".join(rendered_prompt.splitlines()).strip()

    st.subheader("Generated Prompt")
    st.text_area("Prompt", value=clean_output, height=400)

    composed_matter = compose_prompt(vault_path, sources, clean_output)

    export_path = os.path.join(vault_path, exports_dir)
    notename = f"Scene - {selected_character} - {str(uuid.uuid4())[:8]}.md"
    full_export_path = os.path.join(export_path, notename)

    st.button("Export Prompt", on_click=lambda: open(full_export_path, 'w', encoding='utf-8').write(composed_matter))

if __name__ == "__main__":
    main()
