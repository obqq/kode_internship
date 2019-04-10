import re

from rest_framework import serializers
from rest_framework.serializers import ValidationError
import django.contrib.auth.password_validation as validators

from api.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'],
                                        password=validated_data['password'])
        user.save()
        return user

    def validate_password(self, password):
        validators.validate_password(password=password, user=User)

        return password


class SpeechSerializer(serializers.Serializer):
    languageCode = serializers.CharField()
    encoding = serializers.CharField()
    sampleRateHertz = serializers.IntegerField()

    enums = {'ENCODING_UNSPECIFIED': None,
             'LINEAR16': None,
             'FLAC': None,
             'MULAW': None,
             'AMR': [8000],
             'AMR_WB': [16000],
             'OGG_OPUS': [8000, 12000, 16000, 24000, 48000],
             'SPEEX_WITH_HEADER_BYTE': [16000]}

    def validate(self, data):
        if not data:
            raise ValidationError("Required parameters were not specified.")

        self.validate_audio_encoding(data.get('encoding'), data.get('sampleRateHertz'))

        return data

    def validate_languageCode(self, languageCode):
        """
        Raise a ValidationError if the value doesn't match
        the language tag pattern.
        """

        if not bool(re.match("[a-z]{2}-[A-Z]{2}$", languageCode)):
            msg = "'languageCode' value does not match the language tag pattern."
            raise ValidationError(msg)

    def validate_audio_encoding(self, encoding, sampleRateHertz):
        """
        Raise a ValidationError if the value doesn't match
        google's specifications.
        """

        if type(encoding) is not str:
            raise ValidationError("Parameter has invalid type")

        for enum, rates in self.enums.items():
            if encoding != enum:
                continue

            if rates is None:
                break

            if not (8000 <= sampleRateHertz <= 48000) or \
                    sampleRateHertz not in self.enums.get(self.encoding):
                msg = "Parameter 'sampleRateHertz' value does not match Google's specifications."
                raise ValidationError(msg)

            break
        else:
            msg = "Invalid 'encoding' value."
            raise ValidationError(msg)