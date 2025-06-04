from django.db.models.signals import post_save
from django.dispatch import receiver,Signal

from django.template.loader import render_to_string
from .models import Order  # Make sure you import your model
from .tasks import send_mail


status_updated= Signal()

@receiver(post_save, sender=Order)
def handle_order_creation(sender, instance, created, **kwargs):
    if created:
        msg = f"""
        Hello {instance.customer_name},

        Your order {instance.order_id} for {instance.product_name} has been received.
        """
        if not instance.status:
            status = 'received'
        context = {
            'order_message':msg,
            'customer_name': instance.customer_name,
            'order_id': instance.order_id,
            'product_name': instance.product_name,
            'price': instance.price,
            'status': status,
        }

        html_content = render_to_string("email.html", context)  # no need to write "templates/" here
        text_content = f"""
        Hello {instance.customer_name},

        Your order {instance.order_id} for {instance.product_name} has been received.
        Status: {status}
        Price: ₹{instance.price}

        Thank you for ordering!
        """

        subject = f"Order Update - #{instance.order_id} Order has been {status}"

        #sending mail in background
        send_mail.delay(subject,text_content,html_content)


@receiver(status_updated)
def handle_order_status_update(sender, instance,new_status, **kwargs):
    msg = f"""
        Hello {instance.customer_name},

        Your order {instance.order_id} for {instance.product_name} has been {new_status}.
        """
    context = {
            'order_message':msg,
            'customer_name': instance.customer_name,
            'order_id': instance.order_id,
            'product_name': instance.product_name,
            'price': instance.price,
            'status': new_status,
        }
    
    html_content = render_to_string("email.html", context)  # no need to write "templates/" here
    
    text_content = f"""
    Hello {instance.customer_name},
    Your order {instance.order_id} for {instance.product_name} has been {new_status}.
    Status: {new_status}
    Price: ₹{instance.price}
    Thank you for ordering!
    """
    subject = f"Order Update - #{instance.order_id} order has been {new_status}"

    send_mail.apply_async(
    args=[subject, text_content, html_content],
    countdown=60
    )