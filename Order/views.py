from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from .Serializers import OrderSerializer,OrderStatusUpdateSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .Signals import status_updated

class OrderView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderUpdateView(APIView):
    def patch(self, request, order_id):
        print('data is getting updated')
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order does not exist'}, status=status.HTTP_404_NOT_FOUND)

        #chekcing if the current status and new status from the email is same
        old_status = order.status
        new_status = request.data.get('status')
        if old_status == new_status:
            return Response({'error': 'Status already updated'}, status=status.HTTP_204_NO_CONTENT)
        

        serializer = OrderStatusUpdateSerializer(order, data={'status':new_status}, partial=True)

        if serializer.is_valid():
            serializer.save()
            new_status = serializer.validated_data.get('status')
            if old_status is None and new_status == 'received':
                # Send signal with next status 'processing'
                status_updated.send(sender=Order, instance=order, new_status='processing')
                return Response(serializer.data, status=status.HTTP_200_OK)

            if new_status != old_status and new_status not in ['delivered', 'cancelled']:
                next_status_map = {
                    'processing': 'dispatched',
                    'dispatched': 'delivered',
                }
                next_status = next_status_map.get(new_status)
                if next_status:
                    # send the signal
                    status_updated.send(sender=Order, instance=order, new_status=next_status)
                    return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
