from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.task_list, name="task_list"),
    path("create/", views.task_create, name="task_create"),
    path("<int:pk>/edit/", views.task_edit, name="task_edit"),
    path("<int:pk>/delete/", views.task_delete, name="task_delete"),
    path("<int:pk>/toggle/", views.task_toggle, name="task_toggle"),

    path("trash/", views.trash, name="trash"),
    path("<int:pk>/restore/", views.task_restore, name="task_restore"),

    path("login/", auth_views.LoginView.as_view(template_name="tasks/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
]