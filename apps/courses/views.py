# _*_ encoding:utf-8 _*_
from django.views.generic.base import View
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from operation.models import UserFavorite, CouserComments, UserCourse
from .models import Course, CourseResourse, Video
# 这个是自己写的一个类,Mixin结尾代表的是django的基础view,没有强制要求
from utils.mixin_utils import LoginRequiredMixin


class CourseListView(View):
    def get(self, request):
        # 根据XX排列order_by()
        all_courses = Course.objects.all().order_by("-add_time")
        # 热门课程排序
        hot_courses = all_courses.order_by("-click_nums")[:3]

        # 搜索课程
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            # __icontains会执行like语句的操作,有i一般是不区分大小写,下面用了Q方法,将关键词和name,desc,detail比较
            all_courses = all_courses.filter(
                Q(name__icontains=search_keywords) |
                Q(desc__icontains=search_keywords) |
                Q(detail__icontains=search_keywords)
            )

        # 课程排序
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                all_courses = all_courses.order_by("-students")
            elif sort == "hot":
                all_courses = all_courses.order_by("-click_nums")

        # 对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 下面这个数字5是每页显示的数量,文档里面没说,是个坑
        p = Paginator(all_courses, 6, request=request)

        courses = p.page(page)

        return render(request, 'course-list.html', {
            "all_courses": courses,
            "order": sort,
            "hot_courses": hot_courses,
        })


class CourseDetailView(View):
    """
    课程详情页
    """

    # 这个course_id是url里面定义的
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        # 增加课程点击数
        course.click_nums += 1
        course.save()

        # 查询是否收藏课程与机构
        has_fav_course = False
        has_fav_org = False

        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True
        # 课程推荐
        tag = course.tag
        if tag:
            relate_course = Course.objects.filter(tag=tag)[:1]
        else:
            # 防止无数据时报错,传递一个空数组
            relate_course = []

        return render(request, "course-detail.html", {
            "course": course,
            "relate_course": relate_course,
            "has_fav_course": has_fav_course,
            "has_fav_org": has_fav_org,
        })


# 引入LoginRequiredMixin是为了查看视频章节信息前验证是否登录
class CourseInfoView(LoginRequiredMixin, View):
    """
    课程章节信息
    """

    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))

        # 点击课程，学习人数 + 1
        course.students += 1
        course.save()

        # 查询用户是否已经关联了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)  # 查询用户可课程关联是否存在
        if not user_courses:  # 如果没有存在关联则创建一个关联
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()
        # 取出 UserCourse 表里和这个课程一样的所有数据 data,filter是一个django的数组
        user_courses = UserCourse.objects.filter(course=course)
        # 取出 data 里所有用户的 user_ids 列表
        user_ids = [user_course.user.id for user_course in user_courses]
        # 取出 UserCourse 表里， 集合 user_ids 每个元素对应的数据
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [user_course.course.id for user_course in all_user_courses]
        # 获取学过该用户学过的其他课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:3]
        # 获取课程资源
        all_resources = CourseResourse.objects.filter(course=course)
        return render(request, "course-video.html", {
            "course": course,
            "course_resources": all_resources,
            "relate_courses": relate_courses,
        })


class CourseCommentsView(LoginRequiredMixin, View):
    """
    课程评论
    """

    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        # 获取课程资源
        all_resources = CourseResourse.objects.filter(course=course)
        all_comments = CouserComments.objects.all()
        # 取出 UserCourse 表里和这个课程一样的所有数据 data,filter是一个django的数组
        user_courses = UserCourse.objects.filter(course=course)
        # 取出 data 里所有用户的 user_ids 列表
        user_ids = [user_course.user.id for user_course in user_courses]
        # 取出 UserCourse 表里， 集合 user_ids 每个元素对应的数据
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [user_course.course.id for user_course in all_user_courses]
        # 获取学过该用户学过的其他课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:3]
        return render(request, "course-comment.html", {
            "course": course,
            "course_resources": all_resources,
            "all_comments": all_comments,
            "relate_courses": relate_courses,
        })


class AddCommentsView(View):
    """
    用户添加评论
    """

    def post(self, request):
        if not request.user.is_authenticated():
            # 判断用户是否登录
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        course_id = request.POST.get("course_id", 0)
        comments = request.POST.get("comments", "")
        if course_id > 0 and comments:
            course_comments = CouserComments()
            # get只能拿到一条数据,如果多条或者空则会抛出异常
            course = Course.objects.get(id=int(course_id))
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            return HttpResponse('{"status":"success", "msg":"添加成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加失败"}', content_type='application/json')


class VideoPlayView(View):
    """
    视频播放
    """

    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        course = video.lesson.course
        # 点击课程，学习人数 + 1
        course.students += 1
        course.save()

        # 查询用户是否已经关联了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)  # 查询用户可课程关联是否存在
        if not user_courses:  # 如果没有存在关联则创建一个关联
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()
        # 取出 UserCourse 表里和这个课程一样的所有数据 data,filter是一个django的数组
        user_courses = UserCourse.objects.filter(course=course)
        # 取出 data 里所有用户的 user_ids 列表
        user_ids = [user_course.user.id for user_course in user_courses]
        # 取出 UserCourse 表里， 集合 user_ids 每个元素对应的数据
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [user_course.course.id for user_course in all_user_courses]
        # 获取学过该用户学过的其他课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:3]
        # 获取课程资源
        all_resources = CourseResourse.objects.filter(course=course)
        return render(request, "course-play.html", {
            "course": course,
            "course_resources": all_resources,
            "relate_courses": relate_courses,
            "video": video,
        })
