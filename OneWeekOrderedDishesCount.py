import sqlite3
from datetime import datetime, timedelta
from trip_manager import fetch_all_orders
from CONSTS import DISH_TAGS
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


def fetch_past_week_orders():
    # Get the current date and time
    now = datetime.now()

    # Calculate the date and time one week ago
    one_week_ago = now - timedelta(weeks=1)

    # Fetch all orders
    all_orders = fetch_all_orders()

    # Filter the orders to include only those from the past week
    past_week_orders = [order for order in all_orders if
                        datetime.strptime(order[16], '%Y-%m-%d %H:%M:%S') > one_week_ago]

    return past_week_orders


def main():
    past_week_orders = fetch_past_week_orders()

    print(f"Past week orders fetched: {len(past_week_orders)}")
    dish_and_side_count = count_dishes_and_sides_by_orders_list(past_week_orders)

    # Sort dishes by count from high to low
    sorted_dish_and_side_count = sorted(dish_and_side_count.items(), key=lambda x: x[1]['count'], reverse=True)

    # Calculate initial and final dates and their corresponding weekdays
    today = datetime.now()
    f_date = today.strftime("%d/%m")
    f_weekday = today.strftime("%A")
    i_date = (today - timedelta(days=6)).strftime("%d/%m")
    i_weekday = (today - timedelta(days=6)).strftime("%A")

    print(f"Dishes count for the past week - From {i_date}, {i_weekday}, to {f_date}, {f_weekday}:")
    for dish, details in sorted_dish_and_side_count:
        print(f"{details['count']}\t:\t{dish}")


if __name__ == "__main__":
    main()

