import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mcp_embedded_helper.core.env_checker import EnvChecker, EnvCheckResult


def test_check_result_fields():
    r = EnvCheckResult(item="$CROSS_COMPILE", status="MISSING",
                       detail="未设置", fix_hint="export CROSS_COMPILE=...")
    d = r.to_dict()
    assert d["item"] == "$CROSS_COMPILE"
    assert d["status"] == "MISSING"
    assert "CROSS_COMPILE" in d["fix_hint"]


def test_run_all_returns_list():
    checker = EnvChecker()
    results = checker.run_all()
    assert isinstance(results, list)
    assert len(results) >= 5

    items = [r.item for r in results]
    assert "$CROSS_COMPILE" in items
    assert "$ARCH" in items
    assert "$CC" in items
    assert "交叉编译器" in items
    assert "make" in items


def test_make_is_available():
    # WSL 环境下 make 应该是可用的
    checker = EnvChecker()
    for r in checker.run_all():
        if r.item == "make":
            assert r.status == "OK", f"make 不可用: {r.detail}"
            return


def test_each_result_has_status():
    checker = EnvChecker()
    for r in checker.run_all():
        assert r.status in ("OK", "MISSING", "ERROR"), \
            f"{r.item} 状态异常: {r.status}"


def test_summary_format():
    checker = EnvChecker()
    results = checker.run_all()
    summary = checker.summary(results)
    assert "环境诊断结果" in summary
    assert "make" in summary


if __name__ == "__main__":
    tests = [
        test_check_result_fields,
        test_run_all_returns_list,
        test_make_is_available,
        test_each_result_has_status,
        test_summary_format,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  OK  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
