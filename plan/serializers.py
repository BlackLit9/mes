from datetime import datetime

from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from plan.models import ProductDayPlan, ProductClassesPlan, MaterialDemanded, ProductBatchingDayPlan, \
    ProductBatchingClassesPlan, MaterialRequisition, MaterialRequisitionClasses
from basics.models import PlanSchedule
from mes.conf import COMMON_READ_ONLY_FIELDS
from recipe.models import Material


class ProductClassesPlanSerializer(serializers.ModelSerializer):
    classes = serializers.CharField(source='classes_detail.classes.global_name', read_only=True)

    class Meta:
        model = ProductClassesPlan
        exclude = ('product_day_plan',)
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProductDayPlanSerializer(serializers.ModelSerializer):
    # inventory=serializers.IntegerField(source='') TODO:库存暂时不写

    pdp_product_classes_plan = ProductClassesPlanSerializer(many=True,
                                                            help_text='{"sn":1,"num":1,"time":"2020-12-12 12:12:12","weight":1,"unint":1,"classes_detail":1}')

    class Meta:
        model = ProductDayPlan
        fields = ('equip', 'product_master', 'plan_schedule', 'pdp_product_classes_plan')

    @atomic()
    def create(self, validated_data):
        pdp_dic = {}
        pdp_dic['equip'] = validated_data.pop('equip')
        pdp_dic['product_master'] = validated_data.pop('product_master')
        pdp_dic['plan_schedule'] = validated_data.pop('plan_schedule')
        instance = ProductDayPlan.objects.create(**pdp_dic)
        details = validated_data['pdp_product_classes_plan']
        for detail in details:
            detail_dic = dict(detail)
            detail_dic['product_day_plan'] = instance
            ProductClassesPlan.objects.create(**detail_dic)
        return instance


class MaterialDemandedSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.material_name', read_only=True)
    classes_name = serializers.CharField(source='classes.classes_name', read_only=True)

    class Meta:
        model = MaterialDemanded
        fields = (
            'product_day_plan', 'classes', 'material', 'material_name', 'classes_name', 'material_demanded',)


class ProductBatchingClassesPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBatchingClassesPlan
        exclude = ('product_batching_day_plan',)
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProductBatchingDayPlanSerializer(serializers.ModelSerializer):
    pdp_product_batching_classes_plan = ProductBatchingClassesPlanSerializer(many=True,
                                                                             help_text='{"product_master":1,"num":1,"time":"2020-12-12 12:12:12","weight":1,"unint":"1","classes_detail":1}')

    class Meta:
        model = ProductBatchingDayPlan
        fields = (
            'equip', 'product_master', 'plan_schedule', 'sum', 'product_day_plan', 'pdp_product_batching_classes_plan')

    @atomic()
    def create(self, validated_data):
        print(validated_data)
        pdp_dic = {}
        pdp_dic['equip'] = validated_data.pop('equip')
        pdp_dic['product_master'] = validated_data.pop('product_master')
        pdp_dic['plan_schedule'] = validated_data.pop('plan_schedule')
        pdp_dic['sum'] = validated_data.pop('sum')
        pdp_dic['product_day_plan'] = validated_data.pop('product_day_plan')
        instance = ProductBatchingDayPlan.objects.create(**pdp_dic)
        details = validated_data['pdp_product_batching_classes_plan']
        for detail in details:
            detail_dic = dict(detail)
            detail_dic['product_batching_day_plan'] = instance
            ProductBatchingClassesPlan.objects.create(**detail_dic)
        return instance


class MaterialRequisitionClassesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialRequisitionClasses
        exclude = ('material_requisition',)
        read_only_fields = COMMON_READ_ONLY_FIELDS


class MaterialRequisitionSerializer(serializers.ModelSerializer):
    mr_material_requisition_classes = MaterialRequisitionClassesSerializer(many=True,
                                                                           help_text='{"product_master":1,"weight":1,"unint":"1","classes_detail":1}')

    class Meta:
        model = MaterialRequisition
        fields = (
            'material_demanded', 'count', 'plan_schedule', 'unint', 'mr_material_requisition_classes')

    @atomic()
    def create(self, validated_data):
        print(validated_data)
        pdp_dic = {}
        pdp_dic['material_demanded'] = validated_data.pop('material_demanded')
        pdp_dic['count'] = validated_data.pop('count')
        pdp_dic['plan_schedule'] = validated_data.pop('plan_schedule')
        pdp_dic['unint'] = validated_data.pop('unint')
        instance = MaterialRequisition.objects.create(**pdp_dic)
        print(instance)
        details = validated_data['mr_material_requisition_classes']
        for detail in details:
            detail_dic = dict(detail)
            detail_dic['material_requisition'] = instance  # TODO 暂且写1 是否是领料计划
            MaterialRequisitionClasses.objects.create(**detail_dic)
        return instance


class ProductDayPlanCopySerializer(serializers.ModelSerializer):
    src_date = serializers.DateTimeField(help_text="2020-07-31 10:46:00", write_only=True)
    dst_date = serializers.DateTimeField(help_text="2020-07-31 10:50:00", write_only=True)

    class Meta:
        model = ProductDayPlan
        fields = ('src_date', 'dst_date')

    def validate_src_date(self, value):
        instance = PlanSchedule.objects.filter(day_time=value).first()
        if not instance:
            raise serializers.ValidationError('被复制的日期没有计划时间')
        pdp_obj = ProductDayPlan.objects.filter(plan_schedule=instance)
        if not pdp_obj:
            raise serializers.ValidationError('被复制的日期没有计划')
        return value

    def validate_dst_date(self, value):
        instance = PlanSchedule.objects.filter(day_time=value)
        if not instance:
            raise serializers.ValidationError('新建的日期没有计划时间')
        return value

    def validate(self, attrs):
        src_date = attrs['src_date']
        dst_date = attrs['dst_date']
        if dst_date < src_date:
            raise serializers.ValidationError('新建日期不能小于被复制日期')
        return attrs

    @atomic()
    def create(self, validated_data):
        print(validated_data)
        src_date = validated_data.pop('src_date')
        dst_date = validated_data.pop('dst_date')
        ps_obj = PlanSchedule.objects.filter(day_time=dst_date).first()
        pdp_queryset = ProductDayPlan.objects.filter(plan_schedule__day_time=src_date)
        for pdp_obj in pdp_queryset:
            instance = ProductDayPlan.objects.create(equip=pdp_obj.equip, product_master=pdp_obj.product_master,
                                                     plan_schedule=ps_obj)
            pc_obj = ProductClassesPlan.objects.filter(product_day_plan=pdp_obj).first()
            ProductClassesPlan.objects.create(product_day_plan=instance, sn=pc_obj.sn, num=pc_obj.num, time=pc_obj.time,
                                              weight=pc_obj.weight, unint=pc_obj.unint,
                                              classes_detail=pc_obj.classes_detail)
        return instance


class ProductBatchingDayPlanCopySerializer(serializers.ModelSerializer):
    src_date = serializers.DateTimeField(help_text="2020-07-31 10:46:00", write_only=True)
    dst_date = serializers.DateTimeField(help_text="2020-07-31 10:50:00", write_only=True)

    class Meta:
        model = ProductBatchingDayPlan
        fields = ('src_date', 'dst_date')

    def validate_src_date(self, value):
        instance = PlanSchedule.objects.filter(day_time=value).first()
        if not instance:
            raise serializers.ValidationError('被复制的日期没有计划时间')
        pdp_obj = ProductBatchingDayPlan.objects.filter(plan_schedule=instance)
        if not pdp_obj:
            raise serializers.ValidationError('被复制的日期没有计划')
        return value

    def validate_dst_date(self, value):
        instance = PlanSchedule.objects.filter(day_time=value)
        if not instance:
            raise serializers.ValidationError('新建的日期没有计划时间')
        return value

    def validate(self, attrs):
        src_date = attrs['src_date']
        dst_date = attrs['dst_date']
        if dst_date < src_date:
            raise serializers.ValidationError('新建日期不能小于被复制日期')
        return attrs

    @atomic()
    def create(self, validated_data):
        print(validated_data)
        src_date = validated_data.pop('src_date')
        dst_date = validated_data.pop('dst_date')
        ps_obj = PlanSchedule.objects.filter(day_time=dst_date).first()
        pbdp_queryset = ProductBatchingDayPlan.objects.filter(plan_schedule__day_time=src_date)
        for pbdp_obj in pbdp_queryset:
            instance = ProductBatchingDayPlan.objects.create(equip=pbdp_obj.equip,
                                                             product_master=pbdp_obj.product_master,
                                                             plan_schedule=ps_obj, sum=pbdp_obj.sum,
                                                             product_day_plan=pbdp_obj.product_day_plan)
            pc_obj = ProductBatchingClassesPlan.objects.filter(product_batching_day_plan=pbdp_obj).first()
            ProductBatchingClassesPlan.objects.create(product_batching_day_plan=instance,
                                                      product_master=pc_obj.product_master, num=pc_obj.num,
                                                      time=pc_obj.time,
                                                      weight=pc_obj.weight, unint=pc_obj.unint,
                                                      classes_detail=pc_obj.classes_detail)
        return instance


class MaterialRequisitionCopySerializer(serializers.ModelSerializer):
    src_date = serializers.DateTimeField(help_text="2020-07-31 10:46:00", write_only=True)
    dst_date = serializers.DateTimeField(help_text="2020-07-31 10:50:00", write_only=True)

    class Meta:
        model = MaterialRequisition
        fields = ('src_date', 'dst_date')

    def validate_src_date(self, value):
        instance = PlanSchedule.objects.filter(day_time=value).first()
        if not instance:
            raise serializers.ValidationError('被复制的日期没有计划时间')
        pdp_obj = MaterialRequisition.objects.filter(plan_schedule=instance)
        if not pdp_obj:
            raise serializers.ValidationError('被复制的日期没有计划')
        return value

    def validate_dst_date(self, value):
        instance = PlanSchedule.objects.filter(day_time=value)
        if not instance:
            raise serializers.ValidationError('新建的日期没有计划时间')
        return value

    def validate(self, attrs):
        src_date = attrs['src_date']
        dst_date = attrs['dst_date']
        if dst_date < src_date:
            raise serializers.ValidationError('新建日期不能小于被复制日期')
        return attrs

    @atomic()
    def create(self, validated_data):
        print(validated_data)
        src_date = validated_data.pop('src_date')
        dst_date = validated_data.pop('dst_date')
        ps_obj = PlanSchedule.objects.filter(day_time=dst_date).first()
        mr_queryset = MaterialRequisition.objects.filter(plan_schedule__day_time=src_date)
        for mr_obj in mr_queryset:
            instance = MaterialRequisition.objects.create(material_demanded=mr_obj.material_demanded,
                                                          count=mr_obj.count,
                                                          plan_schedule=ps_obj, unint=mr_obj.unint
                                                          )
            pc_obj = MaterialRequisitionClasses.objects.filter(material_requisition=mr_obj).first()
            MaterialRequisitionClasses.objects.create(material_requisition=instance,
                                                      product_master=pc_obj.product_master,
                                                      weight=pc_obj.weight,
                                                      unint=pc_obj.unint,
                                                      classes_detail=pc_obj.classes_detail)
        return instance
