from django.urls import path, include
from rest_framework import routers
from . import api , views

# Router para el ViewSet (CRUD)
router = routers.DefaultRouter()
router.register(r'users', api.UserViewSet, basename='users')
router.register(r'groups', api.GroupViewSet, basename='groups')
router.register(r'empresas', api.EmpresaViewSet, basename='empresas')
router.register(r'userprofiles', api.UserProfileViewSet, basename='userprofiles')

# URLs de la app usuarios
urlpatterns = [
    # APIs de autenticación (funciones con decoradores)
    path('register/', views.Register, name='register'),
    path('login/', views.Login, name='login'),
    path('profile/', views.Profile, name='profile'),
    path('logout/', views.Logout, name='logout'),  # Agregué logout tambiénsss
    
    # APIs CRUD (ViewSets)
    path('', include(router.urls)),
]
 
