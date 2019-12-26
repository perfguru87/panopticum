from rest_framework import serializers

from .models import *


class ComponentDataPrivacyClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentDataPrivacyClassModel
        fields = '__all__'


class ComponentRuntimeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentRuntimeTypeModel
        fields = '__all__'


class ComponentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentCategoryModel
        fields = '__all__'


class ComponentSubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentSubcategoryModel
        fields = '__all__'


class ProductFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFamilyModel
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    family = ProductFamilySerializer(read_only=True)

    class Meta:
        model = ProductModel
        fields = '__all__'


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonModel
        fields = '__all__'


class ComponentSerializer(serializers.ModelSerializer):
    runtime_type = ComponentRuntimeTypeSerializer(read_only=True)
    data_privacy_class = ComponentDataPrivacyClassSerializer(read_only=True)
    category = ComponentCategorySerializer(read_only=True)
    subcategory = ComponentSubcategorySerializer(read_only=True)
    product = ProductSerializer(read_only=True, many=True)

    class Meta:
        model = ComponentModel
        fields = '__all__'


class ComponentVersionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    component = ComponentSerializer(read_only=True)
    owner_maintainer = PersonSerializer(read_only=True)
    owner_responsible_qa = PersonSerializer(read_only=True)

    class Meta:
        model = ComponentVersionModel
        fields = '__all__'
