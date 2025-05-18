from django.urls import path
from .views import *

urlpatterns = [
    path('update_todo/<id>',update_todo,name="update_todo"),
    path("profile",profile,name="profile"),
    path("todo/all_todos", show_all_todos, name="show_all_todos"),
    path("logout",logout_page,name="logout"),
    path("register",register,name = "register"),
    path("login",login_page,name="login"),
    path("todo",home,name="home"),
    path("todo/delete_item/<id>", delete_item, name="delete_item"),
    path("todo/update_status/<id>", update_status_to_finish, name="update_status_to_finish"),
    path("todo/update_status_to_progress/<id>", update_status_to_progress, name="update_status_to_progress"),
    path("forget-password", forget_password, name="forget_password"),
    path("forget-password/<username>",forget_password_authenticate,name="forget_password_authenticate"),
    path("change-password",change_password,name="change_password"),
    path("todo/policy",policy,name="policy"),
    path("delete_account/<username>",delete_account,name="delete_account"),
    path("update_account/<username>",update_account,name="update_account"),
    path('todo/about',about,name="about"),
    path('todo/contact-us',contact_us,name="contact_us"),
    path("todo/donate",payment,name="payment"),
    path("todo/donate/success",payment_success,name="payment_success"),
    path("todo/donate/failed",payment_failed,name="payment_failed"),
]
