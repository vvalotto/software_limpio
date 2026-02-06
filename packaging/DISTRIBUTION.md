# 📦 Guía de Distribución - Software Limpio

> Instrucciones para empaquetar y distribuir **quality-agents** en PyPI

---

## 📋 Pre-requisitos

Antes de distribuir, asegurarse que:

- ✅ Todos los tests pasan (300/300)
- ✅ Versión actualizada en `pyproject.toml`
- ✅ README.md está completo
- ✅ CHANGELOG.md actualizado (crear si no existe)
- ✅ Documentación completa
- ✅ Licencia MIT incluida

---

## 🔧 Instalación de Herramientas

```bash
# Instalar herramientas de distribución
pip install --upgrade pip
pip install --upgrade build twine

# Verificar instalación
python -m build --version
twine --version
```

---

## 🏗️ Construir el Paquete

### 1. Limpiar builds anteriores

```bash
# Eliminar builds previos
rm -rf dist/ build/ *.egg-info

# Verificar que esté limpio
ls dist/  # No debe existir
```

### 2. Construir distribución

```bash
# Construir source distribution (sdist) y wheel
python -m build

# Resultado esperado:
# dist/
#   quality-agents-0.1.0.tar.gz      (source distribution)
#   quality_agents-0.1.0-py3-none-any.whl  (wheel)
```

### 3. Verificar el paquete

```bash
# Verificar archivos incluidos
tar -tzf dist/quality-agents-0.1.0.tar.gz | head -20

# Verificar metadatos
twine check dist/*

# Resultado esperado:
# Checking dist/quality-agents-0.1.0.tar.gz: PASSED
# Checking dist/quality_agents-0.1.0-py3-none-any.whl: PASSED
```

---

## 🧪 Prueba Local

### Instalación en entorno virtual limpio

```bash
# 1. Crear entorno virtual de prueba
python3.11 -m venv test_env
source test_env/bin/activate

# 2. Instalar desde wheel local
pip install dist/quality_agents-0.1.0-py3-none-any.whl

# 3. Verificar instalación
codeguard --version
# → quality-agents v0.1.0

# 4. Probar funcionamiento
codeguard examples/sample_project/

# 5. Desactivar y limpiar
deactivate
rm -rf test_env
```

---

## 🚀 Publicación

### Opción 1: TestPyPI (Prueba)

```bash
# 1. Crear cuenta en https://test.pypi.org/account/register/
# 2. Generar API token en https://test.pypi.org/manage/account/token/

# 3. Configurar token (una sola vez)
# Crear ~/.pypirc:
cat > ~/.pypirc << 'EOF'
[testpypi]
  username = __token__
  password = pypi-AgEI...  # Tu token de TestPyPI
EOF

# 4. Subir a TestPyPI
twine upload --repository testpypi dist/*

# 5. Verificar en: https://test.pypi.org/project/quality-agents/

# 6. Probar instalación desde TestPyPI
pip install --index-url https://test.pypi.org/simple/ quality-agents

# 7. Verificar
codeguard --version
```

### Opción 2: PyPI (Producción)

**⚠️ IMPORTANTE:** Solo ejecutar cuando estés 100% seguro. No se puede eliminar releases de PyPI.

```bash
# 1. Crear cuenta en https://pypi.org/account/register/
# 2. Generar API token en https://pypi.org/manage/account/token/

# 3. Configurar token
cat >> ~/.pypirc << 'EOF'
[pypi]
  username = __token__
  password = pypi-AgEI...  # Tu token de PyPI
EOF

# 4. Subir a PyPI
twine upload dist/*

# 5. Verificar en: https://pypi.org/project/quality-agents/
```

### Instalación desde PyPI

Una vez publicado, los usuarios podrán instalar con:

```bash
pip install quality-agents

# O con extras de desarrollo
pip install quality-agents[dev]
```

---

## 🏷️ Versionado

Seguimos [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Cambios incompatibles en API
- **MINOR** (0.1.0): Nuevas funcionalidades (compatible hacia atrás)
- **PATCH** (0.1.1): Correcciones de bugs

### Proceso de Release

1. **Actualizar versión** en `pyproject.toml`:
   ```toml
   [project]
   version = "0.1.0"  # Cambiar aquí
   ```

2. **Actualizar CHANGELOG.md** (crear si no existe):
   ```markdown
   # Changelog

   ## [0.1.0] - 2026-02-05

   ### Added
   - CodeGuard MVP completo con 6 checks modulares
   - Arquitectura modular con auto-discovery
   - Rich formatter profesional
   - Pre-commit framework integration
   - Documentación completa

   ### Fixed
   - Bug en AIConfig (campo 'model' inexistente)

   ### Tests
   - 300 tests pasando (100%)
   ```

3. **Crear tag de Git**:
   ```bash
   git tag -a v0.1.0 -m "Release v0.1.0 - CodeGuard MVP"
   git push origin v0.1.0
   ```

4. **Construir y publicar** (ver secciones anteriores)

---

## 📝 Checklist Pre-Release

Antes de publicar, verificar:

- [ ] `pytest` - Todos los tests pasan
- [ ] `black src/ tests/` - Código formateado
- [ ] `mypy src/` - Sin errores de tipos
- [ ] `codeguard .` - Sin errores críticos
- [ ] Versión actualizada en `pyproject.toml`
- [ ] CHANGELOG.md actualizado
- [ ] README.md completo y sin TODOs
- [ ] Documentación actualizada
- [ ] Ejemplos funcionan correctamente
- [ ] `python -m build` - Build exitoso
- [ ] `twine check dist/*` - Validación exitosa
- [ ] Prueba local en venv limpio
- [ ] Git tag creado
- [ ] Publicado en TestPyPI (opcional pero recomendado)

---

## 🔄 Actualización de Versión

Para publicar una nueva versión:

```bash
# 1. Actualizar versión en pyproject.toml
# [project]
# version = "0.1.1"  # Nueva versión

# 2. Actualizar CHANGELOG.md

# 3. Limpiar builds anteriores
rm -rf dist/ build/ *.egg-info

# 4. Construir nuevo paquete
python -m build

# 5. Verificar
twine check dist/*

# 6. Crear tag
git add pyproject.toml CHANGELOG.md
git commit -m "Release v0.1.1"
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin main
git push origin v0.1.1

# 7. Publicar en PyPI
twine upload dist/*
```

---

## 🐛 Solución de Problemas

### Error: "File already exists"

Si intentás subir la misma versión dos veces:

```bash
# Solución: Incrementar versión en pyproject.toml
# Ejemplo: 0.1.0 → 0.1.1
# Luego reconstruir y volver a subir
```

### Error: "Invalid distribution"

```bash
# Verificar estructura del paquete
python -m build --verbose

# Verificar contenido del wheel
unzip -l dist/quality_agents-0.1.0-py3-none-any.whl
```

### Error: "Metadata validation failed"

```bash
# Verificar pyproject.toml
cat pyproject.toml | grep -A 20 '\[project\]'

# Verificar con twine
twine check dist/*
```

---

## 📊 Post-Release

Después de publicar:

1. **Anunciar release**:
   - GitHub Releases: https://github.com/vvalotto/software_limpio/releases
   - README.md badges (agregar badge de PyPI)

2. **Verificar instalación**:
   ```bash
   pip install quality-agents
   codeguard --version
   ```

3. **Actualizar documentación**:
   - Cambiar instrucciones de instalación en README.md
   - Actualizar QUICKSTART.md con `pip install quality-agents`

4. **Monitorear**:
   - PyPI Downloads: https://pypistats.org/packages/quality-agents
   - GitHub Issues: https://github.com/vvalotto/software_limpio/issues

---

## 🎯 Roadmap de Versiones

| Versión | Descripción | Estado |
|---------|-------------|--------|
| **0.1.0** | MVP CodeGuard (6 checks, pre-commit, docs) | ✅ Listo |
| **0.2.0** | DesignReviewer completo | 🔜 Pendiente |
| **0.3.0** | ArchitectAnalyst completo | 🔜 Pendiente |
| **1.0.0** | Sistema completo (3 agentes estables) | 🔜 Futuro |

---

## 📚 Referencias

- **PyPI:** https://pypi.org/
- **TestPyPI:** https://test.pypi.org/
- **Python Packaging Guide:** https://packaging.python.org/
- **Twine Docs:** https://twine.readthedocs.io/
- **Build Docs:** https://build.pypa.io/

---

## 🆘 Ayuda

Si tenés problemas:

1. Revisar [Python Packaging Guide](https://packaging.python.org/tutorials/packaging-projects/)
2. Revisar logs de `twine upload --verbose`
3. Probar en TestPyPI primero
4. Reportar issue en GitHub

---

**Software Limpio** - Control de Calidad Automatizado para Python 🚀
