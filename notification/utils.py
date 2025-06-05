from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_notifications(order_id, status):
    """
    Function to send notifications to all connected WebSocket clients
    """
    channel_layer = get_channel_layer()
    print(f'Triggering notification: order_id={order_id}, status={status}')
    
    try:
        async_to_sync(channel_layer.group_send)(
            "notification",  # Group name
            {
                "type": "send_notification",  # This calls the send_notification method in consumer
                "order_id": order_id,
                "status": status
            }
        )
        print('Notification sent to channel layer successfully')
    except Exception as e:
        print(f'Error sending notification: {e}')
        
        
def send_notfication_to_add_data(order_id,customer_name,product_name,price,status=None):
    channel_layer= get_channel_layer()
    try:
        async_to_sync(channel_layer.group_send)(
            "notification",{
                "type":"add_order",
                "order_id":order_id,
                "product_name":product_name,
                "customer_name":customer_name,
                "price":price,
                "status":status
            }
        )
    except Exception as e:
        print(f"error sending notification :{e}")