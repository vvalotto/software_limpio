#!/bin/bash

# =============================================================================
# Script de Demostración de CodeGuard
# =============================================================================
#
# Este script ejecuta CodeGuard con diferentes configuraciones para demostrar
# sus capacidades de análisis de calidad de código.
#
# Uso: ./demo.sh
#

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Header
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        CodeGuard - Demostración de Análisis de Calidad      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if codeguard is installed
if ! command -v codeguard &> /dev/null; then
    echo -e "${RED}ERROR: codeguard no está instalado${NC}"
    echo ""
    echo "Instalación:"
    echo "  cd ../.."
    echo "  pip install -e \".[dev]\""
    exit 1
fi

# Verificar que estamos en el directorio correcto
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}ERROR: Ejecutar desde examples/sample_project/${NC}"
    exit 1
fi

echo -e "${YELLOW}Proyecto de ejemplo con problemas intencionales de calidad${NC}"
echo ""
echo "Archivos a analizar:"
echo "  • src/calculator.py       - Código limpio + alta complejidad"
echo "  • src/security_issues.py  - Vulnerabilidades de seguridad"
echo "  • src/style_issues.py     - Violaciones de PEP8"
echo "  • src/imports_and_types.py - Imports sin usar, tipos faltantes"
echo ""

# =============================================================================
# Demo 1: Análisis Pre-commit (< 5s)
# =============================================================================

echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Demo 1: Análisis Pre-commit (< 5s)${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Solo checks críticos (priority 1-3):"
echo "  • SecurityCheck (priority 1)"
echo "  • PEP8Check (priority 2)"
echo "  • ComplexityCheck (priority 3)"
echo ""
echo -e "${YELLOW}Ejecutando: codeguard --analysis-type pre-commit .${NC}"
echo ""

codeguard --analysis-type pre-commit .

echo ""
echo -e "${BLUE}Presiona ENTER para continuar...${NC}"
read

# =============================================================================
# Demo 2: Análisis PR-Review (~10-15s)
# =============================================================================

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Demo 2: Análisis PR-Review (~10-15s)${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Checks importantes (priority 1-5):"
echo "  • Security, PEP8, Complexity (como pre-commit)"
echo "  • PylintCheck (priority 4)"
echo "  • TypeCheck (priority 5)"
echo ""
echo -e "${YELLOW}Ejecutando: codeguard --analysis-type pr-review .${NC}"
echo ""

codeguard --analysis-type pr-review .

echo ""
echo -e "${BLUE}Presiona ENTER para continuar...${NC}"
read

# =============================================================================
# Demo 3: Análisis Completo (~20-30s)
# =============================================================================

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Demo 3: Análisis Completo (~20-30s)${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Todos los checks (priority 1-6):"
echo "  • Todos los anteriores +"
echo "  • ImportCheck (priority 6)"
echo ""
echo -e "${YELLOW}Ejecutando: codeguard --analysis-type full .${NC}"
echo ""

codeguard --analysis-type full .

echo ""
echo -e "${BLUE}Presiona ENTER para continuar...${NC}"
read

# =============================================================================
# Demo 4: Output en JSON
# =============================================================================

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Demo 4: Output en JSON (para CI/CD)${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Formato JSON con metadata completa."
echo ""
echo -e "${YELLOW}Ejecutando: codeguard --format json . | jq${NC}"
echo ""

if command -v jq &> /dev/null; then
    codeguard --format json . | jq
else
    echo -e "${YELLOW}jq no instalado, mostrando JSON sin formatear:${NC}"
    echo ""
    codeguard --format json .
fi

echo ""
echo -e "${BLUE}Presiona ENTER para continuar...${NC}"
read

# =============================================================================
# Demo 5: Análisis con Presupuesto de Tiempo
# =============================================================================

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Demo 5: Análisis con Presupuesto de Tiempo (3s)${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Ejecuta solo checks que caben en 3 segundos."
echo "Orquestador selecciona por prioridad."
echo ""
echo -e "${YELLOW}Ejecutando: codeguard --time-budget 3.0 .${NC}"
echo ""

codeguard --time-budget 3.0 .

# =============================================================================
# Resumen
# =============================================================================

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Demostración Completada${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Revisar los problemas detectados"
echo "2. Corregir algunos problemas:"
echo "   • black src/ --line-length 100"
echo "   • autoflake --remove-unused-variables --in-place src/*.py"
echo "   • isort src/ --profile black"
echo ""
echo "3. Re-ejecutar CodeGuard para verificar:"
echo "   • codeguard ."
echo ""
echo "4. Integrar con pre-commit:"
echo "   • pip install pre-commit"
echo "   • pre-commit install"
echo "   • git add . && git commit -m 'Test'"
echo ""
echo "5. Usar en tus propios proyectos"
echo ""
echo -e "${BLUE}Documentación completa: ../../docs/guias/codeguard.md${NC}"
echo ""
