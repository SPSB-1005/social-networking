from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Friend_Request

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only =True)
    class Meta:
        model = User
        fields = ('id', 'email', 'username','password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend_Request
        fields = ('id', 'sender', 'receiver', 'status', 'timestamp')
    