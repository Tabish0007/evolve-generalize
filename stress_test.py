#!/usr/bin/env python3
"""
Workspace overfitting stress test.

Phase A: evolve on benchmark X, freeze the workspace.
Phase B: evaluate the frozen workspace on benchmark Y.
Compare against (a) seed-on-Y and (b) directly-evolved-on-Y.

Two A-Evolve bugs this harness works around:
  - BENCHMARK_REGISTRY in api.py maps names to modules that don't exist in
    this clone (swe_verified, terminal2 at top level). Adapter instances are
    passed directly instead of strings.
  - _resolve_agent looks up a Path string in _SEED_REGISTRY, misses, and
    falls back to TerminalAgent regardless of the workspace manifest.
    SkillBenchAgent is constructed directly and passed as an instance.
"""

import json
import shutil
from pathlib import Path

import agent_evolve as ae
from agent_evolve.algorithms.skillforge import AEvolveEngine
from agent_evolve.llm.openai import OpenAIProvider
from agent_evolve.agents.skillbench.agent import SkillBenchAgent
from agent_evolve.benchmarks.skill_bench import SkillBenchBenchmark


CYCLES_A = 5
CYCLES_B = 2
SEEDS = [0]

SEED_WORKSPACE = Path("/Users/tabishsayyed/a-evolve/seed_workspaces/skillbench")
RUNS_DIR = Path("./runs")

# X and Y are the same benchmark for the smoke test. Once the pipeline runs
# end-to-end, swap X_ADAPTER for a genuinely different adapter (tb2.terminal2
# after fixing its relative import, or arc_agi3) and re-run.
X_ADAPTER = SkillBenchBenchmark()
Y_ADAPTER = SkillBenchBenchmark()
X_NAME = "skill-bench"
Y_NAME = "skill-bench"

OLLAMA = OpenAIProvider(
    model="qwen2.5-coder:7b",
    api_key="ollama",
    base_url="http://localhost:11434/v1",
)


def _freeze_config(max_cycles: int) -> ae.EvolveConfig:
    return ae.EvolveConfig(
        batch_size=10,
        max_cycles=max_cycles,
        evolve_prompts=False,
        evolve_skills=False,
        evolve_memory=False,
        holdout_ratio=0.0,
        egl_threshold=0.0,
    )


def _evolve_config(max_cycles: int) -> ae.EvolveConfig:
    return ae.EvolveConfig(
        batch_size=10,
        max_cycles=max_cycles,
        evolve_prompts=True,
        evolve_skills=True,
        evolve_memory=True,
        egl_threshold=0.02,
    )


def _engine(config):
    return AEvolveEngine(config, llm=OLLAMA)


def _make_agent(workspace: Path) -> SkillBenchAgent:
    # SKILLBENCH_BASE_URL routes the solver through Ollama. Without it,
    # SkillBenchAgent._build_model() falls back to Bedrock.
    return SkillBenchAgent(workspace_dir=str(workspace))


def phase_a(seed: Path, adapter, out: Path, cycles: int = CYCLES_A) -> dict:
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(seed, out)

    cfg = _evolve_config(cycles)
    evolver = ae.Evolver(
        agent=_make_agent(out),
        benchmark=adapter,
        config=cfg,
        engine=_engine(cfg),
    )
    results = evolver.run(cycles=cycles)
    return {"final_score": results.final_score, "workspace": str(out)}


def phase_b(frozen_ws: Path, adapter, label: str, cycles: int = CYCLES_B) -> dict:
    tmp = RUNS_DIR / f"eval_{label}_{frozen_ws.name}"
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(frozen_ws, tmp)

    cfg = _freeze_config(cycles)
    evolver = ae.Evolver(
        agent=_make_agent(tmp),
        benchmark=adapter,
        config=cfg,
        engine=_engine(cfg),
    )
    results = evolver.run(cycles=cycles)
    return {"final_score": results.final_score}


def main():
    RUNS_DIR.mkdir(exist_ok=True)

    print(f"[A] seed on {Y_NAME} (baseline)")
    seed_scores = []
    for s in SEEDS:
        seed_copy = RUNS_DIR / f"seed_copy_{s}"
        if seed_copy.exists():
            shutil.rmtree(seed_copy)
        shutil.copytree(SEED_WORKSPACE, seed_copy)
        r = phase_b(seed_copy, Y_ADAPTER, f"{Y_NAME}_seed")
        seed_scores.append(r["final_score"])
        print(f"    seed={s}: {r['final_score']:.4f}")

    print(f"[B] evolve on {X_NAME} -> freeze -> eval on {Y_NAME}")
    transfer_scores = []
    for s in SEEDS:
        ws = RUNS_DIR / f"x_evolved_{s}"
        phase_a(SEED_WORKSPACE, X_ADAPTER, ws)
        r = phase_b(ws, Y_ADAPTER, Y_NAME)
        transfer_scores.append(r["final_score"])
        print(f"    seed={s}: {r['final_score']:.4f}")

    print(f"[C] evolve on {Y_NAME} directly (upper bound)")
    direct_scores = []
    for s in SEEDS:
        ws = RUNS_DIR / f"y_evolved_{s}"
        phase_a(SEED_WORKSPACE, Y_ADAPTER, ws)
        r = phase_b(ws, Y_ADAPTER, Y_NAME)
        direct_scores.append(r["final_score"])
        print(f"    seed={s}: {r['final_score']:.4f}")

    def mean(xs):
        return sum(xs) / len(xs)

    report = {
        "X_bench": X_NAME,
        "Y_bench": Y_NAME,
        "seeds": SEEDS,
        "cycles_a": CYCLES_A,
        "cycles_b": CYCLES_B,
        "model": "qwen2.5-coder:7b",
        "seed_on_Y": seed_scores,
        "X_evolved_on_Y": transfer_scores,
        "Y_evolved_on_Y": direct_scores,
        "mean_seed_on_Y": mean(seed_scores),
        "mean_X_evolved_on_Y": mean(transfer_scores),
        "mean_Y_evolved_on_Y": mean(direct_scores),
        "transfer_gap": mean(transfer_scores) - mean(seed_scores),
        "headroom": mean(direct_scores) - mean(seed_scores),
    }

    out = RUNS_DIR / "stress_test_report.json"
    out.write_text(json.dumps(report, indent=2))

    print()
    print(f"seed on Y:          {report['mean_seed_on_Y']:.4f}")
    print(f"X-evolved on Y:     {report['mean_X_evolved_on_Y']:.4f}")
    print(f"Y-evolved on Y:     {report['mean_Y_evolved_on_Y']:.4f}")
    print(f"transfer gap:       {report['transfer_gap']:+.4f}")
    print(f"headroom:           {report['headroom']:+.4f}")
    print(f"report: {out}")


if __name__ == "__main__":
    main()
