from django.db.models.signals import post_save
from django.dispatch import receiver

from django.template.loader import render_to_string
from .models import Order  # Make sure you import your model
from .tasks import send_mail


@receiver(post_save, sender=Order)
def handle_order_creation(sender, instance, created, **kwargs):
    if created:
        msg = f"""
        Hello {instance.customer_name},

        Your order {instance.order_id} for {instance.product_name} has been received.
        """
        context = {
            'order_message':msg,
            'customer_name': instance.customer_name,
            'order_id': instance.order_id,
            'product_name': instance.product_name,
            'price': instance.price,
            'status': instance.status,
        }

        html_content = render_to_string("email.html", context)  # no need to write "templates/" here
        text_content = f"""
        Hello {instance.customer_name},

        Your order {instance.order_id} for {instance.product_name} has been received.
        Status: {instance.status.title()}
        Price: ₹{instance.price}

        Thank you for ordering!
        """

        subject = f"Order Confirmation - #{instance.order_id}"

        #sending mail in background
        send_mail.delay(subject,text_content,html_content)

