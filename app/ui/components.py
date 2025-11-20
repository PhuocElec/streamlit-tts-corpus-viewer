# app/ui/components.py
import math
import os
from pathlib import Path

import streamlit as st

from settings import settings
from core.data import (
    load_corpus_metadata,
    clear_metadata_cache,
    get_valid_filenames,
)
from core.audio import get_audio_bytes_local, get_audio_url
from core.auth import require_admin_login


# ================== VIEW MODE ==================


def render_view_mode() -> None:
    st.subheader("🔍 View mode")

    try:
        df = load_corpus_metadata()
    except Exception as e:
        st.error(f"Cannot load metadata: {e}")
        st.info("Admin can upload metadata CSV in the Edit tab.")
        return

    total_items = len(df)
    if total_items == 0:
        st.info("Metadata CSV is empty.")
        return

    if "page" not in st.session_state:
        st.session_state["page"] = 1

    with st.container():
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            page_size = st.selectbox(
                "Items per page",
                options=[10, 20, 50, 100],
                index=1,
            )

        page = st.session_state["page"]
        total_pages = max((total_items - 1) // page_size + 1, 1)

        if page > total_pages:
            page = total_pages
        if page < 1:
            page = 1
        st.session_state["page"] = page

        with col2:
            st.markdown(f"**Page:** {page} / {total_pages}")

        with col3:
            c_prev, c_next = st.columns(2)
            with c_prev:
                top_prev = st.button(
                    "◀ Previous", disabled=page <= 1, key="top_prev"
                )
            with c_next:
                top_next = st.button(
                    "Next ▶", disabled=page >= total_pages, key="top_next"
                )

    if top_prev:
        page = max(1, page - 1)
        st.session_state["page"] = page
    if top_next:
        page = min(total_pages, page + 1)
        st.session_state["page"] = page

    page = st.session_state["page"]

    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_items)
    df_page = df.iloc[start_idx:end_idx].copy()

    st.markdown(
        f"Showing items **{start_idx + 1}–{end_idx}** "
        f"(page {page}/{total_pages})"
    )
    st.markdown("---")

    header_cols = st.columns([3, 4, 2])
    with header_cols[0]:
        st.markdown("**File**")
    with header_cols[1]:
        st.markdown("**Text**")
    with header_cols[2]:
        st.markdown("**Audio**")

    st.markdown("---")

    for _, row in df_page.iterrows():
        item_id = row.get("id", "")
        text = row["text"]
        filename = str(row["file"]).strip()

        row_cols = st.columns([3, 4, 2])

        with row_cols[0]:
            file_label = filename
            if item_id != "":
                file_label = f"#{item_id} — {filename}"
            st.markdown(
                f"""
                <div style="
                    white-space: pre-wrap;
                    word-break: break-all;
                ">
                    {file_label}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with row_cols[1]:
            st.markdown(
                f"""
                <div style="
                    white-space: pre-wrap;
                    line-height: 1.4em;
                ">
                    {text}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with row_cols[2]:
            if settings.AUDIO_MODE.lower() == "local":
                audio_bytes = get_audio_bytes_local(filename)
                if audio_bytes is None:
                    st.error("Not found")
                else:
                    st.audio(audio_bytes, format="audio/mp3")
            else:
                if not settings.AUDIO_BASE_URL:
                    st.error("No AUDIO_BASE_URL")
                else:
                    st.audio(get_audio_url(filename))

    st.markdown("---")

    with st.container():
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            st.markdown(f"**Page:** {page} / {total_pages}")

        with col2:
            st.markdown(
                f"Items **{start_idx + 1}–{end_idx}** / {total_items}"
            )

        with col3:
            c_prev, c_next = st.columns(2)
            with c_prev:
                bottom_prev = st.button(
                    "◀ Previous", disabled=page <= 1, key="bottom_prev"
                )
            with c_next:
                bottom_next = st.button(
                    "Next ▶", disabled=page >= total_pages, key="bottom_next"
                )

    if bottom_prev:
        page = max(1, page - 1)
        st.session_state["page"] = page
    if bottom_next:
        page = min(total_pages, page + 1)
        st.session_state["page"] = page


# ================== EDIT / ADMIN MODE ==================


def render_edit_mode() -> None:
    st.subheader("✏️ Edit mode (Admin only)")

    if not settings.ADMIN_USERNAME or not settings.ADMIN_PASSWORD:
        st.warning(
            "ADMIN_USERNAME / ADMIN_PASSWORD are not configured in environment/.env."
        )
        return

    # Login
    if not require_admin_login():
        return

    st.success(f"Logged in as: {settings.ADMIN_USERNAME}")

    col_logout, _ = st.columns([1, 3])
    with col_logout:
        if st.button("Logout"):
            st.session_state["is_admin"] = False
            st.experimental_rerun()

    st.markdown("---")

    st.markdown("### 📄 Upload metadata CSV")

    csv_file = st.file_uploader(
        "Choose metadata CSV",
        type=["csv"],
        key="metadata_uploader",
    )

    if csv_file is not None:
        if st.button("Save metadata CSV"):
            dest_path: Path = settings.CORPUS_CSV_PATH
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            with open(dest_path, "wb") as f:
                f.write(csv_file.getbuffer())

            clear_metadata_cache()
            st.success(f"Saved metadata to: `{dest_path}`")

    st.markdown("---")

    st.markdown("### 🎧 Upload audio files (mp3)")

    st.caption(
        "Only files whose names exist in the `file` column of the current metadata CSV will be saved."
    )

    audio_files = st.file_uploader(
        "Choose mp3 files",
        type=["mp3"],
        accept_multiple_files=True,
        key="audio_uploader",
    )

    if audio_files:
        st.info(f"{len(audio_files)} file(s) selected.")

        if st.button("Save audio files"):
            try:
                valid_filenames = get_valid_filenames()
            except Exception as e:
                st.error(f"Cannot load metadata CSV: {e}")
                return

            base_dir: Path = settings.AUDIO_BASE_DIR
            base_dir.mkdir(parents=True, exist_ok=True)

            saved = 0
            skipped_not_in_csv = []

            for uploaded in audio_files:
                filename = os.path.basename(uploaded.name).strip()

                if filename not in valid_filenames:
                    skipped_not_in_csv.append(filename)
                    continue

                dest_path = base_dir / filename
                with open(dest_path, "wb") as f:
                    f.write(uploaded.getbuffer())
                saved += 1

            st.success(f"Saved **{saved}** audio file(s) to: `{base_dir}`")

            if skipped_not_in_csv:
                st.warning(
                    "Skipped (not found in `file` column of CSV):\n\n"
                    + ", ".join(skipped_not_in_csv)
                )

    st.markdown("---")
    st.caption(
        f"**Current CORPUS_CSV_PATH:** `{settings.CORPUS_CSV_PATH}`  \n"
        f"**Current AUDIO_BASE_DIR:** `{settings.AUDIO_BASE_DIR}`  \n"
        f"**AUDIO_MODE:** `{settings.AUDIO_MODE}`"
    )
