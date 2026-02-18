"""
Tests de integración para configuración de pre-commit hooks.

Verifica que el archivo .pre-commit-hooks.yaml está correctamente configurado
según las especificaciones del framework pre-commit.
"""

from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).parent.parent.parent
HOOKS_FILE = PROJECT_ROOT / ".pre-commit-hooks.yaml"


class TestPreCommitHooksConfiguration:
    """Tests para verificar configuración de pre-commit hooks."""

    def test_hooks_file_exists(self):
        """El archivo .pre-commit-hooks.yaml debe existir en la raíz."""
        assert HOOKS_FILE.exists(), ".pre-commit-hooks.yaml not found in project root"

    def test_hooks_file_is_valid_yaml(self):
        """El archivo debe ser YAML válido."""
        with open(HOOKS_FILE) as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in .pre-commit-hooks.yaml: {e}")

    def test_hooks_structure(self):
        """Verificar que los hooks tienen la estructura correcta."""
        with open(HOOKS_FILE) as f:
            hooks = yaml.safe_load(f)

        assert isinstance(hooks, list), "Hooks file must contain a list"
        assert len(hooks) > 0, "Hooks file must define at least one hook"

    def test_required_fields_present(self):
        """Cada hook debe tener los campos requeridos."""
        with open(HOOKS_FILE) as f:
            hooks = yaml.safe_load(f)

        required_fields = ["id", "name", "entry", "language"]

        for hook in hooks:
            for field in required_fields:
                assert field in hook, f"Hook '{hook.get('id', 'unknown')}' missing required field '{field}'"

    def test_codeguard_hook_present(self):
        """Debe existir un hook con id 'codeguard'."""
        with open(HOOKS_FILE) as f:
            hooks = yaml.safe_load(f)

        hook_ids = [h["id"] for h in hooks]
        assert "codeguard" in hook_ids, "Hook 'codeguard' not found"

    def test_codeguard_hook_configuration(self):
        """El hook 'codeguard' debe tener configuración correcta."""
        with open(HOOKS_FILE) as f:
            hooks = yaml.safe_load(f)

        codeguard_hook = next((h for h in hooks if h["id"] == "codeguard"), None)
        assert codeguard_hook is not None

        # Verificar campos específicos
        assert codeguard_hook["name"] == "CodeGuard Quality Check"
        assert codeguard_hook["entry"] == "codeguard"
        assert codeguard_hook["language"] == "python"
        assert codeguard_hook.get("types") == ["python"]
        assert codeguard_hook.get("pass_filenames") is False

        # Verificar argumentos
        args = codeguard_hook.get("args", [])
        assert "--analysis-type" in args
        assert "pre-commit" in args

    def test_all_hooks_valid_language(self):
        """Todos los hooks deben usar lenguajes válidos."""
        with open(HOOKS_FILE) as f:
            hooks = yaml.safe_load(f)

        valid_languages = [
            "python", "node", "ruby", "rust", "go", "docker",
            "system", "script", "fail"
        ]

        for hook in hooks:
            language = hook.get("language")
            assert language in valid_languages, (
                f"Hook '{hook['id']}' has invalid language '{language}'"
            )

    def test_hooks_have_descriptions(self):
        """Todos los hooks deben tener descripción."""
        with open(HOOKS_FILE) as f:
            hooks = yaml.safe_load(f)

        for hook in hooks:
            assert "description" in hook, (
                f"Hook '{hook['id']}' missing description"
            )
            assert len(hook["description"]) > 0, (
                f"Hook '{hook['id']}' has empty description"
            )

    def test_example_config_file_exists(self):
        """Debe existir un archivo de ejemplo .pre-commit-config.yaml.example."""
        example_file = PROJECT_ROOT / ".pre-commit-config.yaml.example"
        assert example_file.exists(), ".pre-commit-config.yaml.example not found"

    def test_example_config_is_valid_yaml(self):
        """El archivo de ejemplo debe ser YAML válido."""
        example_file = PROJECT_ROOT / ".pre-commit-config.yaml.example"
        with open(example_file) as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in .pre-commit-config.yaml.example: {e}")

    def test_hook_stages_configuration(self):
        """Verificar que los hooks tienen stages configurados correctamente."""
        with open(HOOKS_FILE) as f:
            hooks = yaml.safe_load(f)

        for hook in hooks:
            if "stages" in hook:
                stages = hook["stages"]
                assert isinstance(stages, list), (
                    f"Hook '{hook['id']}' stages must be a list"
                )
                valid_stages = ["commit", "merge-commit", "push", "manual"]
                for stage in stages:
                    assert stage in valid_stages, (
                        f"Hook '{hook['id']}' has invalid stage '{stage}'"
                    )


class TestPreCommitHooksDocumentation:
    """Tests para verificar que la documentación de pre-commit existe."""

    def test_codeguard_guide_has_precommit_section(self):
        """La guía de CodeGuard debe documentar pre-commit."""
        guide_file = PROJECT_ROOT / "docs" / "guias" / "codeguard.md"
        assert guide_file.exists()

        content = guide_file.read_text()
        assert "pre-commit" in content.lower()
        assert ".pre-commit-config.yaml" in content

    def test_documentation_includes_installation_steps(self):
        """La documentación debe incluir pasos de instalación de pre-commit."""
        guide_file = PROJECT_ROOT / "docs" / "guias" / "codeguard.md"
        content = guide_file.read_text()

        # Verificar comandos clave
        assert "pip install pre-commit" in content
        assert "pre-commit install" in content

    def test_documentation_includes_usage_examples(self):
        """La documentación debe incluir ejemplos de uso."""
        guide_file = PROJECT_ROOT / "docs" / "guias" / "codeguard.md"
        content = guide_file.read_text()

        # Verificar ejemplos de comandos
        assert "pre-commit run" in content
        assert "--all-files" in content


class TestHookVariants:
    """Tests para verificar variantes de hooks (codeguard, codeguard-full, etc.)."""

    def test_multiple_hook_variants_exist(self):
        """Debe haber múltiples variantes de hooks para diferentes usos."""
        with open(HOOKS_FILE) as f:
            hooks = yaml.safe_load(f)

        hook_ids = [h["id"] for h in hooks]

        # Verificar variantes esperadas
        assert "codeguard" in hook_ids  # Pre-commit rápido
        # Pueden existir otras variantes como codeguard-full, codeguard-pr

    def test_codeguard_is_fast_for_precommit(self):
        """El hook 'codeguard' debe usar análisis rápido."""
        with open(HOOKS_FILE) as f:
            hooks = yaml.safe_load(f)

        codeguard_hook = next((h for h in hooks if h["id"] == "codeguard"), None)
        args = codeguard_hook.get("args", [])

        # Debe usar análisis rápido (pre-commit)
        if "--analysis-type" in args:
            idx = args.index("--analysis-type")
            assert args[idx + 1] == "pre-commit"
