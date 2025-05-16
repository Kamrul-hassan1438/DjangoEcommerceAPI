from django.urls import path
from .views import UserListView, UserDetailView, UserUpdateView,CategoryListCreateView

app_name = 'Admin'

urlpatterns = [
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),

     path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
]
