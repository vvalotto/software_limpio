"""Tests unitarios para PrimitiveObsessionAnalyzer."""

import textwrap
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from quality_agents.designreviewer.analyzers.primitive_obsession_analyzer import (
    PrimitiveObsessionAnalyzer,
)
from quality_agents.designreviewer.config import DesignReviewerChecksConfig, DesignReviewerConfig
from quality_agents.designreviewer.models import ReviewSeverity
from quality_agents.shared.verifiable import ExecutionContext


def _write(tmp_path: Path, code: str) -> Path:
    f = tmp_path / "sample.py"
    f.write_text(textwrap.dedent(code))
    return f


def _context(config=None, excluded=False, path="sample.py"):
    ctx = MagicMock(spec=ExecutionContext)
    ctx.file_path = Path(path)
    ctx.is_excluded = excluded
    ctx.config = config
    return ctx


def _analyzer(max_primitive_params=3):
    a = PrimitiveObsessionAnalyzer()
    a._config = DesignReviewerConfig(max_primitive_params=max_primitive_params)
    return a


class TestPrimitiveObsessionAnalyzerProperties:
    def test_name(self):
        assert PrimitiveObsessionAnalyzer().name == "PrimitiveObsessionAnalyzer"

    def test_category(self):
        assert PrimitiveObsessionAnalyzer().category == "smells"

    def test_priority(self):
        assert PrimitiveObsessionAnalyzer().priority == 4

    def test_estimated_duration(self):
        assert PrimitiveObsessionAnalyzer().estimated_duration == 0.8


class TestPrimitiveObsessionAnalyzerShouldRun:
    def test_runs_on_python_file(self):
        assert PrimitiveObsessionAnalyzer().should_run(_context()) is True

    def test_skips_non_python_file(self):
        assert PrimitiveObsessionAnalyzer().should_run(_context(path="sample.js")) is False

    def test_skips_excluded(self):
        assert PrimitiveObsessionAnalyzer().should_run(_context(excluded=True)) is False

    def test_skips_when_toggle_disabled(self):
        config = DesignReviewerConfig(checks=DesignReviewerChecksConfig(primitive_obsession=False))
        assert PrimitiveObsessionAnalyzer().should_run(_context(config=config)) is False

    def test_runs_when_toggle_enabled(self):
        config = DesignReviewerConfig(checks=DesignReviewerChecksConfig(primitive_obsession=True))
        assert PrimitiveObsessionAnalyzer().should_run(_context(config=config)) is True


class TestPrimitiveObsessionPrimitivosRepetidos:
    def test_tres_floats_es_violation(self, tmp_path):
        code = """
            class Point:
                def move(self, x: float, y: float, z: float):
                    pass
        """
        results = _analyzer().execute(_write(tmp_path, code))
        assert len(results) == 1
        assert results[0].severity == ReviewSeverity.WARNING
        assert "float" in results[0].message

    def test_dos_floats_no_es_violation(self, tmp_path):
        code = """
            class Point:
                def move(self, x: float, y: float):
                    pass
        """
        results = _analyzer().execute(_write(tmp_path, code))
        assert results == []

    def test_tres_strings_es_violation(self, tmp_path):
        code = """
            class Address:
                def set(self, street: str, city: str, country: str):
                    pass
        """
        results = _analyzer().execute(_write(tmp_path, code))
        assert len(results) == 1
        assert "str" in results[0].message

    def test_umbral_personalizado(self, tmp_path):
        code = """
            class Foo:
                def bar(self, a: int, b: int):
                    pass
        """
        results = _analyzer(max_primitive_params=2).execute(_write(tmp_path, code))
        assert len(results) == 1

    def test_tipos_distintos_no_es_violation(self, tmp_path):
        code = """
            class Foo:
                def bar(self, name: str, age: int, score: float):
                    pass
        """
        results = _analyzer().execute(_write(tmp_path, code))
        assert results == []

    def test_excluye_dunder(self, tmp_path):
        code = """
            class Foo:
                def __init__(self, x: float, y: float, z: float):
                    pass
        """
        results = _analyzer().execute(_write(tmp_path, code))
        assert results == []

    def test_excluye_metodo_privado(self, tmp_path):
        code = """
            class Foo:
                def _helper(self, x: float, y: float, z: float):
                    pass
        """
        results = _analyzer().execute(_write(tmp_path, code))
        assert results == []

    def test_excluye_classmethod_constructor(self, tmp_path):
        code = """
            class Foo:
                @classmethod
                def from_coords(cls, x: float, y: float, z: float):
                    pass
        """
        results = _analyzer().execute(_write(tmp_path, code))
        assert results == []

    def test_current_value_es_cantidad_params(self, tmp_path):
        code = """
            class Foo:
                def bar(self, a: int, b: int, c: int):
                    pass
        """
        results = _analyzer().execute(_write(tmp_path, code))
        assert results[0].current_value == 3
        assert results[0].threshold == 3


class TestPrimitiveObsessionDictParams:
    def test_dict_param_es_violation(self, tmp_path):
        code = """
            class Processor:
                def process(self, data: dict):
                    pass
        """
        results = _analyzer().execute(_write(tmp_path, code))
        assert len(results) == 1
        assert "dict" in results[0].message

    def test_Dict_param_es_violation(self, tmp_path):
        code = """
            from typing import Dict, Any
            class Processor:
                def process(self, data: Dict):
                    pass
        """
        results = _analyzer().execute(_write(tmp_path, code))
        assert len(results) == 1

    def test_dict_param_excluye_dunder(self, tmp_path):
        code = """
            class Foo:
                def __init__(self, data: dict):
                    pass
        """
        results = _analyzer().execute(_write(tmp_path, code))
        assert results == []

    def test_violation_tiene_suggestion(self, tmp_path):
        code = """
            class Foo:
                def bar(self, data: dict):
                    pass
        """
        results = _analyzer().execute(_write(tmp_path, code))
        assert results[0].suggestion is not None

    def test_multiple_dict_params_genera_resultado_por_cada_uno(self, tmp_path):
        code = """
            class Foo:
                def bar(self, config: dict, data: dict):
                    pass
        """
        results = _analyzer().execute(_write(tmp_path, code))
        assert len(results) == 2


class TestPrimitiveObsessionEdgeCases:
    def test_empty_file(self, tmp_path):
        assert _analyzer().execute(_write(tmp_path, "")) == []

    def test_syntax_error(self, tmp_path):
        f = tmp_path / "bad.py"
        f.write_text("def broken(:")
        assert _analyzer().execute(f) == []

    def test_sin_anotaciones_no_viola(self, tmp_path):
        code = """
            class Foo:
                def bar(self, x, y, z):
                    pass
        """
        assert _analyzer().execute(_write(tmp_path, code)) == []

    def test_clase_sin_metodos_publicos(self, tmp_path):
        code = """
            class Foo:
                def __init__(self):
                    pass
                def _private(self):
                    pass
        """
        assert _analyzer().execute(_write(tmp_path, code)) == []
