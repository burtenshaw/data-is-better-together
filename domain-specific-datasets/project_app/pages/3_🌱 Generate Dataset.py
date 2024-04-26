import streamlit as st

from defaults import ARGILLA_URL
from utils import project_sidebar

st.set_page_config(
    page_title="Domain Data Grower",
    page_icon="🧑‍🌾",
)

project_sidebar()

################################################################################
# HEADER
################################################################################

st.header("🧑‍🌾 Domain Data Grower")
st.divider()
st.subheader("Step 3. Run the pipeline to generate synthetic data")
st.write("Define the distilabel pipeline for generating the dataset.")

###############################################################
# CONFIGURATION
###############################################################

hub_username = st.session_state.get("hub_username")
project_name = st.session_state.get("project_name")
hub_token = st.session_state.get("hub_token")

st.divider()

st.markdown("#### 🤖 Inference configuration")

st.write(
    "Add the url of the Huggingface inference API or endpoint that your pipeline should use. You can find compatible models here:"
)

with st.expander("🤗 Recommended Models"):
    st.write("All inference endpoint compatible models can be found via the link below")
    st.link_button(
        "🤗 Inference compaptible models on the hub",
        "https://huggingface.co/models?pipeline_tag=text-generation&other=endpoints_compatible&sort=trending",
    )
    st.write("🔋Projects with sufficient resources could take advantage of LLama3 70b")
    st.code("https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-70B")

    st.write("🪫Projects with less resources could take advantage of LLama 3 8b")
    st.code("https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B")

    st.write("🍃Projects with even less resources could take advantage of Phi-2")
    st.code("https://api-inference.huggingface.co/models/microsoft/phi-2")

    st.write("Note Hugggingface Pro gives access to more compute resources")
    st.link_button(
        "🤗 Huggingface Pro",
        "https://huggingface.co/pricing",
    )


base_url = st.text_input(
    label="Base URL for the Inference API",
    value="https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta",
)
st.divider()
st.markdown("#### 🔬 Argilla API details to push the generated dataset")
argilla_url = st.text_input("Argilla API URL", ARGILLA_URL)
argilla_api_key = st.text_input("Argilla API Key", "owner.apikey")
argilla_dataset_name = st.text_input("Argilla Dataset Name", project_name)
st.divider()

###############################################################
# LOCAL
###############################################################

st.markdown("## Run the pipeline")

st.markdown(
    "Once you've defined the pipeline configuration above, you can run the pipeline from your local machine."
)


if all(
    [
        argilla_api_key,
        argilla_url,
        base_url,
        hub_token,
        project_name,
        hub_token,
        argilla_dataset_name,
    ]
):
    st.markdown(
        "To run the pipeline locally, you need to have the `distilabel` library installed. You can install it using the following command:"
    )

    st.code(
        f"""
        
        # Install the distilabel library
        pip install git+https://github.com/argilla-io/distilabel.git
        """
    )

    st.markdown("Next, you'll need to clone your dataset repo and run the pipeline:")

    st.code(
        f"""
        # Clone the project and install the requirements
        git clone https://huggingface.co/datasets/{hub_username}/{project_name}
        cd {project_name}
        pip install -r requirements.txt
        
        # Run the pipeline
        python pipeline.py 
            --argilla-api-key {argilla_api_key} 
            --argilla-api-url {argilla_url} 
            --argilla-dataset-name {argilla_dataset_name} 
            --endpoint-base-url {base_url}
            --hub-token {st.session_state["hub_token"]}
        """,
        language="bash",
    )
    st.markdown(
        "👩‍🚀 If you want to customise the pipeline take a look in `pipeline.py` and teh [distilabel docs](https://distilabel.argilla.io/)"
    )

else:
    st.info("Please fill all the required fields.")
