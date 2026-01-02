from django import forms
from apps.users.models import Usuario

class UsuarioForm(forms.ModelForm):
    contraseña = forms.CharField(widget=forms.PasswordInput) 
    class Meta:
        model = Usuario
        fields = [
            'nombre',
            'apellido_paterno',
            'apellido_materno',
            'correo',
            'contraseña',
            'curp',
            'rol',
            'institucion',
        ]
