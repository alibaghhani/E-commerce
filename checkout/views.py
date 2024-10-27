from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from order.basket import BasketAndOrderRedisAdapter
from django.http import HttpRequest
from rest_framework.decorators import api_view, authentication_classes


@api_view(["GET", 'POST'])
@authentication_classes([JWTAuthentication])
def payment_gateway(request: HttpRequest):
    basket = BasketAndOrderRedisAdapter(request)
    if request.method == "POST":
        card_number = request.POST.get("card_number")
        cvv2 = request.POST.get("cvv2")
        expiration_date = request.POST.get("exp_date")
        password = request.POST.get("password")
        for item in [card_number, cvv2, expiration_date, password]:
            if item == None:
                basket.set_payment_information(message="fail")
                return Response({"message": "please enter all information"})
            basket.set_payment_information(message="success")
            return Response({"message": "payment was successful!"})
    else:
        return Response({"message": f"pay {basket.total_price}"})
