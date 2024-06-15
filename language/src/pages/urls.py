from django.urls import path


from pages import views

urlpatterns = [
    path("", views.home, name="home"),
    path("learning/", views.learning, name="learning"),
]
