# _*_ encoding:utf-8 _*_
import xadmin
from .models import Course, Lesson, Video, CourseResourse, BannerCourse
from organization.models import CourseOrg


class LessonInline(object):
    model = Lesson
    extra = 0


class CourseResourceInline(object):
    model = CourseResourse
    extra = 0


class CourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_time', 'students', 'get_zj_nums', 'go_to']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_time', 'students']
    # 可以根据点击数的倒序排列
    ordering = ['-click_nums']
    # 设置后台页面的某些数据只能可读
    readonly_fields = ['click_nums']
    # 列表页的数据可以进行快速修改
    list_editable = ['degree', 'desc']
    # 设置后台不可见数据, 这和readonly_fields字段冲突,不可以有相同的数据
    exclude = ['fav_nums']
    inlines = [LessonInline, CourseResourceInline]
    # style_fields是xadmin可以识别的,指定了detail页面采用ueditor的样式
    style_fields = {"detail": "ueditor"}
    # 关于excle导入
    import_excel = True
    # 定时刷新页面
    refresh_times = [3, 5]

    def queryset(self):
        # 这个方法可以让课程和轮播课程管理器不同,过滤掉其他课程
        qs = super(CourseAdmin, self).queryset()
        qs = qs.filter(is_banner=False)
        return qs

    def save_models(self):
        # 在保存课程的时候统计课程机构的课程数
        obj = self.new_obj
        obj.save()
        if obj.course_org is not None:
            course_org = obj.course_org
            course_org.course_nums = Course.objects.filter(course_org=course_org).count()
            course_org.save()

    def post(self, request, *args, **kwargs):
        if 'excel' in request.FILES:
            pass
        return super(CourseAdmin, self).post(request, args, kwargs)


class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_time', 'students']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_time', 'students']
    # 可以根据点击数的倒序排列
    ordering = ['-click_nums']
    # 设置后台页面的某些数据只能可读
    readonly_fields = ['click_nums']
    # 设置后台不可见数据, 这和readonly_fields字段冲突,不可以有相同的数据
    exclude = ['fav_nums']
    inlines = [LessonInline, CourseResourceInline]

    def queryset(self):
        # 这个方法可以让课程和轮播课程管理器不同,过滤掉其他课程
        qs = super(BannerCourseAdmin, self).queryset()
        qs = qs.filter(is_banner=True)
        return qs


class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    list_filter = ['course__name', 'name', 'add_time']


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time']


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course', 'name', 'download']
    list_filter = ['course', 'name', 'download',  'add_time']


xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResourse, CourseResourceAdmin)