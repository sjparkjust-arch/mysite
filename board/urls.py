from django.urls import path
from . import views

app_name = "board"

urlpatterns = [
    path("", views.post_list, name="post_list"),

    path("posts/add/", views.post_add, name="post_add"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("posts/<int:post_id>/update/", views.post_update, name="post_update"),
    path("posts/<int:post_id>/delete/", views.post_delete, name="post_delete"),

    path("attachments/<int:attachment_id>/download/", views.attachment_download, name="attachment_download"),

    path("signin/", views.signin, name="signin"),
    path("signout/", views.signout, name="signout"),
    path("signup/", views.signup, name="signup"),
]
