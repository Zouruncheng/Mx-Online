# _*_ encoding:utf-8 _*_
from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from organization.models import CourseOrg, Teacher
from DjangoUeditor.models import UEditorField


class Course(models.Model):
    course_org = models.ForeignKey(CourseOrg, verbose_name=u"课程机构", null=True, blank=True )
    name = models.CharField(max_length=50, verbose_name=u"课程名")
    desc = models.CharField(max_length=300, verbose_name=u"课程描述")
    detail = UEditorField(verbose_name=u"课程详情", width=600, height=300,
                                           imagePath = "courses/image/ueditor/%(basename)s_%(datetime)s.%",
                                           filePath = "courses/ueditor/%(basename)s_%(datetime)s.%", default="")

    # 关联teacher这model的外键
    teacher = models.ForeignKey(Teacher, verbose_name=u"讲师", null=True, blank=True)
    degree = models.CharField(verbose_name=u"难度", choices=(("cj", "初级"),
                                                           ("zj", "中级"),
                                                           ("gj", "高级")), max_length=2)
    learn_time = models.IntegerField(default=0, verbose_name=u"学习时长(分钟)")
    students = models.IntegerField(default=0, verbose_name=u"学习人数")
    fav_nums = models.IntegerField(default=0, verbose_name=u"收藏人数")
    image = models.ImageField(upload_to="courses/%Y/%m", verbose_name=u"封面", max_length=100)
    click_nums = models.IntegerField(default=0, verbose_name=u"点击数")
    category = models.CharField(max_length=20, verbose_name=u"课程类别", default=u"后端开发")
    tag = models.CharField(default="", max_length=20, verbose_name=u"课程标签")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")
    youneed_know = models.CharField(max_length=300, verbose_name=u"课程须知", default="")
    teacher_tips = models.CharField(max_length=300, verbose_name=u"老师告诉你", default="")
    is_banner = models.BooleanField(default=False, verbose_name=u"是否轮播")

    class Meta:
        verbose_name = u"课程"
        verbose_name_plural = verbose_name

    def get_zj_nums(self):
        # 获取课程章节数,下面的lesson_set调用的是下面的Lesson类,set是django生成的,这样可以在course中获取章节数
        return self.lesson_set.all().count()
    # 这可以让后台显示正确的中文名字
    get_zj_nums.short_description = "章节数"

    def go_to(self):
        # 这个可以让后台显示html的内容
        # django的mark_safe可以让显示a标签里面的内容,而不是直接输出文本
        from django.utils.safestring import mark_safe
        return mark_safe("<a href='http://www.projectsedu.com'>跳转</a>")
    go_to.short_description = "跳转"

    def get_learn_users(self):
        # 获取学习用户
        return self.usercourse_set.all()[:5]

    def get_course_lesson(self):
        # 获取课程所有章节
        return self.lesson_set.all()

    def __unicode__(self):
        return self.name


class BannerCourse(Course):
    """
    让轮播课程独立在后台有个管理器
    """
    class Meta:
        verbose_name = "轮播课程"
        verbose_name_plural = verbose_name
        # proxy这个参数非常重要!如果没有它,则会再生成一张表,添加这个参数则有model的功能又不会生成表
        proxy = True


class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name=u"课程")
    name = models.CharField(max_length=100, verbose_name=u"章节名")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"章节"
        verbose_name_plural = verbose_name

    def get_lesson_video(self):
        # 获取章节所有视频
        return self.video_set.all()

    def __unicode__(self):
        return self.name


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name=u"章节")
    name = models.CharField(max_length=100, verbose_name=u"视频名")
    url = models.CharField(max_length=200, verbose_name=u"访问网址", default="")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")
    learn_time = models.IntegerField(default=0, verbose_name=u"学习时长(分钟)")

    class Meta:
        verbose_name = u"视频"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name


class CourseResourse(models.Model):
    course = models.ForeignKey(Course, verbose_name=u"课程")
    name = models.CharField(max_length=100, verbose_name=u"名称")
    download = models.FileField(upload_to="course/resource/%Y/%m", verbose_name=u"资源文件", max_length=100)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"课程资源"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name
