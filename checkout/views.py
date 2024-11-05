from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from order.basket import BasketAndOrderRedisAdapter
from django.http import HttpRequest
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from authentication.permissions import ValidateBasket


@api_view(["GET", "POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([ValidateBasket])
def payment_gateway(request: HttpRequest):
    """
    Handles payments by interacting with the user's basket and processing payment details.

    Args:
        request (HttpRequest): The HTTP request object containing user data.

    Returns:
        Response: JSON response indicating the success or failure of the payment.
    """
    basket = BasketAndOrderRedisAdapter(request)

    if request.method == "POST":

        card_number = request.data.get("card_number")
        cvv2 = request.data.get("cvv2")
        expiration_date = request.data.get("exp_date")
        password = request.data.get("password")

        for item in [card_number, cvv2, expiration_date, password]:
            if item is None:
                basket.set_payment_information(message="fail")
                return Response({"message": "Please enter all information"})

        basket.set_payment_information(message="success")

        basket.create_order()
        return Response({"message": "Payment was successful!"})

    else:

        return Response({"message": f"Pay {basket.display_basket().get('price_after_discount', 0)}"})
