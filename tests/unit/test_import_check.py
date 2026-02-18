"""
Tests unitarios para ImportCheck.

Fecha de creación: 2026-02-03
Ticket: 2.6
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from quality_agents.codeguard.agent import Severity
from quality_agents.codeguard.checks.import_check import ImportCheck
from quality_agents.codeguard.config import CodeGuardConfig
from quality_agents.shared.verifiable import ExecutionContext


class TestImportCheckProperties:
    """Tests para las propiedades de ImportCheck."""

    def test_name(self):
        check = ImportCheck()
        assert check.name == "UnusedImports"

    def test_category(self):
        check = ImportCheck()
        assert check.category == "quality"

    def test_estimated_duration(self):
        check = ImportCheck()
        assert check.estimated_duration == 0.5

    def test_priority(self):
        check = ImportCheck()
        assert check.priority == 6


class TestImportCheckShouldRun:
    """Tests para el método should_run()."""

    def test_should_run_on_python_file(self):
        check = ImportCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(check_imports=True),
        )
        assert check.should_run(context) is True

    def test_should_not_run_on_excluded_file(self):
        check = ImportCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=True,
            config=CodeGuardConfig(check_imports=True),
        )
        assert check.should_run(context) is False

    def test_should_not_run_on_non_python_file(self):
        check = ImportCheck()
        context = ExecutionContext(
            file_path=Path("test.txt"),
            is_excluded=False,
            config=CodeGuardConfig(check_imports=True),
        )
        assert check.should_run(context) is False

    def test_should_not_run_when_disabled_in_config(self):
        check = ImportCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(check_imports=False),
        )
        assert check.should_run(context) is False

    def test_should_run_when_config_is_none(self):
        # Si no hay config, asumir que está habilitado
        check = ImportCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=None,
        )
        assert check.should_run(context) is True


class TestImportCheckExecute:
    """Tests para el método execute()."""

    @patch("subprocess.run")
    def test_execute_with_no_unused_imports(self, mock_run):
        # Mock de pylint sin imports sin uso
        pylint_output = ""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=pylint_output,
            stderr="",
        )

        check = ImportCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "UnusedImports"
        assert results[0].severity == Severity.INFO
        assert "No unused imports" in results[0].message
        assert results[0].file_path == "test.py"

    @patch("subprocess.run")
    def test_execute_with_single_unused_import(self, mock_run):
        # Mock de pylint con un import sin uso
        pylint_output = "test.py:10:0: W0611: Unused import os (unused-import)"
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=pylint_output,
            stderr="",
        )

        check = ImportCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "UnusedImports"
        assert results[0].severity == Severity.WARNING
        assert "Unused import" in results[0].message
        assert "'os'" in results[0].message
        assert "autoflake" in results[0].message
        assert results[0].line_number == 10

    @patch("subprocess.run")
    def test_execute_with_multiple_unused_imports(self, mock_run):
        # Mock de pylint con múltiples imports sin uso
        pylint_output = """test.py:5:0: W0611: Unused import sys (unused-import)
test.py:10:0: W0611: Unused import os (unused-import)
test.py:15:0: W0611: Unused json imported from json (unused-import)"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=pylint_output,
            stderr="",
        )

        check = ImportCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 3
        assert all(r.check_name == "UnusedImports" for r in results)
        assert all(r.severity == Severity.WARNING for r in results)

        # Verificar line numbers
        line_numbers = [r.line_number for r in results]
        assert line_numbers == [5, 10, 15]

        # Verificar módulos mencionados
        messages = " ".join([r.message for r in results])
        assert "sys" in messages
        assert "os" in messages
        assert "json" in messages

    @patch("subprocess.run")
    def test_execute_with_from_import(self, mock_run):
        # Mock de pylint con "from X import Y" sin uso
        pylint_output = "test.py:10:0: W0611: Unused datetime imported from datetime (unused-import)"
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=pylint_output,
            stderr="",
        )

        check = ImportCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert "'datetime'" in results[0].message

    @patch("subprocess.run")
    def test_execute_pylint_not_installed(self, mock_run):
        # Mock de FileNotFoundError (pylint no instalado)
        mock_run.side_effect = FileNotFoundError()

        check = ImportCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "UnusedImports"
        assert results[0].severity == Severity.ERROR
        assert "not installed" in results[0].message
        assert "pip install pylint" in results[0].message

    @patch("subprocess.run")
    def test_execute_timeout(self, mock_run):
        # Mock de timeout
        mock_run.side_effect = subprocess.TimeoutExpired("pylint", 5)

        check = ImportCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "UnusedImports"
        assert results[0].severity == Severity.ERROR
        assert "timed out" in results[0].message

    @patch("subprocess.run")
    def test_execute_unexpected_error(self, mock_run):
        # Mock de error inesperado
        mock_run.side_effect = RuntimeError("Unexpected error")

        check = ImportCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "UnusedImports"
        assert results[0].severity == Severity.ERROR
        assert "Unexpected error" in results[0].message

    @patch("subprocess.run")
    def test_execute_calls_pylint_with_correct_args(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        check = ImportCheck()
        check.execute(Path("test.py"))

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "pylint"
        assert "--disable=all" in args
        assert "--enable=unused-import" in args
        assert "--score=n" in args
        assert "test.py" in args[-1]


class TestImportCheckParsePylintOutput:
    """Tests para el método _parse_pylint_output()."""

    def test_parse_single_unused_import(self):
        check = ImportCheck()
        output = "test.py:10:0: W0611: Unused import os (unused-import)"
        imports = check._parse_pylint_output(output)

        assert len(imports) == 1
        assert imports[0]["line"] == 10
        assert imports[0]["module"] == "os"

    def test_parse_multiple_unused_imports(self):
        check = ImportCheck()
        output = """test.py:5:0: W0611: Unused import sys (unused-import)
test.py:10:0: W0611: Unused import os (unused-import)
test.py:15:0: W0611: Unused import json (unused-import)"""
        imports = check._parse_pylint_output(output)

        assert len(imports) == 3
        assert imports[0]["line"] == 5
        assert imports[0]["module"] == "sys"
        assert imports[1]["line"] == 10
        assert imports[1]["module"] == "os"
        assert imports[2]["line"] == 15
        assert imports[2]["module"] == "json"

    def test_parse_from_import_format(self):
        check = ImportCheck()
        output = "test.py:10:0: W0611: Unused datetime imported from datetime (unused-import)"
        imports = check._parse_pylint_output(output)

        assert len(imports) == 1
        assert imports[0]["line"] == 10
        assert imports[0]["module"] == "datetime"

    def test_parse_empty_output(self):
        check = ImportCheck()
        output = ""
        imports = check._parse_pylint_output(output)

        assert len(imports) == 0

    def test_parse_output_with_other_warnings(self):
        check = ImportCheck()
        # Output con otros warnings que no son W0611
        output = """test.py:5:0: C0111: Missing docstring (missing-docstring)
test.py:10:0: W0611: Unused import os (unused-import)
test.py:15:0: E0401: Unable to import 'foo' (import-error)"""
        imports = check._parse_pylint_output(output)

        # Solo debe capturar W0611
        assert len(imports) == 1
        assert imports[0]["line"] == 10
        assert imports[0]["module"] == "os"

    def test_parse_multiline_format(self):
        check = ImportCheck()
        # Formato con múltiples líneas (típico de pylint)
        output = """************* Module test
test.py:10:0: W0611: Unused import os (unused-import)
test.py:15:0: W0611: Unused sys imported from sys (unused-import)"""
        imports = check._parse_pylint_output(output)

        assert len(imports) == 2
        assert imports[0]["module"] == "os"
        assert imports[1]["module"] == "sys"

    def test_parse_complex_import_name(self):
        check = ImportCheck()
        # Import de módulo con nombre complejo
        output = "test.py:10:0: W0611: Unused Path imported from pathlib (unused-import)"
        imports = check._parse_pylint_output(output)

        assert len(imports) == 1
        assert imports[0]["module"] == "Path"

    def test_parse_removes_import_keyword(self):
        check = ImportCheck()
        # Algunos formatos incluyen "import" en el nombre
        output = "test.py:10:0: W0611: Unused import os (unused-import)"
        imports = check._parse_pylint_output(output)

        # Debería limpiar "import" del nombre
        assert imports[0]["module"] == "os"
