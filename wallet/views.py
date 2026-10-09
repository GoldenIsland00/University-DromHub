import uuid
from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from accounts.permissions import student_required
from core.models import SystemSettings, Notification
from .forms import ChargeForm
from .models import PaymentRequest, Transaction


@student_required
def wallet_view(request):
    wallet = request.user.wallet
    transactions = wallet.transactions.all()[:50]
    cfg = SystemSettings.get()
    form = ChargeForm()

    if request.method == 'POST':
        if not cfg.allow_student_charge:
            messages.error(request, _('شارژ آنلاین در حال حاضر غیرفعال است. با مدیریت تماس بگیرید.'))
            return redirect('wallet:wallet')
        form = ChargeForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            authority = uuid.uuid4().hex
            PaymentRequest.objects.create(
                user=request.user,
                amount=amount,
                authority=authority,
                gateway='mock' if cfg.mock_payment_enabled else 'pending_gateway',
            )
            return redirect('wallet:pay_mock', authority=authority)

    return render(request, 'wallet/wallet.html', {
        'wallet': wallet,
        'transactions': transactions,
        'form': form,
        'allow_charge': cfg.allow_student_charge,
    })


@student_required
def pay_mock(request, authority):
    """صفحه شبیه‌ساز درگاه پرداخت."""
    pr = get_object_or_404(PaymentRequest, authority=authority, user=request.user)
    if pr.status == PaymentRequest.Status.SUCCESS:
        messages.info(request, _('این پرداخت قبلاً انجام شده است.'))
        return redirect('wallet:wallet')
    return render(request, 'wallet/pay_mock.html', {'payment': pr})


@student_required
@require_POST
def pay_mock_confirm(request, authority):
    pr = get_object_or_404(PaymentRequest, authority=authority, user=request.user)
    if pr.status != PaymentRequest.Status.PENDING:
        messages.error(request, _('وضعیت این درخواست قابل تغییر نیست.'))
        return redirect('wallet:wallet')

    action = request.POST.get('action')
    if action == 'success':
        pr.status = PaymentRequest.Status.SUCCESS
        pr.paid_at = timezone.now()
        pr.save(update_fields=['status', 'paid_at'])
        request.user.wallet.deposit(
            pr.amount,
            description=_('شارژ آنلاین — %(a)s') % {'a': pr.authority[:8]},
            performed_by=request.user,
            transaction_type=Transaction.Type.CHARGE,
        )
        Notification.notify(
            request.user, _('شارژ موفق'),
            _('مبلغ %(a)s تومان به کیف پول اضافه شد.') % {'a': f'{pr.amount:,.0f}'},
            kind='wallet', link='/wallet/',
        )
        messages.success(request, _('پرداخت موفق — کیف پول شارژ شد.'))
    else:
        pr.status = PaymentRequest.Status.CANCELLED
        pr.save(update_fields=['status'])
        messages.warning(request, _('پرداخت لغو شد.'))
    return redirect('wallet:wallet')
