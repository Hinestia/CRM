from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.accounts.models import AccountStatus, PersonalAccount
from apps.billing.models import Charge
from apps.contracts.models import Contract
from apps.debts.services import debtor_accounts_queryset


@login_required
def dashboard(request):
    today = date.today()
    context = {
        "accounts_count": PersonalAccount.objects.filter(status=AccountStatus.ACTIVE).count(),
        "debtors_count": debtor_accounts_queryset().count(),
        "expiring_contracts": Contract.objects.filter(
            end_date__isnull=False,
            end_date__gte=today,
            end_date__lte=today + timedelta(days=30),
        ).select_related("account").order_by("end_date")[:10],
        "latest_charges": Charge.objects.select_related("account").order_by("-generated_at")[:10],
    }
    return render(request, "dashboard.html", context)
