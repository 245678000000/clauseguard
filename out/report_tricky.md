# ClauseGuard scan report — tricky_en.txt

- Findings: **3** (rules 1 / local LLM 2)
- Highest severity: 🟠 high
- 42.1s · 1369 chars · model: local qwen3:4b

## Findings

### 1. 🟠 high one-sided termination `llm:one-sided termination`

> The Consultant shall permit the Client, at any time and without prior notice, to enter and inspect the Consultant's premises, records, and computer systems to verify compliance with this Agreement, and the Consultant shall bear all costs of such audits regardless of outcome

**Why it's risky**: Client can audit without notice and Consultant bears all costs regardless of audit outcome, which is one-sided and risks Consultant's financial exposure

**Suggested fix**: Require Client to pay for audits if they find non-compliance, or limit audit frequency to prevent abuse

### 2. 🟠 high one-sided termination `llm:one-sided termination`

> The Client may, at its option, require revisions after acceptance, which the Consultant shall perform at no additional charge

**Why it's risky**: Client can demand revisions post-acceptance without cost to Consultant, creating imbalance in control and cost

**Suggested fix**: Require explicit written notice for revision requests and limit to a reasonable number of revisions

### 3. 🟠 high Perpetual confidentiality obligation `rule:perpetual-nda`

> The Consultant grants the Client the right to use the Consultant's name, likeness, and testimonials in the Client's marketing materials in perpetuity, without approval, attribution, or compensation

**Why it's risky**: Trade secrets justify long protection, but a perpetual duty on ALL confidential info (not just trade secrets) is overbroad and unenforceable in several jurisdictions.

**Suggested fix**: Split the tail: 2-3 years for general confidential info, longer only for trade secrets.

> ⚠️ ClauseGuard is a reading aid, not legal advice. It can miss issues and flag harmless text. Have a qualified lawyer review anything important.
