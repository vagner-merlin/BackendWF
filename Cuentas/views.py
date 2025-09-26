from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from .serializers import UserSerializer, EmpresaSerializer, UserProfileSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Empresa, UserProfile
from django.db import transaction

# Create your views here.
@api_view(['POST'])
def Register(request):

    try:
        with transaction.atomic():
            # PASO 1: Crear usuario en auth_user
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            
            # Validar campos requeridos del usuario
            if not username or not email or not password:
                return Response({
                    'error': 'Username, email and password are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar si el usuario ya existe
            if User.objects.filter(username=username).exists():
                return Response({
                    'error': 'Username already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            if User.objects.filter(email=email).exists():
                return Response({
                    'error': 'Email already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear usuario como superuser
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_superuser=True,  # Automáticamente superuser
                is_staff=True,      # También staff para acceder al admin
                is_active=True
            )
            
            print(f"✅ Usuario creado: ID={user.id}, Username={user.username}, Is_superuser={user.is_superuser}")
            
            # PASO 2: Crear empresa con el usuario como admin (FK)
            name_empresa = request.data.get('name')  # Nombre de la empresa
            telefono_ref = request.data.get('telefono_ref', '')
            email_empresarial = request.data.get('email_empresarial')
            
            # Validar campos requeridos de la empresa
            if not name_empresa or not email_empresarial:
                return Response({
                    'error': 'Company name and business email are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear empresa usando el usuario recién creado como admin
            empresa = Empresa.objects.create(
                name=name_empresa,
                telefono_ref=telefono_ref,
                email_empresarial=email_empresarial,
                admin=user  # FK al usuario que se acaba de crear
            )
            
            print(f"✅ Empresa creada: ID={empresa.id}, Name={empresa.name}, Admin_ID={empresa.admin.id}")
            
            # PASO 3: Crear UserProfile vinculando usuario y empresa
            nombre_completo = request.data.get('nombre_completo')
            direccion = request.data.get('direccion', '')
            telefono = request.data.get('telefono', '')
            
            if not nombre_completo:
                return Response({
                    'error': 'Full name is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear perfil de usuario
            user_profile = UserProfile.objects.create(
                nombre_completo=nombre_completo,
                direccion=direccion,
                telefono=telefono,
                user=user,      # FK al usuario
                empresa=empresa # FK a la empresa
            )
            
            print(f"✅ UserProfile creado: ID={user_profile.id}, User_ID={user_profile.user.id}, Empresa_ID={user_profile.empresa.id}")
            
            # PASO 4: Crear token para autenticación inmediata
            token = Token.objects.create(user=user)
            
            return Response({
                "message": "Registration successful - User is now superuser",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_superuser": user.is_superuser,
                    "is_staff": user.is_staff
                },
                "empresa": {
                    "id": empresa.id,
                    "name": empresa.name,
                    "telefono_ref": empresa.telefono_ref,
                    "email_empresarial": empresa.email_empresarial,
                    "admin_id": empresa.admin.id
                },
                "profile": {
                    "id": user_profile.id,
                    "nombre_completo": user_profile.nombre_completo,
                    "direccion": user_profile.direccion,
                    "telefono": user_profile.telefono
                }
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        print(f"❌ Error en registro: {str(e)}")
        return Response({
            'error': 'Registration failed', 
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def Login(request):
    """
    Login solo con email y password
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    if not user.check_password(password):
        return Response({"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.is_active:
        return Response({"error": "User account is disabled"}, status=status.HTTP_403_FORBIDDEN)
    
    # Obtener o crear token
    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        "message": "Login successful",
        "token": token.key,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff
        }
    }, status=status.HTTP_200_OK)
    

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def Profile(request):
    """
    Perfil completo del usuario autenticado
    Incluye datos del usuario, empresa y perfil
    """
    user = request.user
    
    try:
        # Obtener el perfil del usuario
        user_profile = UserProfile.objects.get(user=user)
        empresa = user_profile.empresa
        
        # Obtener grupos del usuario
        user_groups = user.groups.all()
        groups_data = [{"id": group.id, "name": group.name} for group in user_groups]
        
        return Response({
            "message": f"Perfil de usuario: {user.username}",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
                "date_joined": user.date_joined,
                "last_login": user.last_login
            },
            "profile": {
                "id": user_profile.id,
                "nombre_completo": user_profile.nombre_completo,
                "direccion": user_profile.direccion,
                "telefono": user_profile.telefono
            },
            "empresa": {
                "id": empresa.id,
                "name": empresa.name,
                "telefono_ref": empresa.telefono_ref,
                "email_empresarial": empresa.email_empresarial,
                "is_admin": empresa.admin == user  # True si es el admin de la empresa
            },
            "groups": groups_data,
            "permissions": {
                "is_company_admin": empresa.admin == user,
                "can_manage_users": user.is_superuser or user.is_staff,
                "can_access_admin": user.is_staff
            },
            "status": "authenticated"
        }, status=status.HTTP_200_OK)
        
    except UserProfile.DoesNotExist:
        return Response({
            "error": "User profile not found",
            "message": "This user doesn't have a complete profile setup",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_superuser": user.is_superuser
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({
            "error": "Error retrieving profile",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def Logout(request):
    """
    Logout del usuario - elimina el token
    """
    try:
        # Eliminar el token del usuario para hacer logout
        token = Token.objects.get(user=request.user)
        token.delete()
        
        return Response({
            "message": "Logout successful",
            "status": "logged_out"
        }, status=status.HTTP_200_OK)
        
    except Token.DoesNotExist:
        return Response({
            "message": "User was already logged out",
            "status": "logged_out"
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            "error": "Error during logout",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
