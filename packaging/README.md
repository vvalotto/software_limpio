# 📦 Packaging - Distribución de CodeGuard

> Documentación y herramientas para empaquetar y distribuir **quality-agents** en PyPI

---

## 📋 Contenido de esta Carpeta

| Archivo | Descripción |
|---------|-------------|
| **QUICKSTART.md** | Guía de inicio rápido (5 minutos) para usar CodeGuard en otros proyectos |
| **DISTRIBUTION.md** | Guía completa de distribución en PyPI/TestPyPI |
| **RESUMEN.md** | Resumen ejecutivo del estado de distribución |
| **build.sh** | Script automatizado de build (tests + build + validate) |
| **publish.sh** | Script automatizado de publicación (TestPyPI o PyPI) |

---

## 🚀 Uso Rápido

### Build del Paquete

```bash
# Desde la raíz del proyecto
./packaging/build.sh
```

Esto ejecuta:
1. Limpieza de builds anteriores
2. Tests completos
3. Quality checks con CodeGuard
4. Build de distribuciones (wheel + sdist)
5. Validación con twine

### Publicación

```bash
# Publicar en TestPyPI (prueba)
./packaging/publish.sh test

# Publicar en PyPI (producción)
./packaging/publish.sh prod
```

---

## 📚 Documentación

- **QUICKSTART.md** - Lee esto primero si querés usar CodeGuard en tus proyectos
- **DISTRIBUTION.md** - Lee esto si querés publicar en PyPI
- **RESUMEN.md** - Estado actual del proyecto y próximos pasos

---

## 🔗 Links Útiles

- **PyPI:** https://pypi.org/
- **TestPyPI:** https://test.pypi.org/
- **Python Packaging Guide:** https://packaging.python.org/
- **Twine Docs:** https://twine.readthedocs.io/

---

**Software Limpio** - Control de Calidad Automatizado para Python 🚀
