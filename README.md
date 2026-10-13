# ClauseGuard 🔍

**Local-first, bilingual (English / 中文) contract risk scanner.** Drop in an NDA
or services agreement; get a severity-ranked risk report. Runs entirely on your
laptop: a deterministic rulebook for the classic traps, plus an open-weight LLM
(via [Ollama](https://ollama.com)) for the ones nobody wrote a rule for yet.

**No third-party Python dependencies. No cloud API. No telemetry. Nothing
leaves your machine** — which matters, because the document you most want
checked (an un-signed contract under negotiation) is exactly the document you
least want uploaded to a stranger's server.

```
$ clauseguard scan samples/risky_nda_zh.txt

ClauseGuard · risky_nda_zh.txt · 10 项发现
  🔴 critical [rule] 无上限赔偿责任 — 乙方违反本协议的，应赔偿甲方因此遭受的全部损失…
  🟠 high [rule] 知识产权归属过度让渡 — 乙方在协议有效期内产生的一切知识产权及成果…
  🟠 high [rule] 永久保密义务 — 本协议项下的保密义务为永久保密，不因本协议终止…
  ...
```

## Why I built this

I'm a law master's student who reviews NDAs and services agreements for
classmates and small studios — usually in Chinese, sometimes bilingual. The
same ten traps show up over and over (perpetual confidentiality, auto-renewal,
uncapped liability, IP over-assignment, 最终解释权…). Cloud "AI contract
review" services exist, but asking a freelancer to upload a *contested*
contract to one is a hard sell — confidentiality is the entire subject matter.

So the design constraint became the product: **the review has to run on the
same laptop the contract lives on, offline.**

## How it works: rules catch the known, the LLM catches the new

ClauseGuard deliberately does **not** just prompt a model and hope:

1. **Rulebook (deterministic, instant).** ~12 bilingual rule families
   (`clauseguard/rules.py`) match known one-sided patterns — unlimited
   liability, perpetual NDAs, evergreen renewal, sole-discretion termination,
   IP over-assignment, non-competes, blanket waivers, unilateral repricing,
   remote forum selection, 最终解释权, and more. Each rule carries a
   plain-language *why it's risky* and a *suggested redline*, in the contract's
   own language.
2. **Local LLM layer (Ollama, default `qwen3:4b`).** The contract is split
   into clauses and scanned in small batches — small open-weight models have
   far better recall on short spans than on a whole document. The model
   returns strict JSON findings.
3. **Verification + merge.** Every LLM quote is checked against the source
   text (whitespace-insensitive containment); anything the model invented is
   dropped — 4B-parameter models hallucinate quotes more than you'd like.
   LLM hits that merely repeat a rule catch are deduplicated. Findings are
   merged and sorted by severity.

### Honest measurements (2026-10-13, M-series MacBook, qwen3:4b)

| Sample | Rules-only | Hybrid (rules + local LLM) | Time |
|---|---|---|---|
| NDA with 9 classic planted traps (EN) | 9/9 caught | 9 (+0 new — rules had it) | rules: <1s · hybrid: ~80s |
| NDA with 10 classic planted traps (中文) | 10/10 caught | 10 | rules: <1s |
| Consulting excerpt with 5 *novel* traps (no rule covers them) | 1/5 | 2–3/5 per run | ~45s |

Read that third row honestly: a 4B local model misses novel traps and varies
run to run. That's exactly why the rulebook exists — the boring, checkable
80% is instant and deterministic, and the model is a second pair of eyes, not
an oracle.

## Quickstart

```bash
# 1) get Ollama and a small open-weight model
ollama pull qwen3:4b

# 2) no pip dependencies at all — just run it
git clone https://github.com/245678000000/clauseguard
cd clauseguard
python3 -m clauseguard.cli scan samples/risky_nda_en.txt -o report.md

# optional: install as a command
pip install -e .
clauseguard scan my_contract.txt --json     # machine-readable
clauseguard scan my_contract.txt --no-llm   # instant, rules only, fully offline
clauseguard rules                            # list the rulebook
```

Output: a terminal summary plus a Markdown report (severity emoji, verbatim
clause quote, why it's risky, suggested fix). `--json` for pipelines.

## What it will not do

- It is **not legal advice** — it's a reading aid that highlights what to
  argue about. Every report says so.
- It won't review your contract *for* the other side's perspective; findings
  are framed for the reviewing party.
- Numbers ("capped at 2× fees") still need a human. Rules match language, not
  economics.

## Roadmap

- [ ] Clause-level diff review ("what changed since the last draft?")
- [ ] Fine-tuning experiments (Tinker) for a dedicated clause classifier
- [ ] More rule families (payment traps, data processing addenda, CN labor)

## License

MIT. Sample contracts in `samples/` are synthetic and written for this project.

---

Built for the [Hacktoberfest 2026 DEV Challenge · Week 2: Side Hustle]
(https://dev.to/challenges/hacktoberfest-week2-2026-10-12).
