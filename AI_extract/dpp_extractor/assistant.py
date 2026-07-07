"""
Product Assistant — a stateless pydantic-ai agent that answers questions about
ONE product's Digital Product Passport.

Design:
  - Stateless: the Agent is a module-level singleton (model + tools + prompt).
    Conversation memory lives in the DB and is passed per-request via
    `message_history`; the agent holds nothing between calls.
  - Provider: OpenAI (extraction stays on Gemini).
  - Hybrid data access: a compact passport summary is injected via a dynamic
    system prompt, plus tools for precise lookups on the full passport.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from pydantic_ai import Agent, RunContext
# pydantic-ai renamed OpenAIModel → OpenAIChatModel in versions after 1.107.
# Handle both so we're not one pip resolve away from a boot crash on a fresh box.
try:
    from pydantic_ai.models.openai import OpenAIChatModel as OpenAIModel
except ImportError:  # older pydantic-ai
    from pydantic_ai.models.openai import OpenAIModel  # type: ignore[no-redef]
from pydantic_ai.providers.openai import OpenAIProvider

from .config import OPENAI_API_KEY, OPENAI_CHAT_MODEL

logger = logging.getLogger(__name__)


# ── Dependencies injected per run ────────────────────────────────────────────

@dataclass
class ProductChatDeps:
    """Carries the product passport the agent answers about."""
    passport: dict
    product_name: str


# ── Passport rendering helpers ───────────────────────────────────────────────

def _ev(obj, *path):
    """Read a nested ExtractedField .value via a path. Safe on missing."""
    cur = obj or {}
    for k in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
        if cur is None:
            return None
    return cur.get("value") if isinstance(cur, dict) and "value" in cur else cur


def _fv(field):
    return field.get("value") if isinstance(field, dict) and "value" in field else field


def render_passport_summary(passport: dict, max_perf: int = 40) -> str:
    """Compact, human-readable rendering of a passport for the system prompt."""
    if not passport:
        return "(no passport data available)"
    o_pi = (passport.get("overview") or {}).get("product_info") or {}
    o_mf = (passport.get("overview") or {}).get("manufacturer") or {}
    lines: list[str] = []

    lines.append("=== PRODUCT ===")
    lines.append(f"Name: {_fv(o_pi.get('product_name'))}")
    lines.append(f"UID: {_fv(o_pi.get('uid'))}")
    fam = _fv(o_pi.get('product_family')) or _fv(o_pi.get('product_family_code'))
    lines.append(f"Family: {fam}")
    for label, key in (("Intended use", "intended_use"), ("Functional unit", "functional_unit"),
                       ("Dimensions", "standard_dimension"), ("Weight", "weight"),
                       ("Production period", "production_period"), ("Description", "product_description")):
        v = _fv(o_pi.get(key))
        if v:
            lines.append(f"{label}: {v}")

    lines.append("\n=== MANUFACTURER ===")
    for label, key in (("Company", "company_name"), ("Address", "address"),
                       ("Manufacturing site", "manufacturing_site"), ("Website", "website"),
                       ("Email", "email"), ("Phone", "phone")):
        v = _fv(o_mf.get(key))
        if v:
            lines.append(f"{label}: {v}")

    materials = (passport.get("composition") or {}).get("materials") or []
    if materials:
        lines.append(f"\n=== COMPOSITION ({len(materials)} materials) ===")
        for m in materials:
            desc = _fv(m.get("description"))
            qty = _fv(m.get("quantity_per_product"))
            unit = _fv(m.get("unit"))
            pct = _fv(m.get("percentage"))
            extra = []
            if pct not in (None, ""):
                extra.append(f"{pct}%")
            if qty not in (None, ""):
                extra.append(f"{qty}{(' ' + unit) if unit else ''}")
            lines.append(f"- {desc}" + (f" ({', '.join(str(e) for e in extra)})" if extra else ""))

    perf = (passport.get("performance") or {}).get("values") or []
    if perf:
        lines.append(f"\n=== PERFORMANCE ({len(perf)} values) ===")
        for v in perf[:max_perf]:
            name = _fv(v.get("property_name"))
            val = _fv(v.get("value"))
            unit = _fv(v.get("unit"))
            cat = _fv(v.get("category"))
            lines.append(f"[{cat}] {name} = {val}{(' ' + unit) if unit else ''}")
        if len(perf) > max_perf:
            lines.append(f"... ({len(perf) - max_perf} more — use list_performance to see all)")

    comp = passport.get("compliance") or {}
    lines.append("\n=== COMPLIANCE ===")
    for label, key in (("DoP reference", "dop_reference"), ("DoP standard", "dop_standard"),
                       ("DoC reference", "doc_reference"), ("CE marking", "ce_marking"),
                       ("Quality control", "quality_control")):
        v = _fv(comp.get(key))
        if v:
            lines.append(f"{label}: {v}")
    safety = comp.get("safety") or {}
    safety_bits = []
    for key, lbl in (("contains_cmrs", "CMR"), ("contains_svhcs", "SVHC"),
                     ("contains_pentane", "pentane"), ("contains_pfas", "PFAS"),
                     ("complies_rohs", "RoHS"), ("produces_voc", "VOC"),
                     ("contains_asbestos", "asbestos"), ("complies_child_labor", "child-labor")):
        v = _fv(safety.get(key))
        if v not in (None, ""):
            safety_bits.append(f"{lbl}={v}")
    if safety_bits:
        lines.append("Safety: " + ", ".join(safety_bits))

    stages = (passport.get("lifecycle") or {}).get("stages") or []
    if stages:
        lines.append("\n=== LIFECYCLE (EPD GWP by stage) ===")
        for s in stages:
            g = _fv(s.get("gwp_total"))
            if g not in (None, ""):
                lines.append(f"{s.get('stage_code', '?')}: GWP {g} kgCO2eq")

    return "\n".join(lines)


# ── Agent (stateless singleton) ──────────────────────────────────────────────

_BASE_SYSTEM_PROMPT = """\
You are the DeePPy product assistant. You answer questions about ONE specific \
construction product's Digital Product Passport (DPP).

Rules:
- Answer using ONLY the passport data provided. Do not invent values.
- If a value is not in the passport, say it is "not declared" (or the user's \
language equivalent). You may add brief, clearly-labelled general context about \
DPP/ESPR/CPR concepts, but never fabricate this product's data.
- Be concise and precise. Quote the exact value and unit when relevant.
- Reply in the same language the user writes in (Italian or English).
- For precise or detailed lookups, use the provided tools.
- You also HELP THE USER COMPLETE the passport. When they ask what is missing, \
how complete it is, or what they still need to provide, call \
get_completion_status and report the missing MANDATORY fields together with \
where each is typically found, so the user knows how to fill them. You advise; \
the user edits the fields manually in the editor.
"""

_agent: Optional[Agent] = None


def _build_agent() -> Agent:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set — the assistant is unavailable.")
    model = OpenAIModel(OPENAI_CHAT_MODEL, provider=OpenAIProvider(api_key=OPENAI_API_KEY))
    agent = Agent(
        model,
        deps_type=ProductChatDeps,
        system_prompt=_BASE_SYSTEM_PROMPT,
    )

    @agent.system_prompt
    def _inject_passport(ctx: RunContext[ProductChatDeps]) -> str:
        return (
            f"The product in this conversation is '{ctx.deps.product_name}'. "
            f"Here is its passport data:\n\n{render_passport_summary(ctx.deps.passport)}"
        )

    @agent.tool
    def lookup_field(ctx: RunContext[ProductChatDeps], path: str) -> str:
        """Look up a single passport field by dotted path (e.g.
        'overview.manufacturer.address' or 'compliance.dop_reference').
        Returns the value plus its confidence and source document if available."""
        cur = ctx.deps.passport or {}
        for key in path.split("."):
            if not isinstance(cur, dict):
                return f"Path '{path}' not found."
            cur = cur.get(key)
            if cur is None:
                return f"'{path}' is not declared in this passport."
        if isinstance(cur, dict) and "value" in cur:
            val = cur.get("value")
            if val in (None, "", [], {}):
                return f"'{path}' is not declared."
            src = cur.get("source") or {}
            doc = src.get("document_name") if isinstance(src, dict) else None
            conf = cur.get("confidence")
            extra = []
            if conf:
                extra.append(f"confidence={conf}")
            if doc:
                extra.append(f"source={doc}")
            return f"{path} = {val}" + (f" ({', '.join(extra)})" if extra else "")
        return f"{path} = {cur}"

    @agent.tool
    def list_performance(ctx: RunContext[ProductChatDeps], category: Optional[str] = None) -> str:
        """List all performance values, optionally filtered by category
        (Mechanical, Thermal, Acoustic, Fire, Durability, Environmental)."""
        vals = (ctx.deps.passport.get("performance") or {}).get("values") or []
        out = []
        for v in vals:
            cat = _fv(v.get("category"))
            if category and (cat or "").lower() != category.lower():
                continue
            name = _fv(v.get("property_name"))
            val = _fv(v.get("value"))
            unit = _fv(v.get("unit"))
            out.append(f"[{cat}] {name} = {val}{(' ' + unit) if unit else ''}")
        if not out:
            return "No performance values" + (f" in category '{category}'." if category else ".")
        return "\n".join(out)

    @agent.tool
    def get_completion_status(ctx: RunContext[ProductChatDeps]) -> str:
        """Report how complete the DPP is: which MANDATORY fields are still
        missing, the mandatory-fields completion percentage, and the overall
        confidence breakdown. Use this whenever the user asks what's missing,
        how complete the passport is, or what they still need to fill in.
        Pair each missing field with where it is typically found (see guidance)."""
        from .db.repository import compute_required, compute_stats
        filled, total, missing = compute_required(ctx.deps.passport)
        stats = compute_stats(ctx.deps.passport)
        conf = stats.get("confidence", {})
        lines = [
            f"Mandatory fields: {filled}/{total} filled "
            f"({round(filled / total * 100) if total else 0}%).",
            f"All fields (incl. optional): {stats.get('fields_filled', 0)}/"
            f"{stats.get('total_fields', 0)} filled ({stats.get('overall_completeness', 0)}%).",
        ]
        if missing:
            lines.append("Missing MANDATORY fields:")
            for m in missing:
                hint = _FIELD_SOURCE_HINTS.get(m)
                lines.append(f"  - {m}" + (f"  → typically from: {hint}" if hint else ""))
        else:
            lines.append("All mandatory fields are present. ✅")
        lines.append(
            f"Overall data: {conf.get('high', 0)} high-confidence, "
            f"{conf.get('medium', 0)} to review, {conf.get('low', 0)} low/empty."
        )
        return "\n".join(lines)

    return agent


# Where each mandatory field is usually sourced — guidance for the assistant
# when advising how to fill a gap.
_FIELD_SOURCE_HINTS = {
    "Product name": "the commercial name on the DoP / Technical Sheet / brochure",
    "UID": "the product code on the DoP or Technical Sheet",
    "Item type": "inferred from the product family (System/Product/Component/Material)",
    "Product family": "the CPR/DoP classification of the product",
    "Intended use": "the 'intended use' clause of the DoP",
    "Functional unit": "the declared/reference unit in the EPD (e.g. piece, m², m³)",
    "Production period": "the validity dates on the Certificate, or EPD validity",
    "Company name": "the manufacturer block of the DoP / EPD",
    "Address": "the registered address on the DoP / manufacturer profile",
    "Website": "the manufacturer's website (DoP footer, brochure, or company profile)",
    "Manufacturing site": "the plant address stated on the DoP or EPD",
    "Email": "the manufacturer contact on the DoP / brochure / company profile",
    "Bill of materials (≥1 product)": "the EPD composition table or an uploaded BoM (xlsx)",
}


def get_agent() -> Agent:
    """Return the singleton assistant agent (built lazily on first use)."""
    global _agent
    if _agent is None:
        _agent = _build_agent()
        logger.info(f"Assistant agent initialized (model={OPENAI_CHAT_MODEL})")
    return _agent


def assistant_available() -> bool:
    return bool(OPENAI_API_KEY)
