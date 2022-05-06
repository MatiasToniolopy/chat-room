from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),

    path('home', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),

    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),
    path('update-user/', views.updateUser, name="update-user"),

    path('topics/', views.topicsPage, name="topics"),
    path('activity/', views.activityPage, name="activity"),
    path('chang-pass/', views.passupdate, name="chang-pass"),
    
    path('follow/<str:pk>/', views.follow, name="follow"),
    path('unfollow/<str:pk>/', views.unfollow, name="unfollow"),
    
    path('reset-passw', views.PassView.as_view(), name='reset-passw'),
    path('change-passw/<uidb64>/<token>/', views.ChangePasswordView.as_view(), name='change-passw'),
    path('activate/<uidb64>/<token>/', views.VerificationView.as_view(), name='activate'),
    
]
