import streamlit as st

st.set_page_config(
    page_title="Veridian AI",
    layout="wide",
)

st.title("Veridian AI")
st.subheader("Evaluation-Driven Enterprise Query Engine")

st.markdown(
    """
    Veridian AI is designed to answer enterprise analytics questions using
    semantic mapping, retrieval, SQL execution, planning, verification, and evaluation.
    """
)

query = st.text_input(
    "Ask a business question:",
    "Why did enterprise revenue decline in APAC despite higher marketing spend?",
)

if st.button("Run Query"):
    st.info(
        "Pipeline not implemented yet. Current stage focuses on architecture, failure taxonomy, and benchmark design."
    )

st.divider()

st.header("Planned Execution Trace")

st.code(
    """
1. Intent Understanding
2. Semantic Mapping
3. Query Planning
4. Retrieval
5. SQL Execution
6. Analysis
7. Synthesis
8. Verification
9. Final Answer
"""
)

st.header("Planned Evaluation Metrics")

st.write(
    [
        "Retrieval Recall@K",
        "Mean Reciprocal Rank",
        "SQL correctness",
        "Metric mapping accuracy",
        "Faithfulness",
        "Citation precision",
        "Hallucination rate",
        "Latency",
        "Cost",
    ]
)
