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


class SoftwareVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftwareVendorModel
        fields = '__all__'


class ComponentSerializerSimple(serializers.ModelSerializer):
    runtime_type = ComponentRuntimeTypeSerializer(read_only=True)
    data_privacy_class = ComponentDataPrivacyClassSerializer(read_only=True)
    category = ComponentCategorySerializer(read_only=True)
    subcategory = ComponentSubcategorySerializer(read_only=True)
    product = ProductSerializer(read_only=True, many=True)
    vendor = SoftwareVendorSerializer(read_only=True)

    class Meta:
        model = ComponentModel
        fields = '__all__'


class ComponentVersionSerializerSimple(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    owner_maintainer = PersonSerializer(read_only=True)
    owner_responsible_qa = PersonSerializer(read_only=True)
    dev_languages = serializers.SerializerMethodField()
    dev_frameworks = serializers.SerializerMethodField()

    def get_dev_languages(self, component):
        objs = component.dev_language.get_queryset()
        return ", ".join([o.name for o in objs])

    def get_dev_frameworks(self, component):
        objs = component.dev_framework.get_queryset()
        return ", ".join([o.name for o in objs])

    class Meta:
        model = ComponentVersionModel
        fields = '__all__'


class ComponentSerializer(ComponentSerializerSimple):
    latest_version = serializers.SerializerMethodField()

    def get_latest_version(self, component):
         objs = ComponentVersionModel.objects.filter(component=component.id).order_by('-meta_update_date')
         if len(objs):
              return ComponentVersionSerializerSimple(objs[0]).data
         return None


class ComponentVersionSerializer(ComponentVersionSerializerSimple):
    component = ComponentSerializerSimple(read_only=True)
