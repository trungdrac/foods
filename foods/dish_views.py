from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import View

from .constants.pagination import *
from .forms import DishForm, RatingForm
from .i18n.vi import *
from .models import Dish, Rating
from .views import SelfUpdateView, SelfDeleteView, UserListView, LoginRequiredView, UserOnlyView, AdminOnlyView, \
    AdminListView, SuperuserDeleteView


class AdminDishView(AdminOnlyView):
    def get(self, request, pk):
        dish = get_object_or_404(Dish, pk=pk, user=request.user)
        ratings = Rating.objects.filter(dish=dish)
        p = Paginator(ratings, RATINGS_PER_PAGE)
        page = p.get_page(request.GET.get('page', 1))
        return render(request, 'admins/dish.html', {
            'object': dish,
            'page_obj': page
        })


class AdminAllDishView(AdminListView):
    model = Dish
    template_name = 'admins/dishes.html'
    queryset = Dish.objects.all()
    paginate_by = DISHES_PER_PAGE

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_context_data(self, **kwarg):
        context = super().get_context_data(**kwarg)
        return context


class UserDishView(UserOnlyView):
    def get(self, request, pk):
        dish = get_object_or_404(Dish, pk=pk, user=request.user)
        ratings = Rating.objects.filter(dish=dish)
        p = Paginator(ratings, RATINGS_PER_PAGE)
        page = p.get_page(request.GET.get('page', 1))
        return render(request, 'users/dish.html', {
            'object': dish,
            'page_obj': page
        })


class UserAllDishView(UserListView):
    model = Dish
    template_name = 'users/dishes.html'
    queryset = Dish.objects.all()
    paginate_by = DISHES_PER_PAGE

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_context_data(self, **kwarg):
        context = super().get_context_data(**kwarg)
        return context


class UpdateDishView(SelfUpdateView):
    form_class = DishForm
    queryset = Dish.objects.all()
    success_message = DISH_UPDATED

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse('admin_dish_detail', kwargs={'pk': self.object.pk})
        else:
            return reverse('user_dish_detail', kwargs={'pk': self.object.pk})


class DeleteDishView(SelfDeleteView):
    model = Dish
    success_message = DISH_DELETED

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse('admin_all_dishes')
        else:
            return reverse('user_all_dishes')


class SuperuserDeleteDishView(SuperuserDeleteView):
    model = Dish
    success_message = DISH_DELETED

    def get_success_url(self):
        return reverse('index')


class CreateDishView(LoginRequiredView):
    def get(self, request):
        return render(request, 'foods/dish_add.html')

    def post(self, request):
        dish_form = DishForm(request.POST, request.FILES)
        if dish_form.is_valid():
            dish = dish_form.save(False)
            dish.user = request.user
            dish.save()
            messages.success(request, DISH_CREATED)
            if request.user.is_staff:
                return redirect('admin_all_dishes')
            else:
                return redirect('user_all_dishes')
        else:
            messages.error(request, dish_form.errors)
            return render(request, 'foods/dish_add.html')


class UserRatingView(UserOnlyView):
    def post(self, request, pk):
        dish = get_object_or_404(Dish, pk=pk)
        user = request.user
        if dish.user != user:
            ratings = Rating.objects.filter(dish=dish, user=user)
            if ratings:
                rating_instance = ratings.get()
                rating_form = RatingForm(request.POST, instance=rating_instance)
                if rating_form.is_valid():
                    rating_form.save()
                    messages.success(request, RATE_UPDATED)
                else:
                    messages.error(request, rating_form.errors)
            else:
                rating_form = RatingForm(request.POST)
                if rating_form.is_valid():
                    rating = rating_form.save(False)
                    rating.dish = dish
                    rating.user = user
                    rating.save()
                    messages.success(request, RATE_CREATED)
                else:
                    messages.error(request, rating_form.errors)
        return redirect('dish_detail', pk=pk)


class DishDetailView(View):
    def get(self, request, pk):
        dish = get_object_or_404(Dish, pk=pk)
        ratings = Rating.objects.filter(dish=dish)
        p = Paginator(ratings, RATINGS_PER_PAGE)
        page = p.get_page(request.GET.get('page', 1))
        context = {
            'object': dish,
            'page_obj': page
        }
        user = request.user
        if user.is_authenticated and not user.is_staff:
            user_rating = Rating.objects.filter(dish=dish, user=user)
            if user_rating:
                context['user_rating'] = user_rating.get()
        return render(request, 'dish.html', context)


class SearchDishView(View):
    def get(self, request):
        query = self.request.GET.get('search')
        dishes = Dish.objects.filter(
            Q(dish_name__icontains=query) |
            Q(description__icontains=query) |
            Q(ingredients__icontains=query),
            is_public=True
        )
        if not dishes:
            dishes = Dish.objects.filter(is_public=True)
            messages.error(request, NO_DISH_FOUND)
        p = Paginator(dishes, DISHES_PER_PAGE)
        page = p.get_page(request.GET.get('page', 1))
        return render(request, 'dishes.html', {
            'page_obj': page
        })


class AllPublicDishView(View):
    def get(self, request):
        dishes = Dish.objects.filter(is_public=True)
        if dishes:
            p = Paginator(dishes, DISHES_PER_PAGE)
            page = p.get_page(request.GET.get('page', 1))
            return render(request, 'dishes.html', {
                'page_obj': page
            })
        else:
            messages.error(request, NO_DISH_FOUND)
            return render(request, 'dishes.html')
