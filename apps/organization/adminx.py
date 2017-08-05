# _*_ encoding:utf-8 _*_
# __author__ = 'han'
# __date__ = '2017/1/12 23:18'
import xadmin
from .models import CityDict, CourseOrg, Teacher


class CityDictAdmin(object):
    list_display = ['name', 'desc', 'add_time']
    search_fields = ['name', 'desc']
    list_filter = ['name', 'desc', 'add_time']
    model_icon = 'fa fa-university'


class CourseOrgAdmin(object):
    list_display = ['name', 'desc', 'click_num', 'fav_num', 'image', 'address', 'city', 'add_time']
    search_fields = ['name', 'desc', 'click_num', 'fav_num', 'image', 'address', 'city']
    list_filter = ['name', 'desc', 'click_num', 'fav_num', 'image', 'address', 'city', 'add_time']

    # 设置在选择课程机构时,可以搜索,fk代表当有一个外键指向他的时候用ajax加载
    # 默认情况下也是可以搜索的,但如果数据量过大的情况下,一次性就需要加载很多了
    # relfield_style = 'fk-ajax'


class TeacherAdmin(object):
    list_display = ['org', 'name', 'work_years', 'work_company', 'work_position', 'points', 'click_num', 'fav_num',
                    'add_time']
    search_fields = ['org', 'name', 'work_years', 'work_company', 'work_position', 'points', 'click_num', 'fav_num']
    list_filter = ['org', 'name', 'work_years', 'work_company', 'work_position', 'points', 'click_num', 'fav_num',
                   'add_time']


xadmin.site.register(CityDict, CityDictAdmin)
xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(Teacher, TeacherAdmin)