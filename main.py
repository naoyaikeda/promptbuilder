import streamlit as st

pages = {
    "Builder": [
        st.Page("character-builder.py", title="Character Prompt Builder", icon="🧙‍♂️"),
    ]
}

def main():
    pg = st.navigation(pages)
    pg.run()

if __name__ == "__main__":
    main()
