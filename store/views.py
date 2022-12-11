from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from .models import *
from django.http import JsonResponse
import json
import datetime 
from .utils import cookieCart,cartData,guestOrder
from django.contrib import messages
from django.contrib.auth.models import User,auth


def store(request):
    data=cartData(request)
    cartItems=data['cartItems']
    products=Product.objects.all()
    context={'products':products,'cartItems':cartItems}
    return render(request,'store/store.html',context)

def cart(request):
    data=cartData(request)
    cartItems=data['cartItems']
    order=data['order']
    items=data['items']
    context={'items':items,'order':order,'cartItems':cartItems}
    return render(request,'store/cart.html',context)

def checkout(request):
    data=cartData(request)
    cartItems=data['cartItems']
    order=data['order']
    items=data['items']
    if len(items)==0:
        messages.warning(request,'you have not selected any item')
        return redirect('store') 
    context={'items':items,'order':order,'cartItems':cartItems}
    return render(request,'store/checkout.html',context)

def updateItem(request):
    data=json.loads(request.body)
    productID=data['productID']
    action=data['action']
    print('productID:',productID)
    print('action:',action)
    customer=request.user.customer
    product=Product.objects.get(id=productID)
    order,created=Order.objects.get_or_create(customer=customer,complete=False)
    orderItem,created=OrderItem.objects.get_or_create(order=order,product=product)
    if action=='add':
        orderItem.quantity=(orderItem.quantity+1)
    elif action=='remove':
        orderItem.quantity=(orderItem.quantity-1)
    orderItem.save()    
    if orderItem.quantity <=0:
        orderItem.delete()
    return JsonResponse('item was added',safe=False)

def processOrder(request):
    transaction_id=datetime.datetime.now().timestamp()
    data=json.loads(request.body)
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
    else:
        customer,order=guestOrder(request,data)  
    total=float(data['form']['total'])
    order.transaction_id=transaction_id
    if total==float(order.get_cart_total):
        order.complete=True
        messages.info(request,f'Your Transaction ID is {transaction_id} ')
    order.save()

    if order.shipping==True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('payment submitted..',safe=False)

def contact(request):
    if request.method=='POST':
        name=request.POST['name']
        email=request.POST['email']
        phone=request.POST['phone']
        content=request.POST['content']
        contact=Contact(name=name,email=email,phone=phone,content=content)
        contact.save()
        messages.success(request, 'Your details saved')
        return redirect('store')
    return render(request,'store/contact.html')


def register(request):
    if request.method=='POST':
        firstname=request.POST['first_name']
        lastname=request.POST['last_name']
        user=request.POST['username']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']
        if pass1==pass2:
            if User.objects.filter(username=user).exists():
                messages.info(request,'already exists username')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request,'already exists email')
                return redirect('register')
            else:
                user=User.objects.create_user(first_name=firstname,last_name=lastname,username=user,email=email,password=pass1)
                messages.info(request,'user is registered')
                Customer.objects.create(user=user,email=email,name=firstname)
                
                return redirect('login')
    else:
        return render(request,'store/register.html')        

def view(request,id):
    data=cartData(request)
    cartItems=data['cartItems']
    product=Product.objects.filter(id=id)
    context={'products':product,'cartItems':cartItems}
    return render(request,'store/view.html',context)

def login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user= auth.authenticate(username=username,password=password)
        if user is not None :
            auth.login(request,user)
            messages.info(request,'login succefully')
            return redirect('store')
        else:
            messages.info(request,'info not correct')
            return redirect('login')
    else:
        return render(request,'store/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request,"logout succefully")
    return redirect('store')        



def search(request):
    keyword=request.POST['search']
    data=cartData(request)
    cartItems=data['cartItems']
    if keyword:
        product=Product.objects.filter(name__icontains=keyword)   
    context={'query':keyword,'products':product,'cartItems':cartItems}
    return render(request,'store/search.html',context)

    
   