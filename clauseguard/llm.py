"""Local-LLM layer: Ollama chat API, zero third-party dependencies.

Uses only the Python standard library so the tool can run on an air-gapped
laptop with `ollama serve` on localhost — nothing is sent anywhere else.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

DEFAULT_MODEL = "qwen3:4b"
OLLAMA_URL = "http://127.0.0.1:11434"

SYSTEM_PROMPT = """You are a meticulous contract-review assistant embedded in a
local tool. You read a confidentiality agreement or service contract clause by
clause and flag clauses that are risky or one-sided for the reviewing party.

Return STRICT JSON only: a single ARRAY (if there is exactly one risk, return
an array containing that one object; if none, return []). No markdown, no
commentary. Each element:
{"type": "<short risk label, same language as the clause>",
 "severity": <1-5 integer>,
 "quote": "<exact short excerpt from the input, max ~25 words>",
 "why": "<one or two sentences, plain language, same language as the clause>",
 "fix": "<one concrete redline suggestion>"}

Rules:
- Only quote text that appears verbatim in the input.
- Focus on: uncapped liability, perpetual obligations, auto-renewal, one-sided
  termination/modification, IP over-assignment, non-compete scope, blanket
  waivers, unilateral pricing, forum traps, and anything grossly unbalanced.
- Ignore boilerplate that is normal and balanced.
- If nothing is risky, return [].
"""

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


class LLMError(RuntimeError):
    pass


def _strip_think(text: str) -> str:
    return _THINK_RE.sub("", text).strip()


def chat(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    url: str = OLLAMA_URL,
    timeout: int = 120,
) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt + "\n\n/no_think"},
        ],
        "stream": False,
        "format": "json",
        "think": False,
        "options": {"temperature": 0.1, "num_ctx": 8192, "num_predict": 1024},
    }
    req = urllib.request.Request(
        f"{url.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        raise LLMError(
            f"cannot reach Ollama at {url} ({e}). Is `ollama serve` running?"
        ) from e
    except json.JSONDecodeError as e:
        raise LLMError(f"Ollama returned non-JSON output: {e}") from e
    if "error" in data:
        raise LLMError(str(data["error"]))
    return _strip_think(data.get("message", {}).get("content", ""))


def _parse_findings(raw: str) -> list[dict]:
    raw = raw.strip()
    # model was asked for a bare array via format=json; Ollama guarantees an
    # object, so accept both {"findings": [...]}-style and bare arrays.
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, dict):
        for key in ("findings", "risks", "result", "items", "array"):
            if isinstance(parsed.get(key), list):
                parsed = parsed[key]
                break
        else:
            # a single bare finding object {"type": .., "quote": .., ...}
            if parsed.get("quote") and parsed.get("why"):
                parsed = [parsed]
            else:
                parsed = []
    out = []
    if isinstance(parsed, list):
        for item in parsed:
            if not isinstance(item, dict):
                continue
            if not item.get("quote") or not item.get("why"):
                continue
            try:
                sev = max(1, min(5, int(item.get("severity", 2))))
            except (TypeError, ValueError):
                sev = 2
            out.append(
                {
                    "type": str(item.get("type", "risk"))[:80],
                    "severity": sev,
                    "quote": str(item["quote"])[:600],
                    "why": str(item["why"])[:1000],
                    "fix": str(item.get("fix", ""))[:1000],
                    "source": "llm",
                }
            )
    return out


def scan_text(
    text: str,
    *,
    model: str = DEFAULT_MODEL,
    url: str = OLLAMA_URL,
    clauses_per_call: int = 3,
    max_clause_chars: int = 800,
) -> list[dict]:
    """Scan contract text clause-group by clause-group.

    Small open-weight models have much better recall on short spans, so we
    batch a few clauses per call instead of feeding the whole contract.
    """
    import re

    findings: list[dict] = []
    text = text.strip()
    if not text:
        return findings

    normalized = text.replace("\r", " ").replace("\n", " ")
    clauses = [
        c.strip()[:max_clause_chars]
        for c in re.split(r"[。；;.!？?]+", normalized)
        if len(c.strip()) >= 12
    ]
    batches = [
        clauses[i : i + clauses_per_call]
        for i in range(0, len(clauses), clauses_per_call)
    ]
    for idx, batch in enumerate(batches, 1):
        numbered = "\n".join(f"[{j}] {c}" for j, c in enumerate(batch, 1))
        prompt = (
            f"Contract clauses {idx * len(batch) - len(batch) + 1}.."
            f"{idx * len(batch)} of {len(clauses)}:\n\n{numbered}\n\n"
            "Identify EVERY clause above that is risky or one-sided for the "
            "reviewing party. Typically 0-2 per batch. Quote from the clause text."
        )
        raw = None
        for attempt in (1, 2):  # one retry, then skip the batch
            try:
                raw = chat(prompt, model=model, url=url)
                break
            except LLMError:
                if attempt == 2:
                    raw = None
            except (TimeoutError, OSError):
                if attempt == 2:
                    raw = None
        if raw is None:
            continue
        findings.extend(_parse_findings(raw))
    # drop duplicate quotes across batches
    seen: set[str] = set()
    unique = []
    for f in findings:
        key = f["quote"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)
    # small models sometimes invent quotes: keep only quotes locatable in the
    # source text (whitespace-insensitive containment with alnum fallback)
    norm_text = " ".join(text.split()).lower()
    norm_alnum = "".join(ch for ch in norm_text if ch.isalnum())
    verified = []
    for f in unique:
        q_norm = " ".join(f["quote"].split()).lower()
        q_alnum = "".join(ch for ch in q_norm if ch.isalnum())
        # short generic quotes at low severity are usually noise
        if len(q_alnum) < 40 and f["severity"] < 4:
            continue
        if q_norm and q_norm in norm_text:
            f["quote_verified"] = True
            verified.append(f)
        elif len(q_alnum) >= 20 and q_alnum in norm_alnum:
            f["quote_verified"] = True
            verified.append(f)
        else:
            f["quote_verified"] = False
    return verified


def server_ok(url: str = OLLAMA_URL) -> bool:
    try:
        with urllib.request.urlopen(f"{url.rstrip('/')}/api/tags", timeout=5) as r:
            return r.status == 200
    except Exception:
        return False
