# Resumen del Pull Request

##  Tipo de Cambio
- [ ]  Nueva funcionalidad (Feature)
- [ ]  Corrección de error (Bugfix)
- [ ]  Refactorización / Deuda Técnica
- [ ]  Documentación

##  Descripción
*Describe de manera concisa QUÉ hace este PR y POR QUÉ es necesario. Incluye enlaces a tickets de Jira/Trello si aplica.*

##  Cómo probarlo (Instrucciones de QA)
1. *Paso 1...*
2. *Paso 2...*
3. *Comando de prueba:* `pytest tests/mi_modulo/`

##  Checklist de Ingeniería (Obligatorio)
- [ ] **Pre-commit:** El código pasa localmente las reglas de `black`, `ruff` y `bandit`.
- [ ] **Testing:** Se añadieron/actualizaron pruebas unitarias o de integración.
- [ ] **Migraciones:** Si hay cambios en modelos (Django/SQLAlchemy), se incluyó el archivo de migración.
- [ ] **Documentación:** Se actualizó Swagger/OpenAPI o los README correspondientes.
- [ ] **Seguridad:** No hay secretos (`.env`, passwords, tokens) quemados en el código.

## Cumplimiento ISO 25000
- [ ] Artefactos de diseño y reportes de rendimiento actualizados.
- [ ] Identificación de nuevos riesgos técnicos documentada.