"""One-shot probe: does the classification agent work in-container?

Run inside the api container to bypass the app's logging (which is silently
swallowing pipeline errors in prod). Whatever exception this prints IS the
exception killing the /api/extract flow.

Usage on the EC2:
    sudo docker exec deploy-api-1 python /app/deploy/probe_gemini.py
"""
import asyncio
import io
import logging
import os
import sys
import traceback
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, force=True, stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

print("=" * 72)
print("ENV")
print("=" * 72)
for k in ("GOOGLE_API_KEY", "GEMINI_MODEL", "OPENAI_API_KEY", "ENVIRONMENT"):
    v = os.environ.get(k, "")
    if k.endswith("_KEY") and v:
        v = f"<len={len(v)} prefix={v[:6]}...{v[-4:]}>"
    print(f"  {k}={v!r}")


def _make_tiny_pdf() -> Path:
    from pypdf import PdfWriter
    w = PdfWriter()
    w.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    w.write(buf)
    tmp = Path("/tmp/probe.pdf")
    tmp.write_bytes(buf.getvalue())
    return tmp


async def probe_model_factory():
    print()
    print("=" * 72)
    print("STAGE 1  —  model_factory")
    print("=" * 72)
    try:
        from dpp_extractor.pipeline import model_factory
        m = model_factory.get_model()
        print(f"  OK  model = {m!r}")
        return m
    except Exception as e:
        print(f"  FAIL  {type(e).__name__}: {e}")
        traceback.print_exc()
        return None


async def probe_pydantic_ai_direct(model):
    print()
    print("=" * 72)
    print("STAGE 2  —  pydantic-ai direct call")
    print("=" * 72)
    if model is None:
        print("  skipped (no model)")
        return
    try:
        from pydantic_ai import Agent
        a = Agent(model, system_prompt="Reply with exactly the word: OK")
        r = await a.run("Say hello.")
        print(f"  OK  output = {r.output!r}")
    except Exception as e:
        print(f"  FAIL  {type(e).__name__}: {e}")
        traceback.print_exc()


async def probe_classifier():
    print()
    print("=" * 72)
    print("STAGE 3  —  ClassificationAgent.classify() on a tiny PDF")
    print("=" * 72)
    try:
        from dpp_extractor.pipeline.classify import ClassificationAgent
        tmp = _make_tiny_pdf()
        print(f"  tiny PDF: {tmp} ({tmp.stat().st_size} bytes)")
        agent = ClassificationAgent()
        result = await agent.classify(tmp)
        print(f"  OK  result = {result!r}")
    except Exception as e:
        print(f"  FAIL  {type(e).__name__}: {e}")
        traceback.print_exc()


async def main():
    m = await probe_model_factory()
    await probe_pydantic_ai_direct(m)
    await probe_classifier()


asyncio.run(main())
