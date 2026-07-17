import os

import pandas as pd
import requests
import streamlit as st


API_URL = os.getenv("VERIDIAN_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Veridian AI", layout="wide")

st.title("Veridian AI")
st.subheader("Deterministic Enterprise Analytics Prototype")

query = st.text_input(
    "Ask a controlled business question:",
    "Why did enterprise revenue decline in APAC despite higher marketing spend?",
)

col1, col2 = st.columns([1, 5])
with col1:
    run = st.button("Run Query", help="Submit the query to the local FastAPI backend.")
with col2:
    show_trace = st.checkbox("Show trace", value=True, help="Show timed backend execution stages.")

if run:
    with st.spinner("Processing query..."):
        try:
            resp = requests.post(
                f"{API_URL}/api/query",
                json={"query": query, "include_trace": show_trace},
                timeout=30,
            )
            if resp.status_code != 200:
                st.error(f"API error: {resp.status_code} - {resp.text}")
            else:
                data = resp.json()
                status = data.get("status", "unknown")
                if status == "rejected":
                    st.error(f"Query rejected: {data.get('message', '')}")
                elif status == "needs_clarification":
                    st.warning(f"Clarification needed: {data.get('message', '')}")
                elif status == "error":
                    st.error("Query completed with typed errors.")
                else:
                    st.success("Query processed")

                with st.expander("Query Understanding", expanded=True):
                    intent = data.get("intent") or {}
                    semantic = data.get("semantic_parse") or {}
                    st.write("**Query type:**", intent.get("query_type", "?"))
                    st.write("**Metrics:**", [m.get("canonical_name") for m in semantic.get("metrics", [])])
                    st.write("**Dimensions:**", [d.get("canonical_name") for d in semantic.get("dimensions", [])])
                    st.write("**Filters:**", {f.get("dimension"): f.get("value") for f in semantic.get("filters", [])})
                    st.write("**Periods:**", (semantic.get("time_range") or {}).get("periods", []))
                    st.write("**Aggregation:**", semantic.get("aggregation") or "metric default")
                    st.write("**Comparison:**", semantic.get("comparison"))
                    if semantic.get("warnings"):
                        st.warning(semantic["warnings"])
                    if semantic.get("errors"):
                        st.error(semantic["errors"])
                    if semantic.get("requires_clarification"):
                        st.info("This query requires clarification before SQL execution.")

                if data.get("sql_plan"):
                    with st.expander("Structured Query Plan", expanded=True):
                        plan = data["sql_plan"]
                        if plan.get("errors"):
                            st.error(plan["errors"])
                        for spec in plan.get("specs", []):
                            st.write(
                                {
                                    "shape": spec.get("query_shape"),
                                    "source_table": spec.get("source_table"),
                                    "metric": spec.get("metric"),
                                    "dimensions": spec.get("dimensions"),
                                    "filters": spec.get("filters"),
                                    "periods": spec.get("periods"),
                                }
                            )

                if data.get("compiled_queries"):
                    with st.expander("SQL", expanded=True):
                        for compiled in data["compiled_queries"]:
                            st.code(compiled.get("sql", ""), language="sql")
                            st.write("**Parameters:**", compiled.get("parameters", []))
                            st.caption(compiled.get("explanation", ""))

                if data.get("sql_results"):
                    with st.expander("SQL Results", expanded=True):
                        for result in data["sql_results"]:
                            st.write(f"**{result.get('query_id')}** - {result.get('row_count', 0)} row(s), {result.get('execution_ms')} ms")
                            if result.get("error"):
                                st.error(result["error"])
                            elif result.get("rows"):
                                st.dataframe(pd.DataFrame(result["rows"]), use_container_width=True)
                            else:
                                st.info("No rows returned.")
                        if data.get("comparison_results"):
                            st.write("**Comparison calculations:**")
                            st.dataframe(pd.DataFrame(data["comparison_results"]), use_container_width=True)

                if data.get("retrieved_documents"):
                    with st.expander(f"Retrieved Evidence ({len(data['retrieved_documents'])} chunks)", expanded=True):
                        for doc in data["retrieved_documents"]:
                            st.markdown(f"**#{doc['rank']} - {doc['title']}** (score: {doc['score']:.4f})")
                            metadata = doc.get("metadata") or {}
                            st.caption(
                                f"Source: {doc.get('source_path', 'N/A')} | "
                                f"Section: {doc.get('section') or metadata.get('section', 'N/A')}"
                            )
                            st.text(doc["text"][:500])
                            st.divider()

                st.info("Natural-language evidence synthesis is not implemented yet.")

                if data.get("execution_trace") and show_trace:
                    with st.expander("Execution Trace", expanded=True):
                        for step in data["execution_trace"]:
                            st.markdown(f"**{step.get('stage', step.get('step_name'))}** - {step.get('status')}")
                            st.caption(f"Duration: {step.get('duration_ms')} ms")
                            if step.get("input_summary"):
                                st.caption(f"Input: {step['input_summary']}")
                            if step.get("output_summary"):
                                st.caption(f"Output: {step['output_summary']}")
                            if step.get("error"):
                                st.error(step["error"])

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to the API. Start the backend with:\n\n"
                "`python -m uvicorn app.main:app --reload`"
            )

st.divider()
st.caption(
    "Veridian AI currently supports controlled deterministic analytical queries over a local DuckDB warehouse. "
    "It does not yet provide general-purpose text-to-SQL, LLM-generated answers, evidence synthesis, or verification."
)
