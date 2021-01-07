from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView


def index(request):
    context = {
        'app_name': 'Foods'
    }
    return render(request, 'index.html', context)


class LoginRequiredView(LoginRequiredMixin, View):
    login_url = '/accounts/login'


class SelfLoginView(UserPassesTestMixin, LoginRequiredView):
    def test_func(self):
        pass


class UserOnlyView(SelfLoginView):
    def test_func(self):
        return not self.request.user.is_staff


class AdminOnlyView(SelfLoginView):
    def test_func(self):
        return self.request.user.is_staff


class UserDetailView(DetailView, UserOnlyView):
    def test_func(self):
        return super().test_func() and (self.request.user.pk == self.get_object().user.pk)


class UserListView(ListView, UserOnlyView):
    def test_func(self):
        return super().test_func()


class UserCreateView(CreateView, UserOnlyView):
    def test_func(self):
        return super().test_func() and (self.request.user.pk == self.get_object().user.pk)


class UserUpdateView(UpdateView, UserOnlyView):
    def test_func(self):
        return super().test_func() and (self.request.user.pk == self.get_object().user.pk)


class UserDeleteView(DeleteView, UserOnlyView):
    def test_func(self):
        return super().test_func() and (self.request.user.pk == self.get_object().user.pk)


class AdminDetailView(DetailView, AdminOnlyView):
    def test_func(self):
        return super().test_func() and (self.request.user.pk == self.get_object().user.pk)


class AdminListView(ListView, AdminOnlyView):
    def test_func(self):
        return super().test_func()


class AdminCreateView(CreateView, AdminOnlyView):
    def test_func(self):
        return super().test_func() and (self.request.user.pk == self.get_object().user.pk)


class AdminUpdateView(UpdateView, AdminOnlyView):
    def test_func(self):
        return super().test_func() and (self.request.user.pk == self.get_object().user.pk)


class AdminDeleteView(DeleteView, AdminOnlyView):
    def test_func(self):
        return super().test_func() and (self.request.user.pk == self.get_object().user.pk)


class SelfCreateView(CreateView, SelfLoginView):
    def test_func(self):
        return self.request.user.pk == self.get_object().user.pk


class SelfUpdateView(UpdateView, SelfLoginView):
    def test_func(self):
        return self.request.user.pk == self.get_object().user.pk


class SelfDeleteView(DeleteView, SelfLoginView):
    def test_func(self):
        return self.request.user.pk == self.get_object().user.pk


class SuperuserDeleteView(DeleteView, SelfLoginView):
    def test_func(self):
        user = self.request.user
        return user.is_staff or (user.pk == self.get_object().user.pk)


def error_404(request, exception):
    return render(request, 'error.html')


def error_500(request):
    return render(request, 'error.html')
