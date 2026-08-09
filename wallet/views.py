from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from .forms import ChargeForm
from .models import Transaction


@login_required
def wallet_view(request):
    wallet = request.user.wallet
    transactions = wallet.transactions.all()[:50]

    if request.method == 'POST':
        form = ChargeForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            # In real production: redirect to payment gateway
            # For demo we simulate successful charge
            wallet.deposit(amount, description=_('شارژ آنلاین (دمو)'), performed_by=request.user)
            messages.success(request, _('حساب شما با موفقیت شارژ شد.'))
            return redirect('wallet:wallet')
    else:
        form = ChargeForm()

    return render(request, 'wallet/wallet.html', {
        'wallet': wallet,
        'transactions': transactions,
        'form': form,
    })
