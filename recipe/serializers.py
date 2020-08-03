from datetime import datetime

from django.db.models import Sum
from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from mes.base_serializer import BaseModelSerializer
from recipe.models import Material, ProductInfo, ProductRecipe, ProductBatching, ProductBatchingDetail, \
    MaterialAttribute
from mes.conf import COMMON_READ_ONLY_FIELDS


class MaterialSerializer(serializers.ModelSerializer):
    material_type_name = serializers.CharField(source='material_type.global_name', read_only=True)
    packet_unit_name = serializers.CharField(source='packet_unit.global_name', read_only=True)
    created_user_name = serializers.CharField(source='created_user.username', read_only=True)
    update_user_name = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_update_user_name(obj):
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
        recipe_weight = sum(i.get('ratio') if i.get('ratio') else 0 for i in recipes)
        attrs['used_type'] = 1
        attrs['recipe_weight'] = recipe_weight
        return attrs

    @atomic()
    def create(self, validated_data):
        recipes = validated_data.pop('productrecipe_set', None)
        validated_data['created_user'] = self.context['request'].user
        instance = super().create(validated_data)
        recipes_list = []
        product_recipe_no = '{}-{}-{}'.format(instance.factory.global_no, instance.product_no, instance.versions)
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

    @staticmethod
    def get_product_standard_no(obj):
        """胶料标准编码"""
        return '{}-{}-{}'.format(obj.factory.global_no, obj.product_no, obj.versions)

    @staticmethod
    def get_update_user(obj):
        return obj.last_updated_user.username if obj.last_updated_user else None

    @staticmethod
    def get_used_user(obj):
        return obj.used_user.username if obj.used_user else None

    class Meta:
        model = ProductInfo
        fields = ('id', 'product_standard_no', 'product_name', 'factory', 'used_type', "used_user",
                  'recipe_weight', 'used_time', 'obsolete_time', 'update_user')


class ProductInfoPartialUpdateSerializer(serializers.ModelSerializer):
    pass_flag = serializers.BooleanField(help_text='通过标志，1：通过, 0:驳回', write_only=True)

    def update(self, instance, validated_data):
        pass_flag = validated_data['pass_flag']
        if pass_flag:
            if instance.used_type == 1:  # 审核通过
                instance.used_type = 2
            elif instance.used_type == 2:  # 应用
                # 废弃旧版本
                ProductInfo.objects.filter(used_type=3,
                                           product_no=instance.product_no,
                                           factory=instance.factory
                                           ).update(used_type=5,
                                                    obsolete_time=datetime.now())
                instance.used_type = 3
                instance.used_user = self.context['request'].user
                instance.used_time = datetime.now()
        else:
            if instance.used_type == 3:  # 废弃
                instance.obsolete_user = self.context['request'].user
                instance.used_type = 5
                instance.obsolete_time = datetime.now()
            else:  # 驳回
                instance.used_type = 4
        instance.last_updated_user = self.context['request'].user
        instance.save()
        return instance

    class Meta:
        model = ProductInfo
        fields = ('id', 'pass_flag')


class ProductInfoUpdateSerializer(serializers.ModelSerializer):
    product_standard_no = serializers.SerializerMethodField(read_only=True)
    productrecipe_set = ProductRecipeSerializer(many=True)

    @staticmethod
    def get_product_standard_no(obj):
        """胶料标准编码"""
        return '{}-{}-{}'.format(obj.factory.global_no, obj.product_no, obj.versions)

    @atomic()
    def update(self, instance, validated_data):
        if instance.used_type != 1:
            raise PermissionDenied('当前胶料不是编辑状态，无法操作')
        recipes = validated_data.pop('productrecipe_set', None)
        recipe_weight = sum(i.get('ratio', 0) for i in recipes)
        if recipes:
            ProductRecipe.objects.filter(product_info=instance).delete()
            recipes_list = []
            product_recipe_no = '{}-{}-{}'.format(instance.factory.global_no, instance.product_no, instance.versions)
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
        fields = ('id', 'product_standard_no', 'product_name', 'recipe_weight', 'productrecipe_set')
        read_only_fields = ('product_name', 'recipe_weight')


class ProductInfoCopySerializer(serializers.ModelSerializer):
    product_info_id = serializers.PrimaryKeyRelatedField(queryset=ProductInfo.objects.exclude(used_type=1),
                                                         write_only=True, help_text='复制配方工艺id')

    def validate(self, attrs):
        versions = attrs['versions']
        factory = attrs['factory']
        product_no = attrs['product_info_id'].product_no
        product_info = ProductInfo.objects.filter(factory=factory, product_no=product_no).order_by('-versions').first()
        if product_info:
            if product_info.versions >= versions:  # TODO 目前版本检测根据字符串做比较，后期搞清楚具体怎样填写版本号
                raise serializers.ValidationError('版本不得小于目前已有的版本')
        attrs['used_type'] = 1
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
    material_type = serializers.SerializerMethodField()
    material_name = serializers.SerializerMethodField()

    @staticmethod
    def get_material_type(obj):
        if obj.material:
            return obj.material.material_type.global_name
        elif obj.previous_product_batching:
            return obj.previous_product_batching.stage.global_name
        else:
            return None

    @staticmethod
    def get_material_name(obj):
        if obj.material:
            return obj.material.material_name
        elif obj.previous_product_batching:
            return obj.previous_product_batching.stage_product_batch_no
        else:
            return None

    class Meta:
        model = ProductBatchingDetail
        exclude = ('product_batching', 'density')
        extra_kwargs = {'ratio': {'read_only': True}}


class ProductBatchingListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_info.product_name')
    dev_type_name = serializers.CharField(source='dev_type.global_name')
    created_user_name = serializers.CharField(source='created_user.username', read_only=True)
    update_user_name = serializers.SerializerMethodField(read_only=True)
    stage_name = serializers.CharField(source="stage.global_name")
    versions_name = serializers.CharField(source="product_info.versions")
    used_type_flag = serializers.SerializerMethodField()
    used_time = serializers.CharField(source="product_info.used_time")
    obsolete_time = serializers.CharField(source="product_info.obsolete_time")
    used_user_name = serializers.SerializerMethodField()
    obsolete_user_name = serializers.SerializerMethodField()

    @staticmethod
    def get_used_type_flag(obj):
        return 'Y' if obj.product_info.used_type == 3 else 'N'

    @staticmethod
    def get_used_user_name(obj):
        return obj.product_infoused_user.username if obj.product_info.used_user else None

    @staticmethod
    def get_obsolete_user_name(obj):
        return obj.product_infoobsolete_user.username if obj.product_info.obsolete_user else None

    @staticmethod
    def get_update_user_name(obj):
        return obj.product_infolast_updated_user.username if obj.product_info.last_updated_user else None

    class Meta:
        model = ProductBatching
        fields = ('id', 'stage_product_batch_no', 'product_name', 'dev_type_name',
                  'batching_weight', 'production_time_interval', 'rm_flag', 'rm_time_interval',
                  'created_user_name', 'created_date', 'update_user_name', 'last_updated_date',
                  'stage_name', 'versions_name', 'used_type_flag', 'used_time', 'obsolete_time',
                  'used_user_name', 'obsolete_user_name')


class ProductBatchingCreateSerializer(serializers.ModelSerializer):
    batching_details = ProductBatchingDetailSerializer(many=True, help_text="""配料详情：{
                                                                                     'num': '序号',
                                                                                     'material': '原材料id',
                                                                                     'ratio_weight': '配比体积',
                                                                                     'standard_volume': '标准体积',
                                                                                     'actual_volume': '计算体积',
                                                                                     'standard_weight': '实际体积',
                                                                                     'actual_weight': '标准重量',
                                                                                     'time_interval': '时间,格式：00:12:12',
                                                                                     'temperature': '温度',
                                                                                     'rpm': '转速',
                                                                                     'previous_product_batching':上段位配料id
                                                                                 }""")

    def validate(self, attrs):
        recipe = ProductRecipe.objects.filter(product_info=attrs['product_info'],
                                              stage=attrs['stage'],
                                              delete_flag=False)
        if not recipe.exists():
            raise serializers.ValidationError('当前段次配方不存在')
        batching_details = attrs.get('batching_details')
        batching_weight = manual_material_weight = volume = 0
        for detail in batching_details:
            actual_weight = detail.get('actual_weight')
            batching_weight += actual_weight if actual_weight else 0
            actual_volume = detail.get('actual_volume')
            volume += actual_volume if actual_volume else 0
            material = detail.get('material')
            if material:
                if material.material_type.global_type.type_name == '手动小料':
                    actual_weight = detail.get('actual_weight')
                    manual_material_weight += actual_weight if actual_weight else 0
                mat_recipe = recipe.filter(material=detail['material']).first()
                if not mat_recipe:
                    raise serializers.ValidationError('当前段次配方无此原材料信息：{}'.format(material.material_name))
                detail['ratio'] = mat_recipe.ratio
                detail['density'] = detail.get('material').density
            else:
                detail['density'] = 0
            if detail.get('previous_product_batching'):
                recipe_num = recipe.order_by('-num').first().num
                ratio = ProductRecipe.objects.filter(product_info=attrs['product_info'],
                                                     num__lte=recipe_num
                                                     ).aggregate(ratio=Sum('ratio'))['ratio']
                detail['ratio'] = ratio
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
            batching_detail_list.append(ProductBatchingDetail(**detail))
        ProductBatchingDetail.objects.bulk_create(batching_detail_list)
        return instance

    class Meta:
        model = ProductBatching
        fields = ('product_info', 'stage_product_batch_no', 'stage', 'dev_type',
                  'batching_time_interval', 'rm_time_interval', 'production_time_interval', 'batching_details'
                  )


class ProductBatchingRetrieveSerializer(ProductBatchingListSerializer):
    batching_details = ProductBatchingDetailSerializer(many=True, required=False)

    class Meta:
        model = ProductBatching
        fields = '__all__'


class ProductBatchingUpdateSerializer(ProductBatchingRetrieveSerializer):

    def validate(self, attrs):
        recipe = ProductRecipe.objects.filter(product_info=self.instance.product_info,
                                              stage=self.instance.stage, delete_flag=False)
        batching_details = attrs.get('batching_details')
        batching_weight = manual_material_weight = volume = 0
        if batching_details:
            for detail in batching_details:
                actual_weight = detail.get('actual_weight')
                batching_weight += actual_weight if actual_weight else 0
                actual_volume = detail.get('actual_volume')
                volume += actual_volume if actual_volume else 0
                material = detail.get('material')
                if material:
                    if material.material_type.global_type.type_name == '手动小料':
                        actual_weight = detail.get('actual_weight')
                        manual_material_weight += actual_weight if actual_weight else 0
                    mat_recipe = recipe.filter(material=detail['material']).first()
                    if not mat_recipe:
                        raise serializers.ValidationError('当前段次配方无此原材料信息：{}'.format(material.material_name))
                    detail['ratio'] = mat_recipe.ratio
                    detail['density'] = detail.get('material').density
                else:
                    detail['density'] = 0
                if detail.get('previous_product_batching'):
                    recipe_num = recipe.order_by('-num').first().num
                    ratio = ProductRecipe.objects.filter(product_info=self.instance.product_info,
                                                         num__lte=recipe_num
                                                         ).aggregate(ratio=Sum('ratio'))['ratio']
                    detail['ratio'] = ratio
            attrs['manual_material_weight'] = manual_material_weight
            attrs['batching_weight'] = batching_weight
            attrs['volume'] = volume
            attrs['batching_proportion'] = float(batching_weight / volume) if volume else 0
            attrs['last_updated_user'] = self.context['request'].user
        return attrs

    @atomic()
    def update(self, instance, validated_data):
        batching_details = validated_data.pop('batching_details', None)
        instance = super().update(instance, validated_data)
        if batching_details:
            instance.batching_details.all().delete()
            batching_detail_list = []
            for detail in batching_details:
                detail['product_batching'] = instance
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
