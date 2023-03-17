from django.shortcuts import render
from .models import *
from django.http import JsonResponse

import json
import datetime


# Create your views here.
def login(request):
    if request.method == "GET":
        return render(request, 'store/login.html')
    if request.method == "POST":
        return


def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        total_item = order.get_total_item
    else:
        items = []
        order = {"get_total_item": 0, "get_total_payment": 0, "shipping": False}
        total_item = order['get_total_item']
    products = Product.objects.all()
    context = {"products": products, "total_item": total_item}
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        total_item = order.get_total_item
    else:
        items = []
        order = {"get_total_item": 0, "get_total_payment": 0, "shipping": False}
        total_item = order['get_total_item']
    context = {"items": items, "order": order, "total_item": total_item}
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        total_item = order.get_total_item
    else:
        items = []
        order = {"get_total_item": 0, "get_total_payment": 0, "shipping": False}
        total_item = order['get_total_item']
    context = {"items": items, "order": order, "total_item": total_item}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productID = data['productID']
    action = data['action']
    # print('Action: ', action)
    # print('ProductID: ', productID)

    customer = request.user.customer
    product = Product.objects.get(id=productID)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = orderItem.quantity + 1
    elif action == 'remove':
        orderItem.quantity = orderItem.quantity - 1
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was updated', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    # print("Data: ", request.body)
    data = json.loads(request.body)

    if request.user.is_authenticated:
        print("User is logged in...")
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == float(order.get_total_payment):
            order.complete = True
        order.save()

        if order.shipping:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
                date_added=datetime.datetime.now()
            )
    else:
        print("User is not logged in...")
    return JsonResponse("Payment submitted...", safe=False)
