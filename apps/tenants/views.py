from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import PersonalAccount

from .forms import TenantAccountAssignmentForm, TenantForm
from .models import Tenant, TenantAccountAssignment


@login_required
def tenant_list(request):
    q = request.GET.get("q", "").strip()
    tenants = Tenant.objects.order_by("last_name", "first_name")
    if q:
        tenants = tenants.filter(
            Q(last_name__icontains=q) | Q(first_name__icontains=q) | Q(middle_name__icontains=q)
            | Q(phone__icontains=q) | Q(email__icontains=q) | Q(passport_number__icontains=q)
        )
    return render(request, "tenants/list.html", {"tenants": tenants, "q": q})


@login_required
def tenant_detail(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk)
    assignments = tenant.account_assignments.select_related(
        "account", "account__unit__house__street"
    ).order_by("-start_date")
    return render(request, "tenants/detail.html", {"tenant": tenant, "assignments": assignments})


@login_required
def tenant_create(request):
    if request.method == "POST":
        form = TenantForm(request.POST)
        if form.is_valid():
            tenant = form.save()
            messages.success(request, f"Наниматель {tenant.full_name} добавлен.")
            return redirect("tenants:detail", pk=tenant.pk)
    else:
        form = TenantForm()
    return render(request, "tenants/form.html", {"form": form, "title": "Новый наниматель"})


@login_required
def tenant_update(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk)
    if request.method == "POST":
        form = TenantForm(request.POST, instance=tenant)
        if form.is_valid():
            form.save()
            messages.success(request, "Данные нанимателя обновлены.")
            return redirect("tenants:detail", pk=tenant.pk)
    else:
        form = TenantForm(instance=tenant)
    return render(request, "tenants/form.html", {"form": form, "title": f"Редактирование — {tenant}"})


@login_required
def assignment_create(request, account_pk):
    account = get_object_or_404(PersonalAccount, pk=account_pk)
    if request.method == "POST":
        form = TenantAccountAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.account = account
            assignment.save()
            messages.success(request, f"{assignment.tenant} назначен(а) на ЛС №{account.number}.")
            return redirect("accounts:detail", pk=account.pk)
    else:
        form = TenantAccountAssignmentForm(initial={"start_date": date.today()})
    return render(request, "tenants/assignment_form.html", {
        "form": form, "account": account,
    })


@login_required
def assignment_end(request, pk):
    assignment = get_object_or_404(TenantAccountAssignment, pk=pk)
    if request.method == "POST":
        assignment.end_date = date.today()
        assignment.save(update_fields=["end_date"])
        messages.success(request, "Назначение завершено.")
    return redirect("accounts:detail", pk=assignment.account_id)
