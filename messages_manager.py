from CONSTS import DELIVERY_PERSONNEL_NUMBERS, BUSINESS_NUMBER, SHAHARS_NUMBER
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from twilio.rest import Client

def send_whatsapp_message(order_data):
    message_text = f"# Note: dynamic content may be written in Hebrew\n" \
                   f"Phone: {order_data['customer_phone']}\n" \
                   f"Name: {order_data['customer_name']}, Company: {order_data['company_name']}\n" \
                   f"Address: {order_data['customer_address']}\n" \
                   f"Wanted at: {order_data['order_time']}"
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    sids = []

    for number in DELIVERY_PERSONNEL_NUMBERS:
        try:
            message = client.messages.create(
                body=message_text,
                from_=f"whatsapp:{BUSINESS_NUMBER}",
                to=f"whatsapp:{number}"
            )
            print(f"message sent to {number}")
            sids.append(message.sid)
        except Exception as e:
            print(f"Error sending message to {number}: {e}")

    return sids


def send_whatsapp_message_old(order_data):
    message_text = order_data_to_message(order_data)
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    sids = []

    for number in DELIVERY_PERSONNEL_NUMBERS:
        message = client.messages.create(
            body=message_text,
            from_=f"whatsapp:{BUSINESS_NUMBER}",
            to=f"whatsapp:{number}"
        )
        print(f"message sent to {number}")
        sids.append(message.sid)

    return sids

