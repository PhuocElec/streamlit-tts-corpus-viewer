import streamlit as st
from ui.components import render_view_mode, render_edit_mode


def main() -> None:
    st.set_page_config(
        page_title="Streamlit TTS Corpus Viewer",
        layout="wide",
    )

    st.title("🗣️ Streamlit TTS Corpus Viewer")

    tab_view, tab_edit = st.tabs(["View", "Edit (Admin)"])
    with tab_view:
        render_view_mode()
    with tab_edit:
        render_edit_mode()


if __name__ == "__main__":
    main()
