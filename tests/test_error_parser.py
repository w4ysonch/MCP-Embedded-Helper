import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.error_parser import ErrorParser, BuildError


def load_fixture(filename: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, "r") as f:
        return f.read()


def test_empty_input():
    parser = ErrorParser()
    assert parser.parse("") == []


def test_no_errors():
    parser = ErrorParser()
    output = "CC drivers/led_drv.o\nLD drivers/led_drv.ko\n"
    assert parser.parse(output) == []


def test_parse_all_error_types():
    parser = ErrorParser()
    text = load_fixture("sample_arm_gcc_errors.txt")
    errors = parser.parse(text)
    types = [e["type"] for e in errors]

    assert "syntax_error" in types
    assert "header_missing" in types
    assert "linker_error" in types
    assert "arch_mismatch" in types
    assert "toolchain_missing" in types
    assert "make_error" in types
    assert "warning" in types


def test_syntax_error_details():
    parser = ErrorParser()
    text = "drivers/led_drv.c:42:5: error: expected ';' before '}' token"
    errors = parser.parse(text)

    assert len(errors) == 1
    e = errors[0]
    assert e["file"] == "drivers/led_drv.c"
    assert e["line"] == 42
    assert e["type"] == "syntax_error"
    assert e["severity"] == "ERROR"
    assert "expected ';'" in e["message"]


def test_header_missing():
    parser = ErrorParser()
    text = "drivers/led_drv.c:3:22: fatal error: linux/gpio.h: No such file or directory"
    errors = parser.parse(text)

    assert len(errors) == 1
    assert errors[0]["type"] == "header_missing"
    assert errors[0]["file"] == "drivers/led_drv.c"


def test_linker_error():
    parser = ErrorParser()
    text = "drivers/led_drv.c:(.text+0x42): undefined reference to 'gpio_request'"
    errors = parser.parse(text)

    assert len(errors) == 1
    assert errors[0]["type"] == "linker_error"
    assert "gpio_request" in errors[0]["message"]


def test_arch_mismatch():
    parser = ErrorParser()
    text = "/usr/bin/ld: skipping incompatible /usr/lib/libfoo.so when searching for -lfoo"
    errors = parser.parse(text)

    assert len(errors) == 1
    assert errors[0]["type"] == "arch_mismatch"


def test_toolchain_missing():
    parser = ErrorParser()
    text = "make: arm-buildroot-linux-gnueabihf-gcc: Command not found"
    errors = parser.parse(text)

    assert len(errors) == 1
    assert errors[0]["type"] == "toolchain_missing"
    assert errors[0]["severity"] == "FATAL"


def test_warning_severity():
    parser = ErrorParser()
    text = "led.c:55:3: warning: unused variable 'ret'"
    errors = parser.parse(text)

    assert len(errors) == 1
    assert errors[0]["type"] == "warning"
    assert errors[0]["severity"] == "WARNING"


def test_summary():
    parser = ErrorParser()
    text = load_fixture("sample_arm_gcc_errors.txt")
    errors = parser.parse(text)
    summary = parser.summary(errors)

    assert "条错误" in summary
    assert "语法/声明错误" in summary


def test_build_error_repr():
    error = BuildError("led.c", 42, "syntax_error", "missing ;",
                       "led.c:42: error: missing ;", severity="ERROR")
    repr_str = repr(error)
    assert "led.c" in repr_str
    assert "42" in repr_str
    assert "ERROR" in repr_str
    assert "syntax_error" in repr_str


if __name__ == "__main__":
    tests = [
        test_empty_input,
        test_no_errors,
        test_parse_all_error_types,
        test_syntax_error_details,
        test_header_missing,
        test_linker_error,
        test_arch_mismatch,
        test_toolchain_missing,
        test_warning_severity,
        test_summary,
        test_build_error_repr,
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
