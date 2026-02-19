"""
Tests unitarios para DesignReviewerConfig y load_config().

Ticket: 1.7
"""

from pathlib import Path

import pytest

from quality_agents.designreviewer.config import AIConfig, DesignReviewerConfig, load_config


class TestAIConfig:
    """Tests para AIConfig de DesignReviewer."""

    def test_defaults(self):
        """Debe tener IA deshabilitada por defecto (opt-in)."""
        ai = AIConfig()

        assert ai.enabled is False
        assert ai.suggest_refactoring is True
        assert ai.max_tokens == 800

    def test_habilitada(self):
        """Debe poder habilitarse la IA."""
        ai = AIConfig(enabled=True)

        assert ai.enabled is True


class TestDesignReviewerConfig:
    """Tests para DesignReviewerConfig."""

    def test_defaults(self):
        """Debe tener los umbrales por defecto correctos."""
        config = DesignReviewerConfig()

        assert config.max_cbo == 5
        assert config.max_fan_out == 7
        assert config.max_dit == 5
        assert config.max_nop == 1
        assert config.max_lcom == 1
        assert config.max_wmc == 20

    def test_exclude_patterns_por_defecto(self):
        """Debe tener patrones de exclusión por defecto."""
        config = DesignReviewerConfig()

        assert "__pycache__" in config.exclude_patterns
        assert ".venv" in config.exclude_patterns

    def test_ai_deshabilitada_por_defecto(self):
        """La IA debe estar deshabilitada por defecto."""
        config = DesignReviewerConfig()

        assert isinstance(config.ai, AIConfig)
        assert config.ai.enabled is False

    def test_umbrales_personalizados(self):
        """Debe aceptar umbrales personalizados."""
        config = DesignReviewerConfig(max_cbo=3, max_wmc=15)

        assert config.max_cbo == 3
        assert config.max_wmc == 15
        # Resto mantiene defaults
        assert config.max_fan_out == 7

    def test_from_pyproject_toml_basico(self, tmp_path):
        """Debe leer umbrales desde [tool.designreviewer]."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.designreviewer]
max_cbo = 3
max_fan_out = 5
max_wmc = 15
""")

        config = DesignReviewerConfig.from_pyproject_toml(pyproject)

        assert config.max_cbo == 3
        assert config.max_fan_out == 5
        assert config.max_wmc == 15
        # Campos no especificados mantienen defaults
        assert config.max_dit == 5

    def test_from_pyproject_toml_con_ai(self, tmp_path):
        """Debe leer configuración de IA desde [tool.designreviewer.ai]."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.designreviewer]
max_cbo = 5

[tool.designreviewer.ai]
enabled = true
max_tokens = 1000
""")

        config = DesignReviewerConfig.from_pyproject_toml(pyproject)

        assert config.max_cbo == 5
        assert config.ai.enabled is True
        assert config.ai.max_tokens == 1000

    def test_from_pyproject_toml_sin_seccion_designreviewer(self, tmp_path):
        """Debe retornar defaults si no hay [tool.designreviewer]."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.other]
key = "value"
""")

        config = DesignReviewerConfig.from_pyproject_toml(pyproject)

        assert config.max_cbo == 5
        assert config.ai.enabled is False

    def test_from_pyproject_toml_archivo_inexistente(self, tmp_path):
        """Debe lanzar FileNotFoundError si el archivo no existe."""
        pyproject = tmp_path / "no_existe.toml"

        with pytest.raises(FileNotFoundError):
            DesignReviewerConfig.from_pyproject_toml(pyproject)


class TestLoadConfig:
    """Tests para la función load_config()."""

    def test_defaults_sin_config(self, tmp_path):
        """Debe retornar defaults si no hay ningún archivo de config."""
        config = load_config(project_root=tmp_path)

        assert isinstance(config, DesignReviewerConfig)
        assert config.max_cbo == 5
        assert config.ai.enabled is False

    def test_desde_pyproject_toml(self, tmp_path):
        """Debe auto-descubrir pyproject.toml en project_root."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.designreviewer]
max_cbo = 3
max_wmc = 10

[tool.designreviewer.ai]
enabled = true
""")

        config = load_config(project_root=tmp_path)

        assert config.max_cbo == 3
        assert config.max_wmc == 10
        assert config.ai.enabled is True

    def test_config_path_explicito(self, tmp_path):
        """Debe cargar desde path explícito cuando se provee."""
        config_file = tmp_path / "custom.toml"
        config_file.write_text("""
[tool.designreviewer]
max_fan_out = 4
""")

        config = load_config(config_path=config_file)

        assert config.max_fan_out == 4

    def test_config_path_inexistente_usa_defaults(self, tmp_path):
        """Debe retornar defaults si el path explícito no existe."""
        config_file = tmp_path / "no_existe.toml"

        config = load_config(config_path=config_file)

        assert config.max_cbo == 5

    def test_pyproject_sin_seccion_usa_defaults(self, tmp_path):
        """Si pyproject.toml existe pero sin [tool.designreviewer], usa defaults."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.codeguard]
max_line_length = 100
""")

        config = load_config(project_root=tmp_path)

        assert config.max_cbo == 5

    def test_retorna_instancia_valida_siempre(self):
        """load_config() siempre debe retornar una instancia de DesignReviewerConfig."""
        config = load_config()

        assert isinstance(config, DesignReviewerConfig)
        assert isinstance(config.ai, AIConfig)
