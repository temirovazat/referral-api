from django.urls import include, path

from api.v1.users import urls as urls_users

urlpatterns = [
    path('', include(urls_users)),
]
