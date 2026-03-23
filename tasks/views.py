from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, Value, IntegerField
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import SignUpForm, TaskForm
from .models import Task


def _get_user_task_or_404(user, pk: int) -> Task:
    return get_object_or_404(Task, pk=pk, user=user)

def home(request):
    if request.user.is_authenticated:
        return redirect("tasks:task_list")
    return render(request, "tasks/home.html")

@login_required
def task_list(request):
    query = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip()
    due = (request.GET.get("due") or "").strip()
    sort = (request.GET.get("sort") or "new").strip()


    per_page_raw = (request.GET.get("per_page") or "10").strip()
    try:
        per_page = int(per_page_raw)
    except ValueError:
        per_page = 10
    if per_page not in (2, 10, 20, 50):
        per_page = 10

    qs = Task.objects.filter(user=request.user, deleted_at__isnull=True)

    if query:
        qs = qs.filter(Q(title__icontains=query) | Q(content__icontains=query))

    if status == "done":
        qs = qs.filter(is_done=True)
    elif status == "pending":
        qs = qs.filter(is_done=False)

    today = timezone.localdate()

    if due == "overdue":
        qs = qs.filter(is_done=False, due_date__lt=today)
    elif due == "today":
        qs = qs.filter(due_date=today)
    elif due == "week":
        qs = qs.filter(due_date__gte=today, due_date__lte=today + timedelta(days=7))


    if sort == "old":
        qs = qs.order_by("created_at")
    elif sort == "priority":
        qs = qs.order_by("-priority", "-created_at")
    elif sort == "due":

        qs = qs.annotate(
            due_is_null=Case(
                When(due_date__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by("due_is_null", "due_date", "-priority", "-created_at")
    else:
        qs = qs.order_by("-created_at")


    total_pending = Task.objects.filter(
        user=request.user,
        deleted_at__isnull=True,
        is_done=False,
    ).count()

    total_done = Task.objects.filter(
        user=request.user,
        deleted_at__isnull=True,
        is_done=True,
    ).count()

    total_overdue = Task.objects.filter(
        user=request.user,
        deleted_at__isnull=True,
        is_done=False,
        due_date__lt=today,
    ).count()


    paginator = Paginator(qs, 3)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "tasks/task_list.html",
        {
            "page_obj": page_obj,
            "tasks": page_obj.object_list,
            "query": query,
            "status": status,
            "due": due,
            "sort": sort,
            "per_page": per_page,
            "total_pending": total_pending,
            "total_done": total_done,
            "total_overdue": total_overdue,
        },
    )


@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, "Užduotis sukurta.")
            return redirect("tasks:task_list")
        messages.error(request, "Pataisyk klaidas formoje.")
    else:
        form = TaskForm()

    return render(request, "tasks/task_create.html", {"form": form})


@login_required
def task_edit(request, pk):
    task = _get_user_task_or_404(request.user, pk)
    if task.deleted_at:
        messages.error(request, "Ši užduotis yra šiukšlinėje. Pirma atstatyk.")
        return redirect("tasks:trash")

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Užduotis atnaujinta.")
            return redirect("tasks:task_list")
        messages.error(request, "Pataisyk klaidas formoje.")
    else:
        form = TaskForm(instance=task)

    return render(request, "tasks/task_edit.html", {"form": form, "task": task})


@login_required
def task_delete(request, pk):
    task = _get_user_task_or_404(request.user, pk)
    if request.method != "POST":
        return render(request, "tasks/task_confirm_delete.html", {"task": task})

    task.soft_delete()
    task.save(update_fields=["deleted_at"])
    messages.success(request, "Užduotis perkelta į šiukšlinę.")
    return redirect("tasks:task_list")


@login_required
@require_POST
def task_restore(request, pk):
    task = _get_user_task_or_404(request.user, pk)
    task.restore()
    task.save(update_fields=["deleted_at"])
    messages.success(request, "Užduotis atstatyta.")
    return redirect("tasks:trash")


@login_required
def trash(request):
    qs = Task.objects.filter(user=request.user, deleted_at__isnull=False).order_by("-deleted_at")
    return render(request, "tasks/trash.html", {"tasks": qs})


@login_required
@require_POST
def task_toggle(request, pk):
    task = _get_user_task_or_404(request.user, pk)
    if task.deleted_at:
        return JsonResponse({"ok": False, "error": "deleted"}, status=400)

    task.is_done = not task.is_done
    task.save(update_fields=["is_done"])

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "is_done": task.is_done})

    return redirect("tasks:task_list")


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Paskyra sukurta. Prisijungei.")
            return redirect("tasks:task_list")
        messages.error(request, "Pataisyk klaidas formoje.")
    else:
        form = SignUpForm()

    return render(request, "tasks/signup.html", {"form": form})

def csrf_failure(request, reason=""):
    messages.error(request, "Sesija pasikeitė. Atnaujink puslapį ir bandyk dar kartą.")
    return redirect("tasks:login")