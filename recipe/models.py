from django.db import models
from django.db.models import Sum, F, Q

from basics.models import GlobalCode, Equip, EquipCategoryAttribute
from system.models import AbstractEntity, User


class Material(AbstractEntity):
    """原材料信息"""
    material_no = models.CharField(max_length=64, help_text='原材料编码', verbose_name='原材料编码', unique=True)
    material_name = models.CharField(max_length=64, help_text='原材料名称', verbose_name='原材料名称')
    for_short = models.CharField(max_length=64, help_text='原材料简称', verbose_name='原材料简称', blank=True, null=True)
    material_type = models.ForeignKey(GlobalCode, help_text='原材料类别', verbose_name='原材料类别',
                                      on_delete=models.CASCADE, related_name='mt_materials')
    package_unit = models.ForeignKey(GlobalCode, help_text='包装单位', verbose_name='包装单位',
                                     on_delete=models.CASCADE, related_name='pu_materials', blank=True, null=True)
    use_flag = models.BooleanField(help_text='是否启用', verbose_name='是否启用', default=True)

    def __str__(self):
        return self.material_name

    class Meta:
        db_table = 'material'
        verbose_name_plural = verbose_name = '原材料'


class MaterialAttribute(AbstractEntity):
    """原材料属性"""
    material = models.OneToOneField(Material, help_text='原材料', verbose_name='原材料',
                                    on_delete=models.CASCADE, related_name='material_attr', null=True, blank=True)
    safety_inventory = models.PositiveIntegerField(help_text='安全库存标准', verbose_name='安全库存标准', null=True, blank=True)
    period_of_validity = models.PositiveIntegerField(help_text='有效期', verbose_name='有效期', null=True, blank=True)
    validity_unit = models.CharField(verbose_name='有效期单位', help_text='有效期单位', max_length=8, default="天")
    ratio = models.DecimalField(max_digits=8, decimal_places=2, default=100.00, verbose_name='抽检比例', help_text='抽检比例')
    send_flag = models.BooleanField(default=False, verbose_name='抽检比例是否已发送标志', help_text='抽检比例是否已发送标志')
    storage_time = models.PositiveIntegerField(verbose_name='放置时间（小时）', help_text='放置时间（小时）', null=True, blank=True)

    class Meta:
        db_table = 'material_attribute'
        verbose_name_plural = verbose_name = '原材料属性'


class MaterialSupplier(AbstractEntity):
    """原材料产地"""
    material = models.ForeignKey(Material, help_text='原材料', verbose_name='原材料', on_delete=models.CASCADE,
                                 related_name='suppliers')
    supplier_no = models.CharField(max_length=64, help_text='产地编码', verbose_name='编码', unique=True)
    provenance = models.CharField(max_length=64, help_text='产地', verbose_name='产地')
    use_flag = models.BooleanField(help_text='是否启用', verbose_name='是否启用', default=True)

    class Meta:
        db_table = 'material_supplier'
        verbose_name_plural = verbose_name = '原材料产地'


class ProductInfo(AbstractEntity):
    """胶料工艺信息"""
    product_no = models.CharField(max_length=64, help_text='胶料编码', verbose_name='胶料编码', unique=True)
    product_name = models.CharField(max_length=64, help_text='胶料名称', verbose_name='胶料名称')

    def __str__(self):
        return self.product_name

    class Meta:
        db_table = 'product_info'
        verbose_name_plural = verbose_name = '胶料代码'


class ProductRecipe(AbstractEntity):
    """胶料段次配方标准"""
    product_recipe_no = models.CharField(max_length=64, help_text='胶料标准编号', verbose_name='胶料标准编号')
    sn = models.PositiveIntegerField(verbose_name='序号', help_text='序号')
    product_info = models.ForeignKey(ProductInfo, verbose_name='胶料工艺', help_text='胶料工艺',
                                     on_delete=models.CASCADE)
    material = models.ForeignKey(Material, verbose_name='原材料', help_text='原材料',
                                 on_delete=models.CASCADE, blank=True, null=True)
    stage = models.ForeignKey(GlobalCode, help_text='段次', verbose_name='段次',
                              on_delete=models.CASCADE)
    ratio = models.DecimalField(verbose_name='配比', help_text='配比',
                                decimal_places=2, max_digits=8, blank=True, null=True)

    def __str__(self):
        return self.product_recipe_no

    class Meta:
        db_table = 'product_recipe'
        verbose_name_plural = verbose_name = '胶料段次配方标准'


class ProductBatching(AbstractEntity):
    """胶料配料标准"""
    USE_TYPE_CHOICE = (
        (1, '编辑'),
        (2, '提交'),
        (3, '校对'),
        (4, '启用'),
        (5, '驳回'),
        (6, '废弃'),
        (7, '停用')
    )
    BATCHING_TYPE_CHOICE = (
        (1, '机台'),
        (2, '机型'),
        (3, '外发特殊配方')
    )
    factory = models.ForeignKey(GlobalCode, help_text='工厂', verbose_name='工厂',
                                on_delete=models.CASCADE, related_name='f_batching', blank=True, null=True)
    site = models.ForeignKey(GlobalCode, help_text='SITE', verbose_name='SITE',
                             on_delete=models.CASCADE, related_name='s_batching', blank=True, null=True)
    product_info = models.ForeignKey(ProductInfo, help_text='胶料工艺信息',
                                     on_delete=models.CASCADE, blank=True, null=True)
    precept = models.CharField(max_length=64, help_text='方案', verbose_name='方案', blank=True, null=True)
    stage_product_batch_no = models.CharField(max_length=63, help_text='胶料配方编码')
    dev_type = models.ForeignKey(EquipCategoryAttribute, help_text='机型', on_delete=models.CASCADE, blank=True,
                                 null=True)
    stage = models.ForeignKey(GlobalCode, help_text='段次', verbose_name='段次',
                              on_delete=models.CASCADE, related_name='stage_batches', blank=True, null=True)
    versions = models.CharField(max_length=64, help_text='版本', verbose_name='版本', blank=True, null=True)
    used_type = models.PositiveSmallIntegerField(help_text='使用状态', choices=USE_TYPE_CHOICE, default=1)
    batching_weight = models.DecimalField(verbose_name='配料重量', help_text='配料重量',
                                          decimal_places=2, max_digits=8, default=0)
    manual_material_weight = models.DecimalField(verbose_name='手动小料重量', help_text='手动小料重量',
                                                 decimal_places=2, max_digits=8, default=0)
    auto_material_weight = models.DecimalField(verbose_name='自动小料重量', help_text='自动小料重量',
                                               decimal_places=2, max_digits=8, default=0)
    volume = models.DecimalField(verbose_name='配料体积', help_text='配料体积', decimal_places=2, max_digits=8,
                                 blank=True, null=True)
    submit_user = models.ForeignKey(User, help_text='提交人', blank=True, null=True,
                                    on_delete=models.CASCADE, related_name='submit_batching')
    submit_time = models.DateTimeField(help_text='提交时间', blank=True, null=True)
    check_user = models.ForeignKey(User, help_text='提交人', blank=True, null=True,
                                   on_delete=models.CASCADE, related_name='check_batching')
    check_time = models.DateTimeField(help_text='提交时间', blank=True, null=True)
    reject_user = models.ForeignKey(User, help_text='驳回人', blank=True, null=True,
                                    on_delete=models.CASCADE, related_name='reject_batching')
    reject_time = models.DateTimeField(help_text='驳回时间', blank=True, null=True)
    used_user = models.ForeignKey(User, help_text='启用人', blank=True, null=True,
                                  on_delete=models.CASCADE, related_name='used_batching')
    used_time = models.DateTimeField(help_text='启用时间', verbose_name='启用时间', blank=True, null=True)
    obsolete_user = models.ForeignKey(User, help_text='弃用人', blank=True, null=True,
                                      on_delete=models.CASCADE, related_name='obsolete_batching')
    obsolete_time = models.DateTimeField(help_text='弃用时间', verbose_name='弃用时间', blank=True, null=True)
    production_time_interval = models.DecimalField(help_text='炼胶时间(分)', default=0, decimal_places=2, max_digits=8)
    equip = models.ForeignKey(Equip, help_text='设备', blank=True, null=True, on_delete=models.CASCADE)
    batching_type = models.PositiveIntegerField(verbose_name='配料类型', help_text='配料类型',
                                                choices=BATCHING_TYPE_CHOICE, default=2)
    is_synced = models.BooleanField(default=False, help_text='是否已同步至MES')
    is_changed = models.BooleanField(default=False, help_text='较上次同步是否做过修改')

    def __str__(self):
        return self.stage_product_batch_no

    def save(self, *args, **kwargs):
        batching_detail_weight = self.batching_details.filter(
            delete_flag=False).aggregate(total_weight=Sum('actual_weight'))['total_weight']
        weight_detail_weight = WeighBatchingDetail.objects.filter(
            delete_flag=False,
            weigh_cnt_type__product_batching=self).aggregate(total_weight=Sum('standard_weight'))['total_weight']
        batching_detail_weight = batching_detail_weight if batching_detail_weight else 0
        weight_detail_weight = weight_detail_weight if weight_detail_weight else 0
        self.batching_weight = batching_detail_weight + weight_detail_weight
        super(ProductBatching, self).save(*args, **kwargs)

    @property
    def batching_material_names(self):
        # 配方物料详情（料包）
        material_names = set((self.batching_details.filter(
            delete_flag=False).values_list('material__material_name', flat=True)))
        for weight_cnt_type in self.weight_cnt_types.filter(delete_flag=False):
            material_names.add(weight_cnt_type.name)
        return material_names

    @property
    def batching_details_info(self):
        # 配方物料详情（料包）
        res = {}
        batching_names = self.batching_details.filter(delete_flag=False).values('material__material_name', 'actual_weight', 'type', 'standard_error').order_by('type', 'id')
        for i in batching_names:
            res[i['material__material_name']] = i
        weighting_names = WeighBatchingDetail.objects.filter(delete_flag=False, weigh_cnt_type__delete_flag=False, weigh_cnt_type__product_batching=self).annotate(actual_weight=F('standard_weight')).values('material__material_name', 'actual_weight', 'standard_error').order_by('id')
        for i in weighting_names:
            res[i['material__material_name']] = i
        return res

    def get_product_batch(self, classes_plan):
        equip_no, dev_type, plan_classes_uid = classes_plan.equip.equip_no, classes_plan.equip.category.category_no, classes_plan.plan_classes_uid
        material_name_weight, cnt_type_details = [], []
        # 获取机台配方详情
        sfj_details = ProductBatchingDetailPlan.objects.using('SFJ').filter(~Q(material_name__icontains='待处理料'),
                                                                            ~Q(material_name__icontains='掺料'),
                                                                            plan_classes_uid=plan_classes_uid)
        # 查看是否存在对搭设置
        mixed = ProductBatchingMixed.objects.filter(product_batching__stage_product_batch_no=self.stage_product_batch_no,
                                                    product_batching__used_type=4, product_batching__delete_flag=False,
                                                    product_batching__dev_type__category_no=dev_type).last()
        if mixed:
            material_name_weight = list(sfj_details.exclude(material_name=mixed.origin_material_name)
                                        .annotate(material__material_name=F('material_name'))
                                        .values('material__material_name', 'actual_weight', 'standard_error'))
            material_name_weight = [{'material__material_name': mixed.f_feed_name, 'actual_weight': mixed.f_weight,
                                     'standard_error': 0},
                                    {'material__material_name': mixed.s_feed_name, 'actual_weight': mixed.s_weight,
                                     'standard_error': 0}] + material_name_weight
        else:
            material_name_weight = list(sfj_details.annotate(material__material_name=F('material_name'))
                                        .values('material__material_name', 'actual_weight', 'standard_error'))
        from terminal.models import OtherMaterialLog
        common_scan = OtherMaterialLog.objects.filter(plan_classes_uid=plan_classes_uid, other_type='通用料包', status=1)
        if not common_scan:  # 扫的通用料包码则过滤掉细料
            # 料包明细
            details = ProductBatchingEquip.objects.filter(Q(~Q(feeding_mode__startswith='C'),
                                                            ~Q(feeding_mode__startswith='P'),
                                                            ~Q(feeding_mode__startswith='R')),
                                                          product_batching__stage_product_batch_no=self.stage_product_batch_no,
                                                          product_batching__dev_type__category_name=dev_type,
                                                          equip_no=equip_no, is_used=True, type=4,
                                                          cnt_type_detail_equip__delete_flag=False)
            cnt_type_details += list(details.annotate(actual_weight=F('cnt_type_detail_equip__standard_weight'),
                                                      standard_error=F('cnt_type_detail_equip__standard_error'))
                                     .values('material__material_name', 'actual_weight', 'standard_error'))
        else:
            material_name_weight = [i for i in material_name_weight if i['material__material_name'] not in ['细料', '硫磺']]
        return material_name_weight, cnt_type_details

    class Meta:
        db_table = 'product_batching'
        verbose_name_plural = verbose_name = '胶料配料标准'


class ProductBatchingDetail(AbstractEntity):
    AUTO_FLAG = (
        (0, None),
        (1, '自动'),
        (2, '手动'),
    )
    TYPE_CHOICE = (
        (1, '胶料'),
        (2, '炭黑'),
        (3, '油料')
    )
    product_batching = models.ForeignKey(ProductBatching, help_text='配料标准', on_delete=models.CASCADE,
                                         related_name='batching_details')
    sn = models.PositiveIntegerField(verbose_name='序号', help_text='序号')
    material = models.ForeignKey(Material, verbose_name='原材料', help_text='原材料', on_delete=models.CASCADE)
    actual_weight = models.DecimalField(verbose_name='重量', help_text='重量', decimal_places=3, max_digits=8)
    standard_error = models.DecimalField(help_text='误差值范围', decimal_places=2, max_digits=8, default=0)
    auto_flag = models.PositiveSmallIntegerField(help_text='手动/自动', choices=AUTO_FLAG, default=0)
    type = models.PositiveSmallIntegerField(help_text='类别', choices=TYPE_CHOICE, default=1)

    class Meta:
        db_table = 'product_batching_detail'
        verbose_name_plural = verbose_name = '胶料配料标准详情'


class ProductBatchingDetailPlan(models.Model):
    """下达计划时胶料配料标准详情"""
    receive_time = models.DateTimeField(auto_now_add=True, help_text='创建时间')
    plan_classes_uid = models.CharField(max_length=64, help_text='计划号')
    stage_product_batch_no = models.CharField(max_length=32, help_text='胶料名称')
    dev_type = models.CharField(max_length=16, help_text='机型')
    equip = models.CharField(max_length=16, help_text='机台')
    sn = models.PositiveIntegerField(help_text='称量顺序')
    material_name = models.CharField(max_length=64, help_text='物料名称')
    actual_weight = models.DecimalField(help_text='重量', decimal_places=3, max_digits=8)
    standard_error = models.DecimalField(help_text='误差值范围', decimal_places=2, max_digits=8, default=0)

    class Meta:
        managed = False
        db_table = 'product_batching_detail_plan'


# class WeighBatching(AbstractEntity):
#     """小料称量配方标准"""
#     USE_TYPE_CHOICE = (
#         (1, '编辑'),
#         (2, '提交'),
#         (3, '校对'),
#         (4, '启用'),
#         (5, '驳回'),
#         (6, '废弃'),
#         (7, '停用')
#     )
#     product_batching = models.OneToOneField(ProductBatching, verbose_name='胶料配料标准', on_delete=models.CASCADE)
#     weight_batch_no = models.CharField('小料配方编码', max_length=64, blank=True, default='')
#     used_type = models.PositiveSmallIntegerField('使用状态', choices=USE_TYPE_CHOICE, default=1)
#     submit_user = models.ForeignKey(User, help_text='提交人',
#                                     related_name='submit_wb_set',
#                                     blank=True, null=True,
#                                     on_delete=models.CASCADE)
#     submit_time = models.DateTimeField(help_text='提交时间', blank=True, null=True)
#     check_user = models.ForeignKey(User, help_text='提交人',
#                                    related_name='check_wb_set',
#                                    blank=True, null=True,
#                                    on_delete=models.CASCADE)
#     check_time = models.DateTimeField(help_text='提交时间', blank=True, null=True)
#     reject_user = models.ForeignKey(User, help_text='驳回人',
#                                     related_name='reject_wb_set',
#                                     blank=True, null=True,
#                                     on_delete=models.CASCADE)
#     reject_time = models.DateTimeField(help_text='驳回时间', blank=True, null=True)
#     used_user = models.ForeignKey(User, help_text='启用人',
#                                   related_name='used_wb_set',
#                                   blank=True, null=True,
#                                   on_delete=models.CASCADE)
#     used_time = models.DateTimeField(help_text='启用时间', verbose_name='启用时间', blank=True, null=True)
#     obsolete_user = models.ForeignKey(User, help_text='弃用人',
#                                       related_name='obsolete_wb_set',
#                                       blank=True, null=True,
#                                       on_delete=models.CASCADE)
#     obsolete_time = models.DateTimeField(help_text='弃用时间', verbose_name='弃用时间', blank=True, null=True)
#
#     class Meta:
#         db_table = 'weigh_batching'
#         verbose_name_plural = verbose_name = '小料称量配方标准'


class SmallMaterialPackageSet(models.Model):
    """同类小料包集"""
    code = models.CharField(max_length=64, help_text='料包编码')
    recipe = models.ForeignKey('SmallMaterialRecipePre', on_delete=models.CASCADE)
    num = models.PositiveIntegerField(default=1)


class SmallMaterialRecipePre(models.Model):
    """小料配方基础数据，仿照万隆"""
    name = models.CharField('配方名称', unique=True, max_length=200)
    ver = models.IntegerField('配方版本', null=True, blank=True)
    remark1 = models.CharField(max_length=50, blank=True, null=True)
    weight = models.DecimalField(max_digits=6, help_text='原材料总重量，计算得出', decimal_places=3, blank=True, null=True)
    error = models.DecimalField(max_digits=5, help_text='总误差，界面写入', decimal_places=3, blank=True, null=True)
    time = models.CharField(max_length=19, help_text='修改时间', blank=True, null=True)
    use_not = models.IntegerField(blank=True, help_text='是否使用，0是1否', null=True)

    class Meta:
        unique_together = ('name', 'ver')


class SMRecipeMaterial(models.Model):
    """配方物料数据"""
    recipe_pre = models.ForeignKey(SmallMaterialRecipePre, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, verbose_name='原材料', on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    error = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    time = models.CharField(max_length=19, blank=True, null=True)


class WeighCntType(models.Model):
    """小料包"""
    WEIGH_TYPE_CHOICE = (
        (1, '硫磺包'),
        (2, '细料包'),
    )
    PACKAGE_TYPE_CHOICE = (
        (1, '自动'),
        (2, '手动'),
    )
    name = models.CharField(max_length=64, help_text='料包名称', default='')
    product_batching = models.ForeignKey(ProductBatching, verbose_name='小料称量配方标准', on_delete=models.CASCADE,
                                         related_name='weight_cnt_types', null=True)
    weigh_type = models.PositiveIntegerField('料包类型', choices=WEIGH_TYPE_CHOICE, default=1)
    package_cnt = models.PositiveIntegerField('分包数量', default=1)
    package_type = models.PositiveIntegerField('打包类型', choices=PACKAGE_TYPE_CHOICE, default=1)
    delete_flag = models.BooleanField(help_text='是否删除', verbose_name='是否删除', default=False)
    total_standard_error = models.DecimalField(help_text='总误差', decimal_places=2, max_digits=8, default=0)

    @property
    def weighting_material_nos(self):
        return list(self.weight_details.filter(delete_flag=0).values_list('material__material_no', flat=True))

    @property
    def total_weight(self):
        total_weight = self.weight_details.filter(
            delete_flag=False).aggregate(total_weight=Sum('standard_weight'))['total_weight']
        return total_weight if total_weight else 0

    def cnt_total_weight(self, equip_no):
        """获取料包重量(除去走罐体称量部分)"""
        total_weight = ProductBatchingEquip.objects.filter(Q(~Q(feeding_mode__startswith='C'),
                                                             ~Q(feeding_mode__startswith='P'),
                                                             ~Q(feeding_mode__startswith='R')),
                                                           type=4, equip_no=equip_no, is_used=True,
                                                           cnt_type_detail_equip__weigh_cnt_type=self) \
            .aggregate(total_weight=Sum('cnt_type_detail_equip__standard_weight'))['total_weight']
        return total_weight if total_weight else 0

    class Meta:
        db_table = 'weigh_cnt_type'
        verbose_name_plural = verbose_name = '小料称重分包分类'


class WeighBatchingDetail(models.Model):
    """小料包明细"""
    weigh_cnt_type = models.ForeignKey(WeighCntType, on_delete=models.CASCADE, related_name='weight_details')
    material = models.ForeignKey(Material, verbose_name='原材料', on_delete=models.CASCADE)
    standard_weight = models.DecimalField('计算重量', decimal_places=3, max_digits=8, default=0.0)
    standard_error = models.DecimalField(help_text='误差值范围', decimal_places=2, max_digits=8, default=0)
    delete_flag = models.BooleanField(help_text='是否删除', verbose_name='是否删除', default=False)

    class Meta:
        db_table = 'weigh_batching_detail'
        verbose_name_plural = verbose_name = '小料称量配方明细'


class ZCMaterial(AbstractEntity):
    """中策原材料信息"""
    wlxxid = models.CharField(max_length=64, help_text='物料信息ID', verbose_name='物料信息ID', unique=True)
    material_no = models.CharField(max_length=64, help_text='物料编号', verbose_name='物料编号')
    material_name = models.CharField(max_length=200, help_text='物料名称', verbose_name='物料名称')
    jybj = models.CharField(max_length=64, help_text='检验标记', verbose_name='检验标记', blank=True, null=True)
    bgsj = models.DateTimeField(help_text='变更时间', verbose_name='变更时间', blank=True, null=True)
    material = models.ManyToManyField(Material, help_text='原材料', related_name='zc_materials',
                                      through='ERPMESMaterialRelation')

    def __str__(self):
        return self.material_name

    class Meta:
        db_table = 'zc_material'
        verbose_name_plural = verbose_name = '中策原材料信息'


class ERPMESMaterialRelation(models.Model):
    material = models.ForeignKey(Material, help_text='MES原材料id', on_delete=models.CASCADE)
    zc_material = models.ForeignKey(ZCMaterial, help_text='ERP原材料id', on_delete=models.CASCADE)
    use_flag = models.BooleanField(help_text='是否启用', verbose_name='是否启用', default=True)

    class Meta:
        db_table = 'erp_mes_material_relation'
        verbose_name_plural = verbose_name = 'ERP与MES信息绑定关系'


class ProductBatchingEquip(models.Model):
    product_batching = models.ForeignKey(ProductBatching, on_delete=models.CASCADE, help_text='配方id', related_name='product_batching_equip')
    equip_no = models.CharField(max_length=8, help_text='机台名称')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, help_text='物料id')
    handle_material_name = models.CharField(max_length=255, help_text='去除-C, -X后缀的物料名称')
    batching_detail_equip = models.ForeignKey(ProductBatchingDetail, on_delete=models.CASCADE, help_text='胶块信息表id', null=True, blank=True)
    cnt_type_detail_equip = models.ForeignKey(WeighBatchingDetail, on_delete=models.CASCADE, help_text='小料详情id', null=True, blank=True)
    type = models.IntegerField(help_text='类别: 1: 胶料, 2: 炭黑, 3: 油料, 4: 小料')
    feeding_mode = models.CharField(max_length=4, help_text='投料方式: P密炼口投料, C炭黑罐自动, O油料罐自动', null=True, blank=True)
    is_used = models.BooleanField(default=True)
    send_recipe_flag = models.BooleanField(default=False, help_text='发送配方结果标志: 0 未发送或者发送失败; 1 发送成功')
    is_manual = models.BooleanField(default=False, help_text='是否人工单配')
    send_xl_equip = models.CharField(max_length=64, help_text='已经下传的纤体', default='')

    class Meta:
        db_table = 'product_batching_equip'
        verbose_name_plural = verbose_name = '机台配方详情'


class ProductBatchingMixed(models.Model):
    product_batching = models.ForeignKey(ProductBatching, on_delete=models.CASCADE, help_text='配方id',
                                         related_name='product_batching_mixed')
    origin_material_name = models.CharField(max_length=64, help_text='被对搭的原始物料', null=True, blank=True)
    f_feed = models.CharField(max_length=8, help_text='对搭原料段次1')
    s_feed = models.CharField(max_length=8, help_text='对搭原料段次2')
    f_feed_name = models.CharField(max_length=64, help_text='对搭原料名1')
    s_feed_name = models.CharField(max_length=64, help_text='对搭原料名2')
    f_ratio = models.IntegerField(help_text='对搭原料名1比例')
    s_ratio = models.IntegerField(help_text='对搭原料名2比例')
    f_weight = models.DecimalField(decimal_places=3, max_digits=6, help_text='对搭原料名1重量')
    s_weight = models.DecimalField(decimal_places=3, max_digits=6, help_text='对搭原料名2重量')

    class Meta:
        db_table = 'product_batching_mixed'
        verbose_name_plural = verbose_name = '对搭设置表'


class MultiReplaceMaterial(AbstractEntity):
    """批量替换原材料履历表"""
    product_batching = models.ForeignKey(ProductBatching, help_text='配方记录', on_delete=models.CASCADE)
    sfj_product_batching = models.IntegerField(help_text='上辅机配方id', null=True, blank=True)
    equip_no = models.CharField(max_length=64, help_text='机台', null=True, blank=True)
    origin_material = models.CharField(max_length=64, help_text='被替换原材料名称')
    replace_material = models.CharField(max_length=64, help_text='替换原材料名称')
    failed_reason = models.CharField(max_length=128, help_text='替换失败原因', null=True, blank=True)
    status = models.CharField(max_length=4, help_text='替换结果: 成功或者失败', default='失败')
    times = models.IntegerField(help_text='执行替换的次数')

    class Meta:
        db_table = 'multi_replace_material'
        verbose_name_plural = verbose_name = '批量替换原材料履历表'


class RecipeChangeHistory(models.Model):
    recipe_no = models.CharField(max_length=64, help_text='配方名称')
    dev_type = models.CharField(max_length=64, help_text='机型')
    used_type = models.PositiveSmallIntegerField(help_text='使用状态')
    created_time = models.DateTimeField(help_text='创建时间')
    created_username = models.CharField(max_length=64, help_text='创建人')
    updated_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    updated_username = models.CharField(max_length=64, help_text='修改人')

    class Meta:
        db_table = 'recipe_change_history'
        verbose_name_plural = verbose_name = '配方变更履历'


class RecipeChangeDetail(models.Model):
    change_history = models.ForeignKey(RecipeChangeHistory, help_text='修改履历', on_delete=models.CASCADE,
                                       related_name='change_details')
    desc = models.CharField(max_length=256, help_text='描述信息', blank=True, null=True)
    changed_time = models.DateTimeField(verbose_name='修改时间', auto_now_add=True)
    changed_username = models.CharField(max_length=64, help_text='修改人', null=True, blank=True)
    submit_username = models.CharField(max_length=64, help_text='提交人', null=True, blank=True)
    submit_time = models.DateTimeField(help_text='提交时间', null=True, blank=True)
    confirm_username = models.CharField(max_length=64, help_text='确认人', null=True, blank=True)
    confirm_time = models.DateTimeField(help_text='确认时间', null=True, blank=True)
    sfj_down_username = models.CharField(max_length=64, help_text='群控下传人', null=True, blank=True)
    sfj_down_time = models.DateTimeField(help_text='群控下传时间', null=True, blank=True)
    weight_down_username = models.CharField(max_length=64, help_text='称量下传人', null=True, blank=True)
    weight_down_time = models.DateTimeField(help_text='称量下传时间', null=True, blank=True)
    details = models.TextField(help_text='变更详情', blank=True, null=True)
    # {1(配料): [{'type': 1(1：胶料 2：炭黑 3：油料 4: 料包), 'material_no': "aaa", 'flag': 'add', 'pv(修改前的值)': '12', 'cv(修改后的值)': '13'}], 2（投料方式）: "", 3（称量误差）: ""}

    class Meta:
        db_table = 'recipe_change_detail'
        verbose_name_plural = verbose_name = '配方变更履历详情'
