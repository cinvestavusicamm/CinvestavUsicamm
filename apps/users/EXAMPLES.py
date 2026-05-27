"""
EJEMPLO: Cómo usar la arquitectura en capas

Este archivo demuestra los patrones correctos de implementación
"""

# ============================================================================
# EJEMPLO 1: Vista para listar cursos de un docente
# ============================================================================
from django.shortcuts import render
from django.http import JsonResponse
from apps.users.infrastructure.decorators import require_role, api_view, handle_exceptions
from apps.users.repositories import CursoRepository, UsuarioRepository
from apps.users.serializers import CursoSerializer, UsuarioSerializer
from apps.users.config.constants import ROLE_DOCENTE


@require_role(ROLE_DOCENTE)
@handle_exceptions
def listar_cursos_docente(request):
    """
    Ejemplo de vista web que:
    1. Obtiene datos usando repositories
    2. Los serializa
    3. Renderiza un template
    """
    # ✅ CORRECTO: Usar repository
    usuario_id = request.session.get("usuario_id")
    cursos = CursoRepository.get_by_docente(usuario_id, limit=10)
    
    # ✅ CORRECTO: Serializar datos
    cursos_dict = CursoSerializer.to_list(cursos)
    
    context = {
        'cursos': cursos_dict,
        'total': len(cursos),
    }
    return render(request, 'docentes/mis_cursos.html', context)


# ============================================================================
# EJEMPLO 2: API endpoint para crear un curso
# ============================================================================
import json
from django.views.decorators.http import require_http_methods
from apps.users.validators import CursoValidator
from apps.users.services import CursoService
from apps.users.infrastructure.exceptions import ValidationException, PermissionDeniedException


@require_http_methods(["POST"])
@require_role(ROLE_GENERADOR)
@handle_exceptions
def crear_curso_endpoint(request):
    """
    Ejemplo de API endpoint que:
    1. Valida entrada
    2. Crea recurso usando service
    3. Retorna JSON serializado
    """
    try:
        # ✅ CORRECTO: Parsear JSON
        data = json.loads(request.body)
        
        # ✅ CORRECTO: Validar entrada
        CursoValidator.validar_curso_data(data)
        
        # ✅ CORRECTO: Usar service para lógica de negocio
        curso = CursoService.crear_curso(
            titulo=data['titulo'],
            descripcion=data.get('descripcion', ''),
            docente_id=request.session.get("usuario_id"),
            generado_con_ia=data.get('generado_con_ia', False)
        )
        
        # ✅ CORRECTO: Serializar respuesta
        return JsonResponse({
            'success': True,
            'data': CursoSerializer.to_dict(curso),
            'message': 'Curso creado exitosamente'
        }, status=201)
        
    except ValidationException as e:
        return JsonResponse({
            'success': False,
            'errors': e.detalles,
            'message': e.mensaje
        }, status=400)
    except PermissionDeniedException as e:
        return JsonResponse({
            'success': False,
            'message': e.mensaje
        }, status=403)


# ============================================================================
# EJEMPLO 3: Construcción de dashboard (usando builders)
# ============================================================================
from apps.users.services.dashboard_builders import GeneradorContextBuilder, EvaluadorContextBuilder


@require_role(ROLE_GENERADOR)
def dashboard_generador(request):
    """
    Ejemplo de construcción de dashboard usando builders
    """
    # ✅ CORRECTO: Usar builder para contexto
    context = GeneradorContextBuilder.build(request)
    
    return render(request, 'generador_cursos/dashboard.html', context)


@require_role('Evaluador')
def dashboard_evaluador(request):
    """
    Ejemplo de construcción de dashboard para evaluador
    """
    # ✅ CORRECTO: Usar builder específico
    context = EvaluadorContextBuilder.build(request)
    
    return render(request, 'evaluador/dashboard.html', context)


# ============================================================================
# EJEMPLO 4: Servicio con lógica de negocio
# ============================================================================
from apps.users.repositories import (
    CursoRepository, 
    ProcesoAprobacionRepository,
    BitacoraEventoRepository
)


class CursoAprobacionService:
    """
    Servicio que maneja lógica compleja de aprobación de cursos
    """
    
    @staticmethod
    def aprobar_curso(curso_id, evaluador_id, comentarios=""):
        """
        Aprueba un curso e introduce registros en base de datos
        """
        # ✅ CORRECTO: Usar repositories
        curso = CursoRepository.get_by_id(curso_id)
        
        if not curso:
            raise ValidationException("Curso no encontrado")
        
        if curso.estado != 'Pendiente':
            raise ValidationException(f"No se puede aprobar curso en estado {curso.estado}")
        
        # Crear aprobación
        aprobacion = ProcesoAprobacionRepository.create(
            curso_id=curso_id,
            evaluador_id=evaluador_id,
            decision='Aprobado',
            comentarios=comentarios
        )
        
        # Actualizar estado del curso
        CursoRepository.update(curso_id, estado='Aprobado')
        
        # Registrar en bitácora
        BitacoraEventoRepository.registrar(
            usuario_id=evaluador_id,
            tipo_evento='APROBACION_CURSO',
            descripcion=f'Curso {curso.titulo} aprobado',
            detalles={'curso_id': curso_id}
        )
        
        return aprobacion


# ============================================================================
# EJEMPLO 5: Manejo de errores con excepciones personalizadas
# ============================================================================
from apps.users.infrastructure.exceptions import (
    NotFoundException,
    PermissionDeniedException,
    ValidationException,
    ConflictException
)


@require_role('Administrador')
@handle_exceptions
def eliminar_usuario(request, usuario_id):
    """
    Ejemplo de manejo robusto de errores
    """
    try:
        # ✅ CORRECTO: Validar existencia
        usuario = UsuarioRepository.get_by_id(usuario_id)
        if not usuario:
            raise NotFoundException(
                "Usuario no encontrado",
                {'usuario_id': usuario_id}
            )
        
        # ✅ CORRECTO: Verificar permisos
        if usuario.rol.nombre_rol == 'Administrador' and usuario.id_usuario != request.user.id:
            raise PermissionDeniedException(
                "No puedes eliminar otros administradores"
            )
        
        # ✅ CORRECTO: Verificar estado
        if usuario.activo == False:
            raise ConflictException(
                "El usuario ya está inactivo"
            )
        
        # Eliminar
        UsuarioRepository.delete(usuario_id)
        
        # Registrar en bitácora
        BitacoraEventoRepository.registrar(
            usuario_id=request.session.get("usuario_id"),
            tipo_evento='ELIMINAR_USUARIO',
            descripcion=f'Usuario {usuario.nombre} eliminado',
            detalles={'usuario_id': usuario_id}
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Usuario {usuario.nombre} eliminado exitosamente'
        })
        
    except NotFoundException as e:
        return JsonResponse({
            'success': False,
            'error': e.mensaje,
            'details': e.detalles
        }, status=404)
    except PermissionDeniedException as e:
        return JsonResponse({
            'success': False,
            'error': e.mensaje
        }, status=403)
    except ConflictException as e:
        return JsonResponse({
            'success': False,
            'error': e.mensaje
        }, status=409)


# ============================================================================
# EJEMPLO 6: Uso de validadores
# ============================================================================
from apps.users.validators import UsuarioValidator, CursoValidator, LoginValidator


def registrar_usuario_endpoint(request):
    """
    Ejemplo de validación de entrada
    """
    try:
        data = json.loads(request.body)
        
        # ✅ CORRECTO: Validar datos completos
        UsuarioValidator.validar_usuario_data(data)
        
        # Crear usuario...
        
        return JsonResponse({'success': True}, status=201)
        
    except ValidationException as e:
        return JsonResponse({
            'success': False,
            'errors': e.detalles
        }, status=400)


# ============================================================================
# EJEMPLO 7: Uso de decoradores
# ============================================================================
from apps.users.infrastructure.decorators import validate_json, api_view


@api_view(['GET', 'POST', 'DELETE'])
@require_role('Administrador')
@validate_json('titulo')  # Validar que 'titulo' esté presente en POST/PUT
def admin_api(request):
    """
    Ejemplo de uso de decoradores
    """
    if request.method == 'GET':
        return JsonResponse({'data': []})
    
    elif request.method == 'POST':
        # request.json_data ya contiene los datos validados
        titulo = request.json_data['titulo']
        return JsonResponse({'created': titulo})
    
    elif request.method == 'DELETE':
        return JsonResponse({'deleted': True})


# ============================================================================
# EJEMPLO 8: Serialización en diferentes contextos
# ============================================================================
from apps.users.serializers import (
    UsuarioSerializer,
    CursoSerializer,
    ProcesoAprobacionSerializer
)


def api_cursos_completo(request):
    """
    Ejemplo de serialización completa vs simple
    """
    usuario_id = request.session.get("usuario_id")
    
    # Obtener datos
    usuario = UsuarioRepository.get_by_id(usuario_id)
    cursos = CursoRepository.get_by_docente(usuario_id)
    aprobaciones = ProcesoAprobacionRepository.get_by_docente(usuario_id)
    
    return JsonResponse({
        # ✅ Serialización completa para perfil
        'perfil': UsuarioSerializer.to_dict(usuario),
        
        # ✅ Serialización completa para cursos
        'cursos': CursoSerializer.to_list(cursos),
        
        # ✅ Serialización simple en lista (ahorra datos)
        'resumen_aprobaciones': [
            {
                'curso': a.curso.titulo,
                'estado': a.decision
            }
            for a in aprobaciones
        ]
    })


# ============================================================================
# PATRONES A EVITAR ❌
# ============================================================================

def MAL_EJEMPLO_1(request):
    """❌ INCORRECTO: Queries directas en vistas"""
    # ❌ Esto es malo
    cursos = Curso.objects.filter(docente_id=request.user.id)
    
    # ✅ Hacer esto en su lugar
    cursos = CursoRepository.get_by_docente(request.user.id)


def MAL_EJEMPLO_2(request):
    """❌ INCORRECTO: Serialización manual"""
    cursos = CursoRepository.get_by_docente(request.user.id)
    
    # ❌ Esto es malo - serialización ad-hoc
    cursos_data = [
        {
            'id': c.id_curso,
            'titulo': c.titulo,
            'estado': c.estado,
            # ... campos repetidos en múltiples vistas
        }
        for c in cursos
    ]
    
    # ✅ Hacer esto en su lugar
    cursos_data = CursoSerializer.to_list(cursos)


def MAL_EJEMPLO_3(request):
    """❌ INCORRECTO: Sin validación"""
    # ❌ Esto es malo - no valida entrada
    data = json.loads(request.body)
    titulo = data.get('titulo', '')  # Puede ser vacío
    curso = Curso.objects.create(titulo=titulo)
    
    # ✅ Hacer esto en su lugar
    data = json.loads(request.body)
    CursoValidator.validar_curso_data(data)
    curso = CursoService.crear_curso(titulo=data['titulo'], ...)


def MAL_EJEMPLO_4(request):
    """❌ INCORRECTO: Sin manejo de excepciones"""
    # ❌ Esto es malo - sin try/except
    def obtener_curso(curso_id):
        return Curso.objects.get(id_curso=curso_id)
    
    # ✅ Hacer esto en su lugar
    def obtener_curso(curso_id):
        try:
            return CursoRepository.get_by_id(curso_id)
        except Curso.DoesNotExist:
            raise NotFoundException("Curso no encontrado")


# ============================================================================
# Conclusión
# ============================================================================
"""
La arquitectura en capas proporciona:

1. ✅ SEPARACIÓN DE RESPONSABILIDADES: Cada capa tiene un propósito claro
2. ✅ REUTILIZACIÓN: Services, repositories y serializers se reutilizan
3. ✅ TESTABILIDAD: Cada capa puede testearse de forma aislada
4. ✅ MANTENIBILIDAD: Cambios localizados a una capa específica
5. ✅ ESCALABILIDAD: Fácil agregar nuevas funcionalidades
6. ✅ CONSISTENCIA: Patrones uniformes en toda la aplicación
"""
