
import os
import sys
from datetime import datetime

import django
from django.db.models import Max

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

from plan.uuidfield import UUidTools
from production.models import PalletFeedbacks
from quality.models import MaterialTestOrder, MaterialTestResult
from basics.models import WorkSchedulePlan

import pymssql

data_bases = [
    {"server": "10.4.23.140", "user": "sa", "password": "123456", "name": "NIDAS3"},
    {"server": "10.4.23.141", "user": "sa", "password": "123456", "name": "NIDAS3"}
]


def get_min_max_id(server, user, password, database, test_date):
    sql = """select min(RID), max(RID) from ResultInfo where TestDate>'{}';""".format(test_date)
    conn = pymssql.connect(server, user, password, database)
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    return data[0][0], data[0][1]


def main():
    max_test_date = MaterialTestResult.objects.aggregate(
        max_test_date=Max('test_factory_date'))['max_test_date']
    if not max_test_date:
        max_test_date = '2020-11-10 00:00:00'
    else:
        max_test_date = datetime.strftime(max_test_date, "%Y-%m-%d %H:%M:%S")

    for data_base in data_bases:
        server = data_base['server']
        user = data_base['user']
        password = data_base['password']
        name = data_base['name']

        min_id, max_id = get_min_max_id(server, user, password, name, max_test_date)
        while max_id >= min_id+1:
            sql = """select
                   r.DValue,
                   c.CompoundName,
                   rf.TestClass,
                   rf.TestGroup,
                   r.DataName,
                   mtm.MethodName,
                   rf.Result,
                   rf.Shift,
                   rf.MixDate,
                   rf.MixerNo,
                   rf.TestDate,
                   rf.TestNo,
                   mt.MachineTypename,
                   rf.CompoundCode
                from Result r
            inner join ResultInfo rf on r.RID=rf.RID
            inner join Compound c on c.id=rf.CompoundID
            inner join MainTestMethod mtm on mtm.id=rf.MainMethodID
            inner join TestType tt on tt.ID=mtm.TestTypeID
            inner join MachineType1 mt on mt.ID=tt.MachineTypeID
            where 
                rf.RID>={} 
                and rf.RID<={} 
                and rf.TestGroup!='' 
                and rf.MixerNo in ('Z01', 'Z02','Z03','Z04','Z05',
                                   'Z06','Z07','Z08','Z09','Z10',
                                   'Z11', 'Z12','Z13','Z14','Z15')
                and rf.TestClass!='';""".format(str(min_id), str(min_id+1000))
            conn = pymssql.connect(server, user, password, name)
            cur = conn.cursor()
            cur.execute(sql)
            data = cur.fetchall()
            for item in data:
                value = item[0]
                product_no = item[1].strip(' ')  # 胶料代码
                group = item[2].strip(' ') + '班'  # 班组
                data_point_name = item[4].strip(' ')  # 数据点
                method_name = item[5].strip(' ')  # 试验方法名称
                result = item[6].strip(' ')  # 结果
                trains = int(item[7])  # 车次
                d = []
                for a in item[8].strip(' ').split('/'):
                    d.append(a.zfill(2))
                product_date = '-'.join(d)  # 生产日期
                equip_no = item[9].strip(' ')  # 设备编号
                test_date = item[10]  # 试验日期
                test_times = item[11]  # 试验次数
                machine_name = item[12].strip(' ')  # 机器名称
                try:
                    interval = int(item[13].strip(' '))
                except Exception:
                    interval = 1
                test_class = item[3].strip(' ')

                # 根据机器名称找到指标点
                if machine_name == '流变仪':
                    indicator_name = '流变'
                elif machine_name == '门尼粘度':
                    indicator_name = '门尼'
                else:
                    continue

                # 根据班组找班次（找到的不一定对）
                schedule_plan = WorkSchedulePlan.objects.filter(
                    plan_schedule__work_schedule__schedule_name='三班两运转',
                    plan_schedule__day_time=product_date,
                    group__global_name=group
                ).first()
                if schedule_plan:
                    classes = schedule_plan.classes.global_name
                else:
                    continue

                # print('生产日期：{}, 胶料：{}， 班组：{}， 班次：{}， 指标点：{}，'
                #       '试验方法：{}，数据点：{}, 车次：{}， 值：{}， 结果：{}'.format(
                #         product_date, product_no, group, classes, indicator_name,
                #         method_name, data_point_name, trains, value, result))

                # 根据机台编号、胶料代码、班次、日期找托盘lot_no
                pallet = PalletFeedbacks.objects.filter(
                    equip_no=equip_no,
                    product_no__icontains=product_no,
                    classes=classes,
                    end_time__date=product_date,
                    begin_trains__lte=trains,
                    end_trains__gte=trains
                ).first()

                # 关键看能不能找到托盘反馈数据
                if pallet:
                    if indicator_name:
                        for i in range(trains, trains+interval):
                            lot_no = pallet.lot_no
                            test_order = MaterialTestOrder.objects.filter(lot_no=lot_no,
                                                                          actual_trains=i).first()
                            if not test_order:
                                test_order = MaterialTestOrder.objects.create(
                                    lot_no=lot_no,
                                    material_test_order_uid=UUidTools.uuid1_hex('KJ'),
                                    actual_trains=i,
                                    product_no=product_no,
                                    plan_classes_uid=pallet.plan_classes_uid,
                                    production_class=classes,
                                    production_group=group,
                                    production_equip_no=equip_no,
                                    production_factory_date=product_date,
                                )
                                MaterialTestResult.objects.get_or_create(
                                    material_test_order=test_order,
                                    test_factory_date=test_date,
                                    value=value,
                                    test_times=test_times,
                                    data_point_name=data_point_name,
                                    test_method_name=method_name,
                                    test_indicator_name=indicator_name,
                                    result=result,
                                    machine_name=machine_name,
                                    test_class=test_class,
                                    level=1 if result == '合格' else 3
                                )
            conn.close()
            min_id += 1000


if __name__ == '__main__':
    main()
