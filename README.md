## Hi there 👋

<!--
**cinvestavusicamm/CinvestavUsicamm** is a ✨ _special_ ✨ repository because its `README.md` (this file) appears on your GitHub profile.

Here are some ideas to get you started:

- 🔭 I’m currently working on ...
- 🌱 I’m currently learning ...
- 👯 I’m looking to collaborate on ...
- 🤔 I’m looking for help with ...
- 💬 Ask me about ...
- 📫 How to reach me: ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...
-->
# Sistema de Gestión Escolar con IA (EscalofonIA) 🎓🤖

Base de datos relacional PostgreSQL diseñada para la gestión de instituciones educativas, optimizada con **pgvector** para funcionalidades de Inteligencia Artificial (RAG).

## 🚀 Características Técnicas
* **Motor:** PostgreSQL 16.
* **Infraestructura:** Servidor Ubuntu Linux accedido vía SSH y Tailscale VPN.
* **Inteligencia Artificial:** Implementación de búsqueda semántica vectorial para normativas educativas.
* **Seguridad:** Gestión de roles (RBAC) y sanitización de datos.

## 📂 Estructura del Proyecto
* `db_schema.sql`: Script principal con la creación de tablas, relaciones y vectores.
* `postgres.sql`: Scripts auxiliares de configuración.

## 🛠️ Instalación
1. Clonar el repositorio.
2. Ejecutar el script `db_schema.sql` en una instancia de PostgreSQL con la extensión `vector` instalada.
