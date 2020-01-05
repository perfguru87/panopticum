from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict

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


class ProductVersionSerializer(serializers.ModelSerializer):
    family = ProductFamilySerializer(read_only=True)

    class Meta:
        model = ProductVersionModel
        fields = '__all__'


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonModel
        fields = '__all__'


class SoftwareVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftwareVendorModel
        fields = '__all__'


class DeploymentLocationClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeploymentLocationClassModel
        fields = '__all__'


class DeploymentEnvironmentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeploymentEnvironmentModel
        fields = '__all__'


class ComponentDeploymentSerializer(serializers.ModelSerializer):
    product_version = ProductVersionSerializer(read_only=True)
    environment = DeploymentEnvironmentModelSerializer(read_only=True)
    location_class = DeploymentLocationClassSerializer(read_only=True)
    open_ports = serializers.SerializerMethodField()

    def get_open_ports(self, deployment):
        return ", ".join([str(p.port) for p in deployment.open_ports.all()])

    class Meta:
        model = ComponentDeploymentModel
        fields = '__all__'


class ComponentSerializerSimple(serializers.ModelSerializer):
    runtime_type = ComponentRuntimeTypeSerializer(read_only=True)
    data_privacy_class = ComponentDataPrivacyClassSerializer(read_only=True)
    category = ComponentCategorySerializer(read_only=True)
    subcategory = ComponentSubcategorySerializer(read_only=True)
    product = ProductVersionSerializer(read_only=True, many=True)
    vendor = SoftwareVendorSerializer(read_only=True)

    class Meta:
        model = ComponentModel
        fields = '__all__'


class ComponentDependencySerializerSimple(serializers.ModelSerializer):
    component = ComponentSerializerSimple(read_only=True)

    class Meta:
        model = ComponentDependencyModel
        fields = '__all__'


class ComponentVersionSerializerSimple(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    depends_on = ComponentDependencySerializerSimple(source='componentdependencymodel_set', many=True, read_only=True)

    owner_maintainer = PersonSerializer(read_only=True)
    owner_responsible_qa = PersonSerializer(read_only=True)

    owner_product_manager = PersonSerializer(read_only=True, many=True)
    owner_program_manager = PersonSerializer(read_only=True, many=True)
    owner_escalation_list = PersonSerializer(read_only=True, many=True)
    owner_expert = PersonSerializer(read_only=True, many=True)
    owner_architect = PersonSerializer(read_only=True, many=True)

    dev_languages = serializers.SerializerMethodField()
    dev_frameworks = serializers.SerializerMethodField()

    compliance = serializers.SerializerMethodField()
    operations = serializers.SerializerMethodField()
    maintenance = serializers.SerializerMethodField()
    quality_assurance = serializers.SerializerMethodField()

    deployments = serializers.SerializerMethodField()

    meta_locations = DeploymentLocationClassSerializer(read_only=True, many=True)
    meta_product_versions = ProductVersionSerializer(read_only=True, many=True)

    def get_dev_languages(self, component):
        objs = component.dev_language.get_queryset()
        return ", ".join([o.name for o in objs])

    def get_dev_frameworks(self, component):
        objs = component.dev_framework.get_queryset()
        return ", ".join([o.name for o in objs])

    def _serialize_fields(self, component, applicable, fields):
        ret = []
        for f in fields:
            signoff = getattr(component, f.replace('_status', '_signoff'))
            ret.append({'title': component._meta.get_field(f).verbose_name,
                        'field': f,
                        'status': getattr(component, f) if applicable else "n/a",
                        'notes': getattr(component, f.replace('_status', '_notes')) if applicable else "",
                        'signoff': signoff.email if signoff and applicable else ""})
        return ret

    def get_compliance(self, component):
        return self._serialize_fields(component, component.compliance_applicable, ComponentVersionModel.get_compliance_fields())

    def get_operations(self, component):
        return self._serialize_fields(component, component.op_applicable, ComponentVersionModel.get_operations_fields())

    def get_maintenance(self, component):
        return self._serialize_fields(component, component.mt_applicable, ComponentVersionModel.get_maintenance_fields())

    def get_quality_assurance(self, component):
        return self._serialize_fields(component, component.qa_applicable, ComponentVersionModel.get_quality_assurance_fields())

    def get_deployments(self, component):
        return ComponentDeploymentSerializer(ComponentDeploymentModel.objects.filter(component_version=component),
                                             read_only=True, many=True).data

    class Meta:
        model = ComponentVersionModel
        exclude = ComponentVersionModel.get_compliance_fields() + \
                  ComponentVersionModel.get_maintenance_fields() + \
                  ComponentVersionModel.get_operations_fields() + \
                  ComponentVersionModel.get_quality_assurance_fields()


class ComponentSerializer(ComponentSerializerSimple):
    latest_version = serializers.SerializerMethodField()

    def get_latest_version(self, component):
         objs = ComponentVersionModel.objects.filter(component=component.id).order_by('-meta_update_date')
         if len(objs):
              return ComponentVersionSerializerSimple(objs[0]).data
         return None


class ComponentVersionSerializer(ComponentVersionSerializerSimple):
    component = ComponentSerializerSimple(read_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = ('password', )
