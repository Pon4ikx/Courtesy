from rest_framework.serializers import ModelSerializer
from .models import Address


class AdressSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
