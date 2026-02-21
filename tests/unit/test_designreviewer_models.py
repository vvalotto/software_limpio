"""
Tests unitarios para ReviewSeverity y ReviewResult.

Ticket: 1.7
"""

from pathlib import Path

from quality_agents.designreviewer.models import ReviewResult, ReviewSeverity


class TestReviewSeverity:
    """Tests para el enum ReviewSeverity."""

    def test_valores(self):
        """Debe tener los tres niveles de severidad correctos."""
        assert ReviewSeverity.INFO.value == "info"
        assert ReviewSeverity.WARNING.value == "warning"
        assert ReviewSeverity.CRITICAL.value == "critical"

    def test_comparacion_enum(self):
        """Los valores del enum deben ser comparables por identidad."""
        assert ReviewSeverity.INFO is ReviewSeverity.INFO
        assert ReviewSeverity.WARNING is not ReviewSeverity.CRITICAL

    def test_todos_los_valores(self):
        """Debe haber exactamente tres niveles."""
        assert len(ReviewSeverity) == 3


class TestReviewResult:
    """Tests para el dataclass ReviewResult."""

    def test_campos_requeridos(self):
        """Debe instanciarse correctamente con campos requeridos."""
        result = ReviewResult(
            analyzer_name="CBOAnalyzer",
            severity=ReviewSeverity.CRITICAL,
            current_value=8,
            threshold=5,
            message="Acoplamiento excesivo",
            file_path=Path("src/service.py"),
        )

        assert result.analyzer_name == "CBOAnalyzer"
        assert result.severity == ReviewSeverity.CRITICAL
        assert result.current_value == 8
        assert result.threshold == 5
        assert result.message == "Acoplamiento excesivo"
        assert result.file_path == Path("src/service.py")

    def test_campos_opcionales_por_defecto(self):
        """Los campos opcionales deben tener valores por defecto correctos."""
        result = ReviewResult(
            analyzer_name="FanOutAnalyzer",
            severity=ReviewSeverity.WARNING,
            current_value=9,
            threshold=7,
            message="Fan-out elevado",
            file_path=Path("src/module.py"),
        )

        assert result.class_name is None
        assert result.suggestion is None
        assert result.estimated_effort == 0.0

    def test_campos_opcionales_con_valores(self):
        """Debe aceptar todos los campos opcionales."""
        result = ReviewResult(
            analyzer_name="LCOMAnalyzer",
            severity=ReviewSeverity.WARNING,
            current_value=3,
            threshold=1,
            message="Baja cohesión",
            file_path=Path("src/model.py"),
            class_name="UserModel",
            suggestion="Separar en UserProfile y UserCredentials",
            estimated_effort=4.0,
        )

        assert result.class_name == "UserModel"
        assert result.suggestion == "Separar en UserProfile y UserCredentials"
        assert result.estimated_effort == 4.0

    def test_estimated_effort_float(self):
        """estimated_effort debe aceptar valores float."""
        result = ReviewResult(
            analyzer_name="CBOAnalyzer",
            severity=ReviewSeverity.CRITICAL,
            current_value=12,
            threshold=5,
            message="CBO muy alto",
            file_path=Path("src/god_class.py"),
            estimated_effort=7.5,
        )

        assert result.estimated_effort == 7.5

    def test_current_value_puede_ser_float(self):
        """current_value debe aceptar float además de int."""
        result = ReviewResult(
            analyzer_name="WMCAnalyzer",
            severity=ReviewSeverity.CRITICAL,
            current_value=25.3,
            threshold=20,
            message="WMC excesivo",
            file_path=Path("src/complex.py"),
        )

        assert result.current_value == 25.3


class TestReviewResultIsBlocking:
    """Tests para el método is_blocking()."""

    def test_critical_bloquea(self):
        """CRITICAL debe bloquear el merge."""
        result = ReviewResult(
            analyzer_name="CBOAnalyzer",
            severity=ReviewSeverity.CRITICAL,
            current_value=10,
            threshold=5,
            message="CBO excesivo",
            file_path=Path("src/foo.py"),
        )

        assert result.is_blocking() is True

    def test_warning_no_bloquea(self):
        """WARNING no debe bloquear el merge."""
        result = ReviewResult(
            analyzer_name="FanOutAnalyzer",
            severity=ReviewSeverity.WARNING,
            current_value=8,
            threshold=7,
            message="Fan-out elevado",
            file_path=Path("src/foo.py"),
        )

        assert result.is_blocking() is False

    def test_info_no_bloquea(self):
        """INFO no debe bloquear el merge."""
        result = ReviewResult(
            analyzer_name="CBOAnalyzer",
            severity=ReviewSeverity.INFO,
            current_value=2,
            threshold=5,
            message="CBO dentro del umbral",
            file_path=Path("src/foo.py"),
        )

        assert result.is_blocking() is False


class TestReviewResultStr:
    """Tests para la representación __str__ de ReviewResult."""

    def test_str_incluye_campos_clave(self):
        """__str__ debe incluir nombre del analyzer, severidad y mensaje."""
        result = ReviewResult(
            analyzer_name="CBOAnalyzer",
            severity=ReviewSeverity.CRITICAL,
            current_value=8,
            threshold=5,
            message="Acoplamiento excesivo",
            file_path=Path("src/service.py"),
        )

        texto = str(result)
        assert "CBOAnalyzer" in texto
        assert "CRITICAL" in texto
        assert "Acoplamiento excesivo" in texto
        assert "src/service.py" in texto

    def test_str_incluye_class_name_si_existe(self):
        """__str__ debe incluir el nombre de la clase si está definido."""
        result = ReviewResult(
            analyzer_name="LCOMAnalyzer",
            severity=ReviewSeverity.WARNING,
            current_value=3,
            threshold=1,
            message="Baja cohesión",
            file_path=Path("src/model.py"),
            class_name="UserModel",
        )

        assert "UserModel" in str(result)
