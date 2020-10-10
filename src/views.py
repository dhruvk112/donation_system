from django.shortcuts import render
import razorpay
from .models import Donate
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Create your views here.
def home(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        amount = int(request.POST.get('amount')) * 100
        email = request.POST.get('email')
        client = razorpay.Client(auth = ("rzp_test_8WVJYezFus1ddM", "b0nLzSVn2FKzhkkdZXPTWGqO"))
        payment = client.order.create({'amount':amount, 'currency':'INR', 'payment_capture':'1'})
        donate = Donate(name=name, amount=amount, email=email, payment_id=payment['id'])
        donate.save()
        return render(request,'index.html',context={'payment':payment})
    return render(request,'index.html')

@csrf_exempt
def success(request):
    if request.method == 'POST':
        donation_details = request.POST
        for key, val in donation_details.items():
            if key == "razorpay_order_id":
                order_id = val
                break
        user = Donate.objects.filter(payment_id=order_id).first()
        user.paid = True
        user.save()
        amount = int(Donate.objects.filter(payment_id=order_id).first().amount) / 100
        msg_plain = render_to_string('email.txt')
        msg_html = render_to_string('success.html',context={'amount':amount})

        send_mail("Your donation has been received.", msg_plain, settings.EMAIL_HOST_USER, 
                [user.email], html_message = msg_html)

    return render(request,'success.html',context={'amount':amount})

