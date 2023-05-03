import tkinter as tk
from tkinter import ttk
import platform
from trip_manager import fetch_orders_by_status
from trip_manager import fetch_order_by_id
from trip_manager import update_order_status
from trip_manager import count_dishes_and_sides
from trip_manager import  asses_pending_orders_status
from CONSTS import ACCEPTED, PENDING, QUEUED, PREPARING, DISPATCHED
import json
# TODO: ensure orders statused PENDING do not stuck there. Occasionally check PENDING (here or elsewhere)


class Display(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Orders Management")
        self.geometry("1600x900")
        self.state("zoomed")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Create a canvas and scrollbar for the entire application
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Add mouse / touchpad scrolling
        if platform.system() == "Windows":
            self.bind("<MouseWheel>", self._on_mousewheel)
        else:
            self.bind("<Button-4>", self._on_mousewheel)
            self.bind("<Button-5>", self._on_mousewheel)

        # Create window
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Create the frames inside the scrollable_frame instead of self
        self.create_frames()

        # db functionality
        self.ids_queued = set()
        self.ids_preparing = set()
        self.update_all()
        self.check_queued_orders()
        self.check_preparing_orders()

    def create_frames(self):
        # queued_orders_frame
        self.queued_orders_frame = ttk.LabelFrame(self.scrollable_frame, text="Queued Orders")
        self.queued_orders_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.queued_orders_list = ttk.Treeview(self.queued_orders_frame, columns=("Name", "Exp/ASAP", "Address"), show="headings")
        self.queued_orders_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.queued_orders_list.column("Name", width=150, anchor="w", stretch=False)
        self.queued_orders_list.column("Exp/ASAP", width=80, anchor="w", stretch=False)
        self.queued_orders_list.column("Address", width=500, anchor="w", stretch=False)
        self.queued_orders_list.heading("Name", text="Name")
        self.queued_orders_list.heading("Exp/ASAP", text="Exp/ASAP")
        self.queued_orders_list.heading("Address", text="Address")

        self.queued_orders_list.bind("<Double-1>", self.show_order_popup)

        # prepare_orders_button
        self.prepare_orders_button = ttk.Button(self.scrollable_frame, text="⬇ Prepare Orders in Queue", command=self.prepare_queued_orders)
        self.prepare_orders_button.pack(padx=10, pady=10, anchor="w")

        # summary_frame
        self.summary_frame = ttk.LabelFrame(self.scrollable_frame, text="Preparation Summary")
        self.summary_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.summary_list = ttk.Treeview(self.summary_frame, columns=("Dish Total", "Dish Name"), show="headings")
        self.summary_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.summary_list.column("Dish Total", width=80, anchor="w", stretch=False)
        self.summary_list.column("Dish Name", width=500, anchor="w", stretch=False)
        self.summary_list.heading("Dish Total", text="Dish Total")
        self.summary_list.heading("Dish Name", text="Dish Name")

        # preparing_orders_frame
        self.preparing_orders_frame = ttk.LabelFrame(self.scrollable_frame, text="Preparing Orders")
        self.preparing_orders_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.orders_frame = tk.Frame(self.preparing_orders_frame)
        self.orders_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.preparing_orders_list = ttk.Treeview(self.preparing_orders_frame, columns=("Name", "Exp/ASAP", "Address"), show="headings")
        self.preparing_orders_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.preparing_orders_list.column("Name", width=150, anchor="w", stretch=False)
        self.preparing_orders_list.column("Exp/ASAP", width=80, anchor="w", stretch=False)
        self.preparing_orders_list.column("Address", width=500, anchor="w", stretch=False)
        self.preparing_orders_list.heading("Name", text="Name")
        self.preparing_orders_list.heading("Exp/ASAP", text="Exp/ASAP")
        self.preparing_orders_list.heading("Address", text="Address")

        self.preparing_orders_list.bind("<Double-1>", self.move_order_back_to_queued)

        # dispatch_orders_button
        self.dispatch_orders_button = ttk.Button(self.scrollable_frame, text="⬇ Dispatch Prepared Orders", command=self.dispatch_prepared_orders)
        self.dispatch_orders_button.pack(padx=10, pady=10, anchor="w")

    def adjust_treeview_height(self, treeview, min_rows=5, max_rows=30):
        num_items = len(treeview.get_children())

        if num_items < min_rows:
            height = min_rows
        elif num_items > max_rows:
            height = max_rows
        else:
            height = num_items

        treeview.configure(height=height)

    def _on_mousewheel(self, event):
        if platform.system() == "Windows":
            self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        else:
            self.canvas.yview_scroll(1, "units")

    def insert_order_into_treeview(self, treeview, order):
        time_tuple_text = f'{order[12]}/{"Yes" if order[11] else "No"}'
        treeview.insert('', 'end', text='', values=(order[4], time_tuple_text, order[5]),
                        tags=(order[0],))

    def add_order_to_queued(self, order):

        if order[0] not in self.ids_queued:
            self.insert_order_into_treeview(self.queued_orders_list, order)
            self.ids_queued.add(order[0])
        else:
            return False

    def update_summary_list(self):
        # Clear the current items in the Treeview
        for item in self.summary_list.get_children():
            self.summary_list.delete(item)

        # Get the dish and side counts
        dish_and_side_counts = count_dishes_and_sides(PREPARING)

        # Sort the dish and side counts by their tag
        sorted_dish_and_side_counts = sorted(dish_and_side_counts.items(), key=lambda x: x[1]['tag'])

        # Initialize the last_tag variable to track the last printed tag
        last_tag = None

        # Loop through the sorted dish and side counts
        for dish, count_info in sorted_dish_and_side_counts:
            # Print the tag number before printing each tag for the first time
            if last_tag != count_info['tag']:
                last_tag = count_info['tag']
                tag_text = "Freezer " if last_tag > 0 else "No Freezer" if last_tag == 0 else "Untagged"
                self.summary_list.insert("", "end", values=(f"{tag_text + str(last_tag) if last_tag > 0 else tag_text}", ""))

            # Insert the dish name and count into the Treeview
            self.summary_list.insert("", "end", values=(count_info['count'], dish))

    def add_order_to_preparing(self, order):
        # Adds an order to preparing without cleaning it from queued.
        # Created for when starting the program
        if order[0] not in self.ids_preparing:
            self.insert_order_into_treeview(self.preparing_orders_list, order)
            self.ids_preparing.add(order[0])
            self.update_summary_list()

        else:
            print(f"Error - order {order[0]} added to preparing but already in ids_preparing")

    def move_order_to_preparing(self, order_id, item, popup=None):
        order = fetch_order_by_id(order_id)
        if order_id not in self.ids_preparing:
            # Update the order status in the database
            update_order_status(order_id, PREPARING)

            # Remove the order from the queued orders list
            self.queued_orders_list.delete(item)
            self.ids_queued.remove(order_id)

            # Add the order to the preparing orders list
            self.insert_order_into_treeview(self.preparing_orders_list, order)
            self.ids_preparing.add(order_id)
            self.update_summary_list()

            # Adjust the Treeview heights
            self.adjust_treeview_height(self.queued_orders_list)
            self.adjust_treeview_height(self.preparing_orders_list)
            self.adjust_treeview_height(self.summary_list)

            # Close the popup if it's provided
            if popup:
                popup.destroy()
        else:
            print(f"Error - order {order[0]} sent to preparing but already in ids_preparing")

    def move_order_back_to_queued(self, event):
        # Get the item that was double-clicked
        item = self.preparing_orders_list.item(self.preparing_orders_list.focus())

        # Get the order ID from the item's tags
        order_id = int(item['tags'][0])

        # Fetch the order from the database
        order = fetch_order_by_id(order_id)

        if order_id not in self.ids_queued:
            # Update the order status in the database
            update_order_status(order_id, QUEUED)

            # Remove the order from the preparing orders list
            item_id = self.preparing_orders_list.focus()
            self.preparing_orders_list.delete(item_id)
            self.ids_preparing.remove(order_id)

            # Add the order back to the queued orders list
            self.insert_order_into_treeview(self.queued_orders_list, order)
            self.ids_queued.add(order_id)
            self.update_summary_list()

            # Adjust the Treeview heights
            self.adjust_treeview_height(self.queued_orders_list)
            self.adjust_treeview_height(self.preparing_orders_list)
            self.adjust_treeview_height(self.summary_list)


        else:
            print(f"Error - order {order_id} sent back to queued but already in ids_queued")

    def prepare_queued_orders(self):
        # Get all the items in the queued orders list
        queued_orders = self.queued_orders_list.get_children()

        # Iterate through the queued orders
        for item_id in queued_orders:
            # Get the item from the queued_orders_list
            item = self.queued_orders_list.item(item_id)

            # Get the order ID from the item's tags
            order_id = int(item['tags'][0])

            # Move the order to the preparing list
            self.move_order_to_preparing(order_id, item_id)

    def dispatch_prepared_orders(self):
        # Get all the items in the preparing orders list
        preparing_orders = self.preparing_orders_list.get_children()

        # Iterate through the preparing orders
        for item_id in preparing_orders:
            # Get the order ID from the item's tags
            order_id = int(self.preparing_orders_list.item(item_id)['tags'][0])

            # Update the order status to DISPATCHED

            update_order_status(order_id, DISPATCHED)

            # Remove the order from the preparing list
            self.ids_preparing.remove(order_id)

        # Clear the preparing orders list
        self.preparing_orders_list.delete(*preparing_orders)

        # Adjust the Treeview heights
        self.update_summary_list()
        self.adjust_treeview_height(self.summary_list)
        self.adjust_treeview_height(self.preparing_orders_list)

    def update_all(self):
        # asses_orders_status()
        asses_pending_orders_status()
        self.after(5000, self.update_all)

    def check_queued_orders(self):

        # Check for new orders in the database
        for order in fetch_orders_by_status(QUEUED):
            ret = self.add_order_to_queued(order)

        # Adjust the Treeview heights
        self.adjust_treeview_height(self.queued_orders_list)
        self.adjust_treeview_height(self.summary_list)
        # Schedule the next check in 5 seconds
        self.after(5000, self.check_queued_orders)

    def check_preparing_orders(self):
        # Check for new orders in the database
        # Runs only when the program starts
        for order in fetch_orders_by_status(PREPARING):
            self.add_order_to_preparing(order)

        self.adjust_treeview_height(self.preparing_orders_list)

    def show_order_popup(self, event):
        # Get the item that was clicked
        item = self.queued_orders_list.item(self.queued_orders_list.focus())
        item_id = self.queued_orders_list.focus()

        # Get the order ID from the item's tags
        order_id = int(item['tags'][0])

        # Fetch the order from the database
        order = fetch_order_by_id(order_id)

        # Display the popup with the order information
        popup = tk.Toplevel(self)
        popup.title(f"Order {order_id}")
        popup.geometry("400x200")

        # Parse and format the order content
        content = json.loads(order[9])
        formatted_content = []
        for item in content:
            dish = item['dish']
            count = item['count']
            formatted_item = f"{count} x {dish}\t\t\t"
            for s in item['sides']:
                formatted_item += f"\n{count} x {s}\t\t\t)"
            formatted_content.append(formatted_item)
        formatted_content_str = '\n'.join(formatted_content)

        order_text = tk.Text(popup, wrap="word", padx=10, pady=10, width=80)  # Increase the width value as needed

        order_text.insert('1.0', #f"Order ID:   \t\t{order[0]}\n"
                                #f"Customer ID:\t\t{order[1]}\n"
                                #f"Phone       \t\t{order[2]}\n"
                                #f"Email       \t\t{order[3] if order[3] else None}\n"
                                f"{order[4]}\n"
                                #f"Address     \t\t{order[5]}\n"
                                #f"Company     \t\t{order[6]}\n"
                                #f"Package     \t\t{order[7]}\n"
                                #f"Source order ID\t\t{order[8]}\n"
                                f"\n{formatted_content_str}\n"
                                #f"Note        \t\t{order[10] if order[10] else None}\n"
                                #f"Asap        \t\t{order[11]}\n"
                                #f"Expected    \t\t{order[12]}\n"
                                #f"Amount      \t\t{order[13]}\n"
                                #f"Source      \t\t{'Cibus' if order[14] == 0 else 'ERROR'}\n"
                                #f"Status      \t\t{order[15]}\n"
                                #f"Timestamp   \t\t{order[16]}"
                                    )
        # order_text.pack(expand=True, fill=tk.BOTH)

        order_text.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Configure the grid
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_columnconfigure(0, weight=1)

        # Add the "Prepare" button
        prepare_button = ttk.Button(popup, text="Prepare", command=lambda: self.move_order_to_preparing(order_id, item_id, popup))
        prepare_button.grid(row=1, column=1, padx=10, pady=10, sticky="e")

        # Display the popup
        popup.transient(self)
        popup.grab_set()
        self.wait_window(popup)


if __name__ == "__main__":
    display = Display()
    display.mainloop()
