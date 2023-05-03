import os
import tempfile
import subprocess
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from trip_manager import fetch_order_by_id
import json
from reportlab.lib.utils import ImageReader
from trip_manager import fetch_orders_by_status, update_order_status
from CONSTS import REFUNDED, REJECTED, WAITING, ACCEPTED, PENDING, QUEUED, PREPARING, DISPATCHED, FULFILLED


def manage_and_print_order_stickers(db_order_id):
    order = fetch_order_by_id(order_id=db_order_id)

    def _split_long_line(line, max_width, c, font_name, font_size):
        words = line.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            line_width = c.stringWidth(' '.join(current_line), font_name, font_size)

            if line_width > max_width:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]

        lines.append(' '.join(current_line))
        return lines

    def _create_order_pdf(order, font_size=10, leading=12, left_margin=5, top_margin=5, file_name="temp_print.pdf"):

        # Register Arial-Bold font
        font_folder = "C:\\Users\\My PC\\PycharmProjects\\CibusReader\\assets\\fonts\\Arial-Bold"
        pdfmetrics.registerFont(TTFont("Arial-Bold", os.path.join(font_folder, "arial-bold.ttf")))

        # Register Arial font
        font_folder_arial = "C:\\Users\\My PC\\PycharmProjects\\CibusReader\\assets\\fonts\\Arial"
        pdfmetrics.registerFont(TTFont("Arial", os.path.join(font_folder_arial, "arial.ttf")))

        # Extract the relevant data
        name = order[4]
        address = order[5]
        company = order[6]

        # Set Hebrew Titles
        # Hebrew_name = "שם: "
        Hebrew_address = "כתובת: "
        Hebrew_company = "חברה: "
        Added_text = "תודה שבחרתם בנו, שיהיה בתאבון!"
        Added_text2 = "צוות מיידיז :)"

        # Format the text data for the PDF
        name_text = f"{name}"
        order_text = f"{Hebrew_company}{company}\n{Hebrew_address}{address}\n"
        order_text += f"\n{Added_text}\n{Added_text2}"

        file_name = f'C:\\Users\\My PC\\PycharmProjects\\CibusReader\\assets\\{file_name}'
        user_dir = os.path.expanduser("~")
        temp_file = os.path.join(user_dir, file_name)

        # Set custom page size for the sticker
        sticker_width = 60 * mm
        sticker_height = 60 * mm
        sticker_size = (sticker_width, sticker_height)

        # Create a new PDF file
        c = canvas.Canvas(temp_file, pagesize=sticker_size)

        # Set the initial text position
        text_y = c._pagesize[1] - top_margin * mm
        right_margin = 5 * mm

        # Draw name
        # Set the font size and leading (line spacing)
        name_font_size = font_size + 2
        c.setFont("Arial-Bold", name_font_size, leading=leading)

        reshaped_text = arabic_reshaper.reshape(name_text)  # Reshape the text
        bidi_text = get_display(reshaped_text)  # Reorder the text for RTL
        text_width = c.stringWidth(bidi_text, "Arial-Bold", name_font_size)
        text_x = sticker_width - text_width - right_margin  # Set the x-coordinate for RTL text
        c.drawString(text_x, text_y, bidi_text)

        text_y -= leading * mm

        # Draw the text
        # Set the font size and leading (line spacing)
        c.setFont("Arial", font_size, leading=leading)

        lines = order_text.strip().split('\n')
        processed_lines = []
        max_line_width = 150
        for line in lines:
            if c.stringWidth(line, "Arial", font_size) > max_line_width:
                splitted_lines = _split_long_line(line, max_line_width, c, "Arial", font_size)
                processed_lines.extend(splitted_lines)
            else:
                processed_lines.append(line)

        for line in processed_lines:
            reshaped_text = arabic_reshaper.reshape(line)  # Reshape the text
            bidi_text = get_display(reshaped_text)  # Reorder the text for RTL
            text_width = c.stringWidth(bidi_text, "Arial", font_size)
            text_x = sticker_width - text_width - right_margin  # Set the x-coordinate for RTL text

            c.drawString(text_x, text_y, bidi_text)
            text_y -= leading * mm

        # Add last details line
        staff_line = f' #{db_order_id % 100:03d}    {total_dishes}'
        text_y = c._pagesize[1] - sticker_height + 2 * mm  # Set the y-coordinate to the bottom edge of the sticker
        text_x = left_margin * mm  # Set the x-coordinate for LTR text
        c.setFont("Arial", font_size, leading=leading)  # Change the font to Arial and reduce the font size
        c.drawString(text_x, text_y, staff_line)
        text_y -= leading * mm

        # Save the PDF file
        c.save()

        return temp_file

    def _create_dish_pdf(text_data, font_size=10, leading=12, left_margin=5, top_margin=5, file_name="temp_print.pdf"):
        dish_text, dish_index, total_dishes = text_data

        # Register Arial-Bold font
        font_folder = "C:\\Users\\My PC\\PycharmProjects\\CibusReader\\assets\\fonts\\Arial-Bold"
        pdfmetrics.registerFont(TTFont("Arial-Bold", os.path.join(font_folder, "arial-bold.ttf")))

        # Register Arial font
        font_folder_arial = "C:\\Users\\My PC\\PycharmProjects\\CibusReader\\assets\\fonts\\Arial"
        pdfmetrics.registerFont(TTFont("Arial", os.path.join(font_folder_arial, "arial.ttf")))

        file_name = f'C:\\Users\\My PC\\PycharmProjects\\CibusReader\\assets\\{file_name}'
        user_dir = os.path.expanduser("~")
        temp_file = os.path.join(user_dir, file_name)

        # Set custom page size for the sticker
        sticker_width = 60 * mm
        sticker_height = 60 * mm
        sticker_size = (sticker_width, sticker_height)

        # Create a new PDF file
        c = canvas.Canvas(temp_file, pagesize=sticker_size)

        # Set the font size and leading (line spacing)
        c.setFont("Arial-Bold", font_size, leading=leading)

        # Set the initial text position
        text_x = left_margin * mm
        text_y = c._pagesize[1] - top_margin * mm

        # Draw the text
        lines = dish_text.strip().split(' | ')
        processed_lines = []
        max_line_width = 160
        for line in lines:
            if c.stringWidth(line, "Arial-Bold", font_size) > max_line_width:
                splitted_lines = _split_long_line(line, max_line_width, c, "Arial-Bold", font_size)
                processed_lines.extend(splitted_lines)
            else:
                processed_lines.append(line)

        # Add the QR call to action to processed_lines
        empty_line = ""
        qr_call_to_action1 = "עזרו לנו להשתפר!"
        qr_call_to_action2 = "סירקו ודרגו"

        processed_lines.append(empty_line)
        processed_lines.append(qr_call_to_action1)
        processed_lines.append(qr_call_to_action2)

        right_margin = 5 * mm

        for i, line in enumerate(processed_lines):
            reshaped_text = arabic_reshaper.reshape(line)  # Reshape the text
            bidi_text = get_display(reshaped_text)  # Reorder the text for RTL
            text_width = c.stringWidth(bidi_text, "Arial-Bold", font_size)
            text_x = sticker_width - text_width - right_margin  # Set the x-coordinate for RTL text
            c.drawString(text_x, text_y, bidi_text)
            text_y -= leading * mm

        # Adding an image to the dish sticker:
        # Load the image file
        image_path = "C:\\Users\\My PC\\PycharmProjects\\CibusReader\\assets\\direct_qr.png"  # Replace with the actual path to your image file
        image = ImageReader(image_path)

        # Set the image size and position
        image_width = 14 * mm
        image_height = 14 * mm
        image_x = left_margin * mm  # Change this value to move the image horizontally
        image_y = text_y  #  20 * mm  # Change this value to move the image vertically

        # Draw the image on the PDF
        c.drawImage(image, image_x, image_y, width=image_width, height=image_height)

        # Add last details line
        staff_line = f'#{db_order_id % 100:03d}    {dish_index}/{total_dishes}'
        text_y = c._pagesize[1] - sticker_height + 2 * mm  # Set the y-coordinate to the bottom edge of the sticker
        text_x = left_margin * mm  # Set the x-coordinate for LTR text
        c.setFont("Arial", font_size - 4, leading=leading)  # Change the font to Arial and reduce the font size
        c.drawString(text_x, text_y, staff_line)
        text_y -= leading * mm

        # Save the PDF file
        c.save()

        return temp_file

    def _print_and_delete_pdf(file_name):

        # Print the PDF file
        if os.name == 'nt':  # For Windows
            sumatra_path = "C:\\Users\\My PC\\AppData\\Local\\SumatraPDF\\SumatraPDF.exe"
            printer_name = "Datamax-O'Neil E-4204B Mark III"
            print_command = f'start /min "" "{sumatra_path}" -print-to "{printer_name}" "{file_name}"'

            subprocess.run(print_command, shell=True)

        elif os.name == 'posix':  # For macOS and Linux
            print_command = f'lpr "{file_name}"'
            subprocess.run(print_command, shell=True)
            time.sleep(1)  # Wait for a short time to ensure the file is added to the queue

        time.sleep(10)
        # Delete the temporary file
        os.unlink(file_name)

    def _extract_dishes(content=order[9]):
        # Convert the order_content string to a Python list of dictionaries
        content_list = json.loads(content)

        # Iterate through the list of dictionaries, extracting the dish names and counts
        dishes_and_sides = []
        for item in content_list:
            dish = item['dish']
            count = item['count']
            sides = item['sides']

            # Add the dish to the list multiplied by its count
            dishes_and_sides.extend([dish] * count)

            # Add the sides to the list multiplied by the dish count
            for side in sides:
                dishes_and_sides.extend([side] * count)

        return dishes_and_sides

    stickers_list = _extract_dishes()
    total_dishes = len(stickers_list)

    # Print bag's sticker
    pdf_file_name = _create_order_pdf(order, font_size=10, leading=5, left_margin=0, top_margin=10)
    _print_and_delete_pdf(pdf_file_name)

    # Print order's dishes stickers
    for i, item in enumerate(stickers_list):
        text_data = (item, i+1, total_dishes)
        pdf_file_name = _create_dish_pdf(text_data, font_size=12, leading=5, left_margin=5, top_margin=10)
        _print_and_delete_pdf(pdf_file_name)


def print_accepted_orders_stickers_and_push_status():
    """
    prints order stickers and changes its status to the next in the flow (PENDING)
    """
    orders = fetch_orders_by_status(status=ACCEPTED)
    print(f"print_accepted_orders_stickers_and_push_status in action\n"
          f"{len(orders)} accepted orders fetched")

    for o in orders:
        oid = o[0]
        manage_and_print_order_stickers(db_order_id=oid)
        update_order_status(order_id=oid, new_status=PENDING)


if __name__ == "__main__":
    while True:
        print_accepted_orders_stickers_and_push_status()
        time.sleep(10)


"""
if __name__ == "__main__":
    manage_and_print_order_stickers(db_order_id=302)
"""
