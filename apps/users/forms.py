from django import forms
from apps.users.models import Usuario
from django.contrib.auth.hashers import make_password

class UsuarioForm(forms.ModelForm):
    contraseña = forms.CharField(widget=forms.PasswordInput, required= True)

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
    def clean(self):
        cleaned_data = super().clean()
        campos_obligatorios = [
            'nombre', 
            'apellido_paterno',
            'apellido_materno',
            'correo',
            'contraseña',
            'curp',
            'rol',
            'institucion'
        ]

        for campo in campos_obligatorios:
            if not cleaned_data.get(campo):
                self.add_error(campo, 'Este campo es obligatorio.')
        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.contraseña = make_password(self.cleaned_data['contraseña'])
        if commit:
            usuario.save()

        return usuario