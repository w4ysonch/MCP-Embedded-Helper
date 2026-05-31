import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.context_gatherer import ContextGatherer


FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def test_gather_finds_context():
    g = ContextGatherer(FIXTURES, context_lines=3)
    errors = [{"file": "sample_led_drv.c", "line": 14, "type": "linker_error"}]
    result = g.gather(errors)

    assert "sample_led_drv.c" in str(list(result.keys())[0])
    info = list(result.values())[0]
    snippets = info["snippets"][0]
    assert "gpio_request" in snippets


def test_gather_marks_error_line():
    g = ContextGatherer(FIXTURES, context_lines=3)
    errors = [{"file": "sample_led_drv.c", "line": 14, "type": "linker_error"}]
    result = g.gather(errors)

    info = list(result.values())[0]
    snippets = info["snippets"][0]
    assert ">>>" in snippets
    assert " 14  " in snippets


def test_gather_merges_same_file():
    g = ContextGatherer(FIXTURES, context_lines=3)
    errors = [
        {"file": "sample_led_drv.c", "line": 14, "type": "linker_error"},
        {"file": "sample_led_drv.c", "line": 23, "type": "syntax_error"},
    ]
    result = g.gather(errors)

    assert len(result) == 1
    info = list(result.values())[0]
    assert len(info["snippets"]) == 2


def test_gather_file_not_found():
    g = ContextGatherer(FIXTURES)
    errors = [{"file": "nonexistent.c", "line": 10, "type": "syntax_error"}]
    result = g.gather(errors)
    assert len(result) == 0


def test_gather_empty_error_list():
    g = ContextGatherer(FIXTURES)
    result = g.gather([])
    assert result == {}


def test_gather_line_out_of_range():
    g = ContextGatherer(FIXTURES, context_lines=3)
    errors = [{"file": "sample_led_drv.c", "line": 9999, "type": "warning"}]
    result = g.gather(errors)
    assert len(result) == 0


def test_gather_line_zero():
    g = ContextGatherer(FIXTURES)
    errors = [{"file": "sample_led_drv.c", "line": 0, "type": "warning"}]
    result = g.gather(errors)
    assert len(result) == 0


def test_gather_includes_total_lines():
    g = ContextGatherer(FIXTURES)
    errors = [{"file": "sample_led_drv.c", "line": 14, "type": "linker_error"}]
    result = g.gather(errors)
    info = list(result.values())[0]
    assert info["total_lines"] > 0


if __name__ == "__main__":
    tests = [
        test_gather_finds_context,
        test_gather_marks_error_line,
        test_gather_merges_same_file,
        test_gather_file_not_found,
        test_gather_empty_error_list,
        test_gather_line_out_of_range,
        test_gather_line_zero,
        test_gather_includes_total_lines,
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
