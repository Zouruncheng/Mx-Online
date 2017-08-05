# _*_ encoding:utf-8 _*_
from django.shortcuts import render
from django.views.generic import View
from django.shortcuts import render_to_response
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q

from .models import CityDict, Teacher, CourseOrg
from .forms import UserAskForm
from operation.models import UserFavorite
from courses.models import Course
import json


class OrgView(View):
    """
    课程机构列表功能
    """
    def get(self, request):
        # 课程机构
        all_orgs = CourseOrg.objects.all()

        # 机构排名
        hot_orgs = all_orgs.order_by("-click_num")[:3]

        # 城市
        all_citys = CityDict.objects.all()
        # 搜索机构搜索
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            # __icontains会执行like语句的操作,有i一般是不区分大小写,下面用了Q方法,将关键词和name,desc,detail比较
            all_orgs = all_orgs.filter(
                Q(name__icontains=search_keywords) |
                Q(desc__icontains=search_keywords)
            )

        # 取出筛选城市
        city_id = request.GET.get('city', "")
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        # 类别筛选
        category = request.GET.get('ct', "")
        if category:
            all_orgs = all_orgs.filter(category=category)

        # 排序
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                all_orgs = all_orgs.order_by("-students")
            elif sort == "course":
                all_orgs = all_orgs.order_by("-course_nums")

        # 总数统计
        org_nums = all_orgs.count()

        # 对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 下面这个数字5是每页显示的数量,文档里面没说,是个坑
        p = Paginator(all_orgs, 5, request=request)

        orgs = p.page(page)
        return render(request, "org-list.html", {
            "all_orgs": orgs,
            "all_citys": all_citys,
            "org_nums": org_nums,
            "city_id": city_id,
            "category": category,
            "hot_orgs": hot_orgs,
            "sort": sort,
        })


class AddUserAskView(View):
    """
    用户添加咨询
    """
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            # commit这个可以提交到数据库
            user_ask = userask_form.save(commit=True)

            # content_tpye可以指明传递给html的格式,application/json是固定写法
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加出错"}', content_type='application/json')


class OrgHomeView(View):
    """
    机构首页
    """
    def get(self, request, org_id):
        current_page = "home"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_courses = course_org.course_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[:1]
        return render(request, 'org-detail-homepage.html', {
            'all_courses': all_courses,
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgCourseView(View):
    """
    机构课程列表页
    """
    def get(self, request, org_id):
        # 这个参数是传递给base_org模板,给导航条加active
        current_page = "course"
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_courses = course_org.course_set.all()
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-course.html', {
            'all_courses': all_courses,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgDescView(View):
    """
    机构介绍列表页
    """
    def get(self, request, org_id):
        CourseOrg.click_num += 1
        CourseOrg.save()
        # 这个参数是传递给base_org模板,给导航条加active
        current_page = "desc"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-desc.html', {
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgTeacherView(View):
    """
    机构教师列表页
    """
    def get(self, request, org_id):
        # 这个参数是传递给base_org模板,给导航条加active
        current_page = "teacher"
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 取出所有数据,前面的course_org是上面得到id的变量
        all_teacher = course_org.teacher_set.all()
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-teachers.html', {
            'course_org': course_org,
            'current_page': current_page,
            'all_teacher': all_teacher,
            'has_fav': has_fav,
        })


class AddFavView(View):
    """
    用户收藏，用户取消收藏
    """
    def post(self, request):
        fav_id = int(request.POST.get('fav_id', 0))
        fav_type = int(request.POST.get('fav_type', 0))

        # 判断用户登录状态
        if not request.user.is_authenticated():
            res = {}
            res['status'] = 'fail'
            res['msg'] = u'用户未登录'
            return HttpResponse(json.dumps(res), content_type='application/json')

        # 查询收藏记录
        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=fav_id, fav_type=fav_type)

        # 收藏已经存在
        res = {}
        if exist_records:
            # 如果记录已经存在，则表示用户取消收藏
            exist_records.delete()

            if int(fav_type) == 1:
                course = Course.objects.get(id=int(fav_id))
                course.fav_nums -= 1
                # 因为之前有收藏过课程,但还是0,所以再减一就会是负数
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(fav_type == 2):
                course_org = CourseOrg.objects.get(id=int(fav_id))
                course_org.fav_num -= 1
                if course_org.fav_num < 0:
                    course_org.fav_num = 0
                course_org.save()
            elif int(fav_type == 3):
                teacher = Teacher.objects.get(id=int(fav_id))
                teacher.fav_num -= 1
                if teacher.fav_num < 0:
                    teacher.fav_num = 0
                teacher.save()

            res['status'] = 'success'
            res['msg'] = u'收藏'
        else:
            user_fav = UserFavorite()
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                # 完成收藏需要三个字段 user_id，fav_id， fav_type
                user_fav.save()
                if int(fav_type) == 1:
                    course = Course.objects.get(id=int(fav_id))
                    course.fav_nums += 1
                    course.save()
                elif int(fav_type == 2):
                    course_org = CourseOrg.objects.get(id=int(fav_id))
                    course_org.fav_num += 1
                    course_org.save()
                elif int(fav_type == 3):
                    teacher = Teacher.objects.get(id=int(fav_id))
                    teacher.fav_num += 1
                    teacher.save()

                res['status'] = 'success'
                res['msg'] = u'已收藏'
            else:
                res['status'] = 'fail'
                res['msg'] = u'收藏出错'

        return HttpResponse(json.dumps(res), content_type='application/json')


class TeacherListView(View):
    """
    课程讲师列表页
    """
    def get(self, request):
        all_teachers = Teacher.objects.all()
        # 搜索课程
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            # __icontains会执行like语句的操作,有i一般是不区分大小写,下面用了Q方法,将关键词和name,desc,detail比较
            all_teachers = all_teachers.filter(
                Q(name__icontains=search_keywords) |
                Q(work_company__icontains=search_keywords) |
                Q(work_position__icontains=search_keywords)
            )

        # 排序
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "hot":
                all_teachers = all_teachers.order_by("-click_num")

        # 讲师排行榜
        sorted_teacher = Teacher.objects.all().order_by("-click_num")[:3]

        # 对讲师进行分页,原来的all_teachers这个参数遍历的时候要加上.object_list
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 下面这个数字5是每页显示的数量,文档里面没说,是个坑
        p = Paginator(all_teachers, 5, request=request)

        all_teachers = p.page(page)
        return render(request, "teachers-list.html", {
            "all_teachers": all_teachers,
            "sort": sort,
            "sorted_teacher": sorted_teacher,
        })


class TeacherDetailView(View):
    """
    课程讲师详情页
    """
    def get(self, request, teacher_id):

        teacher = Teacher.objects.get(id=int(teacher_id))
        teacher.click_num += 1
        teacher.save()
        # 找到该讲师的所有课程
        all_courses = Course.objects.filter(teacher=teacher)
        # 收藏功能
        has_fav_org = False
        has_fav_teacher = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=teacher.org.id, fav_type=2):
                has_fav_org = True
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=teacher.id, fav_type=3):
                has_fav_teacher = True
        # 讲师排行榜
        sorted_teacher = Teacher.objects.all().order_by("-click_num")[:3]
        return render(request, "teacher-detail.html", {
            "sorted_teacher": sorted_teacher,
            "teacher": teacher,
            "all_courses": all_courses,
            "has_fav_org": has_fav_org,
            "has_fav_teacher": has_fav_teacher,
        })
