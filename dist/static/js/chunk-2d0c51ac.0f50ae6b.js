(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-2d0c51ac"],{"3e59":function(e,t,a){"use strict";a.r(t);var n=function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{directives:[{name:"loading",rawName:"v-loading",value:e.loading,expression:"loading"}]},[a("el-form",{attrs:{inline:!0}},[a("el-form-item",{attrs:{label:"时间:"}},[a("el-date-picker",{attrs:{clearable:!0,type:"daterange","range-separator":"至","start-placeholder":"开始日期","end-placeholder":"结束日期","value-format":"yyyy-MM-dd"},on:{change:e.changeDate},model:{value:e.search.date,callback:function(t){e.$set(e.search,"date",t)},expression:"search.date"}})],1),a("el-form-item",[a("el-radio-group",{on:{change:e.changeRadio},model:{value:e.search.day_type,callback:function(t){e.$set(e.search,"day_type",t)},expression:"search.day_type"}},[a("el-radio",{attrs:{label:1}},[e._v("自然日")]),a("el-radio",{attrs:{label:2}},[e._v("工厂时间")])],1)],1),a("br"),a("el-form-item",{attrs:{label:"时间跨度:"}},[a("time-span-select",{attrs:{"default-val":e.search.dimension,"day-type":e.search.day_type},on:{changeSelect:e.timeSpanChanged}})],1),a("el-form-item",{attrs:{label:"设备编码:"}},[a("equip-select",{attrs:{equip_no_props:e.search.equip_no},on:{"update:equip_no_props":function(t){return e.$set(e.search,"equip_no",t)},changeSearch:e.equipChanged}})],1)],1),a("el-table",{attrs:{data:e.tableData,border:"","show-summary":"","summary-method":e.getSummaries}},[a("el-table-column",{attrs:{type:"index",label:"No",width:"60"}}),a("el-table-column",{attrs:{label:3===e.search.dimension?"月份":1===e.search.dimension?"班次":"时间"},scopedSlots:e._u([{key:"default",fn:function(t){return[a("span",[e._v(e._s(t.row.date))]),1===e.search.dimension?a("span",[e._v("/"+e._s(t.row.classes))]):e._e()]}}])}),a("el-table-column",{attrs:{prop:"equip_no",label:"设备编码"}}),a("el-table-column",{attrs:{prop:"total_trains",label:"总车数"}}),a("el-table-column",{attrs:{prop:"total_time",label:"总耗时/min"},scopedSlots:e._u([{key:"default",fn:function(t){var a=t.row;return[e._v(" "+e._s(e._f("setTimeMin")(a.total_time))+" ")]}}])}),a("el-table-column",{attrs:{label:"总时间/min",prop:"classes_time"},scopedSlots:e._u([{key:"default",fn:function(t){var n=t.row;return[a("span",[e._v(" "+e._s(e._f("setTimeMin")(n.classes_time))+" ")])]}}])}),a("el-table-column",{attrs:{label:"利用率"},scopedSlots:e._u([{key:"default",fn:function(t){var n=t.row;return[2===Number(e.search.day_type)&&1===e.search.dimension?a("span",[e._v(" "+e._s(e.setUse(n.total_time,n.classes_time,!0))+" ")]):e._e(),2===e.search.dimension?a("span",[e._v(" "+e._s(e.setUse(n.total_time,86400,!0))+" ")]):e._e(),3===e.search.dimension?a("span",[e._v(" "+e._s(e.setUse(n.total_time,15552e4,!0))+" ")]):e._e()]}}])})],1),a("page",{attrs:{total:e.total,"current-page":e.search.page},on:{currentChange:e.currentChange}})],1)},s=[],r=(a("a623"),a("4160"),a("baa5"),a("d81d"),a("13d5"),a("a9e3"),a("b680"),a("ac1f"),a("841c"),a("159b"),a("96cf"),a("1da1")),i=a("4090"),o=a("3e51"),l=a("befc"),c=a("1f6c"),u=a("2c93"),d={components:{page:o["a"],equipSelect:i["a"],timeSpanSelect:l["a"]},mixins:[u["a"]],data:function(){return{total:0,loading:!1,search:{page:1,dimension:1,day_type:2,date:[]},tableData:[]}},created:function(){this.getList()},methods:{getList:function(){var e=this;return Object(r["a"])(regeneratorRuntime.mark((function t(){var a,n;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.prev=0,e.loading=!0,t.next=4,Object(c["i"])("get",null,{params:e.search});case 4:a=t.sent,e.total=a.count,e.tableData=a.results,e.tableData.length>0&&(2!==Number(e.search.day_type)||1!==e.search.dimension)&&(2===e.search.dimension?n=86400:3===e.search.dimension&&(n=2592e3),e.tableData.forEach((function(e){e.classes_time=n}))),e.loading=!1,t.next=14;break;case 11:t.prev=11,t.t0=t["catch"](0),e.loading=!1;case 14:case"end":return t.stop()}}),t,null,[[0,11]])})))()},changeDate:function(e){this.search.st=e?e[0]:"",this.search.et=e?e[1]:"",this.getList(),this.search.page=1},changeRadio:function(e){this.search.day_type=e,this.getList(),this.search.page=1},currentChange:function(e){this.search.page=e,this.getList()},equipChanged:function(e){this.search.equip_no=e,this.getList(),this.search.page=1},timeSpanChanged:function(e){this.search.dimension=e,this.getList(),this.search.page=1},setMonth:function(e){if(e){var t=new Date(e);return t.getFullYear()+"/"+(t.getMonth()+1)}},setUse:function(e,t){if(!e||!t)return 0;var a=parseFloat(e/t*100).toFixed(100),n=a.substring(0,a.lastIndexOf(".")+3);return n+"%"},setNum:function(e){if(e<0)return e;if(!e)return 0;var t=parseFloat(e/60).toFixed(10),a=t.substring(0,t.lastIndexOf(".")+2);return a},getSummaries:function(e){var t=this,a=e.columns,n=e.data,s=[];return a.forEach((function(e,a){if(0!==a){var r=n.map((function(t){return Number(t[e.property])}));r.every((function(e){return isNaN(e)}))?s[a]:(s[a]=r.reduce((function(e,t){var a=Number(t);return isNaN(a)?e:e+t}),0),3===a?s[a]:s[a]=t.setNum(s[a]))}else s[a]="总价"})),s}}},h=d,p=a("2877"),m=Object(p["a"])(h,n,s,!1,null,null,null);t["default"]=m.exports}}]);