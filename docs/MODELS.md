# Django Models Documentation - EscalafonIA Jaguar

## Overview

This document describes all Django models in the EscalafonIA Jaguar system. The system uses existing database tables (managed=False) and maps them to Django models for ORM access.

## Model Architecture

The system follows a modular architecture with models organized by domain:

- **User Management**: Usuario, Rol, Institucion
- **Geographic Data**: Estado, Municipio, CP, Colonia, Direccion, TipoHogar
- **Academic Content**: Curso, Foro, PostForo
- **Escalafón Process**: ProcesoEscalafon, Prom, ProcesoAprobacionCursos
- **AI Integration**: RetroalimentacionIaCurso, Document
- **Audit Trail**: BitacoraEvento

---

## User Management Models

### Usuario

**Purpose**: Represents a user in the system with authentication and profile information.

**Table**: `usuarios`

**Fields**:
- `id_usuario` (AutoField, Primary Key): Unique identifier for the user
- `nombre` (CharField, max_length=100): First name
- `apellido_paterno` (CharField, max_length=100): Paternal surname (required)
- `apellido_materno` (CharField, max_length=100, blank=True, null=True): Maternal surname (optional)
- `correo` (EmailField, unique=True): User's email address (must be unique)
- `contrasena` (CharField, max_length=255): Hashed password
- `curp` (CharField, max_length=18, unique=True): CURP (Mexican unique population code)
- `fecha_registro` (DateTimeField, default=timezone.now): Registration timestamp
- `ultimo_acceso` (DateTimeField, blank=True, null=True): Last login timestamp
- `activo` (BooleanField, default=True): Account active status
- `rol` (ForeignKey to Rol, on_delete=PROTECT, db_column='rol_id'): User's role (protected from deletion)
- `institucion` (ForeignKey to Institucion, on_delete=PROTECT, db_column='institucion_id): User's institution (protected from deletion)

**Methods**:
- `check_password(raw_password)`: Verifies if the provided raw password matches the stored hash

**Meta Options**:
- `db_table`: 'usuarios'
- `managed`: False (uses existing table)

**Relationships**:
- `cursos_impartidos` (Reverse ForeignKey from Curso): Courses taught by this user
- `procesos` (Reverse ForeignKey from ProcesoEscalafon): Escalafón processes for this user

**Notes**:
- Password is stored using Django's default hasher
- CURP must be unique across the system
- Role and institution are protected from deletion to maintain referential integrity

---

### Rol

**Purpose**: Defines user roles with associated permissions.

**Table**: `roles`

**Fields**:
- `id_rol` (AutoField, Primary Key): Unique identifier for the role
- `nombre_rol` (CharField, max_length=50, unique=True): Role name (e.g., 'Admin', 'Docente', 'Generador', 'Evaluador')

**Methods**:
- `__str__()`: Returns the role name

**Meta Options**:
- `db_table`: 'roles'
- `managed`: False
- `ordering`: ['nombre_rol']

**Notes**:
- Role names must be unique
- Used for role-based access control via `@requiere_rol` decorator
- Common roles: Admin, Docente, Generador, Evaluador, Agente

---

### Institucion

**Purpose**: Represents educational institutions where users work.

**Table**: `instituciones`

**Fields**:
- `id_institucion` (AutoField, Primary Key, db_column='id_instituciones'): Unique identifier
- `nombre` (CharField, max_length=150): Institution name
- `tipo` (CharField, max_length=100): Institution type (e.g., 'Primaria', 'Secundaria', 'Preparatoria')
- `activo` (BooleanField): Active status

**Meta Options**:
- `db_table`: 'instituciones'
- `managed`: False

**Notes**:
- Custom primary key column name: 'id_instituciones'
- Used to associate users with their workplace
- Active field allows soft deletion

---

## Geographic Data Models

### Estado

**Purpose**: Represents Mexican states (entidades federativas).

**Table**: (not specified, uses Django default)

**Fields**:
- `nombre` (CharField, max_length=100): State name
- `clave_estado` (CharField, max_length=10): State code (e.g., 'MX-CMX' for CDMX)

**Methods**:
- `__str__()`: Returns the state name

**Notes**:
- Used in address hierarchy
- No explicit table name in Meta (uses Django convention)

---

### Municipio

**Purpose**: Represents municipalities within states.

**Table**: (not specified)

**Fields**:
- `nombre` (CharField, max_length=100): Municipality name
- `clave_municipio` (CharField, max_length=10): Municipality code
- `estado` (ForeignKey to Estado, on_delete=CASCADE, related_name="municipios"): Parent state

**Methods**:
- `__str__()`: Returns the municipality name

**Relationships**:
- `cps` (Reverse ForeignKey from CP): Postal codes in this municipality

**Notes**:
- Cascades deletion when parent state is deleted
- Part of geographic hierarchy: Estado → Municipio → CP → Colonia

---

### CP

**Purpose**: Represents postal codes (códigos postales).

**Table**: (not specified)

**Fields**:
- `codigo` (CharField, max_length=10): Postal code
- `zona` (CharField, max_length=50): Postal zone
- `municipio` (ForeignKey to Municipio, on_delete=CASCADE, related_name="cps"): Parent municipality

**Methods**:
- `__str__()`: Returns the postal code

**Relationships**:
- `colonias` (Reverse ForeignKey from Colonia): Colonias with this postal code

**Notes**:
- Mexican postal codes are 5 digits
- Cascades deletion when parent municipality is deleted

---

### Colonia

**Purpose**: Represents neighborhoods/colonias within postal codes.

**Table**: (not specified)

**Fields**:
- `nombre` (CharField, max_length=100): Colonia name
- `cp` (ForeignKey to CP, on_delete=CASCADE, related_name="colonias"): Parent postal code

**Methods**:
- `__str__()`: Returns the colonia name

**Relationships**:
- `direcciones` (Reverse ForeignKey from Direccion): Addresses in this colonia

**Notes**:
- Cascades deletion when parent CP is deleted
- Lowest level in geographic hierarchy

---

### Direccion

**Purpose**: Represents physical addresses.

**Table**: (not specified)

**Fields**:
- `calle` (CharField, max_length=150): Street name
- `numero_exterior` (CharField, max_length=20): Exterior number
- `numero_interior` (CharField, max_length=20, blank=True, null=True): Interior number (optional)
- `colonia` (ForeignKey to Colonia, on_delete=CASCADE, related_name="direcciones"): Parent colonia
- `tipo_hogar` (ForeignKey to TipoHogar, on_delete=CASCADE): Housing type

**Methods**:
- `__str__()`: Returns formatted address (calle #numero_exterior)

**Notes**:
- Interior number is optional
- Cascades deletion when parent colonia or tipo_hogar is deleted

---

### TipoHogar

**Purpose**: Represents types of housing.

**Table**: (not specified)

**Fields**:
- `nombre` (CharField, max_length=50): Housing type name

**Methods**:
- `__str__()`: Returns the housing type name

**Notes**:
- Used to categorize addresses (e.g., 'Casa', 'Departamento')

---

## Academic Content Models

### Curso

**Purpose**: Represents academic courses created by teachers or AI.

**Table**: `cursos`

**Fields**:
- `id_curso` (AutoField, Primary Key): Unique identifier for the course
- `titulo` (CharField, max_length=200): Course title
- `descripcion` (TextField, blank=True, null=True): Course description
- `docente` (ForeignKey to Usuario, on_delete=CASCADE, related_name="cursos_impartidos", db_column='id_creador'): Course creator/teacher
- `estado` (CharField, max_length=50, blank=True, null=True, default='Borrador'): Course status (e.g., 'Borrador', 'En Revisión', 'Aprobado')
- `generado_con_ia` (BooleanField, default=False): Whether course was AI-generated
- `version` (IntegerField, default=1): Course version number
- `fecha_creacion` (DateTimeField, auto_now_add=True): Creation timestamp
- `fecha_aprobacion` (DateTimeField, blank=True, null=True): Approval timestamp
- `updated_at` (DateTimeField, auto_now=True): Last update timestamp
- `contenido_json` (JSONField, null=True, blank=True, default=dict): Course content structure (modules, questions, etc.)

**Methods**:
- `__str__()`: Returns the course title

**Meta Options**:
- `db_table`: 'cursos'
- `managed`: False

**Relationships**:
- `foros` (Reverse ForeignKey from Foro): Forums associated with this course
- `aprobaciones` (Reverse ForeignKey from ProcesoAprobacionCursos): Approval processes for this course

**Notes**:
- Content is stored as JSON for flexibility
- Versioning allows tracking of course iterations
- Status workflow: Borrador → En Revisión → Aprobado/Observaciones

---

### Foro

**Purpose**: Represents discussion forums for courses.

**Table**: `foros`

**Fields**:
- `id_foro` (AutoField, Primary Key): Unique identifier for the forum
- `curso` (ForeignKey to Curso, on_delete=CASCADE, related_name="foros", db_column='curso_id'): Associated course
- `titulo` (CharField, max_length=200): Forum title
- `descripcion` (TextField): Forum description
- `fecha_creacion` (DateTimeField, auto_now_add=True): Creation timestamp
- `activo` (BooleanField, default=True): Forum active status

**Methods**:
- `__str__()`: Returns the forum title

**Meta Options**:
- `db_table`: 'foros'

**Relationships**:
- `posts` (Reverse ForeignKey from PostForo): Posts in this forum

**Notes**:
- Forums are course-specific
- Active field allows soft deletion/archiving

---

### PostForo

**Purpose**: Represents posts within forums.

**Table**: `posts_foro`

**Fields**:
- `id_post` (AutoField, Primary Key): Unique identifier for the post
- `foro` (ForeignKey to Foro, on_delete=CASCADE, related_name="posts", db_column='foro_id'): Parent forum
- `autor` (ForeignKey to Usuario, on_delete=CASCADE, db_column='autor_id'): Post author
- `contenido` (TextField): Post content
- `fecha_creacion` (DateTimeField, auto_now_add=True): Creation timestamp
- `fecha_edicion` (DateTimeField, auto_now=True): Last edit timestamp

**Methods**:
- `__str__()`: Returns formatted string "Post en {foro.titulo}"

**Meta Options**:
- `db_table`: 'posts_foro'

**Notes**:
- Tracks both creation and edit timestamps
- Cascades deletion when parent forum or user is deleted

---

## Escalafón Process Models

### ProcesoEscalafon

**Purpose**: Represents the career advancement (escalafón) process for teachers.

**Table**: (not specified)

**Fields**:
- `usuario` (ForeignKey to Usuario, on_delete=CASCADE, related_name="procesos"): Teacher undergoing the process
- `folio` (CharField, max_length=50): Process folio/identifier
- `tipo_proceso` (CharField, max_length=50): Process type (e.g., 'Horizontal', 'Vertical')
- `ciclo_escolar` (CharField, max_length=20): School cycle
- `estado` (ForeignKey to Estado, on_delete=CASCADE): Geographic state
- `funcion` (CharField, max_length=100): Teacher's function
- `tipo_sostenimiento` (CharField, max_length=50): Type of school funding
- `tipo_valoracion` (TextField): Evaluation type/method
- `datos_multifactores` (JSONField): Multifactor evaluation data (scores, metrics)
- `estatus` (CharField, max_length=50): Process status
- `fecha_registro` (DateTimeField, auto_now_add=True): Registration timestamp

**Methods**:
- `__str__()`: Returns the folio

**Notes**:
- Stores multifactor evaluation data as JSON for flexibility
- Tracks both horizontal and vertical promotion processes
- Links to geographic state for regional reporting

---

### Prom

**Purpose**: Represents promotion records (legacy or supplementary data).

**Table**: (not specified)

**Fields**:
- `folio` (CharField, max_length=50): Promotion folio
- `curp` (CharField, max_length=18): Teacher's CURP
- `nombre` (CharField, max_length=100): First name
- `primer_apellido` (CharField, max_length=50): Paternal surname
- `segundo_apellido` (CharField, max_length=50): Maternal surname
- `correo1` (EmailField): Primary email
- `correo2` (EmailField, blank=True, null=True): Secondary email
- `telefono1` (CharField, max_length=15): Primary phone
- `telefono2` (CharField, max_length=15, blank=True, null=True): Secondary phone
- `entidad` (CharField, max_length=50): Entity/state
- `cct` (CharField, max_length=50): School CCT (Clave de Centro de Trabajo)
- `subsistema` (CharField, max_length=120): Educational subsystem
- `sistema` (CharField, max_length=50): Educational system
- `cargo` (CharField, max_length=50): Current position
- `funcion` (CharField, max_length=50): Job function
- `cargo_val` (CharField, max_length=50): Validation position
- `tipo_val` (CharField, max_length=120): Validation type
- `estudios_posgrado` (CharField, max_length=50): Postgraduate studies
- `exp_fds` (CharField, max_length=50): FDS experience

**Methods**:
- `__str__()`: Returns the folio

**Notes**:
- Appears to be a legacy or supplementary model for promotion tracking
- Contains redundant user information (CURP, names, emails)
- Links to school via CCT

---

### ProcesoAprobacionCursos

**Purpose**: Represents the approval workflow for courses.

**Table**: `proceso_aprobacion_cursos`

**Fields**:
- `id_proceso` (AutoField, Primary Key, db_column='id_proceso'): Unique identifier
- `curso` (ForeignKey to Curso, on_delete=CASCADE, db_column='id_curso', related_name='aprobaciones', null=True, blank=True): Course being approved
- `evaluador` (ForeignKey to Usuario, on_delete=CASCADE, db_column='id_evaluador', related_name='evaluaciones_realizadas'): Evaluator
- `iteracion` (CharField, max_length=50): Iteration number (e.g., '1', '2', '3')
- `decision` (CharField, max_length=50): Approval decision (e.g., 'Aprobado', 'Rechazado', 'Observaciones')
- `comentarios` (TextField): Evaluator comments
- `fecha_revision` (DateTimeField): Review timestamp

**Methods**:
- `__str__()`: Returns formatted string "{curso} - {decision}"

**Meta Options**:
- `db_table`: 'proceso_aprobacion_cursos'

**Notes**:
- Supports multiple iterations of review
- Course can be null (for future flexibility)
- Tracks evaluator for accountability

---

## AI Integration Models

### RetroalimentacionIaCurso

**Purpose**: Stores AI-generated feedback for courses.

**Table**: `retroalimentacion_ia_curso`

**Fields**:
- `id_retroalimentacion` (AutoField, Primary Key): Unique identifier
- `sugerencias` (TextField): AI-generated suggestions
- `confianza_pbt` (DecimalField, max_digits=5, decimal_places=2): Confidence probability score (0.00-1.00)
- `version` (IntegerField): Feedback version
- `fecha_generacion` (DateTimeField, auto_now_add=True): Generation timestamp

**Meta Options**:
- `db_table`: 'retroalimentacion_ia_curso'
- `verbose_name`: 'Retroalimentación IA Curso'

**Notes**:
- Currently has commented-out foreign key to Curso (see code)
- Confidence score indicates AI certainty
- Versioning allows tracking of feedback iterations

---

### Document

**Purpose**: Represents documents with embeddings for semantic search.

**Table**: (not specified)

**Fields**:
- `content` (TextField): Document content
- `embedding` (JSONField): Vector embedding for semantic search
- `source` (TextField): Document source/origin
- `created_at` (DateTimeField, auto_now_add=True): Creation timestamp

**Methods**:
- `__str__()`: Returns formatted string "Doc {id}"

**Notes**:
- Used with pgvector for semantic search
- Embeddings stored as JSON (could be converted to pgvector type)
- Supports RAG (Retrieval-Augmented Generation) patterns

---

## Audit Trail Models

### BitacoraEvento

**Purpose**: Audit log for tracking user actions and system events.

**Table**: `bitacora_eventos`

**Fields**:
- `id_evento` (AutoField, Primary Key): Unique identifier for the event
- `usuario` (ForeignKey to Usuario, on_delete=CASCADE, db_column='usuario_id'): User who triggered the event
- `tipo_evento` (CharField, max_length=50): Event type (e.g., 'USUARIO_CREADO', 'LOGIN', 'CURSO_EDITADO')
- `descripcion` (TextField): Event description
- `fecha_evento` (DateTimeField, auto_now_add=True): Event timestamp
- `ip_direccion` (CharField, max_length=50, blank=True, null=True): IP address of the request
- `detalles` (JSONField, blank=True, null=True): Additional event details

**Methods**:
- `__str__()`: Returns formatted string "{usuario} - {tipo_evento} - {fecha_evento}"

**Meta Options**:
- `db_table`: 'bitacora_eventos'

**Notes**:
- IP address is optional (may not be available in all scenarios)
- Details stored as JSON for flexibility
- Cascades deletion when user is deleted
- Used for security auditing and compliance

---

## Model Relationships Summary

### User Hierarchy
```
Usuario
├── Rol (Many-to-One)
├── Institucion (Many-to-One)
├── cursos_impartidos (One-to-Many from Curso)
├── procesos (One-to-Many from ProcesoEscalafon)
└── bitacora_eventos (One-to-Many from BitacoraEvento)
```

### Geographic Hierarchy
```
Estado
├── Municipio (One-to-Many)
    ├── CP (One-to-Many)
        ├── Colonia (One-to-Many)
            └── Direccion (One-to-Many)
```

### Course Hierarchy
```
Curso
├── docente (Many-to-One from Usuario)
├── foros (One-to-Many)
│   └── posts (One-to-Many from PostForo)
│       └── autor (Many-to-One from Usuario)
└── aprobaciones (One-to-Many from ProcesoAprobacionCursos)
    └── evaluador (Many-to-One from Usuario)
```

---

## Database Constraints

### Unique Constraints
- `Usuario.correo`: Must be unique
- `Usuario.curp`: Must be unique
- `Rol.nombre_rol`: Must be unique

### Foreign Key Constraints
- `Usuario.rol`: PROTECT (cannot delete role if users exist)
- `Usuario.institucion`: PROTECT (cannot delete institution if users exist)
- `Curso.docente`: CASCADE (delete course if user deleted)
- `Foro.curso`: CASCADE (delete forum if course deleted)
- `PostForo.foro`: CASCADE (delete post if forum deleted)
- `PostForo.autor`: CASCADE (delete post if user deleted)
- All geographic models: CASCADE (delete child if parent deleted)

---

## Managed vs Unmanaged Models

All models in this system use `managed = False`, meaning:
- Django will NOT create, modify, or delete these tables
- Tables must exist in the database beforehand
- Migrations are generated but not applied automatically
- This is common when integrating with existing databases

---

## JSON Field Usage

Several models use JSONField for flexible data storage:

1. **Curso.contenido_json**: Course structure (modules, questions, exams)
2. **ProcesoEscalafon.datos_multifactores**: Evaluation scores and metrics
3. **Document.embedding**: Vector embeddings for semantic search
4. **BitacoraEvento.detalles**: Additional event metadata

---

## Custom Methods

### Password Verification
- `Usuario.check_password(raw_password)`: Uses Django's password hasher

### String Representations
- All models implement `__str__()` for human-readable output
- Follows Django best practices for admin interface

---

## Model Services

Models are accessed through service classes in `apps/users/services/`:
- `UserService`: User CRUD operations
- `CursoService`: Course CRUD operations
- `ForoService`: Forum CRUD operations
- `ProcesoEscalafonService`: Escalafón process operations
- `BitacoraService`: Audit logging

---

## Serialization

Models are serialized using custom serializers in `apps/users/serializers/`:
- `UsuarioSerializer`: User data to dict
- `CursoSerializer`: Course data to dict
- `ProcesoEscalafonSerializer`: Process data to dict
- `ProcesoAprobacionSerializer`: Approval data to dict
- `BitacoraEventoSerializer`: Event data to dict

---

## Database Indexes

The system relies on database-level indexes (not defined in Django models):
- Primary keys are indexed by default
- Foreign keys should be indexed in the database
- Unique fields have unique constraints

---

## Migration Strategy

Since models use `managed = False`:
1. Migrations are generated for reference only
2. Tables must exist in the database
3. Schema changes must be applied directly to the database
4. Django models must match the existing schema exactly

---

## Performance Considerations

1. **JSONField**: Can impact performance for large datasets
2. **Foreign Keys**: Ensure database has proper indexes
3. **Query Optimization**: Use `select_related()` and `prefetch_related()` for related objects
4. **Caching**: Consider caching frequently accessed user data

---

## Security Considerations

1. **Passwords**: Hashed using Django's default hasher
2. **CURP**: Sensitive personal data, should be protected
3. **Email**: Used for authentication, must be unique
4. **Audit Trail**: All user actions are logged in BitacoraEvento
5. **Rate Limiting**: Applied to sensitive operations (user creation/update)

---

## Future Model Enhancements

Potential improvements:
1. Add Django model validation methods (`clean()`, `validate_unique()`)
2. Implement custom managers for complex queries
3. Add database indexes via Django models
4. Consider using `managed = True` for new tables
5. Add model signals for automated actions (e.g., post_save for audit logging)
