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


def split_long_line(line, max_width, c, font_name, font_size):
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


def create_order_pdf(order, font_size=10, leading=12, left_margin=5, top_margin=5, file_name="temp_print.pdf"):

    # Extract the relevant data
    name = order[4]
    address = order[5]
    company = order[6]

    # Set Hebrew Titles
    Hebrew_name = "שם: "
    Hebrew_address = "כתובת: "
    Hebrew_company = "חברה: "
    Added_text = "תודה שבחרתם בנו, שיהיה בתאבון!"
    Added_text2 = "צוות מיידיז :)"

    # Format the text data for the PDF
    order_text = f"""{Hebrew_name}{name}\n{Hebrew_company}{company}\n{Hebrew_address}{address}\n"""
    order_text += f"\n{Added_text}\n{Added_text2}"
    # Register Arial font
    font_folder = "C:\\Users\\My PC\\PycharmProjects\\CibusReader\\assets\\fonts\\Arial"
    pdfmetrics.registerFont(TTFont("Arial", os.path.join(font_folder, "Arial.ttf")))

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
    c.setFont("Arial", font_size, leading=leading)

    # Set the initial text position
    text_x = left_margin * mm
    text_y = c._pagesize[1] - top_margin * mm

    # Draw the text
    lines = order_text.strip().split('\n')
    processed_lines = []
    max_line_width = 155
    for line in lines:
        if c.stringWidth(line, "Arial", font_size) > max_line_width:
            splitted_lines = split_long_line(line, max_line_width, c, "Arial", font_size)
            processed_lines.extend(splitted_lines)
        else:
            processed_lines.append(line)

    right_margin = 5 * mm

    for line in processed_lines:
        reshaped_text = arabic_reshaper.reshape(line)  # Reshape the text
        bidi_text = get_display(reshaped_text)  # Reorder the text for RTL
        text_width = c.stringWidth(bidi_text, "Arial", font_size)
        text_x = sticker_width - text_width - right_margin  # Set the x-coordinate for RTL text

        c.drawString(text_x, text_y, bidi_text)
        text_y -= leading * mm

    # Save the PDF file
    c.save()

    return temp_file


def create_dish_pdf(text_data, font_size=10, leading=12, left_margin=5, top_margin=5, file_name="temp_print.pdf"):
    dish_text, dish_index, total_dishes = text_data
    # Register Arial font
    font_folder = "C:\\Users\\My PC\\PycharmProjects\\CibusReader\\assets\\fonts\\Arial-Bold"
    pdfmetrics.registerFont(TTFont("Arial-Bold", os.path.join(font_folder, "arial-bold.ttf")))

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
            splitted_lines = split_long_line(line, max_line_width, c, "Arial-Bold", font_size)
            processed_lines.extend(splitted_lines)
        else:
            processed_lines.append(line)

    processed_lines.append(f'{dish_index}/{total_dishes}')

    right_margin = 5 * mm

    for i, line in enumerate(processed_lines):
        if i == len(processed_lines) - 1:  # Check if it's the last line (index information)
            bidi_text = line
            text_x = left_margin * mm  # Set the x-coordinate for LTR text
        else:
            reshaped_text = arabic_reshaper.reshape(line)  # Reshape the text
            bidi_text = get_display(reshaped_text)  # Reorder the text for RTL
            text_width = c.stringWidth(bidi_text, "Arial-Bold", font_size)
            text_x = sticker_width - text_width - right_margin  # Set the x-coordinate for RTL text

        c.drawString(text_x, text_y, bidi_text)
        text_y -= leading * mm
    # Save the PDF file
    c.save()

    return temp_file


def print_and_delete_pdf(file_name):
    # Print the PDF file
    if os.name == 'nt':  # For Windows
        acrobat_path = "C:\\Program Files\\Adobe\\Acrobat DC\\Acrobat\\Acrobat.exe"
        print_command = f'start /min "" "{acrobat_path}" /h /p /s /o "{file_name}"'
        subprocess.run(print_command, shell=True)
    elif os.name == 'posix':  # For macOS and Linux
        print_command = f'lpr "{file_name}"'
        subprocess.run(print_command, shell=True)

    # Wait for a while before deleting the temporary file
    time.sleep(5)

    # Delete the temporary file
    os.unlink(file_name)


def manage_and_print_order_stickers(order):

    # Print bag's sticker
    pdf_file_name = create_order_pdf(order, font_size=8, leading=5, left_margin=0, top_margin=10)
    # print_and_delete_pdf(pdf_file_name)

    order_content = []
    total_dishes = len(order_content)
    # Print order's dishes stickers
    for i, dish in enumerate(order_content):
        dish_text = "מוסקה חצילים ממולאים בבשר ברוטב עגבניות פיקנטי | שף בן גמוניצקי"
        dish_index = 1

        text_data = (dish_text, dish_index, total_dishes)
        # pdf_file_name = create_dish_pdf(text_data, font_size=12, leading=5, left_margin=5, top_margin=10)
        # print_and_delete_pdf(pdf_file_name)

if __name__ == "__main__":
    order = fetch_order_by_id(order_id=17)

    manage_and_print_order_stickers(order)

