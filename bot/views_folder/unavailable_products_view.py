from rest_framework.decorators import api_view
from rest_framework.response import Response
from restaurant_app.models.product import Product
from ..serializers import ProductSerializer

@api_view(['GET'])
def api_unavailable_products(request):
    unavailable_products = Product.objects.filter(is_available=False, show_in_menu=True)
    serializer = ProductSerializer(unavailable_products, many=True)
    return Response(serializer.data)
