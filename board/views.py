from pathlib import Path

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, F, Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Attachment, Post


MAX_FILE_SIZE = 20 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    ".pdf", ".txt", ".doc", ".docx", ".xls", ".xlsx",
    ".ppt", ".pptx", ".zip", ".png", ".jpg", ".jpeg",
}

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/zip",
    "application/x-zip-compressed",
    "image/png",
    "image/jpeg",
}

def validate_uploaded_files(files):
    errors = []

    for uploaded_file in files:
        extension = Path(uploaded_file.name).suffix.lower()

        if uploaded_file.size > MAX_FILE_SIZE:
            errors.append(
                f"{uploaded_file.name}: 파일 크기는 20MB 이하여야 합니다."
            )

        if extension not in ALLOWED_EXTENSIONS:
            errors.append(
                f"{uploaded_file.name}: 허용되지 않는 파일 확장자입니다."
            )
        
        if uploaded_file.content_type not in ALLOWED_CONTENT_TYPES:
            errors.append(
                f"{uploaded_file.name}: 허용되지 않는 MIME 형식입니다."
            )
    
    return errors


def post_list(request):
    search_type = request.GET.get("search_type", "all")
    keyword = request.GET.get("keyword", "").strip()

    posts = (
        Post.objects.select_related("author")
        .annotate(file_count=Count("attachments"))
        .order_by("-id")
    )

    if keyword:
        if search_type == "title":
            posts = posts.filter(title__icontains=keyword)
        elif search_type == "writer":
            posts = posts.filter(author__username__icontains=keyword)
        elif search_type == "content":
            posts = posts.filter(content__icontains=keyword)
        else:
            posts = posts.filter(
                Q(title__icontains=keyword)
                | Q(content__icontains=keyword)
                | Q(author__username__icontains=keyword)
            )

    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    current = page_obj.number
    start = max(current - 2, 1)
    end = min(current + 2, paginator.num_pages)
    page_range = range(start, end + 1)

    return render(
        request,
        "board/post_list.html",
        {
            "page_obj": page_obj,
            "page_range": page_range,
            "search_type": search_type,
            "keyword": keyword,
        },
    )


@login_required
def post_detail(request, post_id):
    Post.objects.filter(pk=post_id).update(
        view_count=F("view_count") + 1
    )

    post = get_object_or_404(
        Post.objects.select_related("author").prefetch_related("attachments"),
        pk=post_id,
    )

    return render(request, "board/post_detail.html", {"post": post})


@login_required
def post_add(request):
    errors = {}

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        files = request.FILES.getlist("files")

        if not title:
            errors["title"] = "제목을 입력하세요."
        elif len(title) > 100:
            errors["title"] = "제목은 100자 이내로 입력하세요."

        if not content:
            errors["content"] = "내용을 입력하세요."

        file_errors = validate_uploaded_files(files)
        if file_errors:
            errors["files"] = " ".join(file_errors)

        if not errors:
            with transaction.atomic():
                post = Post.objects.create(
                    title=title,
                    content=content,
                    author=request.user,
                )

                for uploaded_file in files:
                    Attachment.objects.create(
                        post=post,
                        file=uploaded_file,
                        original_name=uploaded_file.name,
                    )

            messages.success(request, "자료가 성공적으로 등록되었습니다.")
            return redirect(
                reverse("board:post_detail", args=(post.id,))
            )

        return render(
            request,
            "board/post_form.html",
            {
                "mode": "add",
                "errors": errors,
                "title": title,
                "content": content,
            },
        )

    return render(
        request,
        "board/post_form.html",
        {
            "mode": "add", 
            "title": "",
            "content": "",
            "errors": {}
        },
    )


@login_required
def post_update(request, post_id):
    post = get_object_or_404(
        Post.objects.prefetch_related("attachments"),
        pk=post_id,
    )

    if post.author_id != request.user.id:
        messages.error(request, "본인이 작성한 자료만 수정할 수 있습니다.")
        return redirect("board:post_detail", post_id=post.id)

    errors = {}

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        files = request.FILES.getlist("files")
        delete_ids = request.POST.getlist("delete_attachments")

        if not title:
            errors["title"] = "제목을 입력하세요."
        elif len(title) > 100:
            errors["title"] = "제목은 100자 이내로 입력하세요."

        if not content:
            errors["content"] = "내용을 입력하세요."

        file_errors = validate_uploaded_files(files)
        if file_errors:
            errors["files"] = " ".join(file_errors)

        if not errors:
            with transaction.atomic():
                post.title = title
                post.content = content
                post.save(update_fields=["title", "content", "updated_at"])

                attachments = list(post.attachments.filter(id__in=delete_ids))
                file_names = [attachment.file.name for attachment in attachments]
                storage = post.attachments.model._meta.get_field("file").storage

                with transaction.atomic():
                    post.title = title
                    post.content = content
                    post.save(update_fields=["title", "content", "updated_at"])

                    post.attachments.filter(id__in=delete_ids).delete()

                    for uploaded_file in files:
                        Attachment.objects.create(
                            post=post,
                            file=uploaded_file,
                            original_name=uploaded_file.name,
                        )

                    transaction.on_commit(
                        lambda: [
                            storage.delete(file_name)
                            for file_name in file_names
                        ]
                    )

            messages.success(request, "자료가 수정되었습니다.")
            return redirect("board:post_detail", post_id=post.id)

        return render(
            request,
            "board/post_form.html",
            {
                "mode": "update",
                "post": post,
                "errors": errors,
                "title": title,
                "content": content,
            },
        )

    return render(
        request,
        "board/post_form.html",
        {
            "mode": "update", 
            "post": post,
            "title": post.title,
            "content": post.content,
            "errors": {}
        },
    )


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(
        Post.objects.prefetch_related("attachments"),
        pk=post_id,
    )

    if post.author_id != request.user.id:
        messages.error(request, "본인이 작성한 자료만 삭제할 수 있습니다.")
        return redirect("board:post_detail", post_id=post.id)

    if request.method == "POST":
        attachments = list(post.attachments.all())

        # DB 레코드가 삭제된 후 실제 파일을 삭제하기 위해
        # 파일 저장소와 파일 경로를 미리 보관
        file_infos = [
            (attachment.file.storage, attachment.file.name)
            for attachment in attachments
            if attachment.file
        ]

        with transaction.atomic():
            post.delete()

            # DB 트랜잭션이 정상적으로 커밋된 뒤 실행
            transaction.on_commit(
                lambda: [
                    storage.delete(file_name)
                    for storage, file_name in file_infos
                ]
            )

        messages.success(request, "자료가 삭제되었습니다.")
        return redirect("board:post_list")

    return render(
        request,
        "board/post_confirm_delete.html",
        {"post": post},
    )


@login_required
def attachment_download(request, attachment_id):
    attachment = get_object_or_404(Attachment, pk=attachment_id)

    try:
        file_handle = attachment.file.open("rb")
    except FileNotFoundError as exc:
        raise Http404("첨부파일을 찾을 수 없습니다.") from exc

    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=attachment.original_name,
    )


def signin(request):
    if request.user.is_authenticated:
        return redirect("board:post_list")

    errors = {}
    username = ""
    next_url = request.GET.get("next", "")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        next_url = request.POST.get("next", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:
            errors["login"] = "아이디 또는 비밀번호를 확인하세요."
        else:
            login(request, user)
            messages.success(request, f"{user.username}님, 환영합니다.")

            if next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)

            return redirect("board:post_list")

    return render(
        request,
        "board/signin.html",
        {
            "errors": errors,
            "username": username,
            "next": next_url,
        },
    )


@require_POST
def signout(request):
    logout(request)
    messages.success(request, "로그아웃되었습니다.")
    return redirect("board:post_list")


def signup(request):
    if request.user.is_authenticated:
        return redirect("board:post_list")

    errors = {}
    username = ""

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if not username:
            errors["username"] = "아이디를 입력하세요."
        elif User.objects.filter(username=username).exists():
            errors["username"] = "이미 사용 중인 아이디입니다."

        # 복잡성 검증
        # if password1:
        #     try:
        #         validate_password(password1)
        #     except ValidationError as exc:
        #         errors["password1"] = " ".join(exc.messages)

        # 취약한 방식
        if len(password1) < 8:
            errors["password1"] = "비밀번호는 8자 이상 입력하세요."

        if password1 != password2:
            errors["password2"] = "비밀번호가 일치하지 않습니다."

        if not errors:
            try:
                user = User.objects.create_user(
                    username=username,
                    password=password1,
                )
            except IntegrityError:
                errors["username"] = "이미 사용 중인 아이디입니다."
            else:
                login(request, user)
                messages.success(request, "회원가입이 완료되었습니다.")
                return redirect("board:post_list")

    return render(
        request,
        "board/signup.html",
        {"errors": errors, "username": username},
    )
