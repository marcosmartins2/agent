from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Formulário customizado para registro de usuário."""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="Nome Completo",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Digite seu nome completo'
        })
    )
    
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'seu@email.com'
        })
    )
    
    birth_date = forms.DateField(
        required=True,
        label="Data de Nascimento",
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )
    
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••'
        })
    )
    
    password2 = forms.CharField(
        label="Confirmação de Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••'
        })
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'email', 'birth_date', 'password1', 'password2')
    
    def clean_email(self):
        """Valida se o email já existe."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email já está cadastrado.")
        return email
    
    def save(self, commit=True):
        """Salva o usuário com os dados customizados."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.username = self.cleaned_data['email']  # Usa email como username
        
        if commit:
            user.save()
            # Cria ou atualiza o perfil com a data de nascimento
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.birth_date = self.cleaned_data['birth_date']
            profile.save()
        
        return user
