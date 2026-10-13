# ClauseGuard scan report — tricky_en.txt

- Findings: **2** (rules 1 / local LLM 1)
- Highest severity: 🟠 high
- 103.4s · 1369 chars · model: local qwen3:4b

## Findings

### 1. 🟠 high risky `llm:risky`

> The Consultant shall permit the Client, at any time and without prior notice, to enter and inspect the Consultant's premises, records, and computer systems to verify compliance with this Agreement, and the Consultant shall bear all costs of such audits regardless of outcome

**Why it's risky**: Client can audit without notice and Consultant bears all costs regardless of outcome, which is one-sided and risks consultant's privacy and financial burden

**Suggested fix**: Require Consultant to have reasonable notice before audits and limit audit costs to a reasonable amount

### 2. 🟠 high Perpetual confidentiality obligation `rule:perpetual-nda`

> The Consultant grants the Client the right to use the Consultant's name, likeness, and testimonials in the Client's marketing materials in perpetuity, without approval, attribution, or compensation

**Why it's risky**: Trade secrets justify long protection, but a perpetual duty on ALL confidential info (not just trade secrets) is overbroad and unenforceable in several jurisdictions.

**Suggested fix**: Split the tail: 2-3 years for general confidential info, longer only for trade secrets.

> ⚠️ ClauseGuard is a reading aid, not legal advice. It can miss issues and flag harmless text. Have a qualified lawyer review anything important.
