from trip_manager import fetch_orders_by_status
from trip_manager import fetch_order_by_id
from trip_manager import update_order_status
from trip_manager import asses_new_orders_status
from trip_manager import asses_pending_orders_status
from trip_manager import count_dishes_and_sides
import json
import tkinter as tk
from tkinter import ttk
import _tkinter
import platform


from CONSTS import ACCEPTED, PENDING, QUEUED, PREPARING, DISPATCHED


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
            self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        else:
            self.canvas.bind("<Button-4>", self._on_mousewheel)
            self.canvas.bind("<Button-5>", self._on_mousewheel)

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Create the frames inside the scrollable_frame instead of self
        self.create_frames()
        self.update_display()

        self.check_new_orders()
        self.check_pending_orders()

    def create_frames(self):

        # queued_orders_frame
        self.queued_orders_frame = ttk.LabelFrame(self.scrollable_frame, text="Queued Orders")
        self.queued_orders_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.queued_orders_list = ButtonedTreeview(self.queued_orders_frame, on_button_click=self.prepare_single_order_onclick,
                                                   button_text="Prepare ⬇", columns=("Name", "Exp/ASAP", "Address"),
                                                   show="headings")
        self.queued_orders_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Configure column widths and headings for queued_orders_list
        self.queued_orders_list.column("Name", width=150, anchor="w", stretch=False)
        self.queued_orders_list.column("Exp/ASAP", width=80, anchor="w", stretch=False)
        self.queued_orders_list.column("Address", width=500, anchor="w", stretch=False)
        self.queued_orders_list.heading("Name", text="Name")
        self.queued_orders_list.heading("Exp/ASAP", text="Exp/ASAP")
        self.queued_orders_list.heading("Address", text="Address")

        # prepare_orders_button
        self.prepare_orders_button = ttk.Button(self.scrollable_frame, text="⬇ Prepare Orders in Queue",
                                                command=self.prepare_orders)
        self.prepare_orders_button.pack(padx=10, pady=10, anchor="w")

        # preparing_orders_frame
        self.preparing_orders_frame = ttk.LabelFrame(self.scrollable_frame, text="Preparing Orders")
        self.preparing_orders_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.summary_frame = tk.Frame(self.preparing_orders_frame)
        self.summary_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.orders_frame = tk.Frame(self.preparing_orders_frame)
        self.orders_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # summary_list
        self.summary_list = ttk.Treeview(self.summary_frame, columns=("Dish Name", "Dish Total"), show="headings")
        self.summary_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Configure column widths and headings for summary_list
        self.summary_list.column("Dish Name", width=150, anchor="w")
        self.summary_list.column("Dish Total", width=100, anchor="w")
        self.summary_list.heading("Dish Name", text="Dish Name")
        self.summary_list.heading("Dish Total", text="Dish Total")

        self.preparing_orders_list = ButtonedTreeview(self.orders_frame, on_button_click=self.unprep_single_order,
                                                      button_text="Unprep ⬆", columns=("Name", "Exp/ASAP", "Address"),
                                                      show="headings")

        self.preparing_orders_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Configure column widths and headings for preparing_orders_list
        self.preparing_orders_list.column("Name", width=150, anchor="w")
        self.preparing_orders_list.column("Exp/ASAP", width=70, anchor="w")
        self.preparing_orders_list.column("Address", width=500, anchor="w")
        self.preparing_orders_list.heading("Name", text="Name")
        self.preparing_orders_list.heading("Exp/ASAP", text="Exp/ASAP")
        self.preparing_orders_list.heading("Address", text="Address")

        # dispatch_orders_button
        self.dispatch_orders_button = ttk.Button(self.scrollable_frame, text="⬇ Dispatch Prepared Orders",
                                                 command=self.dispatch_prepared_orders)
        self.dispatch_orders_button.pack(padx=10, pady=10, anchor="w")

    def _on_mousewheel(self, event):
        if platform.system() == "Windows":
            self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        else:
            self.canvas.yview_scroll(1, "units")

    def update_display(self):
        self.update_queued_orders()
        self.update_summary_list()
        self.update_preparing_orders()
        self.update_listbox_heights()

    def update_listbox_heights(self):
        queued_height = len(self.queued_orders_list.get_children()) + 1
        self.queued_orders_list.config(height=queued_height)

        preparing_height = len(self.preparing_orders_list.get_children()) + 1
        self.preparing_orders_list.config(height=preparing_height)

        summary_height = len(self.summary_list.get_children()) + 1
        self.summary_list.config(height=summary_height)

    def update_queued_orders(self):
        # Remove all rows from the Treeview
        for row in self.queued_orders_list.get_children():
            self.queued_orders_list.delete(row)

        queued_orders = fetch_orders_by_status(QUEUED)

        for order in queued_orders:
            order_id, name, address, expected, asap = order[0], order[4], order[5], order[12], order[11]
            asap_text = "Yes" if asap else "No"

            # Insert a row into the Treeview with order_id as iid
            self.queued_orders_list.insert("", "end", iid=order_id, values=(name, f"{expected}/{asap_text}", address))

        # Check if there's an extra button and remove it
        for item, button in list(self.queued_orders_list.buttons.items()):
            if item not in self.queued_orders_list.get_children():
                button.destroy()
                del self.queued_orders_list.buttons[item]

        self.update_idletasks()
        self.queued_orders_list.update_buttons()

    def update_summary_list(self):
        self.summary_list.delete(*self.summary_list.get_children())
        dishes_and_sides = count_dishes_and_sides(status=PREPARING)

        for dish, count in dishes_and_sides.items():
            self.summary_list.insert("", "end", values=(dish, count))

    def update_preparing_orders(self):
        # Remove all rows from the Treeview
        for row in self.preparing_orders_list.get_children():
            self.preparing_orders_list.delete(row)

        preparing_orders = fetch_orders_by_status(PREPARING)

        for order in preparing_orders:
            order_id, name, address, expected, asap = order[0], order[4], order[5], order[12], order[11]
            asap_text = "Yes" if asap else "No"

            # Insert a row into the Treeview with order_id as iid
            self.preparing_orders_list.insert("", "end", iid=order_id,
                                              values=(name, f"{expected}/{asap_text}", address))

        self.update_idletasks()
        self.preparing_orders_list.update_buttons()

    def prepare_orders(self):
        queued_orders = fetch_orders_by_status(QUEUED)

        for order in queued_orders:
            order_id = order[0]
            update_order_status(order_id, PREPARING)

        self.update_summary_list()
        self.update_display()

    def prepare_single_order_onclick(self, iid):
        popup = OrderDetailsPopup(self, iid, self.prepare_single_order)
        self.wait_window(popup)

    def prepare_single_order(self, iid):
        update_order_status(iid, new_status=PREPARING)

        # Remove the row and its associated button from the queued_orders_list before updating the display
        self.queued_orders_list.delete(iid)

        self.update_display()

        # Update buttons for both queued_orders_list and preparing_orders_list
        self.queued_orders_list.update_buttons()
        self.preparing_orders_list.update_buttons()

    def unprep_single_order(self, iid):
        update_order_status(iid, new_status=QUEUED)

        # Remove the row and its associated button from the preparing_orders_list before updating the display
        self.preparing_orders_list.delete(iid)

        self.update_display()

        # Update buttons for both queued_orders_list and preparing_orders_list
        self.queued_orders_list.update_buttons()
        self.preparing_orders_list.update_buttons()

    def dispatch_prepared_orders(self):
        preparing_orders = fetch_orders_by_status(PREPARING)

        for order in preparing_orders:
            order_id = order[0]
            update_order_status(order_id, DISPATCHED)

        self.update_display()

    def check_new_orders(self):
        new_orders = fetch_orders_by_status(ACCEPTED)
        asses_new_orders_status(new_orders)
        self.update_display()
        self.after(60000, self.check_new_orders)

    def check_pending_orders(self):
        pending_orders = fetch_orders_by_status(PENDING)
        asses_pending_orders_status(pending_orders)
        self.update_display()
        self.after(300000, self.check_pending_orders)


class ButtonedTreeview(ttk.Treeview):
    def __init__(self, master=None, button_text="Button", on_button_click=None, **kwargs):
        super().__init__(master, **kwargs)
        self.buttons = {}
        self.button_text = button_text
        self.on_button_click = on_button_click

    def yview(self, *args):
        # Call the original yview method
        super().yview(*args)

        # Update the buttons' positions
        self.update_buttons()

    def update_buttons(self):
        for item, button in list(self.buttons.items()):  # Use list() to create a copy of the dictionary items
            try:
                bbox = self.bbox(item)
            except _tkinter.TclError:
                continue

            if not bbox:
                button.destroy()
                del self.buttons[item]
                continue

            x, y, width, height = bbox
            button.place(x=x + width - 70, y=y, width=90, height=height)

    def insert(self, parent, index, iid=None, **kw):
        # Call the original insert method
        item = super().insert(parent, index, iid=iid, **kw)

        # Check if the item is valid before creating a button
        if self.exists(item):
            # Create a button for the row
            button = ttk.Button(self, text=self.button_text, command=lambda: self.on_button_click(iid))

            # Store the button in the buttons dictionary
            self.buttons[item] = button

            # Update the buttons' positions
            self.update_buttons()

        return item

    def delete(self, *items):
        for item in items:
            if not self.exists(item):
                print(f"Item {item} not found")
                continue

            # Call the original delete method
            super().delete(item)

            # Destroy the button associated with the item and remove it from the buttons dictionary
            if item in self.buttons:
                self.buttons[item].destroy()
                del self.buttons[item]


class OrderDetailsPopup(tk.Toplevel):
    def __init__(self, parent, order_id, confirm_callback):
        super().__init__(parent)
        self.title("Order Details")
        self.order_id = order_id
        self.confirm_callback = confirm_callback

        # Retrieve the order details
        order_details = fetch_order_by_id(self.order_id)

        # Define labels
        labels = [
            "Order ID",         # 0
            "Customer ID",      # 1
            "Phone",            # 2
            "Email",            # 3
            "Name",             # 4
            "Address",          # 5
            "Company",          # 6
            "Package",          # 7
            "Source order ID",  # 8
            "Content",    # 9
            "Note",             # 10
            "Asap",             # 11
            "Expected",         # 12
            "Amount",           # 13
            "Source",           # 14
            "Status",           # 15
            "Timestamp"         # 16
        ]

        # Display order details
        content_frame = ttk.Frame(self)
        content_frame.pack(padx=10, pady=10)

        for i, value in enumerate(order_details):
            if i in [4]:    # add wanted data indexes to list
                # key_label = ttk.Label(content_frame, text=f"{labels[i]}:")
                # key_label.grid(row=i, column=0, sticky=tk.W)
                value_label = ttk.Label(content_frame, text=value)
                value_label.grid(row=i, column=0, sticky=tk.W)

        # Display order content
        order_content = json.loads(order_details[9])
        # key_label = ttk.Label(content_frame, text=f"{labels[9]}:")
        # key_label.grid(row=len(order_details), column=0, sticky=tk.W)
        content_text = "\n".join([f"{item['count']} x {item['dish']}" for item in order_content])
        content_label = ttk.Label(content_frame, text=content_text)
        content_label.grid(row=len(order_details), column=0, sticky=tk.W)

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(padx=10, pady=10)

        prepare_button = ttk.Button(button_frame, text="Prepare", command=self.prepare_order)
        prepare_button.pack(side=tk.LEFT)

        close_button = ttk.Button(button_frame, text="Close", command=self.destroy)
        close_button.pack(side=tk.LEFT, padx=10)

    def prepare_order(self):
        self.confirm_callback(self.order_id)
        self.destroy()


if __name__ == "__main__":
    app = Display()
    app.mainloop()
