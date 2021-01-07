from django.urls import path, include

from . import user_views, dish_views, menu_views

urlpatterns = [
    path('', dish_views.AllPublicDishView.as_view(), name='index'),
    path('accounts/', include([
        path('register/', user_views.RegisterView.as_view(), name='register'),
    ])),
    path('users/', include([
        path('profile/', user_views.UpdateProfileView.as_view(), name='account_profile'),
        path('dish/', include([
            path('', dish_views.UserAllDishView.as_view(), name='user_all_dishes'),
            path('add/', dish_views.CreateDishView.as_view(), name='user_add_dish'),
            path('<int:pk>/', include([
                path('', dish_views.UserDishView.as_view(), name='user_dish_detail'),
                path('update/', dish_views.UpdateDishView.as_view(), name='user_update_dish'),
                path('delete/', dish_views.DeleteDishView.as_view(), name='user_delete_dish')
            ]))
        ]))
    ])),
    path('admins/', include([
        # path('', admin_views.Index.as_view(), name='admin_index'),
        # path('user/', admin_views.UserManagement.as_view(), name='user_management'),
        path('profile/', user_views.AdminSearchProfile.as_view(), name='admin_search_profile'),
        path('dish/', include([
            path('', dish_views.AdminAllDishView.as_view(), name='admin_all_dishes'),
            path('add/', dish_views.CreateDishView.as_view(), name='admin_add_dish'),
            path('<int:pk>/', include([
                path('', dish_views.AdminDishView.as_view(), name='admin_dish_detail'),
                path('update/', dish_views.UpdateDishView.as_view(), name='admin_update_dish'),
                path('delete/', dish_views.DeleteDishView.as_view(), name='admin_delete_dish')
            ]))
        ])),
    ])),
    path('dish/', include([
        path('', dish_views.SearchDishView.as_view(), name='search_dish'),
        path('<int:pk>/', include([
            path('', dish_views.DishDetailView.as_view(), name='dish_detail'),
            path('rate/', dish_views.UserRatingView.as_view(), name='user_rating'),
            path('delete/', dish_views.SuperuserDeleteDishView.as_view(), name='self_delete_dish')
        ])),
    ])),
    path('profile/', include([
        path('', user_views.SearchProfile.as_view(), name='search_profile'),
        path('<int:pk>/', include([
            path('', user_views.ProfileView.as_view(), name='profile_detail'),
            path('activate/', user_views.UpdateActivationView.as_view(), name='update_activation')
        ])),
    ])),

    path('menu/', include([
        path('', menu_views.index.as_view(), name="menu_index"),
        path('create', menu_views.create.as_view(), name="menu_create"),
        path('create_query', menu_views.create_query.as_view(), name="menu_create_query"),
        path('update_query', menu_views.update_query.as_view(), name="menu_update_query"),
        path('clone_query', menu_views.clone_query.as_view(), name="menu_clone_query"),
        path('delete_query', menu_views.delete_query.as_view(), name="menu_delete_query"),
        path('history', menu_views.history.as_view(), name="menu_history"),
        path('detail/<int:menu_id>', menu_views.detail.as_view(), name="menu_detail"),
        path('update', menu_views.update.as_view(), name="menu_update"),
        path('delete', menu_views.delete.as_view(), name="menu_delete"),
        path('query_filter_dish', menu_views.query_filter_dish, name="menu_query_filter_dish")
    ]))
]

handler404 = 'foods.views.error_404'
handler500 = 'foods.views.error_500'
