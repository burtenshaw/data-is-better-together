import streamlit as st

from defaults import (
    ARGILLA_SPACE_REPO_ID,
    PROJECT_NAME,
    ARGILLA_URL,
    DIBT_PARENT_APP_URL,
    DATASET_URL,
    DATASET_REPO_ID,
    ARGILLA_SPACE_REPO_ID,
)


def project_sidebar():
    if PROJECT_NAME == "DEFAULT_DOMAIN":
        st.warning(
            "Please set up the project configuration in the parent app before proceeding."
        )
        st.stop()

    st.sidebar.markdown(
        """
        ## 🌱 Domain Data Grower
        
        This space helps you create a dataset seed for building diverse domain-specific datasets for aligning models.
        """
    )
    st.sidebar.subheader(f"Project Details: {PROJECT_NAME}")
    st.sidebar.link_button(f"📚 Dataset Repo", DATASET_URL)
    st.sidebar.link_button(f"🤖 Argilla Space", ARGILLA_URL)
    st.sidebar.divider()
    st.sidebar.link_button("🧑‍🌾 New Project", DIBT_PARENT_APP_URL)
