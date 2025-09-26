from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Empresa(models.Model):
    name = models.CharField(max_length=100)  # Mejor usar snake_case
    telefono_ref = models.CharField(max_length=50, blank=True)
    email_empresarial = models.EmailField(max_length=255, unique=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
class UserProfile(models.Model):
    nombre_completo = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='empleados')
    
    def __str__(self):
        return self.nombre_completo