from django.views.generic import View
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core import serializers
from django.db.models.functions import Now
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .views import LoginRequiredView
from .models import Menu, Dish, Menu_Dish
from utils.calories import bmr
import json
import random
from datetime import datetime

calories_conf = [
    (-1, -1),
    (-1, 200),
    (200, 500),
    (500, 1000),
    (1000, 2000),
    (2000, -1)
]

LIMIT_DISH_FILTER = 10
CRUD_SUCCESS_NAVIGATE = "/menu/history"

class index(LoginRequiredView):
    def get(self, request):
        return self.execute(request)
    def post(self, request):
        return self.execute(request)
    def execute(self, request):
        # Menu.objects.all().delete()
        return render(request, 'menu/index.html', None)


class create(LoginRequiredView):
    def get(self, request):
        return self.execute(request)
    def post(self, request):
        return self.execute(request)
    def execute(self, request):
        user = request.user.user
        data = {}
        weight = user.weight
        height = user.height
        gender = user.gender
        age = datetime.now().year - user.birthday.year
        diet_factor = user.diet_factor
        calories = bmr(weight, height, gender, age, diet_factor)
        data['calories'] = calories
        data['calories_conf'] = calories_conf
        return render(request, 'menu/create.html', data)

class create_query(LoginRequiredView):
    def get(self, request):
        return self.execute(request)
    def post(self, request):
        # dishes = request.POST.getlist('dishes[]')
        content = {}
        content['dishes'] = json.loads(request.POST['dishes'])
        content['description'] = request.POST['description']
        content['limit'] = request.POST['limit']
        return self.execute(request, content)
    def execute(self, request, content):
        user = request.user.user
        menu = Menu(
            user=request.user,
            description=content['description'],
            mealtime=Now(),
            limit=content['limit'],
        )
        menu.save()
        dishes = content['dishes']
        for d in dishes:
            print(d)
            dish = Dish.objects.get(pk=d['dish_id'])
            m_d = Menu_Dish.objects.create(
                dish=dish,
                menu = menu,
                count=d['count']
            )
            m_d.save()
        return HttpResponse(CRUD_SUCCESS_NAVIGATE)

class update_query(LoginRequiredView):
    def get(self, request):
        return self.execute(request)
    def post(self, request):
        # dishes = request.POST.getlist('dishes[]')
        content = {}
        content['menu_id'] = request.POST['menu_id']
        content['dishes'] = json.loads(request.POST['dishes'])
        content['description'] = request.POST['description']
        content['limit'] = request.POST['limit']
        return self.execute(request, content)
    def execute(self, request, content):
        print(content)
        user = request.user.user

        menu_id = content['menu_id']
        description = content['description']
        limit = content['limit']
        dishes = content['dishes']

        menu = Menu.objects.get(pk=menu_id)
        menu.description = description
        menu.limit = limit
        menu.save()

        Menu_Dish.objects.filter(menu=menu).delete()

        for d in dishes:
            dish = Dish.objects.get(pk=d['dish_id'])
            m_d = Menu_Dish.objects.create(
                dish=dish,
                menu = menu,
                count=d['count']
            )
            m_d.save()
        return HttpResponse(CRUD_SUCCESS_NAVIGATE)


class clone_query(create_query):
    pass


class delete_query(LoginRequiredView):
    def get(self, request):
        content = {}
        content['menu_id'] = request.GET['menu_id']
        return self.execute(request, content)
    def post(self, request):
        content = {}
        content['menu_id'] = request.POST['menu_id']
        return self.execute(request, content)
    def execute(self, request, content):
        menu_id = content['menu_id']
        menu = Menu.objects.get(pk = menu_id)
        Menu_Dish.objects.filter(menu=menu).delete()
        menu.delete()
        return HttpResponse(CRUD_SUCCESS_NAVIGATE)





class history(LoginRequiredView):
    PAGE_NUMBER_DEFAULT = 1
    ORDER_TYPE_DEFAULT = "newest"
    DATE_FILTER_DEFAULT = ""
    def get(self, request):
        self.page_number = int(request.GET.get("page_number", self.PAGE_NUMBER_DEFAULT))
        self.order_type = request.GET.get("order_type", self.ORDER_TYPE_DEFAULT)
        self.date_filter = request.GET.get("date_filter", self.DATE_FILTER_DEFAULT)
        return self.execute(request)
    def post(self, request):
        self.page_number = int(request.POST.get("page_number", self.PAGE_NUMBER_DEFAULT))
        self.order_type = request.POST.get("order_type", self.ORDER_TYPE_DEFAULT)
        self.date_filter = request.POST.get("date_filter", self.DATE_FILTER_DEFAULT)
        return self.execute(request)
    def execute(self, request):
        query = Q(user=request.user)
        if self.date_filter != "":
            [day, month, year] = self.date_filter.split("-")
            print(day, month, year)
            query = query & Q(mealtime__day=day, mealtime__month=month, mealtime__year=year)
        menus = Menu.objects.filter(query).order_by('-mealtime' if self.order_type == self.ORDER_TYPE_DEFAULT else 'mealtime') 
        for menu in menus:
            dishes = menu.dishes.all()
            calories = sum((dish.calories for dish in dishes))
            menu.calories = calories
        res_menus, page_count = data_paginator(menus, self.page_number)
        return render(
            request,
            "menu/history.html", 
            {
                "menus": res_menus,
                "page_count": page_count,
                "cur_page": self.page_number,
                "has_next": page_count>self.page_number,
                "has_previous": self.page_number>1,
                "date_filter": self.date_filter
            }
        )


class detail(LoginRequiredView):
    def get(self, request, menu_id):
        content = {}
        content["menu_id"] = menu_id
        return self.execute(request, content)
    def post(self, request, menu_id):
        content = {}
        content["menu_id"] = menu_id
        return self.execute(request, content)
    def execute(self, request, content):
        menu_id = content["menu_id"]
        menu = Menu.objects.get(pk=menu_id)
        dishes = list(menu.dishes.all())
        menus_dishes = []
        for dish in dishes:
            md = {}
            md['count'] = Menu_Dish.objects.get(menu=menu, dish=dish).count
            menus_dishes.append(md)
        return render(request, "menu/detail.html", {
            'menu': menu,
            'dishes': serializers.serialize('json', dishes),
            'menus_dishes': menus_dishes,
            'calories_conf': calories_conf
        })


class update(LoginRequiredView):
    def get(self, request):
        return self.execute(request)
    def post(self, request):
        return self.execute(request)
    def execute(self, request):
        return HttpResponse("Menu Update")


class delete(LoginRequiredView):
    def get(self, request):
        return self.execute(request)
    def post(self, request):
        return self.execute(request)
    def execute(self, request):
        return HttpResponse("Menu Delete")

def query_filter_dish(request):
    calo_select = 0
    field = ""
    if (request.method == "POST"):
        calo_select = request.POST["calo_select"]
        field = request.POST["field"]
    calo_select = int(calo_select)
    calo_set = calories_conf[calo_select]
    query = Q()
    if calo_set[0] != -1:
        query = query & Q(calories__gte=calo_set[0])
    if calo_set[1] != -1:
        query = query & Q(calories__lte=calo_set[1])
    if len(field) != 0:
        query = query & (Q(dish_name__contains=field) | Q(description__contains=field))
    dishs = Dish.objects.filter(query)[:LIMIT_DISH_FILTER]

    json_dishs = serializers.serialize('json', dishs)
    return JsonResponse(json_dishs, content_type="text/json-comment-filtered", safe=False)


def data_paginator(data, page):
    paginator = Paginator(data, 10)
    try:
        rate_paged = paginator.page(page)        
    except PageNotAnInteger:
        rate_paged = paginator.page(1)
    except EmptyPage:
        rate_paged = paginator.page(paginator.num_pages)

    return rate_paged, paginator.num_pages