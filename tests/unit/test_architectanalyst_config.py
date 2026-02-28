"""
Tests unitarios para ArchitectAnalystConfig, AIConfig, LayersConfig y load_config().

Ticket: 1.6
"""

import pytest

from quality_agents.architectanalyst.config import (
    AIConfig,
    ArchitectAnalystConfig,
    LayersConfig,
    load_config,
)


class TestAIConfig:
    """Tests para AIConfig de ArchitectAnalyst."""

    def test_defaults(self):
        """IA debe estar deshabilitada por defecto (opt-in)."""
        ai = AIConfig()

        assert ai.enabled is False
        assert ai.max_tokens == 1500

    def test_habilitada(self):
        """Debe poder habilitarse."""
        ai = AIConfig(enabled=True)

        assert ai.enabled is True

    def test_max_tokens_personalizado(self):
        """Debe aceptar max_tokens personalizado."""
        ai = AIConfig(max_tokens=2000)

        assert ai.max_tokens == 2000


class TestLayersConfig:
    """Tests para LayersConfig."""

    def test_rules_vacio_por_defecto(self):
        """Sin reglas declaradas, el dict debe estar vacío."""
        layers = LayersConfig()

        assert layers.rules == {}

    def test_is_configured_sin_reglas(self):
        """is_configured() debe retornar False cuando no hay reglas."""
        assert not LayersConfig().is_configured()

    def test_is_configured_con_reglas(self):
        """is_configured() debe retornar True cuando hay reglas declaradas."""
        layers = LayersConfig(rules={"domain": [], "application": ["domain"]})

        assert layers.is_configured()

    def test_reglas_personalizadas(self):
        """Debe aceptar reglas de capas arbitrarias."""
        rules = {
            "domain": [],
            "application": ["domain"],
            "infrastructure": ["application", "domain"],
        }
        layers = LayersConfig(rules=rules)

        assert layers.rules["domain"] == []
        assert layers.rules["application"] == ["domain"]
        assert layers.rules["infrastructure"] == ["application", "domain"]


class TestArchitectAnalystConfig:
    """Tests para ArchitectAnalystConfig."""

    def test_defaults_martin_metrics(self):
        """Debe tener los umbrales de Martin correctos según el plan v0.3.0."""
        config = ArchitectAnalystConfig()

        assert config.max_instability == 0.8
        assert config.max_distance_warning == 0.3
        assert config.max_distance_critical == 0.5

    def test_defaults_db_path(self):
        """db_path debe apuntar a .quality_control/architecture.db por defecto."""
        config = ArchitectAnalystConfig()

        assert config.db_path == ".quality_control/architecture.db"

    def test_defaults_exclude_patterns(self):
        """Debe tener patrones de exclusión por defecto."""
        config = ArchitectAnalystConfig()

        assert "__pycache__" in config.exclude_patterns
        assert ".venv" in config.exclude_patterns
        assert "test_" in config.exclude_patterns

    def test_ai_deshabilitada_por_defecto(self):
        """La IA debe estar deshabilitada por defecto."""
        config = ArchitectAnalystConfig()

        assert isinstance(config.ai, AIConfig)
        assert config.ai.enabled is False

    def test_layers_sin_configurar_por_defecto(self):
        """Las capas no deben estar configuradas por defecto."""
        config = ArchitectAnalystConfig()

        assert isinstance(config.layers, LayersConfig)
        assert not config.layers.is_configured()

    def test_umbrales_personalizados(self):
        """Debe aceptar umbrales personalizados."""
        config = ArchitectAnalystConfig(
            max_instability=0.7,
            max_distance_warning=0.25,
            max_distance_critical=0.45,
        )

        assert config.max_instability == 0.7
        assert config.max_distance_warning == 0.25
        assert config.max_distance_critical == 0.45

    def test_from_pyproject_toml_basico(self, tmp_path):
        """Debe leer umbrales desde [tool.architectanalyst]."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.architectanalyst]
max_instability = 0.7
max_distance_warning = 0.25
max_distance_critical = 0.45
""")

        config = ArchitectAnalystConfig.from_pyproject_toml(pyproject)

        assert config.max_instability == 0.7
        assert config.max_distance_warning == 0.25
        assert config.max_distance_critical == 0.45
        # Campos no especificados mantienen defaults
        assert config.db_path == ".quality_control/architecture.db"

    def test_from_pyproject_toml_con_ai(self, tmp_path):
        """Debe leer configuración de IA desde [tool.architectanalyst.ai]."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.architectanalyst]
max_instability = 0.8

[tool.architectanalyst.ai]
enabled = true
max_tokens = 2000
""")

        config = ArchitectAnalystConfig.from_pyproject_toml(pyproject)

        assert config.ai.enabled is True
        assert config.ai.max_tokens == 2000

    def test_from_pyproject_toml_con_layers(self, tmp_path):
        """Debe leer reglas de capas desde [tool.architectanalyst.layers]."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.architectanalyst]
max_instability = 0.8

[tool.architectanalyst.layers]
domain = []
application = ["domain"]
infrastructure = ["application", "domain"]
""")

        config = ArchitectAnalystConfig.from_pyproject_toml(pyproject)

        assert config.layers.is_configured()
        assert config.layers.rules["domain"] == []
        assert config.layers.rules["application"] == ["domain"]

    def test_from_pyproject_toml_sin_seccion_retorna_defaults(self, tmp_path):
        """Debe retornar defaults si no hay [tool.architectanalyst]."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.other]
key = "value"
""")

        config = ArchitectAnalystConfig.from_pyproject_toml(pyproject)

        assert config.max_instability == 0.8
        assert config.ai.enabled is False

    def test_from_pyproject_toml_archivo_inexistente(self, tmp_path):
        """Debe lanzar FileNotFoundError si el archivo no existe."""
        pyproject = tmp_path / "no_existe.toml"

        with pytest.raises(FileNotFoundError):
            ArchitectAnalystConfig.from_pyproject_toml(pyproject)


class TestLoadConfig:
    """Tests para la función load_config()."""

    def test_defaults_sin_config(self, tmp_path):
        """Debe retornar defaults si no hay ningún archivo de config."""
        config = load_config(project_root=tmp_path)

        assert isinstance(config, ArchitectAnalystConfig)
        assert config.max_instability == 0.8
        assert config.ai.enabled is False

    def test_desde_pyproject_toml(self, tmp_path):
        """Debe auto-descubrir pyproject.toml en project_root."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.architectanalyst]
max_instability = 0.6
max_distance_critical = 0.4

[tool.architectanalyst.ai]
enabled = true
""")

        config = load_config(project_root=tmp_path)

        assert config.max_instability == 0.6
        assert config.max_distance_critical == 0.4
        assert config.ai.enabled is True

    def test_config_path_explicito(self, tmp_path):
        """Debe cargar desde path explícito cuando se provee."""
        config_file = tmp_path / "custom.toml"
        config_file.write_text("""
[tool.architectanalyst]
max_instability = 0.75
""")

        config = load_config(config_path=config_file)

        assert config.max_instability == 0.75

    def test_config_path_inexistente_usa_defaults(self, tmp_path):
        """Debe retornar defaults si el path explícito no existe."""
        config_file = tmp_path / "no_existe.toml"

        config = load_config(config_path=config_file)

        assert config.max_instability == 0.8

    def test_pyproject_sin_seccion_usa_defaults(self, tmp_path):
        """Si pyproject.toml existe pero sin [tool.architectanalyst], usa defaults."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.codeguard]
max_line_length = 100
""")

        config = load_config(project_root=tmp_path)

        assert config.max_instability == 0.8

    def test_retorna_instancia_valida_siempre(self):
        """load_config() siempre debe retornar una instancia válida."""
        config = load_config()

        assert isinstance(config, ArchitectAnalystConfig)
        assert isinstance(config.ai, AIConfig)
        assert isinstance(config.layers, LayersConfig)
