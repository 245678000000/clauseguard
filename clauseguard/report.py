"""Markdown report rendering."""

from __future__ import annotations

from .scanner import ScanResult

SEV_LABEL = {5: "🔴 critical", 4: "🟠 high", 3: "🟡 medium", 2: "🔵 low", 1: "⚪ note"}

DISCLAIMER_EN = (
    "> ⚠️ ClauseGuard is a reading aid, not legal advice. It can miss issues and "
    "flag harmless text. Have a qualified lawyer review anything important."
)
DISCLAIMER_ZH = (
    "> ⚠️ ClauseGuard 是阅读辅助工具，不构成法律意见。它可能漏报或误报，"
    "重要文件请交由执业律师审查。"
)


def render(result: ScanResult, source_name: str = "contract") -> str:
    zh = result.lang == "zh"
    lines: list[str] = []
    title = "ClauseGuard 扫描报告" if zh else "ClauseGuard scan report"
    lines.append(f"# {title} — {source_name}")
    lines.append("")

    s = result.summary()
    if zh:
        lines.append(
            f"- 条款总数级发现：**{s['total']}**（规则引擎 {s['rule_findings']} / "
            f"本地模型 {s['llm_findings']}）"
        )
        lines.append(f"- 最高风险等级：{SEV_LABEL.get(s['max_severity'], '—')}")
        lines.append(
            f"- 用时 {result.duration_s}s · 文本 {result.text_length} 字符 · "
            f"模型：{'本地 ' + str(result.model) if result.llm_used else '未启用（仅规则引擎）'}"
        )
    else:
        lines.append(
            f"- Findings: **{s['total']}** (rules {s['rule_findings']} / "
            f"local LLM {s['llm_findings']})"
        )
        lines.append(f"- Highest severity: {SEV_LABEL.get(s['max_severity'], '—')}")
        lines.append(
            f"- {result.duration_s}s · {result.text_length} chars · model: "
            f"{'local ' + str(result.model) if result.llm_used else 'off (rules only)'}"
        )
    lines.append("")

    sev_title = "风险条款" if zh else "Findings"
    lines.append(f"## {sev_title}")
    lines.append("")
    for i, f in enumerate(result.findings, 1):
        lines.append(
            f"### {i}. {SEV_LABEL.get(f.severity, '⚪')} {f.name} "
            f"`{f.source}:{f.rule_id}`"
        )
        lines.append("")
        lines.append(f"> {f.quote}")
        lines.append("")
        why_label = "为什么有风险" if zh else "Why it's risky"
        fix_label = "修改建议" if zh else "Suggested fix"
        lines.append(f"**{why_label}**: {f.why}")
        lines.append("")
        if f.fix:
            lines.append(f"**{fix_label}**: {f.fix}")
            lines.append("")
    lines.append(DISCLAIMER_ZH if zh else DISCLAIMER_EN)
    lines.append("")
    return "\n".join(lines)


def render_terminal(result: ScanResult, source_name: str) -> str:
    """Compact single-line-per-finding output for terminals."""
    zh = result.lang == "zh"
    out = []
    head = f"ClauseGuard · {source_name}" + (
        f" · {result.summary()['total']} 项发现"
        if zh
        else f" · {result.summary()['total']} findings"
    )
    out.append(head)
    for f in result.findings:
        out.append(
            f"  {SEV_LABEL.get(f.severity, '⚪')} [{f.source}] {f.name} — "
            f"{f.quote[:80]}{'…' if len(f.quote) > 80 else ''}"
        )
    out.append(DISCLAIMER_ZH if zh else DISCLAIMER_EN)
    return "\n".join(out)
