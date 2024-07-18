import json

from dateutil import parser
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import timezone

from .models import Transaction
from .forms import NewTransactionForm

# Create your views here.
def dashboard(request):
    if request.method == "GET":
        return dashboard_handle_get(request)
    elif request.method == "POST":
        return dashboard_handle_post(request)
    else:
        return HttpResponseRedirect("/")

def dashboard_handle_post(request):
    name = request.POST.get("name", "")
    description = request.POST.get("description", "")

    amount = request.POST.get("amount", 0)

    day = request.POST.get("date_0", "2024-07-16")
    time = request.POST.get("date_1", "17:13:22.929875+00:00")
    currency = request.POST.get("currency", "EUR")

    date = parser.parse(day + " " + time)

    Transaction.objects.create(name=name, description=description, amount=amount, date=date, currency=currency)

    return HttpResponseRedirect("/")

def dashboard_handle_get(request):
    db_transactions = Transaction.objects.all().order_by("-date")
    context = {
        "transactions": [
        ]
    }

    sum = 0
    cummulative_sum = [0]
    for trans in db_transactions:
        context['transactions'].append({
            'name': trans.name,
            'amount': trans.amount,
            'description': trans.description,
            'currency': trans.currency,
            'date': trans.date,
            'direction': "positive" if trans.amount >= 0 else "negative"
        })
        amount_tuple = trans.amount.as_integer_ratio()

        sum += amount_tuple[0] / amount_tuple[1]
        cummulative_sum.append(sum)


    context['sum'] = sum
    context['sum_currency'] = db_transactions[0].currency
    context['sum_state'] = "positive" if sum >= 0 else "negative"
    context['cummulative_sum'] = json.dumps(cummulative_sum)

    transaction_form = NewTransactionForm()
    transaction_form.date = timezone.now()
    context['form'] = transaction_form

    return render(request, "transactions/dashboard.html", context)