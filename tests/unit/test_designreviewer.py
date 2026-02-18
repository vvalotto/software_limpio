"""
Tests unitarios para DesignReviewer.
"""


from quality_agents.designreviewer import DesignReviewer
from quality_agents.designreviewer.agent import ReviewResult, ReviewSeverity


class TestDesignReviewer:
    """Tests para el agente DesignReviewer."""

    def test_init_default(self):
        """Debe inicializarse con valores por defecto."""
        reviewer = DesignReviewer()

        assert reviewer.config_path is None
        assert reviewer.ai_enabled is True
        assert reviewer.results == []

    def test_init_ai_disabled(self):
        """Debe poder deshabilitarse IA."""
        reviewer = DesignReviewer(ai_enabled=False)

        assert reviewer.ai_enabled is False

    def test_analyze_returns_list(self, temp_project):
        """analyze() debe retornar lista de resultados."""
        reviewer = DesignReviewer(ai_enabled=False)
        results = reviewer.analyze(temp_project)

        assert isinstance(results, list)

    def test_should_block_no_criticals(self):
        """should_block() debe retornar False sin críticos."""
        reviewer = DesignReviewer()
        reviewer.results = [
            ReviewResult(
                metric_name="test",
                severity=ReviewSeverity.WARNING,
                current_value=5,
                threshold=10,
                message="Warning"
            )
        ]

        assert reviewer.should_block() is False

    def test_should_block_with_critical(self):
        """should_block() debe retornar True con críticos."""
        reviewer = DesignReviewer()
        reviewer.results = [
            ReviewResult(
                metric_name="test",
                severity=ReviewSeverity.CRITICAL,
                current_value=15,
                threshold=10,
                message="Critical"
            )
        ]

        assert reviewer.should_block() is True


class TestReviewResult:
    """Tests para ReviewResult."""

    def test_create_review_result(self):
        """Debe crear ReviewResult correctamente."""
        result = ReviewResult(
            metric_name="CBO",
            severity=ReviewSeverity.WARNING,
            current_value=7,
            threshold=5,
            message="Alto acoplamiento",
            suggestion="Considerar extraer dependencias"
        )

        assert result.metric_name == "CBO"
        assert result.current_value == 7
        assert result.threshold == 5
        assert result.suggestion is not None


class TestReviewSeverity:
    """Tests para ReviewSeverity enum."""

    def test_severity_values(self):
        """Debe tener los valores correctos."""
        assert ReviewSeverity.INFO.value == "info"
        assert ReviewSeverity.WARNING.value == "warning"
        assert ReviewSeverity.CRITICAL.value == "critical"
