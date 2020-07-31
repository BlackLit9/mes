from datetime import datetime

from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from basics.models import GlobalCode
from mes.base_serializer import BaseModelSerializer
from recipe.models import Material, ProductInfo, ProductRecipe, ProductBatching, ProductBatchingDetail, MaterialAttribute
from mes.conf import COMMON_READ_ONLY_FIELDS


class MaterialSerializer(serializers.ModelSerializer):
    material_type_name = serializers.CharField(source='material_type.global_name', read_only=True)
    packet_unit_name = serializers.CharField(source='packet_unit.global_name', read_only=True)
    created_user_name = serializers.CharField(source='created_user.username', read_only=True)
    update_user_name = serializers.SerializerMethodField(read_only=True)

    def get_update_user_name(self, obj):
        return obj.last_updated_user.username if obj.last_updated_user else None

    def create(self, validated_data):
        validated_data['created_user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['last_updated_user'] = self.context['request'].user
        return super().update(instance, validated_data)

    class Meta:
        model = Material
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class MaterialAttributeSerializer(serializers.ModelSerializer):
    material_no = serializers.CharField(source='Material.material_no', read_only=True)
    material_name = serializers.CharField(source='Material.material_name', read_only=True)
    # for_short = serializers.CharField(source='Material.for_short', read_only=True)
    # material_type_name = serializers.CharField(source='Material.material_type.global_name', read_only=True)
    # material_type_id = serializers.CharField(source='Material.material_type.id', read_only=True)
    # material_id = serializers.CharField(source='material.id')

    class Meta:
        model = MaterialAttribute
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProductRecipeSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.material_name', read_only=True)
    stage_name = serializers.CharField(source='stage.global_name', read_only=True)
    material_material_type = serializers.CharField(source='material.material_type.global_name', read_only=True)

    class Meta:
        model = ProductRecipe
        exclude = ('product_info', 'product_recipe_no')


class ProductInfoCreateSerializer(serializers.ModelSerializer):
    productrecipe_set = ProductRecipeSerializer(many=True, help_text="""[{"num": 编号, "material": 原材料id, 
    "stage": 段次id, "ratio": 配比}...]""")

    def validate(self, attrs):
        versions = attrs['versions']
        factory = attrs['factory']
        product_no = attrs['product_no']
        product_info = ProductInfo.objects.filter(factory=factory, product_no=product_no).order_by('-versions').first()
        if product_info:
            if product_info.versions >= versions:  # TODO 目前版本检测根据字符串做比较，后期搞清楚具体怎样填写版本号
                raise serializers.ValidationError('版本不得小于目前已有的版本')
        recipes = attrs.get('productrecipe_set')
        recipe_weight = sum(i.get('ratio', 0) for i in recipes)
        used_type = GlobalCode.objects.filter(global_type__type_name='胶料状态',
                                              global_name='编辑',
                                              used_flag=0).first()
        if not used_type:
            raise serializers.ValidationError('请先配置公共代码中的胶料状态【编辑】数据')
        attrs['used_type'] = used_type
        attrs['recipe_weight'] = recipe_weight
        return attrs

    @atomic()
    def create(self, validated_data):
        recipes = validated_data.pop('productrecipe_set', None)
        validated_data['created_user'] = self.context['request'].user
        instance = super().create(validated_data)
        recipes_list = []
        product_recipe_no = '{}-{}-{}'.format(instance.factory.global_no, instance.product_no, instance.versions)
        # TODO 搞清楚product_info表存的是编号还是编码
        for recipe in recipes:
            recipe['product_info'] = instance
            recipe['product_recipe_no'] = product_recipe_no
            recipes_list.append(ProductRecipe(**recipe))
        ProductRecipe.objects.bulk_create(recipes_list)
        return instance

    class Meta:
        model = ProductInfo
        fields = ('product_no', 'product_name', 'versions', 'precept',
                  'factory', 'productrecipe_set')


class ProductInfoSerializer(serializers.ModelSerializer):
    product_standard_no = serializers.SerializerMethodField()
    factory = serializers.CharField(source='factory.global_name')
    update_user = serializers.SerializerMethodField(read_only=True)
    used_user = serializers.SerializerMethodField(read_only=True)
    used_type_name = serializers.CharField(source='used_type.global_name')

    def get_product_standard_no(self, obj):
        """胶料标准编码"""
        return '{}-{}-{}'.format(obj.factory.global_no, obj.product_no, obj.versions)

    def get_update_user(self, obj):
        return obj.last_updated_user.username if obj.last_updated_user else None

    def get_used_user(self, obj):
        return obj.used_user.username if obj.used_user else None

    class Meta:
        model = ProductInfo
        fields = ('id', 'product_standard_no', 'product_name', 'factory', 'used_type', "used_user",
                  'recipe_weight', 'used_time', 'obsolete_time', 'update_user', 'used_type_name')


class ProductInfoPartialUpdateSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        used_type0 = GlobalCode.objects.filter(global_type=self.instance.used_type.global_type,
                                               global_name='编辑',
                                               used_flag=0).first()
        used_type1 = GlobalCode.objects.filter(global_type=self.instance.used_type.global_type,
                                               global_name='应用',
                                               used_flag=0).first()
        used_type2 = GlobalCode.objects.filter(global_type=self.instance.used_type.global_type,
                                               global_name='废弃',
                                               used_flag=0).first()
        if not all([used_type1, used_type2]):
            raise serializers.ValidationError('请先配置公共代码中的胶料状态【应用】数据')
        attrs['used_type0'] = used_type0
        attrs['used_type1'] = used_type1
        attrs['used_type2'] = used_type2
        return attrs

    def update(self, instance, validated_data):
        if instance.used_type == validated_data['used_type0']:  # 应用
            instance.used_type = validated_data['used_type1']
            instance.used_user = self.context['request'].user
            instance.used_time = datetime.now()
            # 废弃旧版本
            ProductInfo.objects.filter(used_type=validated_data['used_type1'],
                                       product_no=instance.product_no,
                                       factory=instance.factory
                                       ).update(used_type=validated_data['used_type2'],
                                                obsolete_time=datetime.now())
        elif instance.used_type == validated_data['used_type1']:  # 应用  # 废弃
            instance.used_type = validated_data['used_type2']
            instance.obsolete_time = datetime.now()
        instance.last_updated_user = self.context['request'].user
        instance.save()
        return instance

    class Meta:
        model = ProductInfo
        fields = ('id',)


class ProductInfoUpdateSerializer(serializers.ModelSerializer):
    product_standard_no = serializers.SerializerMethodField(read_only=True)
    productrecipe_set = ProductRecipeSerializer(many=True)
    used_type = serializers.CharField(source='used_type.global_name', read_only=True)

    def get_product_standard_no(self, obj):
        """胶料标准编码"""
        return '{}-{}-{}'.format(obj.factory.global_no, obj.product_no, obj.versions)

    @atomic()
    def update(self, instance, validated_data):
        if not instance.used_type.global_name == '编辑':
            raise PermissionDenied('当前胶料不是编辑状态，无法操作')
        recipes = validated_data.pop('productrecipe_set', None)
        recipe_weight = sum(i.get('ratio', 0) for i in recipes)
        if recipes:
            ProductRecipe.objects.filter(product_info=instance).delete()
            recipes_list = []
            product_recipe_no = '{}-{}-{}'.format(instance.factory.global_no, instance.product_no, instance.versions)
            # TODO 搞清楚product_info表存的是编号还是编码
            for recipe in recipes:
                recipe['product_recipe_no'] = product_recipe_no
                recipe['product_info'] = instance
                recipes_list.append(ProductRecipe(**recipe))
            ProductRecipe.objects.bulk_create(recipes_list)
        instance.recipe_weight = recipe_weight
        instance.save()
        return instance

    class Meta:
        model = ProductInfo
        fields = ('id', 'product_standard_no', 'product_name', 'used_type', 'recipe_weight', 'productrecipe_set')
        read_only_fields = ('product_name', 'recipe_weight')


class ProductInfoCopySerializer(serializers.ModelSerializer):
    product_info_id = serializers.PrimaryKeyRelatedField(queryset=ProductInfo.objects.exclude(
        used_type__global_type__type_name='胶料状态', used_type__global_name='编辑', used_type__used_flag=0), write_only=True,
        help_text='复制配方工艺id')

    def validate(self, attrs):
        versions = attrs['versions']
        factory = attrs['factory']
        product_no = attrs['product_info_id'].product_no
        product_info = ProductInfo.objects.filter(factory=factory, product_no=product_no).order_by('-versions').first()
        if product_info:
            if product_info.versions >= versions:  # TODO 目前版本检测根据字符串做比较，后期搞清楚具体怎样填写版本号
                raise serializers.ValidationError('版本不得小于目前已有的版本')
        used_type = GlobalCode.objects.filter(global_type__type_name='胶料状态',
                                              global_name='编辑',
                                              used_flag=0).first()
        if not used_type:
            raise serializers.ValidationError('请先配置公共代码中的胶料状态【编辑】数据')
        attrs['used_type'] = used_type
        return attrs

    @atomic()
    def create(self, validated_data):
        base_product_info = validated_data.pop('product_info_id')
        validated_data['created_user'] = self.context['request'].user
        validated_data['recipe_weight'] = base_product_info.recipe_weight
        validated_data['product_no'] = base_product_info.product_no
        validated_data['product_name'] = base_product_info.product_name
        validated_data['precept'] = base_product_info.precept
        instance = super().create(validated_data)
        recipes = base_product_info.productrecipe_set.filter(delete_flag=False).values(
            'product_recipe_no', 'num', 'material_id', 'stage_id', 'ratio')
        recipes_list = []
        for recipe in recipes:
            recipe['product_info'] = instance
            recipes_list.append(ProductRecipe(**recipe))
        ProductRecipe.objects.bulk_create(recipes_list)
        return instance

    class Meta:
        model = ProductInfo
        fields = ('product_info_id', 'factory', 'versions')


class ProductRecipeListSerializer(serializers.ModelSerializer):
    material_type = serializers.CharField(source='material.material_type.global_name')
    material_name = serializers.CharField(source='material.material_name')
    density = serializers.CharField(source='material.density')

    class Meta:
        model = ProductRecipe
        fields = ('material_type', 'material', 'ratio', 'density', 'material_name')


class ProductBatchingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBatchingDetail
        exclude = ('product_batching', 'density', 'ratio')


class ProductBatchingListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_info.product_name')
    dev_type_name = serializers.CharField(source='dev_type.global_name')
    used_type_name = serializers.CharField(source='product_info.used_type.global_name')
    created_user_name = serializers.CharField(source='created_user.username', read_only=True)
    update_user_name = serializers.SerializerMethodField(read_only=True)

    def get_update_user_name(self, obj):
        return obj.last_updated_user.username if obj.last_updated_user else None

    class Meta:
        model = ProductBatching
        fields = ('id', 'stage_product_batch_no', 'product_name', 'dev_type_name', 'used_type_name',
                  'batching_weight', 'production_time_interval', 'rm_flag', 'rm_time_interval',
                  'created_user_name', 'created_date', 'update_user_name', 'last_updated_date')


class ProductBatchingCreateSerializer(serializers.ModelSerializer):
    batching_details = ProductBatchingDetailSerializer(many=True, help_text=
    """
    配料详情：{
             'num': '序号',
             'material': '原材料',
             'ratio_weight': '配比体积',
             'standard_volume': '序号',
             'actual_volume': '计算体积',
             'standard_weight': '实际体积',
             'actual_weight': '标准重量',
             'time_interval': '实际重量',
             'temperature': '温度',
             'rpm': '转速',
         }""")

    def validate(self, attrs):
        batching_details = attrs.get('batching_details', None)
        batching_weight = manual_material_weight = volume = 0
        for detail in batching_details:
            batching_weight += detail.get('actual_weight', 0)
            volume += detail.get('actual_volume', 0)
            if detail.get('material'):
                if detail.get('material').material_type.global_type.type_name == '手动小料':
                    manual_material_weight += detail.get('actual_weight', 0)
        attrs['manual_material_weight'] = manual_material_weight
        attrs['batching_weight'] = batching_weight
        attrs['volume'] = volume
        attrs['batching_proportion'] = float(batching_weight / volume) if volume else 0
        attrs['created_user'] = self.context['request'].user
        return attrs

    @atomic()
    def create(self, validated_data):
        batching_details = validated_data.pop('batching_details', None)
        instance = super().create(validated_data)
        batching_detail_list = []
        for detail in batching_details:
            detail['product_batching'] = instance
            detail['ratio'] = ProductRecipe
            if detail.get('material'):
                recipe = ProductRecipe.objects.filter(product_info=validated_data['product_info'],
                                                      stage=validated_data['stage'],
                                                      material=detail['material']
                                                      ).first()
                if recipe:
                    detail['ratio'] = recipe.ratio
                detail['density'] = detail.get('material').density
            else:
                detail['density'] = 0
            batching_detail_list.append(ProductBatchingDetail(**detail))
        ProductBatchingDetail.objects.bulk_create(batching_detail_list)
        return instance

    class Meta:
        model = ProductBatching
        fields = ('product_info', 'stage_product_batch_no', 'stage', 'dev_type',
                  'batching_time_interval', 'rm_time_interval', 'production_time_interval', 'batching_details'
                  )


class ProductBatchingRetrieveSerializer(ProductBatchingListSerializer):
    batching_details = ProductBatchingDetailSerializer(many=True)

    class Meta:
        model = ProductBatching
        fields = '__all__'


class ProductBatchingUpdateSerializer(ProductBatchingRetrieveSerializer):

    def validate(self, attrs):
        batching_details = attrs.get('batching_details', None)
        batching_weight = manual_material_weight = volume = 0
        for detail in batching_details:
            batching_weight += detail.get('actual_weight', 0)
            volume += detail.get('actual_volume', 0)
            if detail.get('material'):
                if detail.get('material').material_type.global_type.type_name == '手动小料':
                    manual_material_weight += detail.get('actual_weight', 0)
        attrs['manual_material_weight'] = manual_material_weight
        attrs['batching_weight'] = batching_weight
        attrs['volume'] = volume
        attrs['batching_proportion'] = float(batching_weight / volume) if volume else 0
        attrs['created_user'] = self.context['request'].user
        return attrs

    @atomic()
    def update(self, instance, validated_data):
        batching_details = validated_data.pop('batching_details', None)
        instance = super().update(instance, validated_data)
        instance.batching_details.all().delete()
        batching_detail_list = []
        for detail in batching_details:
            detail['product_batching'] = instance
            detail['ratio'] = ProductRecipe
            if detail.get('material'):
                recipe = ProductRecipe.objects.filter(product_info=instance.product_info,
                                                      stage=instance.stage,
                                                      material=detail['material']
                                                      ).first()
                if recipe:
                    detail['ratio'] = recipe.ratio
                detail['density'] = detail.get('material').density
            else:
                detail['density'] = 0
            batching_detail_list.append(ProductBatchingDetail(**detail))
        ProductBatchingDetail.objects.bulk_create(batching_detail_list)
        return instance

    class Meta:
        model = ProductBatching
        fields = ('id', 'batching_details')


class ProductMasterSerializer(BaseModelSerializer):

    factory = serializers.CharField(source="product_info.factory.global_name")
    versions = serializers.CharField(source="product_info.versions")
    stage = serializers.CharField(source="stage.global_name")
    dev_type = serializers.CharField(source="dev_type.global_name")

    class Meta:
        model = ProductBatching
        fields = "__all__"
