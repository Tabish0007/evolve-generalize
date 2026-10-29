import streamlit as st
import json
from pathlib import Path

# Must be the first Streamlit command
st.set_page_config(page_title="Evolve Generalize", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

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

    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #333;
    }

    .streamlit-expanderHeader {
        background-color: #111;
        border: 1px solid #333;
        border-radius: 4px;
        font-weight: 500;
    }
    
    .stAlert {
        border-radius: 4px;
        border: 1px solid #333;
        background-color: #111;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### `EVOLVE` / GENERALIZE")
    st.markdown("---")
    st.markdown("""
    **Environment:** 
    - Local `qwen2.5-coder:7b`
    - Ollama Backend
    - Upstream framework patched
    """)
    st.markdown("---")
    st.caption("v0.1.0 • [GitHub Repo](https://github.com/Tabish0007/evolve-generalize)")

# Main Header
st.title("Evolve Generalize")

# --- EXECUTIVE SUMMARY ---
st.markdown("""
**The Problem:** AI evolution frameworks automatically rewrite an agent's internal instructions (prompts, skills, and memory) to make it better at a specific task. But do these automated rewrites actually make the AI smarter, or does it just **overfit** (memorize) that one specific benchmark and fail at everything else?

**What this does:** This project is a custom evaluation harness that tests AI agents for overfitting. It forces the agent to train on Task A, freezes its brain, and then tests it on Task B to see if the learned skills actually transfer.
""")
# ------------------------------

st.markdown("<hr style='border: 1px solid #333; margin: 2rem 0;'>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Phase A Cycles", "15", "Train")
col2.metric("Phase B Cycles", "5", "Frozen")
col3.metric("Phase C Cycles", "15", "Upper Bound")
col4.metric("LLM Engine", "Ollama", "Local")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["THE HARNESS", "PATCHES & BUGS", "RAW JSON"])

with tab1:
    st.markdown("### The Evaluation Logic")
    st.markdown("The harness isolates the 'overfitting penalty' by comparing three distinct phases:")
    
    st.code("""
# 1. Baseline: Test raw agent on target benchmark
baseline_score = eval(seed_workspace, Y)

# 2. Transfer: Train on X, then test on Y
transfer_score = eval(evolve(seed_workspace, X), Y)

# 3. Upper Bound: Train on Y, then test on Y
upper_bound    = eval(evolve(seed_workspace, Y), Y)

# The Overfitting Signal
overfit_gap = transfer_score - baseline_score
headroom    = upper_bound - baseline_score
    """, language="python")

with tab2:
    st.markdown("### Upstream Bugs Identified")
    st.markdown("While building the local Ollama pipeline, three critical issues were found in the framework's evaluation path and patched in this repository.")
    
    with st.expander("Bug 1: Registry Module Mismatch"):
        st.markdown("""
        The benchmark registry mapped names to modules that didn't exist in the shipped clone (e.g., `swe_verified`, `terminal2` at the top level).
        **Fix:** Bypass the registry and pass adapter instances directly.
        """)
        
    with st.expander("Bug 2: Silent Agent Fallback"):
        st.markdown("""
        The agent resolver looked up a Path string in the seed registry, missed, and silently fell back to `TerminalAgent` regardless of the workspace manifest.
        **Fix:** Construct the agent instance directly instead of passing a path string.
        """)
        
    with st.expander("Bug 3: Hardcoded Cloud Provider"):
        st.markdown("""
        The solver agent imported `BedrockModel` unconditionally, making local Ollama evaluation impossible.
        **Fix:** Patch the agent to accept any OpenAI-compatible endpoint via an environment variable.
        """)

with tab3:
    st.markdown("### Raw Harness Output")
    st.markdown("Output from the harness running on local hardware.")
    st.warning("""
    **Failure Mode:** The native benchmark backend fails during Docker initialization. 
    The failure classifier swallows the traceback before the LLM is called. 
    This is a benchmark issue, not a harness issue.
    """)
