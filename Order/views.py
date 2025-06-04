from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from .Serializers import OrderSerializer,OrderStatusUpdateSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Order

class OrderView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderUpdateView(APIView):

    def patch(self,request,order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({'error':'Order does not exist'},status=status.HTTP_404_NOT_FOUND)

        serializer = OrderStatusUpdateSerializer(order,data=request.data,partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
