;(function () {

    var Main = {

        mixins: [BaseMixin],
        data: function () {

            return {

                startTime: Date.now(),
                workSchedules: [],
                workScheduleOptions: [],
                workScheduleIndex: null,
                classData: [],
                groups: [],
                groupById: {},
                groupIds: [],

                changeShiftsPeriods: [],
                changeShiftsPeriod: null,
                scheduleData: [],
                classes: [],
                fullscreenLoading: false,
                classesByIndex: {}
            }
        },
        methods: {

            dayOfWeek(day) {

                switch (day) {

                    case 0:
                        return "天";
                    case 1:
                        return "一";
                    case 2:
                        return "二";
                    case 3:
                        return "三";
                    case 4:
                        return "四";
                    case 5:
                        return "五";
                    case 6:
                        return "六";
                }
            },
            generateScheduling() {

                var date = dayjs(this.startTime);
                var workSchedule = this.workSchedules[this.workScheduleIndex];
                var shiftsPeriod = Number(this.changeShiftsPeriod);

                this.scheduleData = [];
                for (var i = 0; i < workSchedule.period * shiftsPeriod; i++) {

                    var day = date.get('day');
                    var date_str = date.format('YYYY-MM-DD');
                    var row = {

                        production_time: date_str,
                        day_of_the_week: "星期" + this.dayOfWeek(day),
                        group_infos: []
                    };
                    var classes = this.classesByIndex[i % workSchedule.period];
                    console.log(classes);
                    for (var j = 0; j < classes.length; j++) {
                        var class_ =  JSON.parse(JSON.stringify(classes[j]));
                        Vue.set(class_, 'is_rest', false);
                        if (class_.group) {
                            class_.group_name = this.groupById[class_.group];
                            console.log(
                            this.groupById[class_.group])
                        }
                        row.group_infos.push(class_)
                    }
                    this.scheduleData.push(row);
                    date = date.add(1, 'day');
                }
            },
            shiftsTimeChange() {

                this.classesByIndex = {};
                var date = dayjs(this.startTime);
                var workSchedule = this.workSchedules[this.workScheduleIndex];
                var classDate_ = [];
                for (var i = 0; i < workSchedule.period; i++) {

                    var date_str = date.format('YYYY-MM-DD');
                    this.classesByIndex[i] = [];
                    for (var k = 0; k < workSchedule.classesdetail_set.length; k++) {

                        var classesdetail = workSchedule.classesdetail_set[k];
                        classesdetail.date = date_str;
                        var classesdetail_ = JSON.parse(JSON.stringify(classesdetail));
                        classDate_.push(classesdetail_);
                        this.classesByIndex[i].push(classesdetail_)
                    }
                    date = date.add(1, 'day');
                }
                this.classData = classDate_;
            }
        },
        created: function () {

            var app = this;
            axios.get(GlobalCodesUrl, {

                params: {

                    class_name: "倒班周期"
                }
            }).then(function (response) {

                app.changeShiftsPeriods = response.data.results;
            }).catch(function (error) {

            });
            axios.get(GlobalCodesUrl, {

                params: {

                    class_name: "班组"
                }
            }).then(function (response) {

                app.groups = response.data.results;
                for (var i = 0; i < app.groups.length; ++i) {

                    app.groupById[app.groups[i].id] = app.groups[i].global_name;
                }
            }).catch(function (error) {

            });
            axios.get(GlobalCodesUrl, {

                params: {

                    class_name: "班次"
                }
            }).then(function (response) {

                app.classes = response.data.results;
            }).catch(function (error) {

            });
            axios.get(WorkSchedulesUrl)
                .then(function (response) {

                    app.workSchedules = response.data.results;
                    for (var i = 0; i < app.workSchedules.length; ++i) {

                        app.workSchedules[i]["group"] = "";
                        var label = app.workSchedules[i].classesdetail_set.length + "班次";
                        for (var j = 0; j < app.workSchedules[i].classesdetail_set.length; ++j) {

                            label += "[" + (j + 1) + "]"
                                + "-"
                                + app.workSchedules[i].classesdetail_set[j].start_time
                                + "/"
                                + app.workSchedules[i].classesdetail_set[j].end_time;
                        }
                        app.workScheduleOptions.push({

                            value: i,
                            label
                        });
                    }
                }).catch(function (error) {

            })
        }
    };
    var Ctor = Vue.extend(Main);
    new Ctor().$mount("#app")
})();
