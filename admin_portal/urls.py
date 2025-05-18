from django.urls import path
from .views import *

urlpatterns = [
    path('',admin_portal,name="admin_portal"),
    path('/all-users',all_users,name="all_users"),
    path('/all-query',all_query,name="all_query"),
    path('/all-donations',all_donations,name="all_donations"),
    path('/all-todos-items',all_todos,name="all_todos"),
    path('/delete_account/<id>',admin_delete_account,name="admin_delete_account"),
    path('/update-query/<id>',update_query,name="update_query")
]
