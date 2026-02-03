from django import forms
from apps.users.models import Usuario
from django.contrib.auth.hashers import make_password

class UsuarioForm(forms.ModelForm):
    contrasena = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = Usuario
        fields = [
            'nombre',
            'apellido_paterno',
            'apellido_materno',
            'correo',
            'contrasena',
            'curp',
            'rol',
            'institucion',
        ]

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.contrasena = make_password(self.cleaned_data['contrasena'])
        if commit:
            usuario.save()
        return usuario
