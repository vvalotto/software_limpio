#!/usr/bin/env python3
"""
Sincroniza docs/ (sin docs/curso/) al wiki de GitHub con estructura plana.

GitHub Wiki no sirve archivos en subdirectorios como páginas wiki, por lo que
todos los archivos se copian al nivel raíz con un nombre que evita conflictos.

Mapeo de nombres:
    docs/guias/codeguard.md              → codeguard.md
    docs/guias/README.md                 → guias.md
    docs/teoria/fundamentos/README.md    → fundamentos.md
    docs/teoria/fundamentos/01_mod.md    → 01_mod.md

Uso:
    GITHUB_REPO=owner/repo python sync_wiki.py
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
# Mapeo de nombres: path en docs/ → nombre de página wiki (sin extensión)
# ---------------------------------------------------------------------------

def wiki_page_name(src: Path) -> str:
    """
    Genera el nombre de página wiki (sin .md) para un archivo de docs/.

    README.md → nombre del directorio padre (o 'Home' si está en la raíz)
    Cualquier otro → stem del archivo
    """
    rel = src.relative_to(DOCS_DIR)
    if src.stem == "README":
        parent = rel.parent
        return parent.name if str(parent) != "." else "Home"
    return src.stem


def build_page_map() -> dict[Path, str]:
    """
    Construye el mapa {path_en_docs → nombre_wiki} para todos los archivos
    a sincronizar. Detecta colisiones de nombres y falla explícitamente.
    """
    page_map: dict[Path, str] = {}
    names_seen: dict[str, Path] = {}

    for src in sorted(DOCS_DIR.rglob("*.md")):
        rel = src.relative_to(DOCS_DIR)
        if rel.parts[0] in EXCLUDE_DIRS:
            continue
        name = wiki_page_name(src)
        if name in names_seen:
            raise ValueError(
                f"Colisión de nombres wiki: '{name}'\n"
                f"  {names_seen[name]}\n"
                f"  {src}"
            )
        page_map[src] = name
        names_seen[name] = src

    return page_map


# ---------------------------------------------------------------------------
# Transformación de links
# ---------------------------------------------------------------------------

def make_link_transformer(page_map: dict[Path, str]):
    """Retorna una función que transforma links Markdown para la wiki plana."""

    # Mapa inverso: path absoluto → nombre wiki
    path_to_name = {src.resolve(): name for src, name in page_map.items()}

    def transform_links(content: str, src_file: Path) -> str:
        """
        Transforma links Markdown:
          - [text](otro_doc.md)        → [text](nombre_wiki)
          - [text](otro_doc.md#anchor) → [text](nombre_wiki#anchor)
          - [text](../../examples/x)   → [text](URL GitHub)
          - [text](https://...)        → sin cambios
        """

        def replace(match: re.Match) -> str:
            text = match.group(1)
            raw_url = match.group(2)

            # Separar anchor del URL
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

            # Destino dentro de docs/ → nombre de página wiki
            if target in path_to_name:
                return f"[{text}]({path_to_name[target]}{anchor_suffix})"

            # Destino fuera de docs/ → link al repo en GitHub
            try:
                rel_to_repo = target.relative_to(REPO_ROOT)
                github_url = f"{GITHUB_BASE_URL}/blob/main/{rel_to_repo}"
                return f"[{text}]({github_url}{anchor_suffix})"
            except ValueError:
                return match.group(0)

        # Solo links inline [text](url), no imágenes ![text](url)
        return re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", replace, content)

    return transform_links


# ---------------------------------------------------------------------------
# Operaciones sobre el wiki
# ---------------------------------------------------------------------------

def clear_wiki() -> None:
    """Elimina el contenido del wiki preservando .git."""
    for item in WIKI_DIR.iterdir():
        if item.name == ".git":
            continue
        shutil.rmtree(item) if item.is_dir() else item.unlink()


def sync_docs(page_map: dict[Path, str], transform_links) -> None:
    """Copia y transforma archivos docs/ → wiki/ con estructura plana."""
    for src, name in page_map.items():
        dst = WIKI_DIR / f"{name}.md"
        content = src.read_text(encoding="utf-8")
        content = transform_links(content, src)
        dst.write_text(content, encoding="utf-8")
    print(f"  {len(page_map)} archivos procesados")


def generate_home() -> None:
    """Genera Home.md como página de entrada del wiki."""
    content = f"""\
# Software Limpio — Documentación

Framework de control de calidad automatizado para Python.
Tres agentes, tres niveles, un pipeline continuo.

| Agente | Nivel | Cuándo usar |
|---|---|---|
| [CodeGuard](codeguard) | Código | Pre-commit (< 5s) |
| [DesignReviewer](designreviewer) | Diseño | Pull Request (2-5 min) |
| [ArchitectAnalyst](architectanalyst) | Arquitectura | Fin de sprint (10-30 min) |

## Secciones

- [Guías de Usuario](guias) — Instalación, uso y configuración de los tres agentes
- [Especificación Técnica](agentes) — Arquitectura interna y decisiones de diseño
- [Teoría](teoria) — Fundamentos, principios y marco conceptual
- [Métricas](metricas) — Catálogo completo con umbrales y herramientas

---

*Documentación sincronizada automáticamente desde el \
[repositorio principal]({GITHUB_BASE_URL}).*
"""
    (WIKI_DIR / "Home.md").write_text(content, encoding="utf-8")


def generate_sidebar(page_map: dict[Path, str]) -> None:
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

        for src in sorted(section_path.rglob("*.md")):
            if src not in page_map:
                continue
            rel = src.relative_to(DOCS_DIR)
            depth = len(rel.parts) - 1
            indent = "  " * depth
            name = page_map[src]

            # Etiqueta legible
            stem = src.stem
            if stem == "README":
                if depth == 0:
                    label = section_name
                else:
                    label = src.parent.name.replace("_", " ").replace("-", " ").title()
            else:
                label = stem.replace("_", " ").replace("-", " ").title()

            lines.append(f"{indent}- [{label}]({name})\n")

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

    print("Construyendo mapa de páginas...")
    page_map = build_page_map()
    print(f"  {len(page_map)} archivos encontrados")

    transform_links = make_link_transformer(page_map)

    print("Limpiando wiki...")
    clear_wiki()

    print("Sincronizando docs/ → wiki/ (estructura plana)...")
    sync_docs(page_map, transform_links)

    print("Generando Home.md...")
    generate_home()

    print("Generando _Sidebar.md...")
    generate_sidebar(page_map)

    print("✓ Sincronización completa")


if __name__ == "__main__":
    main()
