
import email
import imaplib
from itertools import chain
from together import Together
from django.conf import settings
from django.utils.timezone import now
from notification.utils import send_notifications


from Order.models import Order
from django.conf import settings

# Setup Together API
client = Together(api_key=settings.TOGETHER_API_KEY)


def update_order_status(result):
    from .Signals import status_updated

    try:
        order = Order.objects.get(order_id=result['order_id'])
        old_status = order.status
        new_status = result['status']

        if old_status == new_status:
            print("Status already updated")
            return

        # Define the valid transitions and the next signal to send
        status_flow = {
            None: ('received', 'processing'),
            'received': ('processing', 'dispatched'),
            'processing': ('dispatched', 'delivered'),
            'dispatched': ('delivered', None)
        }

        # Final statuses (no further signals)
        final_statuses = ['delivered', 'cancelled']

        if old_status in status_flow:
            expected_status, next_signal = status_flow[old_status]

            if new_status == expected_status:
                order.status = new_status
                order.save(update_fields=['status'])
                print(f"Status updated to {new_status}")
                send_notifications(order.order_id,new_status)

                if next_signal:
                    status_updated.send(sender=Order, instance=order, new_status=next_signal)
                    print(f"Signal sent for next status: {next_signal}")
                return
            else:
                print(f"Ignored update. Expected '{expected_status}' after '{old_status}', but got '{new_status}'")
                return

        # If status already at final state or outside defined flow
        if new_status in final_statuses:
            order.status = new_status
            order.save(update_fields=['status'])
            print('sending notification')
            send_notifications(order.order_id,new_status)
            print(f"Final status '{new_status}' set without sending signal")
        else:
            print(f"Unhandled transition: {old_status} -> {new_status}")

    except Order.DoesNotExist:
        print(f"Order with ID {result['order_id']} does not exist")





def extract_json_from_string(text):
    import re, json
    try:
        # Try extracting using ```json code block
        match = re.search(r'```json\s*({.*?})\s*```', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # Fallback: Extract first {...} block from text
        match = re.search(r'({.*})', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise ValueError("No JSON object found in the string.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")

def extract_order_info(email_body):
    prompt = (
        "Extract the following details from this email: "
        "customer name, order id, product name, and order status. "
        "Return them in JSON format with keys: customer_name, order_id, product_name, status. "
        "If a field is missing, set it as null. Use lowercase for status.\n\n"
        "Valid status values: received, cancelled, processing, dispatched, delivered.\n\n"
        "only give json output"
        f"Email:\n{email_body}"
    )

    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def search_string(criteria):
    c = list(map(lambda t: (t[0], f'"{t[1]}"'), criteria.items()))
    return f'({" ".join(chain(*c))} UNSEEN)'

def check_email_and_process():
    imap_ssl_host = 'imap.gmail.com'
    username = settings.EMAIL_USERNAME
    password = settings.EMAIL_PASSWORD
    criteria = {"FROM": "vishnudask410@gmail.com", "SUBJECT": "order"}
    uid_max = 0

    mail = imaplib.IMAP4_SSL(imap_ssl_host)
    mail.login(username, password)
    mail.select('inbox')

    result, data = mail.uid('search', None, '(UNSEEN FROM "vishnudask410@gmail.com" SUBJECT "order")')
    uids = data[0].split()

    for uid in uids:
        result, data = mail.uid('fetch', uid, '(RFC822)')
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                text = ""

                if msg.is_multipart():
                    if msg.is_multipart():
                        parts = [p for p in msg.walk() if p.get_content_type() in ["text/plain", "text/html"]]
                        if parts:
                            last_part = parts[-1]
                            body = last_part.get_payload(decode=True)
                            charset = last_part.get_content_charset() or 'utf-8'
                            text = body.decode(charset, errors="ignore")

                else:
                    body = msg.get_payload(decode=True)
                    charset = msg.get_content_charset() or 'utf-8'
                    text = body.decode(charset, errors="ignore")

                
                print("----- Email Text Start -----")
                print(text)
                print("----- Email Text End -----")

                extracted = extract_order_info(text)
                print(f"Raw extracted: {extracted}")
                result = extract_json_from_string(extracted)
                update_order_status(result)

        # Mark as read
        mail.uid('store', uid, '+FLAGS', '(\\Seen)')

    mail.logout()






    

