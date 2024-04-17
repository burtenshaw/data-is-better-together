import json
import streamlit as st

from hub import push_dataset_to_hub
from infer import query
from defaults import (
    DEFAULT_DOMAIN,
    DEFAULT_PERSPECTIVES,
    DEFAULT_TOPICS,
    DEFAULT_EXAMPLES,
    DEFAULT_SYSTEM_PROMPT,
    N_PERSPECTIVES,
    N_TOPICS,
    N_EXAMPLES,
    SEED_DATA_PATH,
    PIPELINE_PATH,
)
from pipeline import serialize_pipeline, run_pipeline

################################################################################
# Introduction and Project Setup
################################################################################

introduction = """# 🧑‍🌾 Domain Data Grower
## 🌱 Create a dataset seed for aligning models to a specific domain

This app helps you create a dataset seed for building diverse domain-specific datasets for aligning models.
Alignment datasets are used to fine-tune models to a specific domain or task, but as yet, there's a shortage of diverse datasets for this purpose.
"""
st.markdown(introduction)

(
    tab_details,
    tab_domain_expert,
    tab_domain_perspectives,
    tab_domain_topics,
    tab_examples,
) = st.tabs(
    [
        "📋 Project Details",
        "👩🏼‍🔬 Domain Expert",
        "🔍 Domain Perspectives",
        "🕸️ Domain Topics",
        "📚 Examples",
    ]
)

with tab_details:
    st.text(
        "Define the project details, including the project name, domain, and API credentials"
    )
    project_name = st.text_input("Project Name", DEFAULT_DOMAIN)
    domain = st.text_input("Domain", DEFAULT_DOMAIN)
    hub_username = st.text_input("Hub Username", "argilla")
    hub_token = st.text_input("Hub Token", type="password")
    argilla_url = st.text_input("Argilla API URL", "https://argilla-farming.hf.space")
    argilla_api_key = st.text_input("Argilla API Key", "owner.apikey")


################################################################################
# Domain Expert Section
################################################################################

with tab_domain_expert:
    st.text("Define the domain expertise that you want to train a language model")
    st.info(
        "A domain expert is a person who is an expert in a particular field or area. For example, a domain expert in farming would be someone who has extensive knowledge and experience in farming and agriculture."
    )

    domain_expert_prompt = st.text_area(
        label="Domain Expert Definition",
        value=DEFAULT_SYSTEM_PROMPT,
        height=200,
    )

################################################################################
# Domain Perspectives
################################################################################

with tab_domain_perspectives:
    st.text("Define the different perspectives from which the domain can be viewed")
    st.info(
        """
    Perspectives are different viewpoints or angles from which a domain can be viewed. 
    For example, the domain of farming can be viewed from the perspective of a commercial 
    farmer or an independent family farmer."""
    )

    perspectives = st.session_state.get(
        "perspectives",
        [st.text_input(f"Domain Perspective 0", value=DEFAULT_PERSPECTIVES[0])],
    )
    new_perspective = st.button("Add New Perspective")

    if new_perspective:
        n = len(perspectives)
        value = DEFAULT_PERSPECTIVES[n] if n < N_PERSPECTIVES else ""
        perspectives.append(st.text_input(f"Domain Perspective {n}", value=""))
        st.session_state["perspectives"] = perspectives


################################################################################
# Domain Topics
################################################################################

with tab_domain_topics:
    st.text("Define the main themes or subjects that are relevant to the domain")
    st.info(
        """Topics are the main themes or subjects that are relevant to the domain. For example, the domain of farming can have topics like soil health, crop rotation, or livestock management."""
    )
    topics = st.session_state.get(
        "topics", [st.text_input(f"Domain Topic 0", value=DEFAULT_TOPICS[0])]
    )
    new_topic = st.button("Add New Topic")

    if new_topic:
        n = len(topics)
        value = DEFAULT_TOPICS[n] if n < N_TOPICS else ""
        topics.append(st.text_input(f"Domain Topic {n}", value=value))
        st.session_state["topics"] = topics


################################################################################
# Examples Section
################################################################################
with tab_examples:
    st.text(
        "Add high-quality questions and answers that can be used to generate synthetic data"
    )
    st.info(
        """
    Examples are high-quality questions and answers that can be used to generate 
    synthetic data for the domain. These examples will be used to train the language model
    to generate questions and answers.
    """
    )

    questions_answers = st.session_state.get(
        "questions_answers",
        [
            (
                st.text_area(
                    "Question", key="question_0", value=DEFAULT_EXAMPLES[0]["question"]
                ),
                st.text_area(
                    "Answer", key="answer_0", value=DEFAULT_EXAMPLES[0]["answer"]
                ),
            )
        ],
    )

    new_question = st.button("Add New Example")

    if new_question:
        n = len(questions_answers)
        default_question, default_answer = DEFAULT_EXAMPLES[n].values()
        st.subheader(f"Example {n + 1}")
        if st.button("Generate New Answer", key=f"generate_{n}"):
            default_answer = query(default_question)
        _question = st.text_area(
            "Question", key=f"question_{n}", value=default_question
        )
        _answer = st.text_area("Answer", key=f"answer_{n}", value=default_answer)
        questions_answers.append((_question, _answer))
        st.session_state["questions_answers"] = questions_answers

################################################################################
# Create Dataset Seed
################################################################################

st.divider()
st.header(":seedling: Generate Synthetic Dataset")

st.text(
    "Now that you have defined the domain expertise, perspectives, topics, and examples, you can create a dataset seed."
)

st.subheader("Step 1. Create Dataset Seed from domain data")
st.text(
    "Create a dataset seed and push it to the Hub to grow a domain-specific dataset."
)

if st.button("🤗 Create Dataset Seed"):
    perspectives = list(filter(None, perspectives))
    topics = list(filter(None, topics))
    examples = [{"question": q, "answer": a} for q, a in questions_answers]

    domain_data = {
        "domain": domain,
        "perspectives": perspectives,
        "topics": topics,
        "examples": examples,
        "domain_expert_prompt": domain_expert_prompt,
    }

    with open(SEED_DATA_PATH, "w") as f:
        json.dump(domain_data, f, indent=2)

    ############################################################
    # Setup Dataset on the Hub
    ############################################################

    push_dataset_to_hub(
        domain_seed_data_path=SEED_DATA_PATH,
        project_name=project_name,
        domain=domain,
        hub_username=hub_username,
        hub_token=hub_token,
        pipeline_path=PIPELINE_PATH,
    )

    st.success(
        f"Dataset seed created and pushed to the Hub. Check it out [here](https://huggingface.co/{hub_username}/{project_name})"
    )

    st.session_state["created_dataset"] = True


###############################################################
# Run Pipeline
###############################################################

st.subheader("Step 2. Run the pipeline to generate synthetic data")

st.text("To run the pipeline from here define an inference endpoint URL.")
base_url = st.text_input("Base URL")
st.text("You can run the pipeline locally or on the Hub.")
run_pipeline_locally = st.button("💻 Run pipeline locally")
run_pipeline_on_space = st.button("🔥 Run pipeline right here, right now!")

st.session_state["run_pipeline_locally"] = run_pipeline_locally
st.session_state["run_pipeline_on_space"] = run_pipeline_on_space
st.session_state["base_url"] = base_url

if (run_pipeline_on_space or run_pipeline_locally) and not st.session_state.get(
    "created_dataset"
):
    st.error("You need to create the dataset seed before running the pipeline.")
    st.rerun()
elif (run_pipeline_on_space or run_pipeline_locally) and st.session_state.get(
    "base_url"
):
    serialize_pipeline(
        argilla_api_key=argilla_api_key,
        argilla_dataset_name=project_name or DEFAULT_DOMAIN,
        argilla_api_url=argilla_url,
        topics=topics,
        perspectives=perspectives,
        pipeline_config_path=PIPELINE_PATH,
        domain_expert_prompt=domain_expert_prompt or DEFAULT_SYSTEM_PROMPT,
        hub_token=hub_token,
        endpoint_base_url=base_url,
    )
    st.success(f"Pipeline configuration saved to {PIPELINE_PATH}")
elif (run_pipeline_on_space or run_pipeline_locally) and not st.session_state.get(
    "base_url"
):
    st.error("You need to define an inference endpoint URL.")
    st.rerun()

if st.session_state.get("run_pipeline_locally") and st.session_state.get("base_url"):
    st.info(
        "To run the pipeline locally, you need to have the `distilabel` library installed. You can install it using the following command:"
    )
    st.text(
        "Execute the following command to generate a synthetic dataset from the seed data:"
    )
    st.code(
        f"""
        pip install git+https://github.com/argilla-io/distilabel.git
        git clone https://huggingface.co/{hub_username}/{project_name}
        cd {project_name}
        distilabel pipeline run --config pipeline.yaml
    """
    )

elif st.session_state.get("run_pipeline_on_space") and st.session_state.get("base_url"):
    logs = run_pipeline(PIPELINE_PATH)

    st.success(f"Running the pipeline.")

    with st.expander("View Logs"):
        for out in logs:
            st.text(out)

# st.subheader("Step 3. Explore the generated dataset and improve it")
