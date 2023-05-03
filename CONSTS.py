# TODO: customer_note: צרפו סכו"ם חד פעמי

"""order_statuses"""
# Maybe - Add 'COLLECTED', a new status between WAITING and ACCEPTED and then create a functionality
# that for orders that are less than MIN_AMOUNT will ask a human via GUI what to do
REFUNDED, REJECTED, WAITING, ACCEPTED, PENDING, QUEUED, PREPARING, DISPATCHED, FULFILLED = -2, -1, 0, 1, 2, 3, 4, 5, 6
# REFUNDED:     Orders that have been supplied and fully refunded.
# REJECTED:     Order rejected, mostly because total is less than minimum
# WAITING:      Order submitted and waiting for processing
# ACCEPTED:     Order accepted by criteria. Pool of incoming orders for the trip_manager
# PENDING:      Orders not due for preparation yet
# QUEUED:       Orders that meet the timing criteria
# PREPARING:    Orders moved from the QUEUED stage to actual preparation
# FULFILLED:    Order prepared and fulfilled


"""order_manager"""
CIBUS, WIX = 0, 1
MINIMUM_ORDER_AMOUNT = 45

MINIMUM_SOUND_ALERT = 'assets/order_total_alert.mp3'
CIBUS_ASAP_TEXT = "אשמח לקבל את ההזמנה מוקדם יותר"
TEL_AVIV_IND_TEXT = "תל אביב"

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
    'customer_id': int,
    'customer_phone': '',
    'customer_email': '',
    'customer_name': '',
    'customer_address': '',
    'customer_company': '',
    'package_id': 0,          # TODO: Add a function that gets this.
    'order_id': int,
    'order_content': [],
    'order_note': '',
    'order_asap': False,
    'order_expected': '',
    'order_amount': '',
    'order_source': CIBUS,    # TODO: add functionality when integrating wix
    'order_status': WAITING,
    'timestamp': '',
}

"""messages_manager"""
BUSINESS_NUMBER = '+972512512900'

SHAHAR_NUMBER = '+972528604949'

DAHAN_NUMBER = '+972546588593'

OR_NUMBER = '+972508815670'

DELIVERY_PERSONNEL_NUMBERS = [SHAHAR_NUMBER, DAHAN_NUMBER, OR_NUMBER]

"""routs_manager"""
HOME_BASE = "Haroe Street 59, Ramat Gan"


"""trip_manager"""
BUFFER = 75 + 30  # 105 minutes buffer
ASAP_BUFFER = 75 + 85  # 160 minutes buffer
DISH_TAGS = {
    # NO_FREEZER
    "מיונז אישי": 0,
    "אורז לבן | מיידיז": 0,
    "קוקה קולה": 0,
    "קולה זירו": 0,
    "טרופית": 0,
    # FREEZER 1
    "פרגית אסייאתית מתקתקה | שרון ברקוביץ": 1,
    "צ'ילי קון קרנה | גדי גומז": 1,
    "מוסקה חצילים ממולאים בבשר ברוטב עגבניות פיקנטי | שף בן גמוניצקי": 1,
    "חזה עוף במרינדת טריאקי | מיידיז": 1,
    "חזה עוף במרינדת שום ועשבי תיבול עם הרבה לימון | מיידיז": 1,
    "חזה עוף במרינדת ברבקיו | מיידיז": 1,
    "חזה עוף במרינדת חרדל ודבש | מידייז": 1,
    # FREEZER 2
    "קציצות בקר וכרישה | שף בן גמוניצקי": 2,
    "שעועית ירוקה בנוסח אסייאתי | מיידיז": 2,
    "אורז פרא מעושן | גדי גומז": 2,
    "שניצל פילה עוף | מיידיז": 2,
    "סלמון ברוטב חמוץ מתוק | מיידיז": 2,
    "קוסקוס | שף חן זבולון": 2,
    # FREEZER 3
    "מתכון חדש עם המון רוטב וכמות מוגדלת! פסטה פנה ברוטב עגבניות | מיידיז": 3,
    "פסטה בזיליקום וקרם קוקוס | מיידיז": 3,
    "מרק ירקות ושורשים כתומים | מיידיז": 3,
    "מרק אפונה קטיפתי אמיתי | מיידיז": 3,
    "הקציצות של סבתא נחמה | מיידיז וסבתא נחמה": 3,
    # FREEZER 4
    "דאל עדשים כתומות | סיון טרם": 4,
    "דאל עדשים שחורות ישראלי | מיטל כהן": 4,
    "טופו בקארי ירוק ואפונת גזר | גדי גומז": 4,
    "טופו טריאקי מתוק | שרון ברקוביץ": 4,
    "חריימה טבעוני | שף חן זבולון": 4
}

"""db_manager"""
MOCK = False
if MOCK:
    DB_NAME = "maidiz_mock.db"
    DELIVERY_PERSONNEL_NUMBERS = [SHAHAR_NUMBER]
else:
    DB_NAME = "maidiz.db"

"""display"""