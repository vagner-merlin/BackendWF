from . import serializers 
from rest_framework import viewsets , permissions

#creacion del crud para los modelos 

class UserViewSet(viewsets.ModelViewSet):
    queryset = serializers.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.AllowAny]

class GroupViewSet(viewsets.ModelViewSet):
    queryset = serializers.Group.objects.all()
    serializer_class = serializers.GroupSerializer
    permission_classes = [permissions.AllowAny]

class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = serializers.Empresa.objects.all()
    serializer_class = serializers.EmpresaSerializer
    permission_classes = [permissions.AllowAny]

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = serializers.UserProfile.objects.all()
    serializer_class = serializers.UserProfileSerializer
    permission_classes = [permissions.AllowAny]

