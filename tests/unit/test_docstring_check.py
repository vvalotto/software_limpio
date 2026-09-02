"""
Tests unitarios para DocstringCheck.

Fecha de creación: 2026-09-02
Issue: #69
"""

import ast
from pathlib import Path

from quality_agents.codeguard.agent import Severity
from quality_agents.codeguard.checks.docstring_check import DocstringCheck
from quality_agents.codeguard.config import ChecksConfig, CodeGuardConfig
from quality_agents.shared.verifiable import ExecutionContext


class TestDocstringCheckProperties:
    """Tests para las propiedades de DocstringCheck."""

    def test_name(self):
        check = DocstringCheck()
        assert check.name == "Docstrings"

    def test_category(self):
        check = DocstringCheck()
        assert check.category == "documentation"

    def test_estimated_duration(self):
        check = DocstringCheck()
        assert check.estimated_duration == 0.5

    def test_priority(self):
        check = DocstringCheck()
        assert check.priority == 3


class TestDocstringCheckShouldRun:
    """Tests para el método should_run()."""

    def test_should_run_on_python_file(self):
        check = DocstringCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(checks=ChecksConfig(docstrings=True)),
        )
        assert check.should_run(context) is True

    def test_should_not_run_on_excluded_file(self):
        check = DocstringCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=True,
            config=CodeGuardConfig(checks=ChecksConfig(docstrings=True)),
        )
        assert check.should_run(context) is False

    def test_should_not_run_on_non_python_file(self):
        check = DocstringCheck()
        context = ExecutionContext(
            file_path=Path("test.txt"),
            is_excluded=False,
            config=CodeGuardConfig(checks=ChecksConfig(docstrings=True)),
        )
        assert check.should_run(context) is False

    def test_should_not_run_when_disabled_in_config(self):
        check = DocstringCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(checks=ChecksConfig(docstrings=False)),
        )
        assert check.should_run(context) is False

    def test_should_run_when_config_is_none(self):
        # Si no hay config, asumir que está habilitado
        check = DocstringCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=None,
        )
        assert check.should_run(context) is True


class TestDocstringCheckExecute:
    """Tests para el método execute()."""

    def test_execute_full_coverage(self, tmp_path):
        source = '''"""Module docstring."""


def documented():
    """Has a docstring."""
    return 1


class Documented:
    """Has a docstring."""

    def method(self):
        """Has a docstring."""
        return 1
'''
        file_path = tmp_path / "full.py"
        file_path.write_text(source)

        check = DocstringCheck()
        results = check.execute(file_path)

        assert len(results) == 1
        assert results[0].check_name == "Docstrings"
        assert results[0].severity == Severity.INFO
        assert "100.0%" in results[0].message
        assert "meets threshold" in results[0].message

    def test_execute_below_threshold(self, tmp_path):
        source = '''def documented():
    """Has a docstring."""
    return 1


def undocumented():
    return 2
'''
        file_path = tmp_path / "partial.py"
        file_path.write_text(source)

        check = DocstringCheck()
        check._context = ExecutionContext(
            file_path=file_path,
            is_excluded=False,
            config=CodeGuardConfig(min_docstring_coverage=80.0),
        )
        results = check.execute(file_path)

        assert len(results) == 1
        assert results[0].check_name == "Docstrings"
        assert results[0].severity == Severity.WARNING
        assert "below threshold" in results[0].message
        assert "undocumented" in results[0].message
        # <module> también cuenta como símbolo sin docstring
        assert results[0].line_number is not None

    def test_execute_counts_private_symbols(self, tmp_path):
        # 2 de 3 símbolos documentables (módulo + _private) no tienen docstring
        source = '''def _private():
    return 1


def public():
    """Documented."""
    return 2
'''
        file_path = tmp_path / "private.py"
        file_path.write_text(source)

        check = DocstringCheck()
        results = check.execute(file_path)

        assert len(results) == 1
        assert results[0].severity == Severity.WARNING
        assert "_private" in results[0].message

    def test_execute_uses_configured_threshold(self, tmp_path):
        source = '''def documented():
    """Has a docstring."""
    return 1


def undocumented():
    return 2
'''
        file_path = tmp_path / "custom_threshold.py"
        file_path.write_text(source)

        check = DocstringCheck()
        # Módulo + 2 funciones = 3 símbolos, 1 con docstring → 33.3%
        check._context = ExecutionContext(
            file_path=file_path,
            is_excluded=False,
            config=CodeGuardConfig(min_docstring_coverage=30.0),
        )
        results = check.execute(file_path)

        assert results[0].severity == Severity.INFO

    def test_execute_module_without_docstring_counts_as_missing(self, tmp_path):
        # Un archivo sin funciones/clases igual tiene un símbolo documentable:
        # el módulo. Sin docstring de módulo, coverage es 0%.
        file_path = tmp_path / "no_module_docstring.py"
        file_path.write_text("x = 1\ny = 2\n")

        check = DocstringCheck()
        results = check.execute(file_path)

        assert len(results) == 1
        assert results[0].severity == Severity.WARNING
        assert "0.0%" in results[0].message
        assert "<module>" in results[0].message

    def test_execute_syntax_error(self, tmp_path):
        file_path = tmp_path / "broken.py"
        file_path.write_text("def broken(:\n    pass\n")

        check = DocstringCheck()
        results = check.execute(file_path)

        assert len(results) == 1
        assert results[0].check_name == "Docstrings"
        assert results[0].severity == Severity.ERROR
        assert "Could not parse" in results[0].message

    def test_execute_many_missing_truncates_names(self, tmp_path):
        functions = "\n\n".join(f"def f{i}():\n    return {i}" for i in range(8))
        file_path = tmp_path / "many_missing.py"
        file_path.write_text(functions + "\n")

        check = DocstringCheck()
        results = check.execute(file_path)

        assert results[0].severity == Severity.WARNING
        assert "more)" in results[0].message


class TestDocstringCheckCollectSymbols:
    """Tests para el método _collect_symbols()."""

    def test_collects_module_symbol(self):
        check = DocstringCheck()
        tree = ast.parse('"""Module doc."""\n')
        symbols = check._collect_symbols(tree)

        assert len(symbols) == 1
        assert symbols[0]["name"] == "<module>"
        assert symbols[0]["has_docstring"] is True

    def test_collects_function_and_class(self):
        check = DocstringCheck()
        tree = ast.parse(
            "def foo():\n    pass\n\n\nclass Bar:\n    def method(self):\n        pass\n"
        )
        symbols = check._collect_symbols(tree)

        names = {s["name"] for s in symbols}
        assert names == {"<module>", "foo", "Bar", "method"}
        assert all(s["has_docstring"] is False for s in symbols)

    def test_includes_private_symbols(self):
        check = DocstringCheck()
        tree = ast.parse("def _private():\n    pass\n")
        symbols = check._collect_symbols(tree)

        names = {s["name"] for s in symbols}
        assert "_private" in names

    def test_includes_async_functions(self):
        check = DocstringCheck()
        tree = ast.parse("async def fetch():\n    pass\n")
        symbols = check._collect_symbols(tree)

        names = {s["name"] for s in symbols}
        assert "fetch" in names
