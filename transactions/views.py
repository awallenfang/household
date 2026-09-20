import json

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.db import models
from django.contrib.auth.decorators import login_required, user_passes_test


from .models import Recipient, Tag, Transaction, TransactionToTag
from .forms import NewTransactionForm

staff_required = user_passes_test(lambda u: u.is_staff)

@login_required
@staff_required
def dashboard(request):
    if request.method == "GET":
        return dashboard_handle_get(request)
    if request.method == "POST":
        return dashboard_handle_post(request)

    return HttpResponseRedirect("/")

@login_required
@staff_required
def dashboard_handle_post(request):
    form = NewTransactionForm(request.POST)
    if not form.is_valid():
        return HttpResponseRedirect("/")
    data = form.cleaned_data

    name = data["name"]
    description = data.get("description", "")
    amount = data.get("amount", 0)
    date = data.get("date") or timezone.now()
    currency = data.get("currency", "EUR")

    receiver_name = (data.get("receiver") or "").lower()
    sender_name = (data.get("sender") or "").lower()

    # Since these are still seperate checks, if it was give, query for it
    if receiver_name:
        receiver = Recipient.objects.get_or_create(name=receiver_name[:100])[0]
    else:
        receiver = None

    if sender_name:
        sender = Recipient.objects.get_or_create(name=sender_name[:100])[0]
    else:
        sender = None

    tag_name = (request.POST.get("tag", "") or "")[:100]

    # Create the transaction
    transaction = Transaction.objects.create(name=name[:100], description=description[:500], amount=amount, date=date, currency=currency, receiver=receiver, sender=sender)
    if tag_name:
        tag_obj, _ = Tag.objects.get_or_create(tag=tag_name, defaults={"colour": "#000000"})
        TransactionToTag.objects.create(transaction=transaction, tag=tag_obj)

    return HttpResponseRedirect("/")

@login_required
@staff_required
def dashboard_handle_get(request):
    db_transactions = Transaction.objects.all().order_by("-date")
    context = {
        "transactions": [
        ]
    }


    summation = 0
    cummulative_sum = [0]
    for trans in db_transactions:
        try:
            tag = TransactionToTag.objects.get(transaction = trans).tag
        except TransactionToTag.DoesNotExist:
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

        summation += amount_tuple[0] / amount_tuple[1]
        cummulative_sum.append(summation)


    context['sum'] = summation
    if len(db_transactions) > 0:
        context['sum_currency'] = db_transactions[0].currency
    else:
        context['sum_currency'] = "EUR"
    context['sum_state'] = "text-bg-success" if summation >= 0 else "text-bg-danger"
    context['cummulative_sum'] = json.dumps(cummulative_sum)

    transaction_form = NewTransactionForm()
    transaction_form.date = timezone.now()
    context['form'] = transaction_form

    existing_recipient_names = get_all_elements_with_map(Recipient, lambda rec: rec.name)

    context['possible_recipients'] = existing_recipient_names

    return render(request, "transactions/dashboard_full.html", context)

# @login_required
# def recipient_page(request, recipient_name):
#     context = {
#         "transactions": []
#     }
#     # recipient_name = recipient_name.lower()
#     # recipient = Recipient()
#     # try:
#     #     recipient = Recipient.objects.get(name = recipient_name)
#     # except Recipient.DoesNotExist:
#     #     HttpResponseRedirect("/")

#     # received_transactions = Transaction.objects.filter(receiver = recipient.id) 
#     # sent_transactions = Transaction.objects.filter(sender=recipient.id)

#     return render(request, "transactions/recipient.html", context)




# Helper functions
def get_all_elements_with_map(model: models.Model, map_lambda):
    return [map_lambda(elem) for elem in model.objects.all()]
    # return list(map(map_lambda, list(model.objects.all())))