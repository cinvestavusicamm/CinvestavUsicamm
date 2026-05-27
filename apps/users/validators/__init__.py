"""
Validadores para entrada de datos
"""
from django.core.exceptions import ValidationError
import re


class UsuarioValidator:
    """Valida datos de Usuario"""
    
    @staticmethod
    def validar_correo(correo):
        """Valida formato de correo"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, correo):
            raise ValidationError("Correo electrónico inválido")
        return correo
    
    @staticmethod
    def validar_curp(curp):
        """Valida formato de CURP"""
        if curp and len(curp) != 18:
            raise ValidationError("CURP debe tener 18 caracteres")
        return curp
    
    @staticmethod
    def validar_nombre(nombre):
        """Valida que el nombre no esté vacío"""
        if not nombre or len(nombre.strip()) == 0:
            raise ValidationError("El nombre no puede estar vacío")
        return nombre
    
    @staticmethod
    def validar_usuario_data(data):
        """Valida datos completos de usuario"""
        errores = {}
        
        if not data.get('nombre'):
            errores['nombre'] = 'Nombre es requerido'
        
        if not data.get('correo'):
            errores['correo'] = 'Correo es requerido'
        else:
            try:
                UsuarioValidator.validar_correo(data['correo'])
            except ValidationError as e:
                errores['correo'] = str(e)
        
        if data.get('curp'):
            try:
                UsuarioValidator.validar_curp(data['curp'])
            except ValidationError as e:
                errores['curp'] = str(e)
        
        if errores:
            raise ValidationError(errores)
        
        return data


class CursoValidator:
    """Valida datos de Curso"""
    
    @staticmethod
    def validar_titulo(titulo):
        """Valida que el título no esté vacío"""
        if not titulo or len(titulo.strip()) < 3:
            raise ValidationError("El título debe tener al menos 3 caracteres")
        return titulo
    
    @staticmethod
    def validar_curso_data(data):
        """Valida datos completos de curso"""
        errores = {}
        
        if not data.get('titulo'):
            errores['titulo'] = 'Título es requerido'
        elif len(data['titulo'].strip()) < 3:
            errores['titulo'] = 'El título debe tener al menos 3 caracteres'
        
        if 'contenido' in data and not isinstance(data['contenido'], dict):
            errores['contenido'] = 'El contenido debe ser un objeto JSON válido'
        
        if errores:
            raise ValidationError(errores)
        
        return data
    
    @staticmethod
    def validar_estado(estado):
        """Valida que el estado sea válido"""
        estados_validos = ['Borrador', 'Pendiente', 'Revisión', 'Aprobado', 'Rechazado', 'Inactivo']
        if estado and estado not in estados_validos:
            raise ValidationError(f"Estado debe ser uno de: {', '.join(estados_validos)}")
        return estado


class LoginValidator:
    """Valida datos de login"""
    
    @staticmethod
    def validar_credenciales(correo, contrasena):
        """Valida que correo y contraseña no estén vacíos"""
        errores = {}
        
        if not correo or len(correo.strip()) == 0:
            errores['correo'] = 'Correo es requerido'
        
        if not contrasena or len(contrasena.strip()) == 0:
            errores['contrasena'] = 'Contraseña es requerida'
        
        if errores:
            raise ValidationError(errores)
        
        return {'correo': correo, 'contrasena': contrasena}


class PaginationValidator:
    """Valida parámetros de paginación"""
    
    @staticmethod
    def validar_pagina(page, max_page=10000):
        """Valida número de página"""
        try:
            page_num = int(page)
            if page_num < 1 or page_num > max_page:
                raise ValidationError(f"Página debe estar entre 1 y {max_page}")
            return page_num
        except (ValueError, TypeError):
            raise ValidationError("Página debe ser un número entero")
    
    @staticmethod
    def validar_limit(limit, max_limit=100):
        """Valida límite de registros"""
        try:
            limit_num = int(limit)
            if limit_num < 1 or limit_num > max_limit:
                raise ValidationError(f"Límite debe estar entre 1 y {max_limit}")
            return limit_num
        except (ValueError, TypeError):
            raise ValidationError("Límite debe ser un número entero")
