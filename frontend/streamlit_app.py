import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Veridian AI",
    layout="wide",
)

st.title("Veridian AI")
st.subheader("Evaluation-Driven Enterprise Query Engine")

query = st.text_input(
    "Ask a business question:",
    "Why did enterprise revenue decline in APAC despite higher marketing spend?",
)

if st.button("Run Query"):
    st.info(
        "Pipeline not implemented yet. Current stage focuses on architecture, failure taxonomy, and benchmark design."
    )

if run:
    with st.spinner("Processing query..."):
        try:
            resp = requests.post(
                f"{API_URL}/api/query",
                json={"query": query, "include_trace": show_trace},
                timeout=30,
            )
            if resp.status_code != 200:
                st.error(f"API error: {resp.status_code} — {resp.text}")
            else:
                data = resp.json()

                status = data.get("status", "unknown")
                if status == "rejected":
                    st.error(f"Query rejected: {data.get('message', '')}")
                elif status == "needs_clarification":
                    st.warning(f"Clarification needed: {data.get('message', '')}")
                else:
                    st.success("Query processed successfully")

                if data.get("intent"):
                    with st.expander("Intent Classification", expanded=True):
                        intent = data["intent"]
                        st.metric("Query Type", intent.get("query_type", "?"))
                        st.metric(
                            "Confidence", f"{intent.get('confidence', 0):.2f}"
                        )
                        if intent.get("metrics"):
                            st.write("**Metrics:**", ", ".join(intent["metrics"]))
                        if intent.get("filters"):
                            st.write("**Filters:**", intent["filters"])
                        if intent.get("rationale"):
                            st.caption(f"Rationale: {intent['rationale']}")

                if data.get("semantic_mapping"):
                    with st.expander("Semantic Mapping", expanded=True):
                        sm = data["semantic_mapping"]
                        st.write("**Canonical Query:**", sm.get("canonical_query", ""))
                        if sm.get("mapped_terms"):
                            st.write("**Mapped Terms:**", sm["mapped_terms"])
                        if sm.get("warnings"):
                            st.warning("; ".join(sm["warnings"]))

                if data.get("retrieved_documents"):
                    with st.expander(
                        f"Retrieved Documents ({len(data['retrieved_documents'])} chunks)",
                        expanded=True,
                    ):
                        for doc in data["retrieved_documents"]:
                            with st.container():
                                st.markdown(
                                    f"**#{doc['rank']}** — {doc['title']} "
                                    f"_(score: {doc['score']:.4f})_"
                                )
                                st.text(doc["text"][:300])
                                st.caption(f"Source: {doc.get('source_path', 'N/A')}")
                                st.divider()

                if data.get("trace") and show_trace:
                    with st.expander("Execution Trace", expanded=True):
                        for step in data["trace"]:
                            emoji = {
                                "completed": "✅",
                                "skipped": "⏭️",
                                "failed": "❌",
                            }.get(step.get("status"), "➡️")
                            st.markdown(f"{emoji} **{step['step_name']}** — {step['status']}")
                            if step.get("input_summary"):
                                st.caption(f"Input: {step['input_summary']}")
                            if step.get("output_summary"):
                                st.caption(f"Output: {step['output_summary']}")

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to the API. Make sure the backend is running:\n\n"
                "`uvicorn app.main:app --reload`"
            )

st.divider()

st.header("Planned Pipeline Stages")
st.code(
    """
1. Intent Understanding  ✅ (Week 3)
2. Semantic Mapping     ✅ (Week 3)
3. Retrieval (BM25)     ✅ (Week 3)
4. SQL Execution         - (Week 4)
5. Analysis             - (Week 4)
6. Synthesis            - (Week 5)
7. Verification         - (Week 5)
8. Final Answer         - (Week 5)
"""
)
