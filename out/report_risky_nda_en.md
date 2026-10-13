# ClauseGuard scan report — risky_nda_en.txt

- Findings: **9** (rules 9 / local LLM 0)
- Highest severity: 🔴 critical
- 78.2s · 2793 chars · model: local qwen3:4b

## Findings

### 1. 🔴 critical Unlimited / uncapped liability `rule:unlimited-liability`

> The Receiving Party shall be liable for any and all losses, damages, and costs arising from any breach of this Agreement, without limitation

**Why it's risky**: One party bears uncapped damages. In a negotiated NDA, liability is usually capped at a fixed amount or at fees paid under the agreement.

**Suggested fix**: Cap liability (e.g. 'aggregate liability shall not exceed USD ___').

### 2. 🟠 high Blanket waiver of rights `rule:blanket-waiver`

> The Receiving Party irrevocably waives any and all claims and rights against the Disclosing Party arising from or related to this Agreement

**Why it's risky**: Signing away unknown future claims (including for breach or IP infringement) is rarely justified in an ordinary NDA.

**Suggested fix**: Waive only claims that have actually arisen and are identified in the agreement.

### 3. 🟠 high IP assignment overreach `rule:ip-assignment-overreach`

> All inventions, works, and intellectual property conceived by the Receiving Party during the term of this Agreement, whether or not related to the Purpose or based on the Confidential Information, shall be the sole and exclusive property of the Disclosing Party, including all background intellectual property previously developed by the Receiving Party

**Why it's risky**: Sweeping assignment can swallow your pre-existing IP and unrelated future work, not just deliverables under this contract.

**Suggested fix**: Limit assignment to work product 'developed specifically under this agreement'; carve out background IP.

### 4. 🟠 high Perpetual confidentiality obligation `rule:perpetual-nda`

> The confidentiality obligations under this Agreement shall remain in effect indefinitely and shall survive in perpetuity following the termination of this Agreement for any reason

**Why it's risky**: Trade secrets justify long protection, but a perpetual duty on ALL confidential info (not just trade secrets) is overbroad and unenforceable in several jurisdictions.

**Suggested fix**: Split the tail: 2-3 years for general confidential info, longer only for trade secrets.

### 5. 🟠 high One-sided termination / sole discretion `rule:sole-discretion`

> The Disclosing Party may terminate this Agreement at any time in its sole discretion without notice or liability

**Why it's risky**: The counterparty can walk away or rewrite the deal at will, while you remain bound — a classic asymmetry.

**Suggested fix**: Make termination mutual, or add notice periods and cost-reimbursement on convenience termination.

### 6. 🟡 medium Automatic renewal (evergreen clause) `rule:auto-renewal`

> Thereafter, this Agreement shall automatically renew for successive one (1) year periods unless either party provides written notice of non-renewal at least ninety (90) days prior to the expiration of the then-current term

**Why it's risky**: The term renews silently unless you remember to opt out by a deadline; missing it locks you in for another full cycle.

**Suggested fix**: Require affirmative written renewal, or a short renewal cycle with a clear notice window.

### 7. 🟡 medium Non-compete / restrictive covenant `rule:non-compete`

> The Receiving Party shall not engage in any business competitive with the Disclosing Party during the term of this Agreement and for a period of five (5) years thereafter, in any territory worldwide

**Why it's risky**: In an employment context (mainland China), non-compete is capped at 2 years and requires monthly compensation; in commercial contracts it can be broader but must stay reasonable in scope, area and time.

**Suggested fix**: Narrow scope/time/territory; in employment, check statutory caps and compensation.

### 8. 🟡 medium Unilateral price/fee change `rule:unilateral-price`

> The Disclosing Party reserves the right to adjust fees or charges associated with the Purpose at its sole discretion and without prior notice

**Why it's risky**: The counterparty can raise costs mid-term while you are still bound by the rest of the deal.

**Suggested fix**: Lock pricing for the initial term; allow changes only at renewal with an exit right.

### 9. 🔵 low Forum selection to the counterparty's home court `rule:remote-jurisdiction`

> This Agreement shall be governed by the laws of the State of Delaware, and the parties submit to the exclusive jurisdiction of the courts of Wilmington, Delaware

**Why it's risky**: Litigating far from home multiplies cost and delay. Check whether the chosen forum has a real connection to the deal.

**Suggested fix**: Prefer neutral arbitration (e.g. CIETAC/HKIAC/SIAC) or defendant's domicile courts.

> ⚠️ ClauseGuard is a reading aid, not legal advice. It can miss issues and flag harmless text. Have a qualified lawyer review anything important.
