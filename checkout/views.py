import uuid
from uuid import uuid3

from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from order.basket import BasketRedisAdapter

from django.http import HttpRequest
from rest_framework.decorators import api_view,authentication_classes


@api_view(["GET", 'POST'])
@authentication_classes([JWTAuthentication])
def payment_gateway(request: HttpRequest):
    basket = BasketRedisAdapter(request)
    if request.method == "POST":
        card_number = request.POST.get("card_number")
        cvv2 = request.POST.get("cvv2")
        expiration_date = request.POST.get("exp_date")
        password = request.POST.get("password")
        for i in [card_number, cvv2, expiration_date, password]:
            if i == None:
                basket.set_payment_information(message="fail")
                return Response({"message":"please enter all information"})
            basket.set_payment_information(message="success")
            return Response({"message": "payment was successful!"})
    else:
        print(basket.payment_information)
        return Response({"message": "please enter your information"})
