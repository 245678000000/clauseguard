"""Scanner: merge deterministic rule hits with local-LLM findings."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from . import llm, rules

CLAUSE_SPLIT_RE_STR = r"[。；;.!？?\n]+"


@dataclass
class Finding:
    source: str  # "rule" | "llm"
    rule_id: str  # rule id or llm type label
    category: str
    severity: int
    name: str  # rule name_en/name_zh chosen by language, or llm type
    quote: str
    why: str
    fix: str
    clause_index: int | None = None

    def as_dict(self) -> dict:
        return {
            "source": self.source,
            "rule": self.rule_id,
            "category": self.category,
            "severity": self.severity,
            "name": self.name,
            "quote": self.quote,
            "why": self.why,
            "fix": self.fix,
            "clause": self.clause_index,
        }


@dataclass
class ScanResult:
    findings: list[Finding] = field(default_factory=list)
    lang: str = "en"
    model: str | None = None
    llm_used: bool = False
    llm_error: str | None = None
    duration_s: float = 0.0
    text_length: int = 0

    def summary(self) -> dict:
        by_sev: dict[int, int] = {}
        for f in self.findings:
            by_sev[f.severity] = by_sev.get(f.severity, 0) + 1
        return {
            "total": len(self.findings),
            "rule_findings": sum(1 for f in self.findings if f.source == "rule"),
            "llm_findings": sum(1 for f in self.findings if f.source == "llm"),
            "by_severity": {str(k): v for k, v in sorted(by_sev.items(), reverse=True)},
            "max_severity": max((f.severity for f in self.findings), default=0),
        }


def detect_language(text: str) -> str:
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return "zh" if cjk > len(text) * 0.08 else "en"


def split_clauses(text: str) -> list[str]:
    import re

    # hard-wrapped text: treat newlines as spaces so sentences stay whole
    normalized = text.replace("\r", " ").replace("\n", " ")
    parts = re.split(CLAUSE_SPLIT_RE_STR, normalized)
    return [p.strip() for p in parts if p.strip()]


def rule_scan(text: str, lang: str) -> list[Finding]:
    clauses = split_clauses(text)
    findings: list[Finding] = []
    for rule in rules.RULES:
        for i, clause in enumerate(clauses):
            hit = any(p.search(clause) for p in rule.patterns)
            if hit:
                if lang == "zh":
                    name, why, fix = rule.name_zh, rule.why_zh, rule.fix_zh
                else:
                    name, why, fix = rule.name_en, rule.why_en, rule.fix_en
                findings.append(
                    Finding(
                        source="rule",
                        rule_id=rule.id,
                        category=rule.category,
                        severity=rule.severity,
                        name=name,
                        quote=clause[:400],
                        why=why,
                        fix=fix,
                        clause_index=i,
                    )
                )
    return findings


def _quotes_overlap(a: str, b: str) -> bool:
    """Containment-only check used to drop LLM hits a rule already caught.

    Fuzzy n-gram windows false-positive on generic legal phrasing, so we only
    treat one quote as a duplicate of another when one contains the other.
    """
    a_c = "".join(ch for ch in a.lower() if ch.isalnum())
    b_c = "".join(ch for ch in b.lower() if ch.isalnum())
    if not a_c or not b_c:
        return False
    shorter, longer = (a_c, b_c) if len(a_c) <= len(b_c) else (b_c, a_c)
    return len(shorter) >= 12 and shorter in longer


def scan(
    text: str,
    *,
    use_llm: bool = True,
    model: str = llm.DEFAULT_MODEL,
    url: str = llm.OLLAMA_URL,
) -> ScanResult:
    start = time.time()
    lang = detect_language(text)
    result = ScanResult(lang=lang, text_length=len(text))

    rule_findings = rule_scan(text, lang)
    result.findings.extend(rule_findings)

    if use_llm:
        if llm.server_ok(url):
            try:
                llm_findings = llm.scan_text(text, model=model, url=url)
                result.llm_used = True
                result.model = model
                for item in llm_findings:
                    f = Finding(
                        source="llm",
                        rule_id=item["type"],
                        category="llm",
                        severity=item["severity"],
                        name=item["type"],
                        quote=item["quote"],
                        why=item["why"],
                        fix=item["fix"],
                    )
                    # skip LLM hits that merely repeat a rule catch
                    if any(_quotes_overlap(f.quote, r.quote) for r in rule_findings):
                        continue
                    result.findings.append(f)
            except llm.LLMError as e:
                result.llm_error = str(e)  # degrade gracefully to rules-only
        else:
            result.llm_error = f"Ollama not reachable at {url}; rules-only scan"

    result.findings.sort(key=lambda f: (-f.severity, f.source, f.rule_id))
    result.duration_s = round(time.time() - start, 1)
    return result
