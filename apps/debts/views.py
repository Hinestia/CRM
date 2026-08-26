from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import PenaltySettingsForm
from .models import PenaltySettings
from .services import accrue_penalties, debtor_accounts_queryset


@login_required
def debtor_list(request):
    accounts = debtor_accounts_queryset().select_related("unit__house__street")
    settings_obj = PenaltySettings.objects.filter(is_active=True).first()
    return render(request, "debts/list.html", {"accounts": accounts, "settings_obj": settings_obj})


@login_required
@require_POST
def accrue_now(request):
    result = accrue_penalties()
    messages.success(request, f"Пеня начислена по {len(result)} лицевым счетам.")
    return redirect("debts:list")


@login_required
def penalty_settings_edit(request):
    settings_obj = PenaltySettings.objects.filter(is_active=True).first()
    if request.method == "POST":
        form = PenaltySettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.is_active = True
            obj.save()
            messages.success(request, "Настройки пени сохранены.")
            return redirect("debts:list")
    else:
        form = PenaltySettingsForm(instance=settings_obj)
    return render(request, "debts/settings_form.html", {"form": form})
