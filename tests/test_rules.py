from clauseguard import scanner

EN_SAMPLE = "samples/risky_nda_en.txt"
ZH_SAMPLE = "samples/risky_nda_zh.txt"


def _read(path):
    from pathlib import Path

    return Path(path).read_text(encoding="utf-8")


def test_rules_only_en_catches_planted_risks():
    text = _read(EN_SAMPLE)
    result = scanner.scan(text, use_llm=False)
    ids = {f.rule_id for f in result.findings}
    assert "perpetual-nda" in ids
    assert "auto-renewal" in ids
    assert "non-compete" in ids
    assert "ip-assignment-overreach" in ids
    assert "unlimited-liability" in ids
    assert result.lang == "en"


def test_rules_only_zh_catches_planted_risks():
    text = _read(ZH_SAMPLE)
    result = scanner.scan(text, use_llm=False)
    ids = {f.rule_id for f in result.findings}
    assert "perpetual-nda" in ids  # 永久保密
    assert "auto-renewal" in ids  # 自动续期
    assert "non-compete" in ids  # 竞业
    assert "ip-assignment-overreach" in ids  # 一切知识产权归甲方
    assert "joint-several" in ids  # 连带责任
    assert "final-interpretation" in ids  # 最终解释权
    assert result.lang == "zh"


def test_clean_text_has_no_rule_hits():
    text = (
        "This agreement is made between two friends who trust each other. "
        "They agree to be kind and to share cake on Fridays."
    )
    result = scanner.scan(text, use_llm=False)
    assert result.findings == []
