import sqlite3
from datetime import datetime, timedelta
from trip_manager import fetch_all_orders
from CONSTS import DISH_TAGS, REFUNDED, REJECTED, WAITING, ACCEPTED, PENDING, QUEUED, PREPARING, DISPATCHED, FULFILLED

import ast


def count_dishes_and_sides_by_orders_list(orders):

    content_list = []

    for o in orders:
        item = ast.literal_eval(o[9])
        content_list.extend(item)

    dish_and_side_count = {}

    for item in content_list:
        dish = item['dish']
        count = item['count']
        sides = item['sides']

        if dish not in dish_and_side_count:
            dish_and_side_count[dish] = {'count': count, 'tag': DISH_TAGS.get(dish, -1)}
        else:
            dish_and_side_count[dish]['count'] += count

        for side in sides:
            if side not in dish_and_side_count:
                dish_and_side_count[side] = {'count': count, 'tag': DISH_TAGS.get(side, -1)}
            else:
                dish_and_side_count[side]['count'] += count

    return dish_and_side_count


def fetch_todays_orders():
    # Get the current date
    today = datetime.now().date()

    # Fetch all orders
    all_orders = fetch_all_orders()

    # Filter the orders to include only those from today
    todays_orders = [order for order in all_orders if
                     datetime.strptime(order[16], '%Y-%m-%d %H:%M:%S').date() == today and order[15] == DISPATCHED]

    return todays_orders


def calculate_total_sales(orders):
    total_sales = 0
    for order in orders:
        total_sales += float(order[13].strip(' ₪'))
    return total_sales


def main():
    todays_orders = fetch_todays_orders()

    dish_and_side_count = count_dishes_and_sides_by_orders_list(todays_orders)

    # Sort dishes by count from high to low
    sorted_dish_and_side_count = sorted(dish_and_side_count.items(), key=lambda x: x[1]['count'], reverse=True)

    # Calculate initial and final dates and their corresponding weekdays
    today = datetime.now()
    f_date = today.strftime("%d/%m")
    f_weekday = today.strftime("%A")
    i_date = (today - timedelta(days=6)).strftime("%d/%m")
    i_weekday = (today - timedelta(days=6)).strftime("%A")

    # Calculate total sales of the day
    total_sales = calculate_total_sales(todays_orders)

    print(f"\n\nDaily Summary:")
    print(f"Total Sales: {total_sales:.2f}₪")
    print(f"Total orders: {len(todays_orders)}")
    print(f"Average order amount: {(total_sales/len(todays_orders)):.2f}₪")
    for dish, details in sorted_dish_and_side_count:
        print(f"{details['count']}\t:\t{dish}")


if __name__ == "__main__":
    main()

