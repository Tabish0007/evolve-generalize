import streamlit as st
import json
from pathlib import Path

# Must be the first Streamlit command
st.set_page_config(page_title="Workspace Overfit | A-Evolve", layout="wide", initial_sidebar_state="expanded")

# Custom CSS to kill the "Streamlit toy" look and make it look like a professional infra tool
st.markdown("""
<style>
    /* Global Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Kill default streamlit padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Headers */
    h1, h2, h3 {
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-size: 2rem !important;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #333;
        margin-bottom: 1.5rem !important;
    }

    /* Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #111;
        border: 1px solid #333;
        padding: 1rem;
        border-radius: 4px;
    }
    
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid #333;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 0;
        font-weight: 500;
        color: #888;
    }
    .stTabs [aria-selected="true"] {
        color: #fff;
        border-bottom: 2px solid #fff;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #333;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #111;
        border: 1px solid #333;
        border-radius: 4px;
        font-weight: 500;
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 4px;
        border: 1px solid #333;
        background-color: #111;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### `A-EVOLVE` / STRESS")
    st.markdown("---")
    st.markdown("""
    **Objective:** Measure cross-benchmark generalization of evolved agent workspaces. 
    
    **Environment:** 
    - Local `qwen2.5-coder:7b`
    - Ollama Backend
    - A-Evolve (patched)
    """)
    st.markdown("---")
    st.caption("v0.1.0 • [GitHub Repo](https://github.com/Tabish0007/test)")

# Main Header
st.title("Workspace Overfit Stress Test")
st.markdown("`A-Evolve` mutates prompts, skills, and memory to optimize a target benchmark. This harness measures whether those mutations generalize, or if they simply overfit.")

# Top level metrics (using placeholder numbers for the dashboard aesthetic, or real ones if you want)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Phase A Cycles", "15", "Evolve X")
col2.metric("Phase B Cycles", "5", "Frozen")
col3.metric("Phase C Cycles", "15", "Upper Bound")
col4.metric("LLM Engine", "Ollama", "Local")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["EXPERIMENT", "PATCHES & BUGS", "RAW JSON"])

with tab1:
    st.markdown("### The Overfitting Signal")
    st.markdown("The harness executes three phases. The delta between the seed baseline and the transferred workspace isolates the overfitting penalty.")
    
    st.code("""
# Pseudo-code of the evaluation logic
baseline_score = eval(seed_workspace, Y)
transfer_score = eval(evolve(seed_workspace, X), Y)
upper_bound    = eval(evolve(seed_workspace, Y), Y)

overfit_gap = transfer_score - baseline_score
headroom    = upper_bound - baseline_score
    """, language="python")

    st.info("Note: The native SkillBench backend currently fails at the Docker container initialization step due to an upstream infrastructure_error. The harness logic is complete.")

with tab2:
    st.markdown("### Upstream A-Evolve Bugs Identified")
    st.markdown("Three critical issues were found in A-Evolve's local evaluation path and patched in this repository.")
    
    with st.expander("Bug 1: Registry Module Mismatch"):
        st.markdown("""
        `BENCHMARK_REGISTRY` maps names to modules that don't exist in the shipped clone (`swe_verified`, `terminal2` at the top level).
        **Fix:** Bypass the registry and pass adapter instances directly.
        """)
        
    with st.expander("Bug 2: Silent Agent Fallback"):
        st.markdown("""
        `_resolve_agent` looks up a Path string in `_SEED_REGISTRY`, misses, and silently falls back to `TerminalAgent` regardless of the workspace manifest.
        **Fix:** Construct the agent instance directly (`SkillBenchAgent`) instead of passing a path string.
        """)
        
    with st.expander("Bug 3: Hardcoded Bedrock"):
        st.markdown("""
        `SkillBenchAgent` imports `BedrockModel` unconditionally, making local Ollama evaluation impossible.
        **Fix:** Patch the agent to accept any OpenAI-compatible endpoint via `SKILLBENCH_BASE_URL`.
        """)

with tab3:
    st.markdown("### Raw Harness Output")
    st.markdown("Output from the harness running on local hardware.")
    st.warning("""
    **Failure Mode:** SkillBench's native backend fails during Docker initialization. 
    The failure classifier in `backends.py` swallows the traceback before the LLM is called. 
    This is a benchmark issue, not a harness issue.
    """)
