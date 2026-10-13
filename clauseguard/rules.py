"""Bilingual rule engine: deterministic pattern checks for known risky clauses.

Each rule pairs an English and a Chinese pattern set so the same tool works on
contracts drafted in either language (or mixed, which is common in
cross-border NDAs reviewed in mainland China and Hong Kong).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Rule:
    id: str
    category: str
    severity: int  # 1 (note) .. 5 (red flag)
    name_en: str
    name_zh: str
    patterns: list[re.Pattern] = field(default_factory=list)
    why_en: str = ""
    why_zh: str = ""
    fix_en: str = ""
    fix_zh: str = ""


def _p(*texts: str) -> list[re.Pattern]:
    return [re.compile(t, re.IGNORECASE) for t in texts]


RULES: list[Rule] = [
    Rule(
        id="unlimited-liability",
        category="liability",
        severity=5,
        name_en="Unlimited / uncapped liability",
        name_zh="无上限赔偿责任",
        patterns=_p(
            r"unlimited\s+liabilit",
            r"(liable|liability)\b.{0,60}any\s+and\s+all\s+(losses|damages|costs)",
            r"any\s+and\s+all\s+(losses|damages|costs).{0,40}liabilit",
            r"liable.{0,120}without\s+limitation",
            r"不设上限.{0,12}赔偿",
            r"赔偿.{0,20}(全部|一切).{0,6}(损失|损害)",
        ),
        why_en="One party bears uncapped damages. In a negotiated NDA, liability is "
        "usually capped at a fixed amount or at fees paid under the agreement.",
        why_zh="一方承担无上限赔偿。协商型保密协议中，赔偿责任通常应设上限"
        "（固定金额或本协议项下已付费用）。",
        fix_en="Cap liability (e.g. 'aggregate liability shall not exceed USD ___').",
        fix_zh="增加赔偿上限条款，如「累计赔偿以人民币____元为限」。",
    ),
    Rule(
        id="joint-several",
        category="liability",
        severity=4,
        name_en="Joint and several liability",
        name_zh="连带责任",
        patterns=_p(r"joint(ly)?\s+and\s+severall", r"连带责任", r"承担连带"),
        why_en="You can be pursued for 100% of a loss caused by multiple parties, "
        "including your employees, advisors or affiliates.",
        why_zh="你可能需为他人（员工、顾问、关联方）造成的全部损失先行买单，"
        "事后追偿困难。",
        fix_en="Narrow it to your own acts and those of people under your direct control.",
        fix_zh="将连带范围限于自身及直接控制人员的过错行为。",
    ),
    Rule(
        id="perpetual-nda",
        category="term",
        severity=4,
        name_en="Perpetual confidentiality obligation",
        name_zh="永久保密义务",
        patterns=_p(
            r"in\s+perpetuit",
            r"(remain|survive|continue).{0,30}(indefinitely|in\s+perpetuity)",
            r"(perpetual|everlasting)\s+(confidential|obligation)",
            r"永久保密",
            r"无限期.{0,8}保密",
        ),
        why_en="Trade secrets justify long protection, but a perpetual duty on ALL "
        "confidential info (not just trade secrets) is overbroad and unenforceable "
        "in several jurisdictions.",
        why_zh="仅商业秘密可要求长期保护；对全部保密信息施加永久义务过宽，"
        "在多地司法辖区难以执行。",
        fix_en="Split the tail: 2-3 years for general confidential info, longer only "
        "for trade secrets.",
        fix_zh="区分处理：一般保密信息 2-3 年，商业秘密可更长。",
    ),
    Rule(
        id="auto-renewal",
        category="term",
        severity=3,
        name_en="Automatic renewal (evergreen clause)",
        name_zh="自动续期条款",
        patterns=_p(
            r"automatic(ally)?\s+renew",
            r"auto[-\s]?renew",
            r"evergreen",
            r"自动续(期|约|签)",
            r"视为续期",
        ),
        why_en="The term renews silently unless you remember to opt out by a deadline; "
        "missing it locks you in for another full cycle.",
        why_zh="到期未及时书面反对即自动续约，容易在不知情中被锁入下一个周期。",
        fix_en="Require affirmative written renewal, or a short renewal cycle with a "
        "clear notice window.",
        fix_zh="改为书面续签，或缩短续期周期并明确提前通知窗口。",
    ),
    Rule(
        id="sole-discretion",
        category="termination",
        severity=4,
        name_en="One-sided termination / sole discretion",
        name_zh="单方任意解除",
        patterns=_p(
            r"(terminat\w+|modif\w+|suspend\w+|amend\w+).{0,60}sole\s+discretion",
            r"sole\s+discretion.{0,60}(terminat\w+|modif\w+|suspend\w+|amend\w+)",
            r"单方(随时)?(解除|终止|变更|修改)",
            r"有权(随时)?(解除|终止).{0,10}且.{0,10}(无需|不承担)",
        ),
        why_en="The counterparty can walk away or rewrite the deal at will, while you "
        "remain bound — a classic asymmetry.",
        why_zh="对方可随时退出或改约而你不受对等保护，属典型失衡条款。",
        fix_en="Make termination mutual, or add notice periods and cost-reimbursement "
        "on convenience termination.",
        fix_zh="改为对等解除权，或任意解除时附加通知期与费用补偿。",
    ),
    Rule(
        id="liquidated-damages",
        category="liability",
        severity=3,
        name_en="Liquidated damages clause (check the amount)",
        name_zh="违约金条款（核对金额）",
        patterns=_p(r"liquidated\s+damages", r"违约金", r"定金.{0,20}%"),
        why_en="Liquidated damages are fine in principle, but an amount far above "
        "foreseeable loss can be reduced by courts — or signal a Draconian counterparty.",
        why_zh="违约金本身合法，但过分高于实际损失的部分法院可调减；金额过高也"
        "提示对方可能滥用索赔。",
        fix_en="Benchmark the amount to realistic loss; add a mutual cap.",
        fix_zh="违约金与可预见损失挂钩，并设双向上限。",
    ),
    Rule(
        id="ip-assignment-overreach",
        category="ip",
        severity=4,
        name_en="IP assignment overreach",
        name_zh="知识产权归属过度让渡",
        patterns=_p(
            r"(all|any)\s+(inventions?|works?|intellectual\s+property).{0,200}"
            r"(whether\s+or\s+not|regardless\s+of)",
            r"background\s+intellectual\s+property.{0,120}(assign|transfer|property\s+of|owned\s+by)",
            r"(一切|全部).{0,8}(知识产权|成果|技术).{0,12}(归|属于)\s*(甲方|对方|公司)",
            r"无论是否.{0,10}(相关|利用).{0,20}(均归|皆归)",
        ),
        why_en="Sweeping assignment can swallow your pre-existing IP and unrelated "
        "future work, not just deliverables under this contract.",
        why_zh="全量转让可能吞掉你在先知识产权及与本合同无关的未来成果。",
        fix_en="Limit assignment to work product 'developed specifically under this "
        "agreement'; carve out background IP.",
        fix_zh="转让限于「为本合同专门开发」的成果，明确排除在先知识产权。",
    ),
    Rule(
        id="non-compete",
        category="restrictive",
        severity=3,
        name_en="Non-compete / restrictive covenant",
        name_zh="竞业限制条款",
        patterns=_p(
            r"non[-\s]?compet",
            r"shall\s+not.{0,80}business\s+competit",
            r"compet\w+\s+with\s+the\s+(disclosing|other)\s+party",
            r"restrictive\s+covenant",
            r"竞业(限制|禁止)",
            r"不得.{0,15}(从事|参与|投资).{0,20}(竞争|相同|类似).{0,8}(业务|行业)",
        ),
        why_en="In an employment context (mainland China), non-compete is capped at "
        "2 years and requires monthly compensation; in commercial contracts it can "
        "be broader but must stay reasonable in scope, area and time.",
        why_zh="劳动语境下竞业限制不得超过二年且需按月补偿；商事合同中的竞业"
        "条款也须在范围、地域、期限上合理。",
        fix_en="Narrow scope/time/territory; in employment, check statutory caps and "
        "compensation.",
        fix_zh="收窄范围/期限/地域；劳动场景核对法定上限与补偿。",
    ),
    Rule(
        id="unilateral-price",
        category="payment",
        severity=3,
        name_en="Unilateral price/fee change",
        name_zh="单方调价权",
        patterns=_p(
            r"(adjust|modify|change|increase).{0,40}(fees?|price|charges).{0,60}"
            r"(sole\s+discretion|without\s+(your\s+)?consent|prior\s+notice)",
            r"单方(调整|上调|变更).{0,10}(价格|费用|费率)",
            r"有权(调整|变更).{0,10}(价格|费用).{0,15}(无需|不经).{0,6}(同意|通知)",
        ),
        why_en="The counterparty can raise costs mid-term while you are still bound "
        "by the rest of the deal.",
        why_zh="合同期内对方可单方涨价，而你的其他义务不变。",
        fix_en="Lock pricing for the initial term; allow changes only at renewal with "
        "an exit right.",
        fix_zh="首期内锁价；调价仅限续约时并附退出权。",
    ),
    Rule(
        id="remote-jurisdiction",
        category="dispute",
        severity=2,
        name_en="Forum selection to the counterparty's home court",
        name_zh="异地管辖条款",
        patterns=_p(
            r"exclusive\s+jurisdiction\s+of\s+the\s+courts?\s+of",
            r"任何争议.{0,40}(均|应|应当).{0,10}(提交|由).{0,20}(法院|仲裁).{0,20}(管辖|仲裁)",
            r"(提交|由).{0,15}(甲方|对方|公司)(所在地)?.{0,10}(法院|仲裁)",
        ),
        why_en="Litigating far from home multiplies cost and delay. Check whether the "
        "chosen forum has a real connection to the deal.",
        why_zh="异地诉讼/仲裁显著抬高维权成本，应核查管辖地与合同是否有实际连接点。",
        fix_en="Prefer neutral arbitration (e.g. CIETAC/HKIAC/SIAC) or defendant's "
        "domicile courts.",
        fix_zh="争取中立仲裁机构（贸仲/港仲/新仲）或被告住所地法院。",
    ),
    Rule(
        id="blanket-waiver",
        category="waiver",
        severity=4,
        name_en="Blanket waiver of rights",
        name_zh="概括性权利放弃",
        patterns=_p(
            r"(irrevocably\s+)?waive\w*.{0,30}(any\s+and\s+all|all)\s+(claims?|rights?|remedies?)",
            r"放弃.{0,8}(一切|全部|所有).{0,8}(权利|索赔|异议)",
            r"免除.{0,12}(甲方|对方|公司).{0,12}(一切|全部).{0,8}责任",
        ),
        why_en="Signing away unknown future claims (including for breach or IP "
        "infringement) is rarely justified in an ordinary NDA.",
        why_zh="概括放弃未来索赔（含违约与侵权）在普通保密协议中缺乏正当性。",
        fix_en="Waive only claims that have actually arisen and are identified in the "
        "agreement.",
        fix_zh="仅限于已发生且列明的具体请求。",
    ),
    Rule(
        id="final-interpretation",
        category="adhesion",
        severity=3,
        name_en="'Final interpretation' reservation (CN adhesion term)",
        name_zh="「最终解释权」条款",
        patterns=_p(r"最终解释权.{0,10}(归|属于|保留)", r"保留.{0,6}最终解释权"),
        why_en="A 'we keep the final say' reservation is void under mainland China's "
        "standard-terms rules (Civil Code Art. 497) but still signals a problematic "
        "drafting culture — and confuses counterparties.",
        why_zh="依《民法典》第497条该类条款无效，但仍具误导性并暴露对方合同文化。",
        fix_en="Delete it; interpretation follows law and usage, not one party.",
        fix_zh="删除；合同解释依法律与交易习惯，不归单方。",
    ),
]
