from rest_framework import serializers
from .models import Users, Emails, QuantumKey


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = "__all__"


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emails
        fields = "__all__"

class QuantumKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuantumKey
        fields = "__all__"
