
# order status
REJECTED, WAITING, ACCEPTED, FULFILLED = -1, 0, 1, 2

MINIMUM_ORDER_AMOUNT = 40
MINIMUM_SOUND_ALERT = 'assets/order_total_alert.mp3'
CIBUS_ASAP_TEXT = "אשמח לקבל את ההזמנה מוקדם יותר"

CHEFS_NAMES = [
    "גדי גומז",
    "מיידיז",
    "אתי אדר",
    "שף בן גמוניצקי",
    "סבתא נחמה",
    "שרון ברקוביץ'",
    "מיטל כהן",
    "שף חן זבולון",
    "סיון טרם",
]

ORDER_STRUCTURE = {
    'company_name': '',
    'customer_address': '',
    'customer_phone': '',
    'customer_name': '',
    'order_content': [],
    'order_asap': False,
    'customer_note': '',
    'order_id': '',
    'order_time': '',
    'order_amount': '',
    'order_source': '',
    'status': WAITING,
    'timestamp': '',
}

TEST_ORDER_DATA = {
    'company_name': 'Pizza Palace',
    'company_phone': '+972528604949',
    'customer_address': '123 Main St, Springfield',
    'customer_phone': '+972528604949',
    'customer_name': 'Johny Yal',
    'customer_note': 'Leave at the door',
    'order_content': [
        {
            'item_name': 'Large Pepperoni Pizza',
            'quantity': 1,
            'price': '15.99'
        },
        {
            'item_name': 'Garlic Bread',
            'quantity': 2,
            'price': '3.99'
        }
    ],
    'order_id': '123456789',
    'order_time': '18:30',
    'order_asap': False,
    'order_amount': '43.97',
    'order_source': 'Online',
    'status': 0,  # WAITING
    'timestamp': '2023-03-26T15:30:00',
}

BUSINESS_NUMBER = '+972512512900'

DELIVERY_PERSONNEL_NUMBERS = ['+972528604949', '+972546588593']

SHAHARS_NUMBER = '+972528604949'

HOME_BASE = "Haroe Street 59, Ramat Gan"