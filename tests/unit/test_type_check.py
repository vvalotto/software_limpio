"""
Tests unitarios para TypeCheck.

Fecha de creación: 2026-02-03
Ticket: 2.5
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from quality_agents.codeguard.agent import Severity
from quality_agents.codeguard.checks.type_check import TypeCheck
from quality_agents.codeguard.config import CodeGuardConfig
from quality_agents.shared.verifiable import ExecutionContext


class TestTypeCheckProperties:
    """Tests para las propiedades de TypeCheck."""

    def test_name(self):
        check = TypeCheck()
        assert check.name == "Types"

    def test_category(self):
        check = TypeCheck()
        assert check.category == "quality"

    def test_estimated_duration(self):
        check = TypeCheck()
        assert check.estimated_duration == 3.0

    def test_priority(self):
        check = TypeCheck()
        assert check.priority == 5


class TestTypeCheckShouldRun:
    """Tests para el método should_run()."""

    @patch.object(TypeCheck, "_has_type_hints", return_value=True)
    def test_should_run_on_python_file_with_hints(self, mock_hints):
        check = TypeCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(check_types=True),
        )
        assert check.should_run(context) is True

    @patch.object(TypeCheck, "_has_type_hints", return_value=False)
    def test_should_not_run_on_file_without_hints(self, mock_hints):
        check = TypeCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(check_types=True),
        )
        assert check.should_run(context) is False

    @patch.object(TypeCheck, "_has_type_hints", return_value=True)
    def test_should_not_run_on_excluded_file(self, mock_hints):
        check = TypeCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=True,
            config=CodeGuardConfig(check_types=True),
        )
        assert check.should_run(context) is False

    def test_should_not_run_on_non_python_file(self):
        check = TypeCheck()
        context = ExecutionContext(
            file_path=Path("test.txt"),
            is_excluded=False,
            config=CodeGuardConfig(check_types=True),
        )
        assert check.should_run(context) is False

    @patch.object(TypeCheck, "_has_type_hints", return_value=True)
    def test_should_not_run_when_disabled_in_config(self, mock_hints):
        check = TypeCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=CodeGuardConfig(check_types=False),
        )
        assert check.should_run(context) is False

    @patch.object(TypeCheck, "_has_type_hints", return_value=True)
    def test_should_run_when_config_is_none(self, mock_hints):
        # Si no hay config, asumir que está habilitado
        check = TypeCheck()
        context = ExecutionContext(
            file_path=Path("test.py"),
            is_excluded=False,
            config=None,
        )
        assert check.should_run(context) is True


class TestTypeCheckExecute:
    """Tests para el método execute()."""

    @patch("subprocess.run")
    def test_execute_with_no_type_errors(self, mock_run):
        # Mock de mypy sin errores
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="",
        )

        check = TypeCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Types"
        assert results[0].severity == Severity.INFO
        assert "No type errors" in results[0].message
        assert results[0].file_path == "test.py"

    @patch("subprocess.run")
    def test_execute_with_type_error(self, mock_run):
        # Mock de mypy con error de tipo
        mypy_output = 'test.py:10:5: error: Argument 1 has incompatible type "str"; expected "int"'
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=mypy_output,
            stderr="",
        )

        check = TypeCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Types"
        assert results[0].severity == Severity.WARNING
        assert "incompatible type" in results[0].message
        assert results[0].line_number == 10

    @patch("subprocess.run")
    def test_execute_with_multiple_type_errors(self, mock_run):
        # Mock de mypy con múltiples errores
        mypy_output = """test.py:10:5: error: Argument 1 has incompatible type "str"; expected "int"
test.py:15:10: error: Name 'undefined_var' is not defined
test.py:20:1: error: Function is missing a return type annotation"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=mypy_output,
            stderr="",
        )

        check = TypeCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 3
        assert all(r.check_name == "Types" for r in results)
        assert all(r.severity == Severity.WARNING for r in results)

        # Verificar line numbers
        line_numbers = [r.line_number for r in results]
        assert line_numbers == [10, 15, 20]

    @patch("subprocess.run")
    def test_execute_with_warning(self, mock_run):
        # Mock de mypy con warning (no error)
        mypy_output = "test.py:10:5: warning: Some warning message"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=mypy_output,
            stderr="",
        )

        check = TypeCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].severity == Severity.WARNING

    @patch("subprocess.run")
    def test_execute_with_note_ignored(self, mock_run):
        # Mock de mypy con nota (debe ser ignorada)
        mypy_output = """test.py:10:5: error: Some error
test.py:11:5: note: Some additional info"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=mypy_output,
            stderr="",
        )

        check = TypeCheck()
        results = check.execute(Path("test.py"))

        # Solo debe reportar el error, no la nota
        assert len(results) == 1
        assert "Some error" in results[0].message

    @patch("subprocess.run")
    def test_execute_mypy_not_installed(self, mock_run):
        # Mock de FileNotFoundError (mypy no instalado)
        mock_run.side_effect = FileNotFoundError()

        check = TypeCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Types"
        assert results[0].severity == Severity.ERROR
        assert "not installed" in results[0].message
        assert "pip install mypy" in results[0].message

    @patch("subprocess.run")
    def test_execute_timeout(self, mock_run):
        # Mock de timeout
        mock_run.side_effect = subprocess.TimeoutExpired("mypy", 10)

        check = TypeCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Types"
        assert results[0].severity == Severity.ERROR
        assert "timed out" in results[0].message

    @patch("subprocess.run")
    def test_execute_unexpected_error(self, mock_run):
        # Mock de error inesperado
        mock_run.side_effect = RuntimeError("Unexpected error")

        check = TypeCheck()
        results = check.execute(Path("test.py"))

        assert len(results) == 1
        assert results[0].check_name == "Types"
        assert results[0].severity == Severity.ERROR
        assert "Unexpected error" in results[0].message

    @patch("subprocess.run")
    def test_execute_calls_mypy_with_correct_args(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        check = TypeCheck()
        check.execute(Path("test.py"))

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "mypy"
        assert "--no-error-summary" in args
        assert "--show-column-numbers" in args
        assert "--no-color-output" in args
        assert "test.py" in args[-1]


class TestTypeCheckHasTypeHints:
    """Tests para el método _has_type_hints()."""

    def test_has_type_hints_with_parameter_annotation(self):
        check = TypeCheck()
        code = """
def greet(name: str) -> str:
    return f"Hello, {name}"
"""
        with patch("pathlib.Path.read_text", return_value=code):
            assert check._has_type_hints(Path("test.py")) is True

    def test_has_type_hints_with_return_annotation(self):
        check = TypeCheck()
        code = """
def calculate() -> int:
    return 42
"""
        with patch("pathlib.Path.read_text", return_value=code):
            assert check._has_type_hints(Path("test.py")) is True

    def test_has_type_hints_with_variable_annotation(self):
        check = TypeCheck()
        code = """
name: str = "Alice"
age: int = 30
"""
        with patch("pathlib.Path.read_text", return_value=code):
            assert check._has_type_hints(Path("test.py")) is True

    def test_has_type_hints_with_list_annotation(self):
        check = TypeCheck()
        code = """
from typing import List

numbers: List[int] = [1, 2, 3]
"""
        with patch("pathlib.Path.read_text", return_value=code):
            assert check._has_type_hints(Path("test.py")) is True

    def test_has_type_hints_with_dict_annotation(self):
        check = TypeCheck()
        code = """
from typing import Dict

data: Dict[str, int] = {"a": 1}
"""
        with patch("pathlib.Path.read_text", return_value=code):
            assert check._has_type_hints(Path("test.py")) is True

    def test_has_type_hints_with_optional_annotation(self):
        check = TypeCheck()
        code = """
from typing import Optional

def process(value: Optional[str]) -> None:
    pass
"""
        with patch("pathlib.Path.read_text", return_value=code):
            assert check._has_type_hints(Path("test.py")) is True

    def test_has_no_type_hints_plain_code(self):
        check = TypeCheck()
        code = """
def greet(name):
    return "Hello, " + name

x = 42
"""
        with patch("pathlib.Path.read_text", return_value=code):
            assert check._has_type_hints(Path("test.py")) is False

    def test_has_no_type_hints_empty_file(self):
        check = TypeCheck()
        code = ""
        with patch("pathlib.Path.read_text", return_value=code):
            assert check._has_type_hints(Path("test.py")) is False

    def test_has_type_hints_file_read_error(self):
        check = TypeCheck()
        with patch("pathlib.Path.read_text", side_effect=IOError()):
            # Si no se puede leer, asumir que no tiene hints
            assert check._has_type_hints(Path("test.py")) is False


class TestTypeCheckParseMyPyOutput:
    """Tests para el método _parse_mypy_output()."""

    def test_parse_single_error(self):
        check = TypeCheck()
        output = 'test.py:10:5: error: Argument has incompatible type'
        errors = check._parse_mypy_output(output)

        assert len(errors) == 1
        assert errors[0]["line"] == 10
        assert errors[0]["level"] == "error"
        assert "incompatible type" in errors[0]["message"]

    def test_parse_multiple_errors(self):
        check = TypeCheck()
        output = """test.py:10:5: error: First error
test.py:20:10: error: Second error
test.py:30:1: error: Third error"""
        errors = check._parse_mypy_output(output)

        assert len(errors) == 3
        assert errors[0]["line"] == 10
        assert errors[1]["line"] == 20
        assert errors[2]["line"] == 30

    def test_parse_warning(self):
        check = TypeCheck()
        output = "test.py:10:5: warning: Some warning"
        errors = check._parse_mypy_output(output)

        assert len(errors) == 1
        assert errors[0]["level"] == "warning"

    def test_parse_ignores_notes(self):
        check = TypeCheck()
        output = """test.py:10:5: error: Some error
test.py:11:5: note: Additional info
test.py:12:5: note: More info"""
        errors = check._parse_mypy_output(output)

        # Solo debe parsear el error, no las notas
        assert len(errors) == 1
        assert errors[0]["line"] == 10

    def test_parse_empty_output(self):
        check = TypeCheck()
        output = ""
        errors = check._parse_mypy_output(output)

        assert len(errors) == 0

    def test_parse_output_without_column(self):
        check = TypeCheck()
        # Algunos outputs de mypy no incluyen columna
        output = "test.py:10: error: Some error"
        errors = check._parse_mypy_output(output)

        assert len(errors) == 1
        assert errors[0]["line"] == 10

    def test_parse_mixed_output(self):
        check = TypeCheck()
        output = """test.py:10:5: error: Error message
test.py:15:1: note: Note message (should be ignored)
test.py:20:10: warning: Warning message
Some random line that should be ignored
test.py:25:5: error: Another error"""
        errors = check._parse_mypy_output(output)

        # Debe parsear solo errors y warnings, no notes ni líneas random
        assert len(errors) == 3
        assert errors[0]["line"] == 10
        assert errors[1]["line"] == 20
        assert errors[2]["line"] == 25
