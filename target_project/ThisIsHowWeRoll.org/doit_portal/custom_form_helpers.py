import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader

from helpers import eastern, PDF_FOLDER, BASE_DIR

def build_accident_report_pdf(form_data):
    report_id = form_data.get("report_id", "accident_report")
    pdf_filename = f"Vehicle_accident_report_{report_id}.pdf"
    pdf_path = PDF_FOLDER / pdf_filename

    c = canvas.Canvas(str(pdf_path), pagesize=letter)

    page_width, page_height = letter
    left_margin = 0.6 * inch
    right_margin = page_width - 0.6 * inch
    y = page_height - 0.75 * inch

    def wrap_text(text, font_name, font_size, max_width):
        words = str(text or "").split()
        lines = []
        current = ""

        for word in words:
            test = f"{current} {word}".strip()
            if c.stringWidth(test, font_name, font_size) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines

    def draw_wrapped_value(label, value, x, y, label_width=90, max_width=200, line_gap=12):
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, f"{label}:")

        lines = wrap_text(value, "Helvetica", 9, max_width)

        c.setFont("Helvetica", 9)
        for i, line in enumerate(lines):
            c.drawString(x + label_width, y - (i * line_gap), line)

        return y - max(line_gap * len(lines), line_gap)

    def draw_checkbox(label, x, y, checked=False):
        box_size = 6

        # draw square
        c.rect(x, y, box_size, box_size)

        # fill if checked
        if checked:
            c.setFillColorRGB(0, 0, 0)
            c.rect(x + 1, y, box_size, box_size, fill=1, stroke=0)

        # reset color
        c.setFillColorRGB(0, 0, 0)

        # label
        c.setFont("Helvetica", 10)
        c.drawString(x + 12, y, label)

    def draw_label_value(label, value, x, y):
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x, y, f"{label}:")
        c.setFont("Helvetica", 9)
        c.drawString(x + 90, y, str(value or ""))

    def draw_page_header():
        y = page_height - 0.75 * inch

        c.setFont("Helvetica-Bold", 16)
        c.setFillColorRGB(0.75, 0, 0)
        c.drawString(left_margin, y, "Vehicle Accident Report")

        report_id = form_data.get("report_id", "")

        c.setFont("Helvetica", 10)

        # right align
        c.drawRightString(
            right_margin,
            y,
            f"Report ID: {report_id}"
        )

        y -= 6
        c.setLineWidth(1)
        c.line(left_margin, y, right_margin, y)

        c.setFillColorRGB(0, 0, 0)
        y -= 16

        return y

    def draw_section(title, y):
        c.setFont("Helvetica-Bold", 11)
        c.drawString(left_margin, y, title)
        return y - 14

    y = draw_page_header()

    # Row 1
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 30, y, "Name:")
    c.drawString(left_margin + 250, y, "Age:")

    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 70, y, str(form_data.get("name", "") or ""))
    c.drawString(left_margin + 290, y, str(form_data.get("age", "") or ""))
    y -= 14

    # Row 2
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 30, y, "Address:")
    c.drawString(left_margin + 250, y, "City / State / Zip:")

    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 80, y, str(form_data.get("address", "") or ""))
    c.drawString(left_margin + 340, y, str(form_data.get("city_state_zip", "") or ""))
    y -= 14

    # Row 3
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin, y, "Drivers License:")
    c.drawString(left_margin + 150, y, "License State:")
    c.drawString(left_margin + 260, y, "License Plate:")
    c.drawString(left_margin + 390, y, "Plate State:")

    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 85, y, str(form_data.get("drivers_license", "") or ""))
    c.drawString(left_margin + 225, y, str(form_data.get("license_state", "") or ""))
    c.drawString(left_margin + 330, y, str(form_data.get("license_plate", "") or ""))
    c.drawString(left_margin + 450, y, str(form_data.get("plate_state", "") or ""))
    y -= 20

    # INJURIES header bar
    c.setFillColorRGB(0.85, 0.85, 0.85)
    c.rect(left_margin, y - 10, right_margin - left_margin, 14, fill=1, stroke=1)

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString((left_margin + right_margin) / 2, y - 7, "INJURIES - Describe nature of any apparent injuries")
    y -= 24

    # Driver Injury
    y = draw_wrapped_value(
        "Driver Injury",
        form_data.get("driver_injury", ""),
        left_margin + 6,
        y,
        label_width=75,
        max_width=430
    )
    y -= 8

    # Passenger
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "Passenger Name:")
    c.drawString(left_margin + 280, y, "Injury:")

    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 100, y, str(form_data.get("passenger_name", "") or ""))
    c.drawString(left_margin + 315, y, str(form_data.get("passenger_injury", "") or ""))
    y -= 20

    # Other Driver
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "Other Driver Name:")
    c.drawString(left_margin + 280, y, "Injury:")

    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 100, y, str(form_data.get("other_driver_name", "") or ""))
    c.drawString(left_margin + 315, y, str(form_data.get("other_driver_injury", "") or ""))
    y -= 20

    # Other Passenger
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "Other Passenger Name:")
    c.drawString(left_margin + 280, y, "Injury:")

    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 125, y, str(form_data.get("other_passenger_name", "") or ""))
    c.drawString(left_margin + 315, y, str(form_data.get("other_passenger_injury", "") or ""))
    y -= 20

    other_injuries_rows = form_data.get("other_injuries", []) or []
    row_count1 = max(1, len(other_injuries_rows))

    for i in range(row_count1):
        other_injuries = other_injuries_rows[i] if i < len(other_injuries_rows) else {}

        name = other_injuries.get("name", "")
        injury = other_injuries.get("injury", "")

        # row line 1
        c.setFont("Helvetica-Bold", 10)
        c.drawString(left_margin + 6, y, "Other Name:")
        c.drawString(left_margin + 280, y, "Injury:")

        c.setFont("Helvetica", 9)
        c.drawString(left_margin + 80, y, str(name or ""))
        c.drawString(left_margin + 315, y, str(injury or ""))
        y -= 18

    y -= 2

    # Police Officer header bar
    c.setFillColorRGB(0.85, 0.85, 0.85)
    c.rect(left_margin, y - 10, right_margin - left_margin, 14, fill=1, stroke=1)

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString((left_margin + right_margin) / 2, y - 7, "POLICE OFFICER ASSISTING")
    y -= 24

    # Police Officer Name
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "Officer Name:")
    c.drawString(left_margin + 280, y, "Police Report Made? ")

    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 80, y, str(form_data.get("officer_name", "") or ""))
    c.drawString(left_margin + 385, y, str(form_data.get("police_report_made", "") or ""))
    y -= 20

    # Headquaters
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "Headquaters:")
    c.drawString(left_margin + 280, y, "Badge #:")

    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 80, y, str(form_data.get("headquarters", "") or ""))
    c.drawString(left_margin + 325, y, str(form_data.get("badge_number", "") or ""))
    y -= 20

    # Driver Citation(s)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "Driver Citation(s) Issued:")

    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 130, y, str(form_data.get("driver_citation_issued", "") or ""))

    y = draw_wrapped_value(
        "If yes, state reason",
        form_data.get("driver_citation_reason", ""),
        left_margin + 240,
        y,
        label_width=95,
        max_width=200
    )
    y -= 6

    # Other Driver Citation(s)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "Other Driver")
    c.drawString(left_margin + 6, y - 12, "Citation(s) Issued:")

    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 105, y-6, str(form_data.get("other_driver_citation_issued", "") or ""))

    y = draw_wrapped_value(
        "If yes, state reason",
        form_data.get("other_driver_citation_reason", ""),
        left_margin + 240,
        y,
        label_width=95,
        max_width=200
    )
    y -= 6


    # Property Damage header bar
    c.setFillColorRGB(0.85, 0.85, 0.85)
    c.rect(left_margin, y - 10, right_margin - left_margin, 14, fill=1, stroke=1)

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString((left_margin + right_margin) / 2, y - 7, "PROPERTY DAMAGE – Describe nature of damage")
    y -= 24

    # Driver Vehicle
    y = draw_wrapped_value(
        "Driver Vehicle",
        form_data.get("driver_vehicle_damage", ""),
        left_margin + 6,
        y,
        label_width=75,
        max_width=430
    )
    y -= 8

    # Other Vehicle
    y = draw_wrapped_value(
        "Other Vehicle",
        form_data.get("other_vehicle_damage", ""),
        left_margin + 6,
        y,
        label_width=75,
        max_width=430
    )
    y -= 8

    # Other Driver Name
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "Other Driver Name:")
    c.drawString(left_margin + 240, y, "Phone #:")
    c.drawString(left_margin + 390, y, "License #:")

    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 110, y, str(form_data.get("other_driver_contact_name", "") or ""))
    c.drawString(left_margin + 290, y, str(form_data.get("other_driver_phone", "") or ""))
    c.drawString(left_margin + 445, y, str(form_data.get("other_driver_license", "") or ""))
    y -= 20

    # Other Vehicle Owner
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "Other Vehicle Owner:")
    c.drawString(left_margin + 240, y-6, "Phone #:")
    c.drawString(left_margin + 390, y-6, "Vehicle Make:")

    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 6, y - 12, "(If not same as Driver)")
    c.drawString(left_margin + 110, y, str(form_data.get("other_vehicle_owner", "") or ""))
    c.drawString(left_margin + 290, y-6, str(form_data.get("other_owner_phone", "") or ""))
    c.drawString(left_margin + 460, y-6, str(form_data.get("other_vehicle_make", "") or ""))
    y -= 30

    # Insurance Company
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "Insurance Company:")
    c.drawString(left_margin + 240, y, "Phone #:")

    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 115, y, str(form_data.get("insurance_company", "") or ""))
    c.drawString(left_margin + 290, y, str(form_data.get("insurance_phone", "") or ""))
    y -= 20

    # Other Property Damage
    y = draw_wrapped_value(
        "Other Property Damage",
        form_data.get("other_property_damage", ""),
        left_margin + 6,
        y,
        label_width=120,
        max_width=430
    )
    y -= 8

    # Property Owner
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "Property Owner:")
    c.drawString(left_margin + 240, y, "Phone #:")

    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 90, y, str(form_data.get("property_owner", "") or ""))
    c.drawString(left_margin + 290, y, str(form_data.get("property_owner_phone", "") or ""))
    y -= 20

    # Witness header bar
    c.setFillColorRGB(0.85, 0.85, 0.85)
    c.rect(left_margin, y - 10, right_margin - left_margin, 14, fill=1, stroke=1)

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString((left_margin + right_margin) / 2, y - 7, "WITNESSES")
    y -= 24

    witness_rows = form_data.get("witnesses", []) or []
    row_count2 = max(2, len(witness_rows))

    for i in range(row_count2):
        witness = witness_rows[i] if i < len(witness_rows) else {}

        name = witness.get("name", "")
        phone = witness.get("phone", "")
        address = witness.get("address", "")

        # row line 1
        c.setFont("Helvetica-Bold", 10)
        c.drawString(left_margin + 6, y, "Name:")
        c.drawString(left_margin + 250, y, "Phone #:")

        c.setFont("Helvetica", 9)
        c.drawString(left_margin + 45, y, str(name or ""))
        c.drawString(left_margin + 305, y, str(phone or ""))
        y -= 18

        # row line 2
        c.setFont("Helvetica-Bold", 10)
        c.drawString(left_margin + 6, y, "Address:")

        c.setFont("Helvetica", 9)
        c.drawString(left_margin + 60, y, str(address or ""))
        y -= 20

    c.showPage()

    ##### -------------------- Page 2 -------------------------- #####

    y = draw_page_header()

    # Accident Information header bar
    c.setFillColorRGB(0.85, 0.85, 0.85)
    c.rect(left_margin, y - 10, right_margin - left_margin, 14, fill=1, stroke=1)

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString((left_margin + right_margin) / 2, y - 7, "ACCIDENT INFORMATION")
    y -= 28

    # Top bar
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "Date:")
    c.drawString(left_margin + 100, y, "Time:")

    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 40, y, str(form_data.get("accident_date", "") or ""))
    c.drawString(left_margin + 140, y, str(form_data.get("accident_time", "") or ""))

    # AM or PM
    c.setFont("Helvetica", 10)
    am_pm = form_data.get("am_pm", "")

    draw_checkbox("AM", left_margin + 190, y + 2, am_pm == "AM")
    draw_checkbox("PM", left_margin + 190, y - 8, am_pm == "PM")

    light_condition = form_data.get("light_condition", "")

    draw_checkbox("Daylight", left_margin + 240, y + 2, light_condition == "Daylight")
    draw_checkbox("Dark", left_margin + 240, y - 8, light_condition == "Dark")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 315, y, "Direction:")

    your_dir = form_data.get("your_direction", "")
    other_dir = form_data.get("other_direction", "")

    # Yours row
    c.setFont("Helvetica", 10)
    c.drawString(left_margin + 370, y + 8, "Yours")
    c.setFont("Helvetica", 9)
    draw_checkbox("N", left_margin + 410, y + 8, your_dir == "N")
    draw_checkbox("E", left_margin + 440, y + 8, your_dir == "E")
    draw_checkbox("S", left_margin + 470, y + 8, your_dir == "S")
    draw_checkbox("W", left_margin + 500, y + 8, your_dir == "W")

    # Other row
    c.setFont("Helvetica", 10)
    c.drawString(left_margin + 375, y - 8, "Other")
    c.setFont("Helvetica", 9)
    draw_checkbox("N", left_margin + 410, y - 8, other_dir == "N")
    draw_checkbox("E", left_margin + 440, y - 8, other_dir == "E")
    draw_checkbox("S", left_margin + 470, y - 8, other_dir == "S")
    draw_checkbox("W", left_margin + 500, y - 8, other_dir == "W")

    y -= 24

    right_y = y - 45
    right_x = left_margin + 310

    # SPEED
    c.setFont("Helvetica-Bold", 10)
    c.drawString(right_x + 75, right_y, "SPEED")
    right_y -= 14

    c.setFont("Helvetica", 10)
    c.drawString(right_x + 55, right_y, "Driver")
    c.drawString(right_x + 110, right_y, "Other Driver")
    right_y -= 12

    c.setFont("Helvetica", 9)
    c.drawString(right_x, right_y, "Posted:")
    c.drawString(right_x + 55, right_y, str(form_data.get("driver_speed_posted", "") or ""))
    c.drawString(right_x + 110, right_y, str(form_data.get("other_speed_posted", "") or ""))
    right_y -= 12

    c.drawString(right_x, right_y, "Actual:")
    c.drawString(right_x + 55, right_y, str(form_data.get("driver_speed_actual", "") or ""))
    c.drawString(right_x + 110, right_y, str(form_data.get("other_speed_actual", "") or ""))
    right_y -= 24

    # TRAFFIC CONTROL
    c.setFont("Helvetica-Bold", 10)
    c.drawString(right_x, right_y, "TRAFFIC CONTROL")
    right_y -= 16

    c.setFont("Helvetica", 9)
    traffic_values = form_data.get("traffic_control", []) or []

    c.drawString(right_x, right_y, "Stop Sign")
    right_y -= 3
    draw_checkbox("1 Way", right_x, right_y - 14, "1 Way" in traffic_values)
    draw_checkbox("2 Way", right_x + 80, right_y - 14, "2 Way" in traffic_values)
    draw_checkbox("3 Way", right_x + 160, right_y - 14, "3 Way" in traffic_values)

    draw_checkbox("4 Way", right_x, right_y - 28, "4 Way" in traffic_values)
    draw_checkbox("Yield", right_x + 80, right_y - 28, "Yield" in traffic_values)
    draw_checkbox("RR", right_x + 160, right_y - 28, "RR" in traffic_values)

    draw_checkbox("Police/Flag Person", right_x, right_y - 42, "Police/Flag Person" in traffic_values)
    draw_checkbox("Uncont. Intersection", right_x, right_y - 56, "Uncont. Intersection" in traffic_values)
    draw_checkbox("Not an Intersection", right_x, right_y - 70, "Not an Intersection" in traffic_values)

    # Location Title
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "LOCATION")
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(left_margin + 10, y - 5, "Name of Street or Highway Number")
    c.drawString(left_margin + 200, y - 5, "Closet Intersection or Landmark")
    c.drawString(left_margin + 10, y - 35, "City, County, State")

    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 20, y + 5, str(form_data.get("street_or_highway", "") or ""))
    c.drawString(left_margin + 210, y + 5, str(form_data.get("closest_intersection", "") or ""))
    c.drawString(left_margin + 20, y - 25, str(form_data.get("city_county_state", "") or ""))
    y -= 60


    # Weather Title
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "WEATHER")

    weather_values = form_data.get("weather", "") or []
    y -= 16

    c.setFont("Helvetica", 9)
    draw_checkbox("Clear", left_margin + 10, y, "Clear" in weather_values)
    draw_checkbox("Raining / Fog", left_margin + 80, y, "Raining / Fog" in weather_values)
    draw_checkbox("Snowing", left_margin + 160, y, "Snowing" in weather_values)
    draw_checkbox("Fog", left_margin + 225, y, "Fog" in weather_values)
    y -= 14
    draw_checkbox("Sleeting", left_margin + 10, y, "Sleeting" in weather_values)
    draw_checkbox("Dust/Smoke", left_margin + 80, y, "Dust/Smoke" in weather_values)
    draw_checkbox("High Wind", left_margin + 160, y, "High Wind" in weather_values)
    draw_checkbox("Other", left_margin + 225, y, "Other" in weather_values)
    y -= 18

    # Area Title
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "AREA")

    area_value = form_data.get("area", "") or []
    y -= 16

    c.setFont("Helvetica", 9)
    draw_checkbox("Residential", left_margin + 10, y, area_value == "Residential")
    draw_checkbox("Commercial", left_margin + 80, y, area_value == "Commercial")
    draw_checkbox("Rural", left_margin + 160, y, area_value == "Rural")
    draw_checkbox("Other", left_margin + 225, y, area_value == "Other")
    y -= 18

    # Pavement Title
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "PAVEMENT")

    pavement_values = form_data.get("pavement", "") or []
    y -= 16

    c.setFont("Helvetica", 9)
    draw_checkbox("Asphalt", left_margin + 10, y, pavement_values == "Asphalt")
    draw_checkbox("Concrete", left_margin + 80, y, pavement_values == "Concrete")
    draw_checkbox("Gravel/Dirt", left_margin + 160, y, pavement_values == "Gravel/Dirt")
    draw_checkbox("Brick/Stone", left_margin + 225, y, pavement_values == "Brick/Stone")
    y -= 14
    draw_checkbox("Steel", left_margin + 10, y, pavement_values == "Steel")
    draw_checkbox("Wood", left_margin + 80, y, pavement_values == "Wood")
    draw_checkbox("Other", left_margin + 160, y, pavement_values == "Other")
    y -= 18

    # Condition Title
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 6, y, "CONDITION")

    condition_values = form_data.get("conditions", []) or []
    y -= 16

    c.setFont("Helvetica", 9)
    draw_checkbox("Dry", left_margin + 10, y, "Dry" in condition_values)
    draw_checkbox("Wet", left_margin + 80, y, "Wet" in condition_values)
    draw_checkbox("Slippery", left_margin + 160, y, "Slippery" in condition_values)
    draw_checkbox("Pot Holes", left_margin + 225, y, "Pot Holes" in condition_values)
    y -= 14
    draw_checkbox("Other", left_margin + 10, y, "Other" in condition_values)
    y -= 18

    # Seat Belt Title
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 310, y + 40, "SEAT BELT USED:")
    seat_belt = form_data.get("seat_belt_used", "")

    draw_checkbox("Yes", left_margin + 420, y + 40, seat_belt == "Yes")
    draw_checkbox("No", left_margin + 460, y + 40, seat_belt == "No")

    # AIRBAG Title
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin + 310, y + 25, "AIR BAG INFLATED:")
    seat_belt = form_data.get("air_bag_inflated", "")

    draw_checkbox("Yes", left_margin + 420, y + 25, seat_belt == "Yes")
    draw_checkbox("No", left_margin + 460, y + 25, seat_belt == "No")

    # Accident Information header bar
    c.setFillColorRGB(0.85, 0.85, 0.85)
    c.rect(left_margin, y - 10, right_margin - left_margin, 14, fill=1, stroke=1)

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString((left_margin + right_margin) / 2, y - 7, "ACCIDENT DESCRIPTION")
    y -= 28

    line_y = y

    # draw 4 lines
    for i in range(4):
        c.line(left_margin + 6, line_y, right_margin - 6, line_y)
        line_y -= 16

    description = str(form_data.get("accident_description", "") or "").strip()

    if description:
        text_obj = c.beginText()
        text_obj.setTextOrigin(left_margin + 10, y + 2)
        text_obj.setFont("Helvetica", 9)
        text_obj.setLeading(16)

        max_width = right_margin - left_margin - 20

        words = description.split()
        line = ""

        for word in words:
            test_line = f"{line} {word}".strip()
            if c.stringWidth(test_line, "Helvetica", 9) < max_width:
                line = test_line
            else:
                text_obj.textLine(line)
                line = word

        if line:
            text_obj.textLine(line)

        c.drawText(text_obj)

    y -= 78

    # Accident Sketch header bar
    c.setFillColorRGB(0.85, 0.85, 0.85)
    c.rect(left_margin, y - 10, right_margin - left_margin, 14, fill=1, stroke=1)

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString((left_margin + right_margin) / 2, y - 7, "ACCIDENT SKETCH")
    y -= 5

    sketch_bottom = 100
    sketch_data = form_data.get("accident_sketch_image")

    if sketch_data:
        from io import BytesIO

        image_bytes = base64.b64decode(sketch_data.split(",")[1])
        image = ImageReader(BytesIO(image_bytes))

        c.drawImage(
            image,
            left_margin,
            sketch_bottom,
            width=right_margin - left_margin,
            height=170,
            preserveAspectRatio=True,
            mask='auto'
        )

    key_path = BASE_DIR / "static" / "img" / "accident_report" / "Key_chart.png"


    key_image = ImageReader(str(key_path))
    c.drawImage(
        key_image,
        left_margin,
        sketch_bottom - 75,
        width=right_margin - left_margin,
        height=70,
        preserveAspectRatio=True,
        mask='auto'
    )

    c.save()

    with open(pdf_path, "rb") as f:
        pdf_base64 = base64.b64encode(f.read()).decode("utf-8")

    return {
        "filename": pdf_filename,
        "content": pdf_base64,
        "content_type": "application/pdf",
    }, pdf_filename