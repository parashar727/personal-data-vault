from rest_framework import serializers
from .models import Vault, VaultItem
import json

class VaultSerializer(serializers.ModelSerializer):


    class Meta:
        model = Vault
        fields = ('name',)

    def create(self, validated_data):
        return Vault.objects.create(
            owner=self.context.get("request").user,
            **validated_data
        )

class VaultItemSerializer(serializers.ModelSerializer):
    data = serializers.JSONField(write_only=True)
    item_type = serializers.ChoiceField(
        choices=VaultItem.ITEM_CHOICES,
        default="LOG"
    )
    metadata = serializers.JSONField(required=False)

    class Meta:
        model = VaultItem
        fields = ('vault', 'title', 'item_type', 'data', 'metadata')

    def validate(self, attrs):
        request = self.context.get("request")
        vault = attrs.get("vault") or getattr(self.instance, 'vault', None)
        item_type = attrs.get("item_type") or getattr(self.instance, 'item_type', None)
        data = attrs.get("data")

        if vault and vault.owner != request.user:
            raise serializers.ValidationError(
                {"vault": "You can not make changes to another user's vault."}
            )

        if data is not None:
            if item_type == "LOG":
                email = data.get("email")
                password = data.get("password")
                if not email or not password:
                    raise serializers.ValidationError(
                        {"data": "Email and Password fields are mandatory in Login items."}
                    )

                attrs["data"] = {
                    "email" : email,
                    "password" : password
                }

            elif item_type == "NOT":
                content = data.get("content")
                if not content:
                    raise serializers.ValidationError(
                        {"data": "Content field is mandatory in Note type items."}
                )

                attrs["data"] = {
                    "content" : content
                }

        return attrs

    def create(self, validated_data):
        data = validated_data.pop("data")

        validated_data["encrypted_data"] = json.dumps(data) #Implement encryption later, just plaintext JSON string for now

        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "data" in validated_data:
            data = validated_data.pop("data")

            validated_data["encrypted_data"] = json.dumps(data)

        return super().update(instance, validated_data)