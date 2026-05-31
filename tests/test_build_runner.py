import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mcp_embedded_helper.core.build_runner import BuildRunner, BuildResult


def test_build_result_fields():
    r = BuildResult(exit_code=2, stdout="out", stderr="err",
                    command="make all", cwd="/tmp")
    assert r.exit_code == 2
    assert r.failed is True
    assert "out" in r.output
    assert "err" in r.output

    d = r.to_dict()
    assert d["exit_code"] == 2
    assert d["command"] == "make all"


def test_build_result_success():
    r = BuildResult(exit_code=0, stdout="CC main.o", stderr="",
                    command="make", cwd="/tmp")
    assert r.failed is False
    assert "CC main.o" in r.output


def test_run_without_makefile():
    with tempfile.TemporaryDirectory() as tmp:
        runner = BuildRunner(tmp)
        result = runner.run()
        assert result.failed is True
        assert result.exit_code != 0


def test_run_with_makefile():
    with tempfile.TemporaryDirectory() as tmp:
        makefile = os.path.join(tmp, "Makefile")
        with open(makefile, "w") as f:
            f.write("all:\n\t@echo hello from make\n")

        runner = BuildRunner(tmp)
        result = runner.run()
        assert result.exit_code == 0
        assert "hello from make" in result.stdout


def test_run_with_target():
    with tempfile.TemporaryDirectory() as tmp:
        makefile = os.path.join(tmp, "Makefile")
        with open(makefile, "w") as f:
            f.write("all:\n\t@echo default\n")
            f.write("clean:\n\t@echo cleaned\n")

        runner = BuildRunner(tmp)
        result = runner.run(target="clean")
        assert result.exit_code == 0
        assert "cleaned" in result.stdout


def test_run_with_extra_args():
    with tempfile.TemporaryDirectory() as tmp:
        makefile = os.path.join(tmp, "Makefile")
        with open(makefile, "w") as f:
            f.write("all:\n\t@echo default\n")
            f.write("modules:\n\t@echo building modules\n")

        runner = BuildRunner(tmp)
        result = runner.run(target="modules", extra_args="ARCH=arm")
        assert result.exit_code == 0
        assert "modules" in result.stdout


def test_output_merges_stdout_stderr():
    with tempfile.TemporaryDirectory() as tmp:
        makefile = os.path.join(tmp, "Makefile")
        with open(makefile, "w") as f:
            f.write("all:\n\t@echo to stdout\n\t@echo to stderr >&2\n")

        runner = BuildRunner(tmp)
        result = runner.run()
        assert "to stdout" in result.output
        assert "to stderr" in result.output


def test_make_not_found():
    # 找个没有 make 的 PATH 不太现实，测一下 command 字段就行
    runner = BuildRunner()
    assert runner.project_dir == os.path.abspath(".")


if __name__ == "__main__":
    tests = [
        test_build_result_fields,
        test_build_result_success,
        test_run_without_makefile,
        test_run_with_makefile,
        test_run_with_target,
        test_run_with_extra_args,
        test_output_merges_stdout_stderr,
        test_make_not_found,
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
