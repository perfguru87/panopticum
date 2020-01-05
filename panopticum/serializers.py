from rest_framework import serializers

from .models import *


class ComponentDataPrivacyClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentDataPrivacyClass
        fields = '__all__'


class ComponentRuntimeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentRuntimeType
        fields = '__all__'


class ComponentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentCategory
        fields = '__all__'


class ComponentSubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentSubcategory
        fields = '__all__'


class ProductFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFamily
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    family = ProductFamilySerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'


class SoftwareVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftwareVendor
        fields = '__all__'


class DeploymentLocationClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeploymentLocationClass
        fields = '__all__'


class ComponentSerializerSimple(serializers.ModelSerializer):
    runtime_type = ComponentRuntimeTypeSerializer(read_only=True)
    data_privacy_class = ComponentDataPrivacyClassSerializer(read_only=True)
    category = ComponentCategorySerializer(read_only=True)
    subcategory = ComponentSubcategorySerializer(read_only=True)
    product = ProductSerializer(read_only=True, many=True)
    vendor = SoftwareVendorSerializer(read_only=True)

    class Meta:
        model = Component
        fields = '__all__'


class ComponentDependencySerializerSimple(serializers.ModelSerializer):
    component = ComponentSerializerSimple(read_only=True)

    class Meta:
        model = ComponentDependency
        fields = '__all__'


class ComponentVersionSerializerSimple(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    depends_on = ComponentDependencySerializerSimple(source='componentdependencymodel_set', many=True, read_only=True)
    locations = DeploymentLocationClassSerializer(read_only=True, many=True)

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
        return self._serialize_fields(component, component.compliance_applicable, ComponentVersion.get_compliance_fields())

    def get_operations(self, component):
        return self._serialize_fields(component, component.op_applicable, ComponentVersion.get_operations_fields())

    def get_maintenance(self, component):
        return self._serialize_fields(component, component.mt_applicable, ComponentVersion.get_maintenance_fields())

    def get_quality_assurance(self, component):
        return self._serialize_fields(component, component.qa_applicable, ComponentVersion.get_quality_assurance_fields())

    class Meta:
        model = ComponentVersion
        exclude = ComponentVersion.get_compliance_fields() + \
                  ComponentVersion.get_maintenance_fields() + \
                  ComponentVersion.get_operations_fields() + \
                  ComponentVersion.get_quality_assurance_fields()


class ComponentSerializer(ComponentSerializerSimple):
    latest_version = serializers.SerializerMethodField()

    @staticmethod
    def get_latest_version(component):
        objs = ComponentVersion.objects.filter(component=component.id).order_by('-meta_update_date')
        if len(objs):
            return ComponentVersionSerializerSimple(objs[0]).data
        return None


class ComponentVersionSerializer(ComponentVersionSerializerSimple):
    component = ComponentSerializerSimple(read_only=True)
