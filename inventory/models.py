from django.db import models

# Create your models here.
from basics.models import GlobalCode, Equip
from recipe.models import Material, ProductBatching
from system.models import AbstractEntity, User


class WarehouseInfo(AbstractEntity):
    """仓库信息"""
    no = models.CharField(max_length=64, verbose_name='仓库编码', help_text='仓库编码')
    name = models.CharField(max_length=64, unique=True, verbose_name='仓库名称', help_text='仓库名称')
    ip = models.CharField(max_length=64, verbose_name='仓库ip', help_text='仓库ip', blank=True, default='')
    address = models.CharField(max_length=64, verbose_name='仓库地址', help_text='仓库地址', blank=True, default='')
    use_flag = models.BooleanField(help_text='是否启用', verbose_name='是否启用', default=True)

    class Meta:
        db_table = 'ware_house_info'
        verbose_name_plural = verbose_name = '仓库信息'


class WarehouseMaterialType(AbstractEntity):
    """仓库物料类型"""
    warehouse_info = models.ForeignKey(WarehouseInfo, on_delete=models.CASCADE, related_name="warehouse_material_types")
    material_type = models.ForeignKey(GlobalCode, on_delete=models.CASCADE)
    use_flag = models.BooleanField(help_text='是否启用', verbose_name='是否启用', default=True)

    class Meta:
        db_table = 'ware_house_material_type'
        verbose_name_plural = verbose_name = '仓库物料类型'


class InventoryLog(AbstractEntity):
    """出入库履历"""
    warehouse_no = models.CharField(max_length=64, verbose_name='仓库编号', help_text='仓库编号')
    warehouse_name = models.CharField(max_length=64, verbose_name='仓库名称', help_text='仓库名称')
    order_no = models.CharField(max_length=64, verbose_name='订单号', help_text='订单号')
    pallet_no = models.CharField(max_length=64, verbose_name='托盘号', help_text='托盘号')
    location = models.CharField(max_length=64, verbose_name='货位地址', help_text='货位地址')
    qty = models.PositiveIntegerField(verbose_name='数量', help_text='数量', blank=True, null=True)
    weight = models.DecimalField(verbose_name='重量', help_text='重量', blank=True, null=True, decimal_places=2,
                                 max_digits=8)
    material_no = models.CharField(max_length=64, verbose_name='物料编码', help_text='物料编码')
    quality_status = models.CharField(max_length=8, verbose_name='品质状态', help_text='品质状态')
    lot_no = models.CharField(max_length=64, verbose_name='lot_no', help_text='lot_no')
    order_type = models.CharField(max_length=64, verbose_name='订单类型', help_text='订单类型')
    inout_reason = models.CharField(max_length=64, verbose_name='出入库原因', help_text='出入库原因')
    inout_num_type = models.CharField(max_length=64, verbose_name='出入库数类型', help_text='出入库数类型')
    inventory_type = models.CharField(max_length=64, verbose_name='BZ出入库类型', help_text='BZ出入库数类型')  # 生产出库/快检异常出库
    unit = models.CharField(max_length=64, verbose_name='单位', help_text='单位')
    initiator = models.CharField(max_length=64, blank=True, null=True, verbose_name='发起人',
                                 help_text='发起人')
    start_time = models.DateTimeField('发起时间', blank=True, null=True, help_text='发起时间')
    fin_time = models.DateTimeField(verbose_name='完成时间', help_text='完成时间', auto_now_add=True)

    class Meta:
        db_table = 'inventory_log'
        verbose_name_plural = verbose_name = '出入库履历'


class MaterialInventory(AbstractEntity):
    """库存信息|线边库"""
    material = models.ForeignKey(Material, verbose_name='物料id', help_text='物料id', on_delete=models.CASCADE,
                                 related_name="material_inventory_m")
    container_no = models.CharField(max_length=64, verbose_name='托盘号/容器号', help_text='托盘号/容器号')
    site = models.ForeignKey(GlobalCode, verbose_name='产地', help_text='产地', on_delete=models.CASCADE,
                             related_name="material_inventory_s")
    qty = models.IntegerField(verbose_name='库存数', help_text='库存数')
    unit = models.CharField(max_length=64, verbose_name='单位', help_text='单位')
    unit_weight = models.DecimalField(verbose_name='单位重量', help_text='单位重量', decimal_places=2, max_digits=8, blank=True,
                                      null=True)
    # weight = models.DecimalField(verbose_name='重量', help_text='重量',decimal_places=2, max_digits=8, blank=True, null=True)
    total_weight = models.DecimalField(verbose_name='总重量', help_text='总重量', decimal_places=2, max_digits=8, blank=True,
                                       null=True)
    quality_status = models.CharField(max_length=8, verbose_name='品质状态', help_text='品质状态')
    lot_no = models.CharField(max_length=64, verbose_name='lot_no', help_text='lot_no')
    location = models.CharField(max_length=64, verbose_name='库位', help_text='库位')
    warehouse_info = models.ForeignKey(WarehouseInfo, verbose_name='仓库id', help_text='仓库id', on_delete=models.CASCADE,
                                       related_name="material_inventory_w")

    class Meta:
        db_table = 'material_inventory'
        verbose_name_plural = verbose_name = '库存信息'


class BzFinalMixingRubberInventory(models.Model):
    """bz混炼胶库 | 目前临时存的是终炼胶"""
    id = models.PositiveIntegerField(db_column='库存索引', primary_key=True)
    store_id = models.CharField(max_length=20, db_column='库房编号')
    store_name = models.CharField(max_length=20, db_column='库房名称')
    bill_id = models.CharField(max_length=50, db_column='订单号')
    container_no = models.CharField(max_length=50, db_column='托盘号')
    location = models.CharField(max_length=20, db_column='货位地址')
    qty = models.DecimalField(max_digits=15, decimal_places=3, db_column='数量')
    total_weight = models.DecimalField(max_digits=15, decimal_places=3, db_column='重量')
    quality_status = models.CharField(max_length=20, db_column='品质状态')
    memo = models.CharField(max_length=250, db_column='车号')
    lot_no = models.CharField(max_length=200, db_column='追溯号')
    material_no = models.CharField(max_length=50, db_column='物料编码')
    in_storage_time = models.DateTimeField(db_column='入库时间')
    location_status = models.CharField(max_length=20, db_column='货位状态')

    def material_type(self):
        try:
            mt = self.material_no.split("-")[1]
        except:
            mt = self.material_no
        return mt

    def unit(self):
        return "kg"

    def unit_weight(self):
        return str(round(self.total_weight / self.qty, 3))

    class Meta:
        db_table = 'v_ASRS_STORE_MESVIEW'
        managed = False


class BzFinalMixingRubberInventoryLB(models.Model):
    """bz帘布/终炼"""
    id = models.PositiveIntegerField(db_column='库存索引', primary_key=True)
    store_id = models.CharField(max_length=20, db_column='库房编号')
    store_name = models.CharField(max_length=20, db_column='库房名称')
    bill_id = models.CharField(max_length=50, db_column='订单号')
    container_no = models.CharField(max_length=50, db_column='托盘号')
    location = models.CharField(max_length=20, db_column='货位地址')
    qty = models.DecimalField(max_digits=15, decimal_places=3, db_column='数量')
    total_weight = models.DecimalField(max_digits=15, decimal_places=3, db_column='重量')
    quality_status = models.CharField(max_length=20, db_column='品质状态')
    memo = models.CharField(max_length=250, db_column='车号')
    lot_no = models.CharField(max_length=200, db_column='追溯号')
    material_no = models.CharField(max_length=50, db_column='物料编码')
    in_storage_time = models.DateTimeField(db_column='入库时间')
    location_status = models.CharField(max_length=20, db_column='货位状态')

    def material_type(self):
        try:
            mt = self.material_no.split("-")[1]
        except:
            mt = self.material_no
        return mt

    def unit(self):
        return "kg"

    def unit_weight(self):
        return str(round(self.total_weight / self.qty, 3))

    # def equip_no(self):
    #     try:
    #         equip_no = self.lot_no[4:7]
    #     except:
    #         equip_no = ""
    #     if len(equip_no) != 3:
    #         equip_no = self.bill_id[-3:]
    #     if equip_no.startswith("Z"):
    #         return equip_no
    #     return ""

    # def class_name(self):
    #     class_map = {
    #         1: "早班",
    #         2: "中班",
    #         3: "夜班"
    #     }
    #     try:
    #         class_id = int(self.lot_no[-5])
    #     except:
    #         return ""
    #     else:
    #         return class_map[class_id]

    class Meta:
        db_table = 'v_ASRS_STORE_MESVIEW'
        managed = False


class WmsInventoryStock(models.Model):
    """wms原材料库"""
    sn = models.CharField(max_length=255, db_column='Sn', primary_key=True)
    qty = models.DecimalField(max_digits=18, decimal_places=2, db_column='Quantity')
    material_name = models.CharField(max_length=64, db_column='MaterialName')
    total_weight = models.DecimalField(max_digits=18, decimal_places=2, db_column='WeightOfActual')
    material_no = models.CharField(max_length=64, db_column='MaterialCode')
    location = models.CharField(max_length=255, db_column='ProductionAddress')
    unit = models.CharField(max_length=64, db_column='WeightUnit')
    quality_status = models.IntegerField(db_column='StockDetailState')
    material_type = models.CharField(max_length=64)
    lot_no = models.CharField(max_length=64, db_column='BatchNo')

    class Meta:
        db_table = 't_inventory_stock'
        managed = False

    @classmethod
    def get_sql(cls, material_type=None, material_no=None):
        material_type_filter = """AND material.MaterialGroupName LIKE '%%{0}%%'""" \
            .format(material_type) if material_type else ''
        material_no_filter = """AND stock.MaterialCode LIKE '%%{material_no}%%'""" \
            .format(material_no=material_no) if material_no else ''
        sql = """
                    SELECT *, material.MaterialGroupName AS material_type 
                    FROM zhada_wms_zhongc.dbo.t_inventory_stock stock,
                      zhada_wms_zhongc.dbo.t_inventory_material material
                        WHERE stock.MaterialCode = material.MaterialCode
                        {0} {1}
                    """.format(material_type_filter, material_no_filter)
        return sql

    def container_no(self):
        return "Unknown"

    def unit_weight(self):
        return "Unknown"


class WmsInventoryMaterial(models.Model):
    id = models.PositiveIntegerField(db_column='id', primary_key=True)
    material_no = models.CharField(max_length=64, db_column='MaterialCode')
    material_type = models.CharField(max_length=64, db_column='MaterialGroupName')

    class Meta:
        db_table = 't_inventory_material'
        managed = False


class DeliveryPlan(AbstractEntity):
    """出库计划 | 混炼胶"""
    ORDER_TYPE_CHOICE = (
        (1, '完成'),
        (2, '执行中'),
        (3, '失败'),
        (4, '新建'),
        (5, '关闭')
    )
    warehouse_info = models.ForeignKey(WarehouseInfo, on_delete=models.CASCADE, related_name="delivery_plans")
    order_no = models.CharField(max_length=64, verbose_name='订单号', help_text='订单号')
    pallet_no = models.CharField(max_length=64, verbose_name='托盘号', help_text='托盘号', blank=True, null=True)
    need_qty = models.PositiveIntegerField(verbose_name='需求数量', help_text='需求数量', blank=True, null=True)
    need_weight = models.DecimalField(max_digits=8, decimal_places=3, verbose_name='需求重量', help_text='需求重量', blank=True,
                                      null=True)
    material_no = models.CharField(max_length=64, verbose_name='物料编码', help_text='物料编码', blank=True, null=True)
    inventory_type = models.CharField(max_length=32, verbose_name='出入库类型', help_text='出入库类型', blank=True, null=True)
    order_type = models.CharField(max_length=32, verbose_name='订单类型', help_text='订单类型', blank=True, null=True)
    inventory_reason = models.CharField(max_length=128, verbose_name='出入库原因', help_text='出入库原因', blank=True, null=True)
    unit = models.CharField(max_length=64, verbose_name='单位', help_text='单位', blank=True, null=True)
    status = models.PositiveIntegerField(verbose_name='订单状态', help_text='订单状态', choices=ORDER_TYPE_CHOICE, default=4)
    location = models.CharField(max_length=64, verbose_name='货位地址', help_text='货位地址', blank=True, null=True)
    finish_time = models.DateTimeField(verbose_name='完成时间', blank=True, null=True)
    equip = models.ManyToManyField(Equip, verbose_name="设备", help_text="设备", blank=True, null=True,
                                   related_name='dispatch_mix_deliverys')
    dispatch = models.ManyToManyField('DispatchPlan', verbose_name="发货单", help_text="发货单", blank=True, null=True,
                                      related_name='equip_mix_deliverys')

    class Meta:
        db_table = 'delivery_plan'
        verbose_name_plural = verbose_name = '出库计划'


class DeliveryPlanLB(AbstractEntity):
    """出库计划 | 帘布"""
    ORDER_TYPE_CHOICE = (
        (1, '完成'),
        (2, '执行中'),
        (3, '失败'),
        (4, '新建'),
        (5, '关闭')
    )
    warehouse_info = models.ForeignKey(WarehouseInfo, on_delete=models.CASCADE, related_name="delivery_plans_lb")
    order_no = models.CharField(max_length=64, verbose_name='订单号', help_text='订单号')
    pallet_no = models.CharField(max_length=64, verbose_name='托盘号', help_text='托盘号', blank=True, null=True)
    need_qty = models.PositiveIntegerField(verbose_name='需求数量', help_text='需求数量', blank=True, null=True)
    need_weight = models.DecimalField(max_digits=8, decimal_places=3, verbose_name='需求重量', help_text='需求重量', blank=True,
                                      null=True)
    material_no = models.CharField(max_length=64, verbose_name='物料编码', help_text='物料编码', blank=True, null=True)
    inventory_type = models.CharField(max_length=32, verbose_name='出入库类型', help_text='出入库类型', blank=True, null=True)
    order_type = models.CharField(max_length=32, verbose_name='订单类型', help_text='订单类型', blank=True, null=True)
    inventory_reason = models.CharField(max_length=128, verbose_name='出入库原因', help_text='出入库原因', blank=True, null=True)
    unit = models.CharField(max_length=64, verbose_name='单位', help_text='单位', blank=True, null=True)
    status = models.PositiveIntegerField(verbose_name='订单状态', help_text='订单状态', choices=ORDER_TYPE_CHOICE, default=4)
    location = models.CharField(max_length=64, verbose_name='货位地址', help_text='货位地址', blank=True, null=True)
    finish_time = models.DateTimeField(verbose_name='完成时间', blank=True, null=True)
    equip = models.ManyToManyField(Equip, verbose_name="设备", help_text="设备", blank=True, null=True,
                                   related_name='dispatch_lb_deliverys')
    dispatch = models.ManyToManyField("DispatchPlan", verbose_name="发货单", help_text="发货单", blank=True, null=True,
                                      related_name='equip_lb_deliverys')

    class Meta:
        db_table = 'delivery_plan_lb'
        verbose_name_plural = verbose_name = '帘布库出库计划'


class DeliveryPlanFinal(AbstractEntity):
    """出库计划 | 终炼"""
    ORDER_TYPE_CHOICE = (
        (1, '完成'),
        (2, '执行中'),
        (3, '失败'),
        (4, '新建'),
        (5, '关闭')
    )
    warehouse_info = models.ForeignKey(WarehouseInfo, on_delete=models.CASCADE, related_name="delivery_plans_final")
    order_no = models.CharField(max_length=64, verbose_name='订单号', help_text='订单号')
    pallet_no = models.CharField(max_length=64, verbose_name='托盘号', help_text='托盘号', blank=True, null=True)
    need_qty = models.PositiveIntegerField(verbose_name='需求数量', help_text='需求数量', blank=True, null=True)
    need_weight = models.DecimalField(max_digits=8, decimal_places=3, verbose_name='需求重量', help_text='需求重量', blank=True,
                                      null=True)
    material_no = models.CharField(max_length=64, verbose_name='物料编码', help_text='物料编码', blank=True, null=True)
    inventory_type = models.CharField(max_length=32, verbose_name='出入库类型', help_text='出入库类型', blank=True, null=True)
    order_type = models.CharField(max_length=32, verbose_name='订单类型', help_text='订单类型', blank=True, null=True)
    inventory_reason = models.CharField(max_length=128, verbose_name='出入库原因', help_text='出入库原因', blank=True, null=True)
    unit = models.CharField(max_length=64, verbose_name='单位', help_text='单位', blank=True, null=True)
    status = models.PositiveIntegerField(verbose_name='订单状态', help_text='订单状态', choices=ORDER_TYPE_CHOICE, default=4)
    location = models.CharField(max_length=64, verbose_name='货位地址', help_text='货位地址', blank=True, null=True)
    finish_time = models.DateTimeField(verbose_name='完成时间', blank=True, null=True)
    equip = models.ManyToManyField(Equip, verbose_name="设备", help_text="设备", blank=True, null=True,
                                   related_name='dispatch_final_deliverys')
    dispatch = models.ManyToManyField('DispatchPlan', verbose_name="发货单", help_text="发货单", blank=True, null=True,
                                      related_name='equip_final_deliverys')

    class Meta:
        db_table = 'delivery_plan_final'
        verbose_name_plural = verbose_name = '终炼胶库出库计划'


class DeliveryPlanStatus(AbstractEntity):
    """出库计划状态变更记录"""
    ORDER_TYPE_CHOICE = (
        (1, '完成'),
        (2, '执行中'),
        (3, '失败'),
        (4, '新建'),
        (5, '关闭')
    )
    warehouse_info = models.ForeignKey(WarehouseInfo, on_delete=models.CASCADE, related_name="delivery_plan_status")
    order_no = models.CharField(max_length=64, verbose_name='订单号', help_text='订单号')
    order_type = models.CharField(max_length=32, verbose_name='订单类型', help_text='订单类型')
    status = models.PositiveIntegerField(verbose_name='订单号', help_text='订单号', choices=ORDER_TYPE_CHOICE, default=4)

    class Meta:
        db_table = 'delivery_plan_status'
        verbose_name_plural = verbose_name = '出库计划状态变更表'


class Station(AbstractEntity):
    """站点信息"""
    no = models.CharField('站点编码', max_length=64, help_text='站点编码')
    name = models.CharField('站点名称', max_length=64, help_text='站点名称')
    desc = models.CharField('备注', max_length=64, help_text='备注', blank=True, default='')
    warehouse_info = models.ForeignKey(WarehouseInfo, verbose_name='所属仓库', help_text='所属仓库', on_delete=models.SET_NULL,
                                       null=True, blank=True)
    type = models.ForeignKey(GlobalCode, verbose_name='站点类型', help_text='站点类型', on_delete=models.SET_NULL, null=True,
                             blank=True)
    use_flag = models.BooleanField(help_text='是否启用', verbose_name='是否启用', default=True)

    class Meta:
        db_table = 'station'
        verbose_name_plural = verbose_name = '站点信息'


class DispatchLocation(AbstractEntity):
    """发货地"""

    no = models.CharField('发货地编码', max_length=64, help_text='发货地编码')
    name = models.CharField('发货地名称', max_length=64, help_text='发货地名称', unique=True)
    desc = models.CharField('备注', max_length=64, help_text='备注', blank=True, default='')
    use_flag = models.BooleanField(help_text='是否启用', verbose_name='是否启用', default=True)

    class Meta:
        db_table = 'dispatch_location'
        verbose_name_plural = verbose_name = '发货地'


class DispatchLog(AbstractEntity):
    """发货履历"""
    STATUS_CHOICES = (
        (1, '完成'),
        (2, '撤销')
    )
    order_no = models.CharField(max_length=64, verbose_name='订单号', help_text='订单号')
    pallet_no = models.CharField(max_length=64, verbose_name='托盘号', help_text='托盘号')
    need_qty = models.PositiveIntegerField(verbose_name='需求数量', help_text='需求数量')
    need_weight = models.DecimalField(verbose_name='需求重量', help_text='需求重量', blank=True, null=True,
                                      decimal_places=2, max_digits=8)
    dispatch_type = models.CharField(max_length=64, verbose_name='发货类型', help_text='发货类型')
    material_no = models.CharField(max_length=64, verbose_name='物料编码', help_text='物料编码')
    quality_status = models.CharField(max_length=8, verbose_name='品质状态', help_text='品质状态')
    lot_no = models.CharField(max_length=64, verbose_name='lot_no', help_text='lot_no')
    order_type = models.CharField(max_length=64, verbose_name='订单类型', help_text='订单类型', null=True)
    status = models.PositiveIntegerField(verbose_name="发货状态", help_text="发货状态", choices=STATUS_CHOICES)
    qty = models.PositiveIntegerField(verbose_name='单托数量', help_text='单托数量', default=2)
    weight = models.DecimalField(verbose_name='单托重量', help_text='单托重量', decimal_places=2, max_digits=8)
    dispatch_location = models.CharField(max_length=64, verbose_name='目的地', help_text='目的地')
    dispatch_user = models.CharField(max_length=16, verbose_name='发货人', help_text='发货人')
    order_created_time = models.DateTimeField(verbose_name="订单创建时间", help_text="订单创建时间", auto_now_add=True)
    fin_time = models.DateTimeField(verbose_name='完成时间', help_text='完成时间', null=True, blank=True)

    class Meta:
        db_table = 'dispatch_log'
        verbose_name_plural = verbose_name = '发货履历'


class DispatchPlan(AbstractEntity):
    """发货计划"""
    STATUS_CHOICES = (
        (1, '完成'),
        (2, '执行中'),
        (3, '失败'),
        (4, '新建'),
        (5, '关闭')
    )

    order_no = models.CharField(max_length=64, verbose_name='订单号', help_text='订单号')
    need_qty = models.PositiveIntegerField(verbose_name='需求数量', help_text='需求数量')
    need_weight = models.DecimalField(verbose_name='需求重量', help_text='需求重量', blank=True, null=True, decimal_places=2,
                                      max_digits=8)
    material = models.ForeignKey(Material, verbose_name='物料编码', help_text='物料编码', on_delete=models.SET_NULL,
                                 blank=True, null=True)
    dispatch_type = models.ForeignKey(GlobalCode, verbose_name='发货类型', help_text='发货类型', on_delete=models.SET_NULL,
                                      blank=True, null=True)
    order_type = models.CharField(max_length=8, verbose_name='订单类型', help_text='订单类型', null=True)
    actual_qty = models.PositiveIntegerField(verbose_name='已发数量', help_text='已发数量', default=0)
    actual_weight = models.DecimalField(verbose_name='已发重量', help_text='已发重量', decimal_places=2,
                                        max_digits=8, default=0)
    status = models.PositiveIntegerField(verbose_name="状态", help_text="状态", choices=STATUS_CHOICES, default=4)
    qty = models.PositiveIntegerField(verbose_name='单托数量', help_text='单托数量', blank=True, null=True)
    dispatch_location = models.ForeignKey(DispatchLocation, verbose_name='目的地', help_text='目的地',
                                          on_delete=models.SET_NULL, blank=True, null=True)
    dispatch_user = models.CharField(max_length=16, verbose_name='发货人', help_text='发货人', null=True, blank=True)
    start_time = models.DateTimeField(verbose_name="发起时间", help_text="发起时间", auto_now_add=True)
    fin_time = models.DateTimeField(verbose_name='完成时间', help_text='完成时间', null=True, blank=True)

    class Meta:
        db_table = 'dispatch_plan'
        verbose_name_plural = verbose_name = '发货计划'


class MixGumOutInventoryLog(models.Model):
    """混炼胶库出库履历视图"""
    order_no = models.CharField(max_length=100, db_column='BILLID', primary_key=True)
    pallet_no = models.CharField(max_length=50, db_column='PALLETID')
    location = models.CharField(max_length=50, db_column='CID')
    qty = models.DecimalField(max_digits=15, decimal_places=3, db_column='CarNum')
    weight = models.DecimalField(max_digits=15, decimal_places=3, db_column='Weight')
    quality_status = models.CharField(db_column='MStatus', max_length=6)
    lot_no = models.CharField(max_length=100, db_column='Lot_no', null=True, blank=True)
    inout_num_type = models.CharField(max_length=50, db_column='OutType')
    initiator = models.CharField(max_length=50, db_column='OutUser')
    material_no = models.CharField(max_length=100, db_column='MID')
    fin_time = models.DateTimeField(db_column='DEALTIME')

    def warehouse_no(self):
        return "混炼胶库"

    def warehouse_name(self):
        return "混炼胶库"

    def material_name(self):
        return self.material_no

    def unit(self):
        return "kg"

    def order_type(self):
        return "出库"

    def inout_reason(self):
        return self.inout_num_type

    class Meta:
        db_table = 'v_ASRS_TO_MES_RE_MESVIEW'
        managed = False


class MixGumInInventoryLog(models.Model):
    """混炼胶库入库履历视图"""
    order_no = models.CharField(max_length=50, db_column='BILLID', primary_key=True)
    pallet_no = models.CharField(max_length=50, db_column='PALLETID')
    location = models.CharField(max_length=50, db_column='CID')
    qty = models.DecimalField(max_digits=15, decimal_places=3, db_column='Num')
    weight = models.DecimalField(max_digits=15, decimal_places=3, db_column='SWeight')
    quality_status = models.CharField(db_column='MStatus', max_length=50)
    lot_no = models.CharField(max_length=200, db_column='LotNo', null=True, blank=True)
    inout_num_type = models.CharField(max_length=20, db_column='IOCLASSNAME')
    material_no = models.CharField(max_length=50, db_column='MID')
    material_name = models.CharField(max_length=50, db_column='MATNAME')
    fin_time = models.DateTimeField(db_column='LTIME')
    project_no = models.CharField(db_column='PROJECTNO', max_length=50, null=True, blank=True)
    class_id = models.BigIntegerField(db_column="IOCLASS_ID", null=True, blank=True)

    def warehouse_no(self):
        return "混炼胶库"

    def warehouse_name(self):
        return "混炼胶库"

    def unit(self):
        return "kg"

    def order_type(self):
        return "入库"

    def inout_reason(self):
        return self.inout_num_type

    class Meta:
        db_table = 'v_ASRS_LOG_IN_OPREATE_MESVIEW'
        managed = False
