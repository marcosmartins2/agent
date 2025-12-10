# Squashed migration for Padaria multi-tenant system
# This migration creates the final state of the models directly

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Create Padaria model (final state)
        migrations.CreateModel(
            name='Padaria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Nome da Padaria')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='Slug')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Telefone')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='E-mail')),
                ('cnpj', models.CharField(blank=True, max_length=18, verbose_name='CNPJ')),
                ('address', models.TextField(blank=True, verbose_name='Endereço')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativa')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_padarias', to=settings.AUTH_USER_MODEL, verbose_name='Dono')),
            ],
            options={
                'verbose_name': 'Padaria',
                'verbose_name_plural': 'Padarias',
                'ordering': ['-created_at'],
            },
        ),
        # Create ApiKey model
        migrations.CreateModel(
            name='ApiKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(db_index=True, max_length=64, unique=True, verbose_name='Chave')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativa')),
                ('name', models.CharField(blank=True, max_length=100, verbose_name='Nome/Descrição')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criada em')),
                ('last_used_at', models.DateTimeField(blank=True, null=True, verbose_name='Último uso')),
                ('padaria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_keys', to='organizations.padaria', verbose_name='Padaria')),
            ],
            options={
                'verbose_name': 'Chave de API',
                'verbose_name_plural': 'Chaves de API',
                'ordering': ['-created_at'],
            },
        ),
        # Create PadariaUser model
        migrations.CreateModel(
            name='PadariaUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('dono', 'Dono'), ('funcionario', 'Funcionário')], default='funcionario', max_length=20, verbose_name='Papel')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Adicionado em')),
                ('padaria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='organizations.padaria', verbose_name='Padaria')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='padaria_memberships', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Membro da Padaria',
                'verbose_name_plural': 'Membros da Padaria',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'padaria')},
            },
        ),
    ]
