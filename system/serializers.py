"""
auther :liwei
create_date:
updater:
update_time:
"""
from django.contrib.auth.models import Permission
from rest_framework import serializers
from django.contrib.auth.hashers import make_password


from mes.base_serializer import BaseModelSerializer
from system.models import GroupExtension, Group, User,Section, FunctionBlock, FunctionPermission, \
    Function,Menu

COMMON_READ_ONLY_FIELDS = ('created_date', 'last_updated_date', 'delete_date',
                           'delete_flag', 'created_user', 'last_updated_user',
                           'delete_user')


class GroupSerializer(BaseModelSerializer):
    # user_ids = serializers.ListField()
    class Meta:
        model = Group
        fields = '__all__'
        # read_only_fields = COMMON_READ_ONLY_FIELDS

class PermissionSerializer(BaseModelSerializer):

    # group = serializers.HyperlinkedRelatedField(view_name='group-detail', read_only=True, many=True)

    class Meta:
        model = Permission
        fields = ("id", "codename", "name", )


class UserSerializer(BaseModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    def to_representation(self, instance):
        instance = super().to_representation(instance)
        instance.pop('password')
        return instance

    def create(self, validated_data):
        password = validated_data.get('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = '__all__'
        # read_only_fields = COMMON_READ_ONLY_FIELDS

class UserUpdateSerializer(BaseModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    num = serializers.CharField(required=False)
    def to_representation(self, instance):
        instance = super().to_representation(instance)
        instance.pop('password')
        return instance

    def update(self, instance, validated_data):
        validated_data['password'] = make_password(validated_data['password']) if validated_data.get('password') else instance.password
        return super(UserUpdateSerializer, self).update(instance, validated_data)

    class Meta:
        model = User
        fields = '__all__'
        # read_only_fields = COMMON_READ_ONLY_FIELDS


class GroupExtensionSerializer(BaseModelSerializer):
    class Meta:
        model = GroupExtension
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class SectionSerializer(BaseModelSerializer):

    class Meta:
        model = Section
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class FunctionBlockSerializer(BaseModelSerializer):

    class Meta:
        model = FunctionBlock
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class FunctionPermissionSerializer(BaseModelSerializer):

    class Meta:
        model = FunctionPermission
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class FunctionSerializer(BaseModelSerializer):

    class Meta:
        model = Function
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class MenuSerializer(BaseModelSerializer):

    class Meta:
        model = Menu
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS