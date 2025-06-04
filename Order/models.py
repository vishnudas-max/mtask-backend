from django.db import models



class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('received', 'Order Received'),
        ('processing', 'Processing'),
        ('dispatched', 'Dispatched'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order_id = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=200)
    product_name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        null=True,
        blank=True,
        help_text='Current status of the order'
    )

    def __str__(self):
        return f"Order {self.order_id} - {self.product_name} ({self.get_status_display()}) for {self.customer_name}"
