import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import Vault, VaultItem
import json

from vault.services.encryption import encrypt_data, decrypt_data
from vault.services.file_encryption import encrypt_file

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
    data = serializers.JSONField(write_only=True, required=False)
    item_type = serializers.ChoiceField(
        choices=VaultItem.ITEM_CHOICES,
        default="LOG"
    )
    metadata = serializers.JSONField(required=False)
    item_file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = VaultItem
        fields = ('vault', 'title', 'item_type', 'data', 'item_file' , 'metadata')

    def validate(self, attrs):
        request = self.context.get("request")
        vault = attrs.get("vault") or getattr(self.instance, 'vault', None)
        item_type = attrs.get("item_type") or getattr(self.instance, 'item_type', None)
        data = attrs.get("data")
        item_file = attrs.get("item_file")

        if vault and vault.owner != request.user:
            raise serializers.ValidationError(
                {"vault": "You can not make changes to another user's vault."}
            )

        if item_type == "DOC":
            if not item_file:
                raise serializers.ValidationError(
                    { "item_file": "File is mandatory for Document items." }
                )

        elif item_type in ["LOG", "NOT"]:
            if item_file:
                raise serializers.ValidationError(
                    { "item_file": "Files can only be uploaded for Document items." }
                )

            if not data:
                raise serializers.ValidationError(
                    {"data": "Data field is mandatory."}
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
        data = validated_data.pop("data", None)
        file = validated_data.pop("item_file", None)

        #Encrypt incoming file and store file metadata
        if validated_data["item_type"] == "DOC":
            file_bytes = file.read()
            encrypted_bytes = encrypt_file(file_bytes)

            encrypted_file = ContentFile(
                encrypted_bytes,
                name=f"{uuid.uuid4()}.enc"
            )

            validated_data["item_file"] = encrypted_file

            validated_data["metadata"] = {
                "original name": file.name,
                "size": file.size,
                "content_type": file.content_type
            }

        # Encrypt incoming data dictionary
        else:
            validated_data["encrypted_data"] = encrypt_data(data)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        file = validated_data.pop("item_file", None)

        if instance.item_type == "DOC" and file:
            if instance.item_file:
                instance.item_file.delete(save=False)

            file_bytes = file.read()
            encrypted_bytes = encrypt_file(file_bytes)

            encrypted_file = ContentFile(
                encrypted_bytes,
                name=f"{uuid.uuid4()}.enc"
            )

            instance.item_file = encrypted_file

            instance.metadata = {
                "original name": file.name,
                "size": file.size,
                "content_type": file.content_type
            }

        elif "data" in validated_data:
            data = validated_data.pop("data")

            validated_data["encrypted_data"] = encrypt_data(data)

        return super().update(instance, validated_data)


    #Returns decrypted data dictionary
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.encrypted_data:
            decrypted = decrypt_data(instance.encrypted_data)
            representation["data"] = decrypted

        return representation