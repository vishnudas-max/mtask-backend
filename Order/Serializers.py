from rest_framework.serializers import ModelSerializer
from .models  import Order

class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields ='__all__'

class OrderStatusUpdateSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']  