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
    """
    A viewset for managing basket operations including listing, adding, updating,
    and deleting items in the basket, as well as applying discount codes.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwner]
    user_model = get_user_model()

    def list(self, request: HttpRequest, *args, **kwargs):
        """
        Retrieves and displays the current basket contents.

        Returns:
            Response: A JSON response with the basket details if it exists, or
            a message indicating no basket is present.
        """
        basket = BasketAndOrderRedisAdapter(request=request)
        if basket.check_if_basket_exists():
            return Response({"basket": basket.display_basket()}, status=status.HTTP_200_OK)
        return Response({"message": "You don't have any basket!"}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        """
        Adds a product to the basket based on provided product_id and quantity.

        Returns:
            Response: A message confirming the addition or an error message.
        """
        product = request.POST.get("product_id")
        quantity = request.POST.get("quantity")

        if not product or not quantity:
            return Response({"message": "product_id and quantity must be specified."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not str(product).isnumeric() or not str(quantity).isnumeric():
            return Response({"message": "Enter valid inputs for product_id and quantity."},
                            status=status.HTTP_400_BAD_REQUEST)

        basket = BasketAndOrderRedisAdapter(request=request, product=product, quantity=quantity)
        try:
            basket.add_to_basket()
            return Response({"message": "Product added to basket."}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Deletes a product from the basket based on its ID.

        Args:
            pk (str): Primary key of the product to delete.

        Returns:
            Response: A message confirming deletion or an error message if the product was not found.
        """
        assert str(pk).isnumeric(), "Please enter a valid product ID."
        basket = BasketAndOrderRedisAdapter(request=request, product=pk)
        try:
            basket.delete_from_basket()
            return Response({"message": "Product was deleted successfully!"}, status=status.HTTP_202_ACCEPTED)
        except ValueError as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, *args, **kwargs):
        """
        Updates the quantity of a product in the basket.

        Returns:
            Response: A message confirming the update or an error message if unsuccessful.
        """
        product = request.data.get('product')
        quantity = request.data.get('quantity')
        assert str(quantity).isnumeric(), 'Please enter a valid input for quantity.'
        basket = BasketAndOrderRedisAdapter(request=request, product=product, quantity=quantity)
        try:
            basket.update_basket()
            return Response({"message": "Basket updated successfully."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def set_discount_code(self, request: HttpRequest, *args, **kwargs):
        """
        Applies a discount code to the basket.

        Returns:
            Response: A message confirming successful application or an error if the code is invalid or already used.
        """
        code = request.POST.get("code")
        basket = BasketAndOrderRedisAdapter(request=request)
        try:
            basket.apply_discount(code=code)
            return Response({"message": "Discount successfully applied!"})
        except ValueError:
            return Response({"message": "You have already used this code."})
        except RuntimeError:
            return Response({"message": "Invalid code!"})

    @action(detail=False, methods=['get'])
    def get_discounted_price(self, request, *args, **kwargs):
        """
        Retrieves the basket's contents with applied discounts (if any).

        Returns:
            Response: A JSON response with the basket details including the discounted prices.
        """
        basket = BasketAndOrderRedisAdapter(request=request)
        return Response({"basket": basket.display_basket()})


class BasketSubmitViewSet(ViewSet):
    """
    A viewset to manage the submission of baskets with user address handling.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwner]

    def list(self, request, *args, **kwargs):
        """
        Displays the current basket contents.

        Returns:
            Response: A JSON response with the basket details.
        """
        basket = BasketAndOrderRedisAdapter(request=request)
        return Response({"basket": basket.display_basket()}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Associates an address with the current basket for order submission.

        Returns:
            Response: A message confirming address association or an error if unauthorized.
        """
        address_id = request.POST.get("address_id")
        try:
            address = Address.objects.get(id=int(address_id))
            basket = BasketAndOrderRedisAdapter(request=request, address=str(address_id))
            if request.user.id == address.customer.id:
                basket.add_or_update_address()
                return Response({"message": "Address added successfully."}, status=status.HTTP_201_CREATED)
            return Response({"message": "You are not the address owner!"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, *args, **kwargs):
        """
        Updates the address associated with the current basket.

        Returns:
            Response: A message confirming the update or an error if unsuccessful.
        """
        address_id = request.data.get("address_id")
        assert str(address_id).isnumeric(), 'Please enter a valid address ID.'
        basket = BasketAndOrderRedisAdapter(request=request, address=address_id)
        try:
            basket.update_basket()
            return Response({"message": "Basket updated successfully."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
