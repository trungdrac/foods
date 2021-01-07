from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import View

from .constants.pagination import PROFILES_PER_PAGE
from .forms import UserForm, BaseUserForm
from .i18n.vi import *
from .models import Dish
from .views import LoginRequiredView, AdminOnlyView


class UpdateProfileView(LoginRequiredView):
    def get(self, request):
        user = request.user.user
        return render(request, 'registration/profile.html', {
            'form': user
        })

    def post(self, request):
        user_info = request.user.user
        user_form = UserForm(request.POST, instance=user_info)
        if user_form.is_valid():
            user = user_form.save(False)
            user.save()
            messages.success(request, PROFILE_UPDATED)
            return render(request, 'registration/profile.html', {
                'form': user
            })
        else:
            messages.error(request, user_form.errors)
            return render(request, 'registration/profile.html', {
                'form': user_info
            })


class RegisterView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            base_user_form = BaseUserForm()
            user_form = UserForm()
            return render(request, 'registration/register.html', {
                'user_form': user_form,
                'base_user_form': base_user_form
            })
        else:
            return redirect('account_profile')

    def post(self, request):
        if not request.user.is_authenticated:
            base_user_form = BaseUserForm(request.POST)
            user_form = UserForm(request.POST)
            if base_user_form.is_valid() and user_form.is_valid():
                with transaction.atomic():
                    base_user = base_user_form.save()
                    user = user_form.save(commit=False)
                    user.user = base_user
                    user.save()
                    messages.success(request, REGISTER_SUCCESS)
                return redirect('login')
            else:
                if base_user_form.errors:
                    messages.error(request, base_user_form.errors)
                if user_form.errors:
                    messages.error(request, user_form.errors)
                return render(request, 'registration/register.html', {
                    'user_form': user_form,
                    'base_user_form': base_user_form
                })
        else:
            return redirect('account_profile')


class UpdateActivationView(AdminOnlyView):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.is_active:
            messages.success(request, DEACTIVATE_SUCCESS)
        else:
            messages.success(request, ACTIVATE_SUCCESS)
        user.is_active = not user.is_active
        user.save()
        return redirect('profile_detail', pk=pk)


class ProfileView(View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        dishes = Dish.objects.filter(user=user, is_public=True)
        return render(request, 'profile.html', {
            'user': user,
            'dishes': dishes
        })


class SearchProfile(View):
    def get(self, request):
        query = self.request.GET.get('search')
        if query:
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query),
                is_active=True
            )
            if not users:
                users = User.objects.all().order_by('username')
                messages.error(request, NO_PROFILE_FOUND)
        else:
            users = User.objects.all().order_by('username')
        p = Paginator(users, PROFILES_PER_PAGE)
        page = p.get_page(request.GET.get('page', 1))
        return render(request, 'profiles.html', {
            'page_obj': page
        })


class AdminSearchProfile(AdminOnlyView):
    def get(self, request):
        query = self.request.GET.get('search')
        if query:
            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )
            if not users:
                users = User.objects.all().order_by('username')
                messages.error(request, NO_PROFILE_FOUND)
        else:
            users = User.objects.all().order_by('username')
        p = Paginator(users, PROFILES_PER_PAGE)
        page = p.get_page(request.GET.get('page', 1))
        return render(request, 'profiles.html', {
            'page_obj': page
        })
