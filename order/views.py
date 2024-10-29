from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from authentication.models import Address
from authentication.permissions import IsOwner
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from order.basket import BasketAndOrderRedisAdapter


class BasketViewSet(ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwner]
    user_model = get_user_model()

    def list(self, request: HttpRequest, *args, **kwargs):
        basket = BasketAndOrderRedisAdapter(request=request)
        if basket.check_if_basket_exists():
            return Response({"basket": basket.display_basket()}, status=status.HTTP_200_OK)
        return Response({"message": "you dont have any basket!"}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        product = request.POST.get("product_id")
        quantity = request.POST.get("quantity")

        if not product or not quantity:
            return Response({"message": "product_id and quantity must be specified."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not str(product).isnumeric() or not str(quantity).isnumeric():
            return Response({"message": "enter valid inputs for product_id and quantity."},
                            status=status.HTTP_400_BAD_REQUEST)

        basket = BasketAndOrderRedisAdapter(request=request, product=product, quantity=quantity)

        try:
            basket.add_to_basket()
            return Response({"message": "Product added to basket."}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        assert str(pk).isnumeric(), "please enter a valid id"
        basket = BasketAndOrderRedisAdapter(request=request, product=pk)
        try:
            basket.delete_from_basket()
            return Response({"product was deleted successfully!"}, status=status.HTTP_202_ACCEPTED)
        except ValueError as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, *args, **kwargs):
        product = request.data.get('product')
        quantity = request.data.get('quantity')
        assert str(quantity).isnumeric(), 'please enter a valid input'
        basket = BasketAndOrderRedisAdapter(request=request, product=product, quantity=quantity)
        try:
            basket.update_basket()
            return Response({"message": "basket updated successfully"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def set_discount_code(self, request: HttpRequest, *args, **kwargs):
        code = request.POST.get("code")
        basket = BasketAndOrderRedisAdapter(request=request)
        try:
            basket.apply_discount(code=code)
            return Response({"message": "discount successfully applied!"})
        except ValueError:
            return Response({"message": "You have already used this code"})
        except RuntimeError:
            return Response({"message": "Invalid code!"})

    @action(detail=False, methods=['get'])
    def get_discounted_price(self, request, *args, **kwargs):
        basket = BasketAndOrderRedisAdapter(request=request)
        return Response({"basket": basket.display_basket()})


class BasketSubmitViewSet(ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwner]

    def list(self, reqeust, *args, **kwargs):
        basket = BasketAndOrderRedisAdapter(request=reqeust)
        return Response({"basket": basket.display_basket()}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        address_id = request.POST.get("address_id")
        try:
            address = Address.objects.get(id=int(address_id))
            basket = BasketAndOrderRedisAdapter(request=request, address=str(address_id))
            if request.user.id == address.costumer.id:
                basket.add_or_update_address()
                return Response({"message": "address added successfully"}, status=status.HTTP_403_FORBIDDEN)
            return Response({"message": "you are not the address's owner!"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, *args, **kwargs):
        address_id = request.data.get("address_id")
        assert str(address_id).isnumeric(), 'please enter a valid input'
        basket = BasketAndOrderRedisAdapter(request=request, address=address_id)
        try:
            basket.update_basket()
            return Response({"message": "basket updated successfully"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
