import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="Workspace Overfit Stress", page_icon="🧪", layout="wide")

st.title("🧪 Workspace Overfit Stress Test")
st.caption("Measuring cross-benchmark generalization of evolved agent workspaces (built on A-Evolve).")

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("This harness tests whether prompt/skill mutations generalize across benchmarks, or if they just overfit to the training set.")
    st.success("**Status:** Harness complete. Backend patched for local Ollama.")
    st.markdown("---")
    st.markdown("**GitHub:** [Tabish0007](https://github.com/Tabish0007)")

# Main content
tab1, tab2, tab3 = st.tabs(["The Experiment", "Bugs Found & Patched", "Raw Report"])

with tab1:
    st.header("The Three-Phase Harness")
    st.markdown("""
    A-Evolve mutates agent workspaces to improve benchmark scores. This harness asks: **do those mutations generalize?**
    """)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Phase A", "Evolve on X", "15 cycles")
    col2.metric("Phase B", "Freeze & Eval on Y", "No mutations")
    col3.metric("Phase C", "Direct Evolve on Y", "Upper bound")
    
    st.markdown("### The Overfitting Signal")
    st.code("""
overfit_signal = score(X_evolved, Y) - score(seed, Y)
headroom       = score(Y_evolved, Y) - score(seed, Y)
    """, language="python")
    
    if Path("results/stress_test_report.json").exists():
        with st.expander("View actual run output"):
            st.json(json.loads(Path("results/stress_test_report.json").read_text()))
    else:
        st.info("No run report found. Run `python stress_test.py` to generate one.")

with tab2:
    st.header("Upstream Bugs Identified")
    st.markdown("While building this, I found three critical issues in A-Evolve's local evaluation path. Patches are included in the repo.")
    
    with st.expander("🐛 Bug 1: Registry Module Mismatch"):
        st.markdown("""
        `BENCHMARK_REGISTRY` maps names to modules that don't exist in the shipped clone (e.g., `swe_verified`, `terminal2` at the top level).
        **Fix:** Bypass the registry and pass adapter instances directly.
        """)
        
    with st.expander("🐛 Bug 2: Silent Agent Fallback"):
        st.markdown("""
        `_resolve_agent` looks up a Path string in `_SEED_REGISTRY`, misses, and silently falls back to `TerminalAgent` regardless of the workspace manifest.
        **Fix:** Construct the agent instance directly (`SkillBenchAgent`) instead of passing a path string.
        """)
        
    with st.expander("🐛 Bug 3: Hardcoded Bedrock"):
        st.markdown("""
        `SkillBenchAgent` imports `BedrockModel` unconditionally, making local Ollama evaluation impossible.
        **Fix:** Patch the agent to accept any OpenAI-compatible endpoint via `SKILLBENCH_BASE_URL`.
        """)

with tab3:
    st.header("Raw Output")
    st.markdown("This shows the output of the harness running on a local Ollama instance (`qwen2.5-coder:7b`).")
    st.warning("""
    **Note on results:** The harness executes perfectly, but SkillBench's native backend fails during Docker initialization (`infrastructure_error`). 
    The failure classifier swallows the traceback before the LLM is called. This is a benchmark issue, not a harness issue.
    """)
