"""The agent roster: expert personas loaded from ``config/agents.yaml``.

Each analytic agent in the pipeline mirrors one operation in Richmond's human
workflow (see ``docs/RICHMOND_WORKFLOW_AND_AGENT_MAPPING.md``). This module is the
single place that resolves an agent's persona + model tier, so every LLM call can
be prefixed with the same embedded domain expertise (the MetaGPT lesson: role
expertise lives in the agent definition, not in ad-hoc prompts).
"""

from __future__ import annotations

from res_pipeline.core.config import load_yaml_config


def _roster() -> dict:
    return load_yaml_config("agents")


def persona(agent_id: str) -> str:
    """Return the full system-prompt prefix for an agent: shared expertise + its persona."""
    cfg = _roster()
    if agent_id not in cfg["agents"]:
        raise KeyError(f"Unknown agent '{agent_id}'. Define it in config/agents.yaml.")
    shared = cfg["shared_expertise"].strip()
    role = cfg["agents"][agent_id]["persona"].strip()
    title = cfg["agents"][agent_id]["title"]
    return f"{shared}\n\nYOUR ROLE — {title}:\n{role}"


def agent_tier(agent_id: str) -> str:
    """Model tier for an agent (from config/agents.yaml → config/models.yaml)."""
    return _roster()["agents"][agent_id]["tier"]


def roster_summary() -> list[dict]:
    """One row per agent: id, title, Richmond analogue, tier — for reporting."""
    cfg = _roster()
    return [
        {"id": aid, "title": a["title"], "tier": a["tier"],
         "richmond_analogue": " ".join(a["richmond_analogue"].split())}
        for aid, a in cfg["agents"].items()
    ]


def human_checkpoints() -> list[dict]:
    return _roster()["human_checkpoints"]
