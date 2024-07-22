import json

from dateutil import parser
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import timezone

from .models import Recipient, Tag, Transaction, TransactionToTag
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
    # Grab all the data from the insert form
    name = request.POST.get("name", "")
    description = request.POST.get("description", "")

    amount = request.POST.get("amount", 0)

    day = request.POST.get("date_0", "2024-07-16")
    time = request.POST.get("date_1", "17:13:22.929875+00:00")
    currency = request.POST.get("currency", "EUR")

    date = parser.parse(day + " " + time)

    receiver = request.POST.get("receiver", "")
    sender = request.POST.get("sender", "")

    # Since these are still seperate checks, if it was give, query for it
    if receiver:
        receiver = Recipient.objects.get_or_create(name=receiver)[0]
    else:
        receiver = None

    if sender:
        sender = Recipient.objects.get_or_create(name=sender)[0]
    else:
        sender = None

    tag = request.POST.get("tag", "")

    # Create the transaction
    transaction = Transaction.objects.create(name=name, description=description, amount=amount, date=date, currency=currency, receiver=receiver, sender=sender)
    TransactionToTag.objects.create(transaction=transaction, tag=Tag.objects.get_or_create(tag=tag)[0])

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
        try:
            tag = TransactionToTag.objects.get(transaction = trans).tag
        except:
            tag = None
        context['transactions'].append({
            'name': trans.name,
            'amount': trans.amount,
            'description': trans.description,
            'currency': trans.currency,
            'date': trans.date,
            'direction': "positive" if trans.amount >= 0 else "negative",
            'sender': trans.sender.name if trans.sender else None,
            'receiver': trans.receiver.name if trans.receiver else None,
            'tag': tag.tag if tag else None,
            'tag_color': tag.colour if tag else None
        })
        amount_tuple = trans.amount.as_integer_ratio()

        sum += amount_tuple[0] / amount_tuple[1]
        cummulative_sum.append(sum)


    context['sum'] = sum
    if len(db_transactions) > 0:
        context['sum_currency'] = db_transactions[0].currency
    else:
        context['sum_currency'] = "EUR"
    context['sum_state'] = "positive" if sum >= 0 else "negative"
    context['cummulative_sum'] = json.dumps(cummulative_sum)

    transaction_form = NewTransactionForm()
    transaction_form.date = timezone.now()
    context['form'] = transaction_form

    return render(request, "transactions/dashboard.html", context)