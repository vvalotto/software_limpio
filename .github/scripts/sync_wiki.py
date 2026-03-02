#!/usr/bin/env python3
"""
Sincroniza docs/ (sin docs/curso/) al wiki de GitHub.

Uso:
    GITHUB_REPO=owner/repo python sync_wiki.py

Transformaciones de links:
    - [text](path/file.md)         →  [text](path/file)          (dentro de docs/)
    - [text](path/file.md#anchor)  →  [text](path/file#anchor)   (dentro de docs/)
    - [text](../../examples/x.yml) →  [text](GitHub URL)         (fuera de docs/)
    - [text](https://...)          →  sin cambios                 (absolutos)
"""

import os
import re
import shutil
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DOCS_DIR = REPO_ROOT / "docs"
WIKI_DIR = REPO_ROOT / "wiki"

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

EXCLUDE_DIRS = {"curso"}
GITHUB_REPO = os.environ.get("GITHUB_REPO", "vvalotto/software_limpio")
GITHUB_BASE_URL = f"https://github.com/{GITHUB_REPO}"


# ---------------------------------------------------------------------------
# Transformación de links
# ---------------------------------------------------------------------------

def transform_links(content: str, src_file: Path) -> str:
    """
    Transforma links Markdown para que funcionen en la wiki de GitHub.

    Links a .md dentro de docs/  → wiki links (sin extensión .md)
    Links a archivos fuera docs/ → links al repositorio en GitHub
    Links absolutos / anchors    → sin cambios
    """

    def replace(match: re.Match) -> str:
        text = match.group(1)
        raw_url = match.group(2)

        # Separar URL de anchor (#section)
        if "#" in raw_url:
            url_part, anchor = raw_url.split("#", 1)
            anchor_suffix = f"#{anchor}"
        else:
            url_part, anchor_suffix = raw_url, ""

        # Links absolutos o anchors puros → sin cambios
        if url_part.startswith(("http://", "https://")) or not url_part:
            return match.group(0)

        # Resolver la ruta absoluta del destino
        target = (src_file.parent / url_part).resolve()

        if url_part.endswith(".md"):
            try:
                # Destino dentro de docs/ → link wiki (sin .md)
                rel_to_docs = target.relative_to(DOCS_DIR)
                wiki_path = str(rel_to_docs.with_suffix(""))
                return f"[{text}]({wiki_path}{anchor_suffix})"
            except ValueError:
                pass

        # Destino fuera de docs/ → link al repo en GitHub
        try:
            rel_to_repo = target.relative_to(REPO_ROOT)
            github_url = f"{GITHUB_BASE_URL}/blob/main/{rel_to_repo}"
            return f"[{text}]({github_url}{anchor_suffix})"
        except ValueError:
            return match.group(0)

    # Solo links inline [text](url), no imágenes ![text](url)
    return re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", replace, content)


# ---------------------------------------------------------------------------
# Operaciones sobre el wiki
# ---------------------------------------------------------------------------

def clear_wiki() -> None:
    """Elimina el contenido del wiki preservando .git y _Sidebar.md existente."""
    preserve = {".git", "_Sidebar.md"}
    for item in WIKI_DIR.iterdir():
        if item.name in preserve:
            continue
        shutil.rmtree(item) if item.is_dir() else item.unlink()


def sync_docs() -> int:
    """Copia y transforma archivos docs/ → wiki/. Retorna cantidad de archivos."""
    count = 0
    for src in sorted(DOCS_DIR.rglob("*.md")):
        rel = src.relative_to(DOCS_DIR)
        if rel.parts[0] in EXCLUDE_DIRS:
            continue
        dst = WIKI_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        content = src.read_text(encoding="utf-8")
        content = transform_links(content, src)
        dst.write_text(content, encoding="utf-8")
        count += 1
    return count


def generate_home() -> None:
    """Genera Home.md como página de entrada del wiki."""
    content = f"""\
# Software Limpio — Documentación

Framework de control de calidad automatizado para Python.
Tres agentes, tres niveles, un pipeline continuo.

| Agente | Nivel | Cuándo usar |
|---|---|---|
| [CodeGuard](guias/codeguard) | Código | Pre-commit (< 5s) |
| [DesignReviewer](guias/designreviewer) | Diseño | Pull Request (2-5 min) |
| [ArchitectAnalyst](guias/architectanalyst) | Arquitectura | Fin de sprint (10-30 min) |

## Secciones

- [Guías de Usuario](guias/README) — Instalación, uso y configuración de los tres agentes
- [Especificación Técnica](agentes/README) — Arquitectura interna y decisiones de diseño
- [Teoría](teoria/README) — Fundamentos, principios y marco conceptual
- [Métricas](metricas/README) — Catálogo completo con umbrales y herramientas

---

*Documentación sincronizada automáticamente desde el \
[repositorio principal]({GITHUB_BASE_URL}).*
"""
    (WIKI_DIR / "Home.md").write_text(content, encoding="utf-8")


def generate_sidebar() -> None:
    """Genera _Sidebar.md con la navegación completa del wiki."""
    sections = [
        ("Guías", "guias"),
        ("Agentes", "agentes"),
        ("Teoría", "teoria"),
        ("Métricas", "metricas"),
    ]

    lines = ["**[Software Limpio](Home)**\n\n"]

    for section_name, section_dir in sections:
        section_path = DOCS_DIR / section_dir
        if not section_path.exists():
            continue

        lines.append(f"**{section_name}**\n")

        for md_file in sorted(section_path.rglob("*.md")):
            rel = md_file.relative_to(DOCS_DIR)
            depth = len(rel.parts) - 1
            indent = "  " * depth

            stem = md_file.stem
            if stem == "README":
                if depth == 0:
                    name = section_name
                else:
                    name = md_file.parent.name.replace("_", " ").replace("-", " ").title()
            else:
                name = stem.replace("_", " ").replace("-", " ").title()

            wiki_path = str(rel.with_suffix(""))
            lines.append(f"{indent}- [{name}]({wiki_path})\n")

        lines.append("\n")

    (WIKI_DIR / "_Sidebar.md").write_text("".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not WIKI_DIR.exists():
        print(
            "ERROR: El directorio wiki/ no existe.\n"
            "El workflow debe clonar la wiki antes de ejecutar este script."
        )
        raise SystemExit(1)

    print("Limpiando wiki...")
    clear_wiki()

    print("Sincronizando docs/ → wiki/...")
    count = sync_docs()
    print(f"  {count} archivos procesados")

    print("Generando Home.md...")
    generate_home()

    print("Generando _Sidebar.md...")
    generate_sidebar()

    print("✓ Sincronización completa")


if __name__ == "__main__":
    main()
