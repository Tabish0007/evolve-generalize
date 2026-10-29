# Evolve Generalize

> A stress test for measuring cross-benchmark generalization in agent evolution frameworks.

[![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://evolve-generalize.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

## The Problem

Current agent evolution frameworks optimize agent workspaces by mutating prompts, skills, and memory. However, they only evaluate agents on the *same* benchmark they trained on. This means an agent might achieve a high score by simply memorizing task-specific heuristics, rather than learning transferable intelligence.

## The Solution

`Evolve Generalize` is an infrastructure layer designed to measure cross-benchmark generalization. It runs a three-phase stress test:

1. **Baseline:** Evaluate the raw agent on the target benchmark.
2. **Transfer:** Evolve the agent on a *different* benchmark, freeze it, and evaluate it on the target.
3. **Upper Bound:** Evolve directly on the target.

The delta between the Baseline and the Transfer score is the **Overfitting Penalty**.

## Why this is hard (and what I fixed)

To validate this benchmark, I integrated it with an open-source evolution framework and local `Ollama` inference. During integration, I discovered the framework was heavily coupled to cloud infrastructure (AWS Bedrock) and had broken local evaluation paths. I identified and patched three critical upstream bugs:

1. **Broken Module Registries:** The benchmark registry mapped to modules that didn't exist in the local clone.
2. **Silent Agent Fallbacks:** The agent resolver silently defaulted to the wrong agent type when passed a local path.
3. **Hardcoded Cloud Providers:** The solver agent was hardcoded to Bedrock, making local inference impossible.

All patches are included in the [`patches/`](patches/) directory. The platform can now run end-to-end on local consumer hardware without cloud credits.

## Project Structure

```text
├── app.py                  # Streamlit dashboard (Interactive UI)
├── stress_test.py          # The 3-phase evaluation harness
├── patches/                # Git diffs for the upstream bug fixes
└── requirements.txt        # UI dependencies
