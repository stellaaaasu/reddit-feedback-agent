import streamlit as st

from agent import run_agent


def failure_message(report):
    """Translate the core's error strings without showing internal details."""
    if not isinstance(report, str) or not report.strip():
        return "The agent returned an empty report. Please try again."
    if not report.lstrip().startswith("## 无法生成报告"):
        return None
    if "环境变量" in report:
        return "A required API key is missing. Set AGNES_API_KEY and TAVILY_API_KEY on the server, then try again."
    if "初始化失败" in report:
        return "The model client could not start. Check the server configuration and installed dependencies."
    if "模型请求失败" in report:
        return "The Agnes request failed. Check the network, API key configuration, and account quota, then try again."
    if "空内容" in report:
        return "Agnes returned an empty response. Please try again."
    if "仍请求调用工具" in report:
        return "The search limit was reached, but Agnes did not return a final report. Please try again."
    return "The agent could not generate a report. Please try again."


st.set_page_config(page_title="Reddit Feedback Agent", layout="centered")

st.title("Reddit Feedback Agent")
st.write("Explore user feedback and marketing opportunities for AI products.")

for key in ("report", "report_product", "analysis_error"):
    if key not in st.session_state:
        st.session_state[key] = None

with st.container(border=True):
    product = st.text_input("Product name", placeholder="Cursor")
    context = st.text_input(
        "Product context (optional)", placeholder="AI code editor"
    )
    submitted = st.button(
        "Analyze Feedback", type="primary", disabled=not product.strip()
    )

if submitted and product.strip():
    # Clear the previous result before attempting a new analysis.
    st.session_state.report = None
    st.session_state.report_product = None
    st.session_state.analysis_error = None
    question = (
        f"Analyze Reddit user feedback and marketing opportunities for this AI product: {product.strip()}.\n"
    )
    if context.strip():
        question += f"Product context: {context.strip()}\n"
    question += "Write the entire report in English, including all labels and analysis recommendations."

    with st.spinner("Analyzing Reddit feedback…"):
        try:
            report = run_agent(question)
            error = failure_message(report)
        except Exception:
            report = None
            error = "The analysis could not be completed. Check the server configuration and connection, then try again."

    if error:
        st.session_state.analysis_error = error
    else:
        st.session_state.report = report
        st.session_state.report_product = product.strip()

if st.session_state.analysis_error:
    st.error(st.session_state.analysis_error)

if st.session_state.report is not None:
    st.divider()
    st.subheader("Feedback report")
    st.text(f"Analyzed product: {st.session_state.report_product}")
    st.markdown(st.session_state.report, unsafe_allow_html=False)

st.caption("Based on retrieved search results. Findings may not represent all users.")
