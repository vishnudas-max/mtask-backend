import json
from channels.generic.websocket import AsyncWebsocketConsumer
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "notification"
        
        # Add to group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        print(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        # Remove from group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected: {self.channel_name}")

    # This method handles messages sent to the group
    async def send_notification(self, event):
        """
        This method is called when a message is sent to the group
        The method name must match the 'type' in group_send
        """
        order_id = event['order_id']
        status = event['status']
        
        print(f'Sending notification: order_id={order_id}, status={status}')
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'action':'update',
            'order_id': order_id,
            'status': status
        }))
        
    async def add_order(self, event):
        """
        Handles new order notifications (new)
        """
        order_id = event['order_id']
        product_name = event['product_name']
        customer_name = event['customer_name']
        price = event['price']
        status = event.get('status', None)

        print(f'Sending new order notification: order_id={order_id}')
        
        await self.send(text_data=json.dumps({
            'action': 'new',  
            'order_id': order_id,
            'product_name': product_name,
            'customer_name': customer_name,
            'price': price,
            'status': status,
        }))