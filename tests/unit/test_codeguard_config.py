"""
Tests unitarios para configuración de CodeGuard.
"""


import pytest

from quality_agents.codeguard.config import AIConfig, CodeGuardConfig, load_config


class TestAIConfig:
    """Tests para AIConfig."""

    def test_default_values(self):
        """Debe tener valores por defecto correctos."""
        ai = AIConfig()

        assert ai.enabled is False  # Opt-in
        assert ai.explain_errors is True
        assert ai.suggest_fixes is True
        assert ai.max_tokens == 500

    def test_custom_values(self):
        """Debe aceptar valores personalizados."""
        ai = AIConfig(
            enabled=True,
            explain_errors=False,
            suggest_fixes=True,
            max_tokens=1000
        )

        assert ai.enabled is True
        assert ai.explain_errors is False
        assert ai.max_tokens == 1000


class TestCodeGuardConfig:
    """Tests para CodeGuardConfig."""

    def test_default_config(self):
        """Debe tener valores por defecto correctos."""
        config = CodeGuardConfig()

        # Umbrales
        assert config.min_pylint_score == 8.0
        assert config.max_cyclomatic_complexity == 10
        assert config.max_line_length == 100
        assert config.max_function_lines == 20

        # Checks
        assert config.check_pep8 is True
        assert config.check_pylint is True
        assert config.check_security is True
        assert config.check_complexity is True
        assert config.check_types is True
        assert config.check_imports is True

        # Exclusiones
        assert "__pycache__" in config.exclude_patterns
        assert ".venv" in config.exclude_patterns

        # IA
        assert isinstance(config.ai, AIConfig)
        assert config.ai.enabled is False  # Default opt-in

    def test_from_pyproject_toml_basic(self, tmp_path):
        """Debe leer configuración básica desde pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.codeguard]
min_pylint_score = 7.5
max_cyclomatic_complexity = 15
check_pep8 = false
check_security = true
exclude_patterns = ["tests/*", "migrations/*"]
""")

        config = CodeGuardConfig.from_pyproject_toml(pyproject)

        assert config.min_pylint_score == 7.5
        assert config.max_cyclomatic_complexity == 15
        assert config.check_pep8 is False
        assert config.check_security is True
        assert "tests/*" in config.exclude_patterns
        assert "migrations/*" in config.exclude_patterns

    def test_from_pyproject_toml_with_ai(self, tmp_path):
        """Debe leer configuración de IA desde pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.codeguard]
min_pylint_score = 8.0

[tool.codeguard.ai]
enabled = true
explain_errors = true
suggest_fixes = false
max_tokens = 800
""")

        config = CodeGuardConfig.from_pyproject_toml(pyproject)

        assert config.min_pylint_score == 8.0
        assert config.ai.enabled is True
        assert config.ai.explain_errors is True
        assert config.ai.suggest_fixes is False
        assert config.ai.max_tokens == 800

    def test_from_pyproject_toml_no_codeguard_section(self, tmp_path):
        """Debe retornar defaults si no hay sección [tool.codeguard]."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.other]
something = "value"
""")

        config = CodeGuardConfig.from_pyproject_toml(pyproject)

        # Debe retornar defaults
        assert config.min_pylint_score == 8.0
        assert config.ai.enabled is False

    def test_from_pyproject_toml_file_not_found(self, tmp_path):
        """Debe lanzar FileNotFoundError si el archivo no existe."""
        pyproject = tmp_path / "nonexistent.toml"

        with pytest.raises(FileNotFoundError):
            CodeGuardConfig.from_pyproject_toml(pyproject)

    def test_from_yaml_basic(self, tmp_path):
        """Debe leer configuración desde YAML."""
        config_file = tmp_path / "config.yml"
        config_file.write_text("""
min_pylint_score: 7.0
max_cyclomatic_complexity: 12
check_pep8: true
check_security: false
exclude_patterns:
  - "*.pyc"
  - "build/*"
""")

        config = CodeGuardConfig.from_yaml(config_file)

        assert config.min_pylint_score == 7.0
        assert config.max_cyclomatic_complexity == 12
        assert config.check_pep8 is True
        assert config.check_security is False
        assert "build/*" in config.exclude_patterns

    def test_from_yaml_with_ai(self, tmp_path):
        """Debe leer configuración de IA desde YAML."""
        config_file = tmp_path / "config.yml"
        config_file.write_text("""
min_pylint_score: 8.0
ai:
  enabled: true
  explain_errors: false
  suggest_fixes: true
  max_tokens: 600
""")

        config = CodeGuardConfig.from_yaml(config_file)

        assert config.min_pylint_score == 8.0
        assert config.ai.enabled is True
        assert config.ai.explain_errors is False
        assert config.ai.suggest_fixes is True
        assert config.ai.max_tokens == 600

    def test_from_yaml_empty_file(self, tmp_path):
        """Debe retornar defaults si el archivo YAML está vacío."""
        config_file = tmp_path / "empty.yml"
        config_file.write_text("")

        config = CodeGuardConfig.from_yaml(config_file)

        assert config.min_pylint_score == 8.0
        assert config.ai.enabled is False

    def test_to_yaml(self, tmp_path):
        """Debe guardar configuración a YAML correctamente."""
        config = CodeGuardConfig(
            min_pylint_score=7.5,
            check_pep8=False,
        )
        config.ai.enabled = True

        output_file = tmp_path / "output.yml"
        config.to_yaml(output_file)

        assert output_file.exists()

        # Leer de vuelta para verificar
        config_loaded = CodeGuardConfig.from_yaml(output_file)
        assert config_loaded.min_pylint_score == 7.5
        assert config_loaded.check_pep8 is False
        assert config_loaded.ai.enabled is True


class TestLoadConfig:
    """Tests para load_config()."""

    def test_load_config_explicit_path_toml(self, tmp_path):
        """Debe cargar desde path explícito (TOML)."""
        config_file = tmp_path / "custom.toml"
        config_file.write_text("""
[tool.codeguard]
min_pylint_score = 9.0
check_pep8 = false
""")

        config = load_config(config_path=config_file)

        assert config.min_pylint_score == 9.0
        assert config.check_pep8 is False

    def test_load_config_explicit_path_yaml(self, tmp_path):
        """Debe cargar desde path explícito (YAML)."""
        config_file = tmp_path / "custom.yml"
        config_file.write_text("""
min_pylint_score: 6.5
check_security: false
""")

        config = load_config(config_path=config_file)

        assert config.min_pylint_score == 6.5
        assert config.check_security is False

    def test_load_config_explicit_path_not_found(self, tmp_path):
        """Debe retornar defaults si path explícito no existe."""
        config_file = tmp_path / "nonexistent.yml"

        config = load_config(config_path=config_file)

        # Debe retornar defaults
        assert config.min_pylint_score == 8.0
        assert config.check_pep8 is True

    def test_load_config_from_pyproject_toml(self, tmp_path):
        """Debe auto-descubrir pyproject.toml en project_root."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.codeguard]
min_pylint_score = 7.0
max_cyclomatic_complexity = 12

[tool.codeguard.ai]
enabled = true
max_tokens = 600
""")

        config = load_config(project_root=tmp_path)

        assert config.min_pylint_score == 7.0
        assert config.max_cyclomatic_complexity == 12
        assert config.ai.enabled is True
        assert config.ai.max_tokens == 600

    def test_load_config_from_codeguard_yml(self, tmp_path):
        """Debe caer en fallback a .codeguard.yml si no hay pyproject.toml."""
        yml_file = tmp_path / ".codeguard.yml"
        yml_file.write_text("""
min_pylint_score: 6.0
check_types: false
""")

        config = load_config(project_root=tmp_path)

        assert config.min_pylint_score == 6.0
        assert config.check_types is False

    def test_load_config_pyproject_toml_priority_over_yml(self, tmp_path):
        """pyproject.toml debe tener prioridad sobre .codeguard.yml."""
        # Crear ambos archivos
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.codeguard]
min_pylint_score = 9.5
""")

        yml_file = tmp_path / ".codeguard.yml"
        yml_file.write_text("""
min_pylint_score: 5.0
""")

        config = load_config(project_root=tmp_path)

        # Debe cargar desde pyproject.toml (prioridad)
        assert config.min_pylint_score == 9.5

    def test_load_config_defaults_when_no_config_found(self, tmp_path):
        """Debe retornar defaults si no encuentra ningún archivo de config."""
        # tmp_path está vacío, no hay archivos de config

        config = load_config(project_root=tmp_path)

        # Debe retornar todos los defaults
        assert config.min_pylint_score == 8.0
        assert config.check_pep8 is True
        assert config.ai.enabled is False

    def test_load_config_default_project_root(self):
        """Debe usar directorio actual si no se provee project_root."""
        # No proveer project_root, debe usar Path.cwd()
        config = load_config()

        # Debe retornar una instancia válida (puede tener defaults o config del proyecto actual)
        assert isinstance(config, CodeGuardConfig)
        assert isinstance(config.ai, AIConfig)
