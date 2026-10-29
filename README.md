# Workspace Overfit Stress Test

[Live Demo](https://tabish0007-test-app-xxxx.streamlit.app)

A-Evolve mutates agent workspaces (prompts, skills, memory) to push benchmark scores up. I wanted to know if those mutations actually generalize to a different benchmark, or if they just overfit to the task they were trained on.

To test this, I built a three-phase harness (evolve on X → freeze → evaluate on Y). 

**Status:** The harness works. The SkillBench backend is currently broken on local hardware.

## The Harness

The script (`stress_test.py`) runs three conditions:
1. **Baseline:** Evaluate the raw seed workspace on Benchmark Y.
2. **Transfer:** Evolve on Benchmark X, freeze the workspace, evaluate on Y.
3. **Upper Bound:** Evolve directly on Y, evaluate on Y.

If condition 2 performs worse than condition 1, the evolution loop is overfitting. 

To run this without AWS credentials, the harness forces the evolver to use a local Ollama model (`qwen2.5-coder:7b`) and passes adapter instances directly to the `Evolver` to skip the broken registry.

## Why it doesn't fully run yet (and the 3 bugs I found)

While wiring Ollama into A-Evolve, I hit a wall with their local evaluation path. I ended up patching three bugs just to get the harness to start:

1. **The Registry is broken:** `BENCHMARK_REGISTRY` in `api.py` points to modules (`swe_verified`, `terminal2`) that aren't in the shipped clone.
2. **Silent Agent Fallback:** `_resolve_agent` looks up a `Path` string in `_SEED_REGISTRY`, misses, and silently falls back to `TerminalAgent` regardless of the workspace manifest.
3. **Hardcoded Bedrock:** `SkillBenchAgent` imports `BedrockModel` unconditionally, which makes local inference impossible.

Patches for these are in the `patches/` directory.

After patching the agent to accept an OpenAI-compatible endpoint, the SkillBench native backend still fails with an `infrastructure_error` before Docker even builds. The failure classifier in `backends.py` swallows the actual exception, so I can't debug the container build without modifying their upstream code further. 

## Local Setup

If you want to run the Streamlit UI locally:
```bash
pip install -r requirements.txt
streamlit run app.py
