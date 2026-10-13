I review NDAs for classmates, so I built a contract-risk scanner that never lets the contract leave your laptop

---

It usually starts with a message at 11pm: "学长，帮我看看这个合同能签吗？" — *"can you take a quick look at this contract before I sign it tomorrow?"* Someone's first freelance gig, a studio hiring a friend as an editor, a startup sending an NDA before an interview. Nobody wants to pay a lawyer for a two-page NDA. Everybody signs anyway.

I'm a law master's student in China. After the thirtieth "quick look", I noticed I was running the same checklist every single time: Is confidentiality perpetual? Does it auto-renew? Is liability uncapped? Does their IP assignment quietly swallow my friend's background work? Does it end with 最终解释权归甲方所有 — "final interpretation belongs to Party A"?

So I automated myself. The result is **ClauseGuard**: a bilingual (English / 中文) contract risk scanner that runs entirely on your laptop. Zero third-party Python dependencies. No cloud API. No telemetry. The un-signed contract you're nervous about never leaves the machine it lives on.

```
$ clauseguard scan samples/risky_nda_zh.txt

ClauseGuard · risky_nda_zh.txt · 10 项发现
  🔴 critical [rule] 无上限赔偿责任 — 乙方违反本协议的，应赔偿甲方因此遭受的全部损失…
  🟠 high [rule] 知识产权归属过度让渡 — 乙方在协议有效期内产生的一切知识产权及成果…
  🟠 high [rule] 永久保密义务 — 本协议项下的保密义务为永久保密…
  ...
```

Repo: https://github.com/245678000000/clauseguard

## Why "local-only" isn't a feature here — it's the whole product

The obvious way to build this in 2026 is a wrapper around a frontier-model API. I deliberately didn't, and the reason is the document itself: **the contract under negotiation is the one document you're least able to upload anywhere.** An NDA about your confidential information, uploaded in plaintext to a third-party server, is a self-defeating act. My classmates and the freelancers I help would be right to say no.

That constraint pushed every design decision:

- **Runs offline.** `ollama pull qwen3:4b` and you're done. Airplane mode works. I know, because I tested it on a plane.
- **Costs nothing per contract.** A 4B open-weight model on a laptop is free forever. A "side hustle" tool for people who won't pay ¥500 for a lawyer review can't have a per-document API bill.
- **Swappable models.** The LLM layer takes any Ollama model. `--model llama3.1:8b` if you want more recall, `--no-llm` if you want instant rulebook-only scanning.
- **Zero pip dependencies.** The whole tool is Python stdlib + a local Ollama HTTP call. If your "privacy tool" needs 40 packages, you've already lost the thread.

A closed API could do the fancy parts better in isolation. It can't do *this* — keep a contested contract inside the counterparty-free zone of one laptop.

## The architecture: rules catch the known, the LLM catches the new

Prompting a small model with "find the risks" produces vibes, not review. So ClauseGuard is a hybrid where each layer does what it's actually good at:

**1. A deterministic rulebook.** Twelve bilingual rule families (uncapped liability, perpetual confidentiality, evergreen renewal, sole-discretion termination, IP over-assignment, non-competes, blanket waivers, unilateral repricing, remote forum selection, 最终解释权, …). Each rule carries a plain-language *why-it's-risky* and a *suggested redline*, rendered in whichever language the contract is written in. Instant, testable, explainable.

**2. A local LLM second pass.** The contract is split into clauses and scanned in small batches — this mattered a lot: a 4B model's recall on short spans is far better than on a whole document at once. The model returns strict JSON.

**3. Verification before you ever see a finding.** Every quote the model returns is checked against the source text, whitespace-insensitively. If the model invented a clause, the finding is dropped. Then LLM hits that merely repeat a rulebook catch are deduplicated, and everything is merged into one severity-ranked report.

## The honest benchmark (and why I kept the embarrassing row)

On synthetic NDAs with planted traps, measured on my M-series MacBook:

| Sample | Rulebook only | Hybrid (rules + local 4B) | Time |
|---|---|---|---|
| NDA with 9 classic traps (EN) | 9/9 caught | 9 (+0 new — the rules had it all) | rules: <1s · hybrid: ~80s |
| NDA with 10 classic traps (中文) | 10/10 caught | 10 | rules: <1s |
| Consulting excerpt with 5 *novel* traps no rule covers | 1/5 | 2–3/5 per run | ~45s |

Read the third row the way I had to: a 4B open-weight model, running locally and privately, **misses novel traps and varies run to run.** That's not a reason to hide it — it's the reason the architecture looks like this. The boring 80% of contract risk is checkable patterns; that belongs in deterministic code that costs nothing and never gets creative. The model is a second pair of eyes for the clause nobody wrote a rule for yet, not an oracle.

## Three bugs that taught me more than the happy path

**The newline that split a sentence in half.** My clause splitter treated newlines as clause boundaries — but contracts come hard-wrapped. "All inventions… intellectual property / conceived by the Party, whether or not related…" became two clauses, and the IP-over-assignment rule matched neither. Fix: normalize newlines before splitting. Obvious in hindsight; invisible in the demo until it wasn't.

**The model that invented a quote.** One run flagged a clause — with a quote that appears nowhere in the document. A 4B model will confidently fabricate "The Client shall pay all fees and costs…" in perfectly plausible legalese. That's why quote verification isn't a nice-to-have bolted on later; for small local models it's load-bearing. Anything unverifiable gets dropped, silently, before it reaches the report.

**The dedupe that was too smart.** My first duplicate filter used a fuzzy n-gram window — and generic legal phrases ("theconsultant…") are shared by every clause in every contract. It quietly deleted *real* LLM findings as "duplicates" of rule catches. The scanner looked calm and merged; underneath, the LLM layer was contributing nothing. I only caught it because a sample that should have produced LLM findings produced zero. The fix is dumber and better: one quote only counts as a duplicate if it's contained in the other.

That last one is the lesson I'd keep: **in a privacy tool, every silent failure is invisible by design.** Your user can't check whether the cloud call happened. So the tool has to be loudly honest in its outputs — measured recall, dropped findings, "not legal advice" on every report.

## Who pays for this? (the side-hustle question)

Not lawyers — they have associates. The people who actually ask me at 11pm:

- **Freelancers and student collaborators** signing their first NDAs and services agreements (¥0 today; they sign blind);
- **Small studios** hiring part-time editors/developers, who want a first-pass filter before paying for real counsel;
- **Career-service and incubator communities**, as the world's most honest lead magnet: scan it free, local, offline — then talk to a human when it matters.

The model that makes sense to me: the scanner is free and open forever (that's the trust engine), and what could eventually be paid is the human layer — a review service where you *choose* to hand the contract to a law student like me, with the machine having already highlighted the fight list. ClauseGuard is the first 80%; I'm the other 20%. I've already been that 20% for thirty classmates. The tool just stops me from re-reading for the thirty-first time.

## Try it

```bash
ollama pull qwen3:4b
git clone https://github.com/245678000000/clauseguard
cd clauseguard
python3 -m clauseguard.cli scan samples/risky_nda_en.txt -o report.md
```

`--no-llm` for the instant offline rulebook pass, `--json` for pipelines, `clauseguard rules` to read the rulebook. 中文样本 included (`samples/risky_nda_zh.txt`). MIT licensed; the samples are synthetic.

**Not legal advice** — it's a reading aid that tells you what to argue about. Every report it prints says so, and so do I.

Next on the roadmap: fine-tuning a dedicated clause classifier on [Tinker](https://thinkingmachines.ai/tinker/) to push that third benchmark row up, clause-diff review between drafts, and more CN-specific traps (劳动争议, data processing addenda).

---

*Transparency: I built this pair-programming with an AI agent (the full repo history shows the commits, including the three bugs above and their fixes). The design decisions, the legal judgment baked into the rulebook, and every claim in this post are mine and verified on my machine. The benchmark numbers are from 2026-10-13 on an M-series MacBook with qwen3:4b — your mileage will vary, honestly.*
