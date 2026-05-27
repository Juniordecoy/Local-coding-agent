from flask import request, render_template, send_from_directory, abort, Response
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus
from email_config import BLOCKED_EMAILS, BLOCKED_NAMES
import io
import os
import json
import base64
import pytz
import resend
import csv
import time

import secrets

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from collections import Counter

eastern = pytz.timezone("America/New_York")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))

UPLOAD_FOLDER = DATA_DIR / "uploads"
POSTING_PHOTO_FOLDER = UPLOAD_FOLDER / "postingphotos"
SIGNATURE_FOLDER = DATA_DIR / "signatures" / "contactreport"
PDF_FOLDER = DATA_DIR / "email_pdfs"
LOG_FOLDER = DATA_DIR / "logs"
QUIZ_LOG_FOLDER = LOG_FOLDER / "quiz_logs"
SECURITY_LOG_FILE = LOG_FOLDER / "security_log.jsonl"
ACCIDENT_REPORT_LOG_FILE = LOG_FOLDER / "accident_reports.jsonl"
UCR_PHOTO_FOLDER = UPLOAD_FOLDER / "ucr_photos"

for folder in [
    UPLOAD_FOLDER,
    POSTING_PHOTO_FOLDER,
    UCR_PHOTO_FOLDER,
    SIGNATURE_FOLDER,
    PDF_FOLDER,
    LOG_FOLDER,
    QUIZ_LOG_FOLDER,
]:
    folder.mkdir(parents=True, exist_ok=True)

def is_blocked_email(email):
    if not email:
        return False
    return email.strip().lower() in BLOCKED_EMAILS

def build_submission_pdf(subject, form_data, field_map, skip_empty=True):
    submitted_at = datetime.now(eastern).strftime("%Y-%m-%d %I:%M %p %Z")
    timestamp = datetime.now(eastern).strftime("%Y%m%d_%H%M%S")

    name_fields = [
        "your_name",
        "name",
        "driver_name",
        "voter_name",
        "ack_name",
        "quiz_name"
    ]

    submitter = None
    for field in name_fields:
        if field in form_data and form_data[field]:
            submitter = str(form_data[field]).strip()
            break

    if submitter:
        safe_name = "".join(
            c for c in submitter if c.isalnum() or c in (" ", "_", "-")
        ).strip().replace(" ", "_").lower()
    else:
        safe_name = "submission"

    safe_subject = "".join(
        c if c.isalnum() or c in ("_", "-") else "_"
        for c in subject.lower().replace(" ", "_")
    )

    pdf_filename = f"{safe_name}_{safe_subject}_{timestamp}.pdf"
    pdf_path = PDF_FOLDER / pdf_filename

    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    height = letter[1]

    left = 0.75 * inch
    top = height - 0.75 * inch
    y = top

    def draw_line(text, font="Helvetica", size=10, gap=14):
        nonlocal y
        if y < 0.75 * inch:
            c.showPage()
            y = top
        c.setFont(font, size)
        c.drawString(left, y, text)
        y -= gap

    draw_line(subject, font="Helvetica-Bold", size=14, gap=18)
    draw_line(f"Submitted At: {submitted_at}", font="Helvetica", size=10, gap=18)

    for field_name, label in field_map.items():
        value = form_data.get(field_name, "")

        if field_name in {"accident_sketch_image", "accident_sketch_data", "accident_sketch_summary", "do_not_fill"}:
            continue

        if isinstance(value, list):
            value = [str(v).strip() for v in value if str(v).strip()]
            if skip_empty and not value:
                continue
            value = ", ".join(value)
        else:
            value = str(value).strip()
            if skip_empty and not value:
                continue

        lines = str(value).splitlines() or [str(value)]
        draw_line(f"{label}:", font="Helvetica-Bold", size=10, gap=12)

        for line in lines:
            wrapped = []
            words = line.split()
            current = ""

            for word in words:
                test = f"{current} {word}".strip()
                if c.stringWidth(test, "Helvetica", 10) < 470:
                    current = test
                else:
                    wrapped.append(current)
                    current = word

            if current:
                wrapped.append(current)

            for wrapped_line in wrapped:
                draw_line(f"  {wrapped_line}", font="Helvetica", size=10, gap=12)

        y -= 6

    sketch_image_data = form_data.get("accident_sketch_image", "")

    if sketch_image_data and "," in sketch_image_data:
        try:
            header, encoded = sketch_image_data.split(",", 1)
            image_bytes = base64.b64decode(encoded)
            image_reader = ImageReader(io.BytesIO(image_bytes))

            c.showPage()

            page_width, page_height = letter
            left_margin = 0.6 * inch
            top_margin = page_height - 0.75 * inch
            usable_width = page_width - (left_margin * 2)
            max_height = page_height - 1.5 * inch

            img_width, img_height = image_reader.getSize()
            scale = min(usable_width / img_width, max_height / img_height)

            draw_width = img_width * scale
            draw_height = img_height * scale

            x = (page_width - draw_width) / 2
            y = page_height - draw_height - 0.9 * inch

            c.setFont("Helvetica-Bold", 14)
            c.drawString(left_margin, page_height - 0.6 * inch, "Accident Sketch")

            c.drawImage(
                image_reader,
                x,
                y,
                width=draw_width,
                height=draw_height,
                preserveAspectRatio=True,
                mask="auto"
            )

        except Exception as e:
            print("SKETCH IMAGE PDF ERROR:", e)

    c.save()

    with open(pdf_path, "rb") as f:
        pdf_base64 = base64.b64encode(f.read()).decode("utf-8")

    return {
        "filename": pdf_filename,
        "content": pdf_base64,
        "content_type": "application/pdf",
    }, pdf_filename

def log_email_event(
    subject,
    to_email,
    response=None,
    pdf_filename=None,
    attachments=None,
    status="sent",
    error=None,
    form_slug=None,
    submitter_name=None,
    submitter_email=None,
    route_name=None,
):
    log_path = LOG_FOLDER / "email_log.jsonl"
    now = datetime.now(eastern)
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)

    record = {
        "timestamp": now.strftime("%Y-%m-%d %I:%M %p %Z"),
        "timestamp_iso": now.isoformat(),
        "subject": subject,
        "form_slug": form_slug,
        "route_name": route_name,
        "submitter_name": submitter_name,
        "submitter_email": submitter_email,
        "to": [to_email] if isinstance(to_email, str) else to_email,
        "pdf_filename": pdf_filename,
        "attachment_count": len(attachments or []),
        "has_attachments": len(attachments or []) > 0,
        "status": status,
        "email_id": response.get("id") if isinstance(response, dict) else None,
        "error": str(error) if error else None,
        "ip": ip_address,
    }

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def send_form_email(
    subject,
    form_data,
    field_map,
    to_email,
    attachments=None,
    extra_html="",
    skip_empty=True,
    form_slug=None,
    submitter_name=None,
    submitter_email=None,
    route_name=None,
    include_pdf=True,
):
    if submitter_email and is_blocked_email(submitter_email):
        print(f"BLOCKED EMAIL SUBMISSION: {submitter_email} | {subject}")

        log_security_event(
            reason="blocked_email",
            email=submitter_email,
            form_slug=form_slug
        )

        return None

    if submitter_name and submitter_name.strip().lower() in BLOCKED_NAMES:
        print(f"BLOCKED NAME SUBMISSION: {submitter_name} | {subject}")

        log_security_event(
            reason="blocked_name",
            email=submitter_email,
            form_slug=form_slug
        )

        return None

    # Honeypot check
    honeypot_value = form_data.get("do_not_fill")
    if honeypot_value:
        print(f"HONEYPOT TRIGGERED: {honeypot_value} | {subject}")

        log_security_event(
            reason="honeypot",
            email=submitter_email,
            form_slug=form_slug
        )

        return None

    submitted_at = datetime.now(eastern).strftime("%Y-%m-%d %I:%M %p %Z")

    html = f"""
    <h2>{subject}</h2>
    <p><strong>Submitted At:</strong> {submitted_at}</p>
    <hr>
    """

    for field_name, label in field_map.items():
        value = form_data.get(field_name, "")

        if isinstance(value, list):
            value = [str(v).strip() for v in value if str(v).strip()]
            if skip_empty and not value:
                continue
            value = ", ".join(value)
        else:
            value = str(value).strip()
            if skip_empty and not value:
                continue
            value = value.replace("\n", "<br>")

        html += f"<p><strong>{label}:</strong> {value}</p>"

    if extra_html:
        html += extra_html

    all_attachments = list(attachments or [])
    pdf_filename = None

    if include_pdf:
        pdf_attachment, pdf_filename = build_submission_pdf(
            subject=subject,
            form_data=form_data,
            field_map=field_map,
            skip_empty=skip_empty
        )
        all_attachments.append(pdf_attachment)

    params = {
        "from": "Driver Portal <DriverPortal@changingform.com>",
        "to": [to_email] if isinstance(to_email, str) else to_email,
        "subject": subject,
        "html": html,
    }

    if all_attachments:
        params["attachments"] = all_attachments
        print("ATTACHMENT COUNT:", len(all_attachments))

    try:
        response = resend.Emails.send(params)
        print("EMAIL SENT:", subject)
        print("EMAIL RESPONSE:", response)

        log_email_event(
            subject=subject,
            to_email=to_email,
            response=response,
            pdf_filename=pdf_filename,
            attachments=all_attachments,
            status="sent",
            form_slug=form_slug,
            submitter_name=submitter_name,
            submitter_email=submitter_email,
            route_name=route_name,
        )

        return response

    except Exception as e:
        log_email_event(
            subject=subject,
            to_email=to_email,
            pdf_filename=pdf_filename,
            attachments=all_attachments,
            status="failed",
            error=e,
            form_slug=form_slug,
            submitter_name=submitter_name,
            submitter_email=submitter_email,
            route_name=route_name,
        )
        raise


def render_form(template_name):
    submitted = request.args.get("submitted") == "1"
    return render_template(template_name, submitted=submitted)

def save_uploaded_file(uploaded_file, folder, driver_name=None, form_name=None):
    if not uploaded_file or not uploaded_file.filename:
        return None, None

    timestamp = datetime.now(eastern).strftime("%Y%m%d_%H%M%S")
    ext = os.path.splitext(uploaded_file.filename)[1] or ""
    safe_name = (driver_name or "submission").replace(" ", "_").lower()
    safe_form = (form_name or "upload").replace(" ", "_").lower()

    filename = f"{safe_name}_{safe_form}_{timestamp}{ext}"
    filepath = folder / filename

    uploaded_file.save(filepath)
    return filepath, filename

def save_signature_image(signature_data, folder, prefix="signature"):
    if not signature_data or "," not in signature_data:
        return None, None

    header, encoded = signature_data.split(",", 1)
    image_bytes = base64.b64decode(encoded)

    timestamp = datetime.now(eastern).strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.png"
    filepath = folder / filename

    with open(filepath, "wb") as f:
        f.write(image_bytes)

    return filepath, filename


def build_uploaded_file_attachment(uploaded_file, driver_name=None, form_name=None):
    if not uploaded_file or not uploaded_file.filename:
        return None

    file_bytes = uploaded_file.read()
    if not file_bytes:
        return None

    encoded_content = base64.b64encode(file_bytes).decode("utf-8")
    filename = uploaded_file.filename

    if driver_name and form_name:
        safe_name = driver_name.replace(" ", "_").lower()
        safe_form = form_name.replace(" ", "_").lower()
        ext = os.path.splitext(uploaded_file.filename)[1] or ".jpg"
        filename = f"{safe_name}_{safe_form}{ext}"

    attachment = {
        "filename": filename,
        "content": encoded_content,
    }

    if uploaded_file.mimetype:
        attachment["content_type"] = uploaded_file.mimetype

    return attachment


def build_uploaded_file_attachments(uploaded_files, driver_name=None, form_name=None):
    attachments = []

    for i, uploaded_file in enumerate(uploaded_files, start=1):
        attachment = build_uploaded_file_attachment(
            uploaded_file,
            driver_name=driver_name,
            form_name=f"{form_name}_{i}" if form_name else None
        )

        if attachment:
            attachments.append(attachment)

    return attachments

def build_latest_log_csv_attachment():
    log_path = LOG_FOLDER / "email_log.jsonl"

    if not log_path.exists():
        raise FileNotFoundError("No log file found yet.")

    rows = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

    if not rows:
        raise ValueError("Log file exists but has no entries.")

    timestamp = datetime.now(eastern).strftime("%Y%m%d_%H%M%S")
    csv_filename = f"email_log_export_{timestamp}.csv"
    csv_path = LOG_FOLDER / csv_filename

    fieldnames = [
        "timestamp",
        "timestamp_iso",
        "subject",
        "form_slug",
        "route_name",
        "submitter_name",
        "submitter_email",
        "to",
        "pdf_filename",
        "attachment_count",
        "has_attachments",
        "status",
        "email_id",
        "error",
        "ip",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            to_value = row.get("to", "")
            if isinstance(to_value, list):
                to_value = ", ".join(to_value)

            writer.writerow({
                "timestamp": row.get("timestamp", ""),
                "timestamp_iso": row.get("timestamp_iso", ""),
                "subject": row.get("subject", ""),
                "form_slug": row.get("form_slug", ""),
                "route_name": row.get("route_name", ""),
                "submitter_name": row.get("submitter_name", ""),
                "submitter_email": row.get("submitter_email", ""),
                "to": to_value,
                "pdf_filename": row.get("pdf_filename", ""),
                "attachment_count": row.get("attachment_count", ""),
                "has_attachments": row.get("has_attachments", ""),
                "status": row.get("status", ""),
                "email_id": row.get("email_id", ""),
                "error": row.get("error", ""),
                "ip": row.get("ip", ""),
            })

    with open(csv_path, "rb") as f:
        encoded_csv = base64.b64encode(f.read()).decode("utf-8")

    return {
        "filename": csv_filename,
        "content": encoded_csv,
        "content_type": "text/csv",
    }

def build_accident_report_log_csv_attachment():
    log_path = ACCIDENT_REPORT_LOG_FILE

    if not log_path.exists():
        raise FileNotFoundError("No accident report log file found yet.")

    rows = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

    if not rows:
        raise ValueError("Accident report log exists but has no entries.")

    timestamp = datetime.now(eastern).strftime("%Y%m%d_%H%M%S")
    csv_filename = f"accident_report_log_export_{timestamp}.csv"
    csv_path = LOG_FOLDER / csv_filename

    fieldnames = [
        "report_id",
        "timestamp",
        "timestamp_iso",
        "driver_name",
        "accident_date",
        "accident_time",
        "location",
        "pdf_filename",
        "ip",
        "edit_resubmitter_name",
        "edit_resubmitter_comment",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({
                "report_id": row.get("report_id", ""),
                "timestamp": row.get("timestamp", ""),
                "timestamp_iso": row.get("timestamp_iso", ""),
                "driver_name": row.get("driver_name", ""),
                "accident_date": row.get("accident_date", ""),
                "accident_time": row.get("accident_time", ""),
                "location": row.get("location", ""),
                "pdf_filename": row.get("pdf_filename", ""),
                "ip": row.get("ip", ""),
                "edit_resubmitter_name": row.get("form_data", {}).get("edit_resubmitter_name", ""),
                "edit_resubmitter_comment": row.get("form_data", {}).get("edit_resubmitter_comment", ""),
            })

    with open(csv_path, "rb") as f:
        encoded_csv = base64.b64encode(f.read()).decode("utf-8")

    return {
        "filename": csv_filename,
        "content": encoded_csv,
        "content_type": "text/csv",
    }

def download_return_checklist_log_csv():
    log_path = os.path.join(LOG_FOLDER, "return_checklist_log.jsonl")

    section_items = {
        "does_unit_have": [
            "2 Sets of Keys",
            "4 Thumb Screws & L-Bracket",
            "Vinyl Pole",
            "Max Height Stickers",
            "Extra Fuses Bag (12 fuses)",
            "Fire Extinguisher",
            "Wheel Simulators",
            "Safety Triangles",
            "DOT/FMCSA Decal on Both Cab Doors",
            "Graphics on Backdoor",
            "X2 Storage Bins (Clips, Fluids)",
        ],
        "working_components": [
            "Running Lights",
            "Billboard Lights",
            "Brake Lights",
            "Heater/A/C",
            "Tablet",
            "Inverter",
            "Vinyl System Inspection/Working",
            "Camera System Tested",
            "XRS System with Mount Installed",
            "Samsara",
            "Review under cab",
        ],
        "paperwork": [
            "DOT/State Inspection",
            "Registration Card",
            "Insurance Card",
            "Merchants Packet",
            "Fuel Card",
            "Accident Form",
            "Tow Form",
            "OMNITRACS XRS Cab Card",
            "DOT Exemption Form",
        ],
        "bin_1": [
            "Screw Driver",
            "Lug Wrench",
            "Extender",
            "Channel locks",
            "Clips",
        ],
        "bin_2_all_trucks": [
            "Windshield Washer Fluid",
            "Rain-X 2 in 1 Glass Cleaner",
            "Disinfecting Wipes",
            "Simple Green All Purpose Cleaner",
            "Black Magic Tire Wet",
            "Black Magic No Scrub Wheel Cleaner",
        ],
        "bin_2_new_gas": [
            "Engine Oil (5W-30)",
            "Coolant (50/50 Dexcool)",
            "Power Steering Fluid (Dexron VI)",
            "Brake Fluid (DOT 3)",
            "Transmission Fluid (Dexron VI)",
        ],
        "bin_2_new_diesel": [
            "Engine Oil (15W-40)",
            "Isuzu Coolant Green",
            "Power Steering Fluid (Dexron VI)",
            "Brake Fluid (DOT 3)",
            "Isuzu SCS Transmission Fluid",
            "DEF (Diesel Exhaust Fluid)",
        ],
        "bin_2_old_diesel": [
            "Engine Oil (15W-40)",
            "Coolant (50/50 Color Match)",
            "Power Steering Fluid (Dexron VI)",
            "Brake Fluid (DOT 3)",
            "Transmission Fluid (Dexron VI)",
        ],
    }

    fieldnames = [
        "timestamp_iso",
        "unit_number",
        "checklist_date",
    ]

    fieldnames.extend(section_items["does_unit_have"])
    fieldnames.append("comment_1")

    fieldnames.extend(section_items["working_components"])
    fieldnames.append("comment_2")

    fieldnames.extend(section_items["paperwork"])
    fieldnames.append("comment_3")

    fieldnames.extend(section_items["bin_1"])
    fieldnames.append("comment_4")

    fieldnames.extend(section_items["bin_2_all_trucks"])
    fieldnames.append("comment_5")

    fieldnames.extend(section_items["bin_2_new_gas"])
    fieldnames.append("comment_6")

    fieldnames.extend(section_items["bin_2_new_diesel"])
    fieldnames.append("comment_7")

    fieldnames.extend(section_items["bin_2_old_diesel"])
    fieldnames.append("comment_8")

    fieldnames.extend([
        "completed_by",
        "timestamp",
    ])

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue

                entry = json.loads(line)

                row = {
                    "timestamp_iso": entry.get("timestamp_iso", ""),
                    "unit_number": entry.get("unit_number", ""),
                    "checklist_date": entry.get("checklist_date", ""),
                    "comment_1": entry.get("comment_1", ""),
                    "comment_2": entry.get("comment_2", ""),
                    "comment_3": entry.get("comment_3", ""),
                    "comment_4": entry.get("comment_4", ""),
                    "comment_5": entry.get("comment_5", ""),
                    "comment_6": entry.get("comment_6", ""),
                    "comment_7": entry.get("comment_7", ""),
                    "comment_8": entry.get("comment_8", ""),
                    "completed_by": entry.get("completed_by", ""),
                    "timestamp": entry.get("timestamp", ""),
                }

                for section_name, items in section_items.items():
                    checked_items = entry.get(section_name, [])

                    for item in items:
                        row[item] = "X" if item in checked_items else ""

                writer.writerow(row)

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=return_checklist_log.csv"
        },
    )

def clean_form_data(form):
    data = form.to_dict(flat=False)
    cleaned = {}

    for key, value in data.items():
        cleaned_values = [v.strip() for v in value if isinstance(v, str) and v.strip()]

        if len(cleaned_values) == 1:
            cleaned[key] = cleaned_values[0]
        else:
            cleaned[key] = cleaned_values

    return cleaned

def read_log_rows():
    log_path = LOG_FOLDER / "email_log.jsonl"
    rows = []

    if not log_path.exists():
        return rows

    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return rows


def get_log_summary():
    rows = read_log_rows()
    now = datetime.now(eastern)
    today = now.date()
    week_ago = now - timedelta(days=7)

    total_submissions = len(rows)
    today_submissions = 0
    week_submissions = 0
    failed_submissions = 0
    with_attachments = 0

    form_counter = Counter()

    for row in rows:
        if row.get("status") == "failed":
            failed_submissions += 1

        attachment_count = row.get("attachment_count", 0) or 0
        if row.get("has_attachments") is True or attachment_count > 1:
            with_attachments += 1

        form_slug = row.get("form_slug")
        if form_slug:
            form_counter[form_slug] += 1

        row_dt = None

        timestamp_iso = row.get("timestamp_iso")
        if timestamp_iso:
            try:
                row_dt = datetime.fromisoformat(timestamp_iso)
            except Exception:
                row_dt = None

        if row_dt is None:
            timestamp_str = row.get("timestamp")
            if timestamp_str:
                try:
                    timestamp_no_tz = " ".join(timestamp_str.split(" ")[:-1])
                    naive_dt = datetime.strptime(timestamp_no_tz, "%Y-%m-%d %I:%M %p")
                    row_dt = eastern.localize(naive_dt)
                except Exception:
                    row_dt = None

        if row_dt:
            if row_dt.date() == today:
                today_submissions += 1
            if row_dt >= week_ago:
                week_submissions += 1

    return {
        "total_submissions": total_submissions,
        "today_submissions": today_submissions,
        "week_submissions": week_submissions,
        "failed_submissions": failed_submissions,
        "with_attachments": with_attachments,
        "top_forms": form_counter.most_common(5),
    }

def log_monthly_quiz_submission(quiz_id, employee_name, answers):
    """
    Logs a monthly quiz submission to a CSV file.

    quiz_id: str -> format "YYYY_MM" (example: "2026_03")
    employee_name: str
    answers: list -> ordered answers like [Q1, Q2, Q3, ...]
    """
    file_path = QUIZ_LOG_FOLDER / f"quiz_log_{quiz_id}.csv"
    file_exists = file_path.exists()

    submitted_at = datetime.now(eastern).strftime("%Y-%m-%d %I:%M %p %Z")

    headers = ["Name", "Submitted At"] + [f"Q{i}" for i in range(1, len(answers) + 1)]
    row = [employee_name, submitted_at] + answers

    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(headers)

        writer.writerow(row)

def maps_link(address):
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(address)}"

def resend_failed_email_by_id(email_id):
    rows = read_log_rows()

    for row in rows:
        if row.get("email_id") != email_id:
            continue

        pdf_filename = row.get("pdf_filename")
        to_email = row.get("to")
        subject = row.get("subject")

        attachment = None

        if pdf_filename:
            pdf_path = PDF_FOLDER / pdf_filename

            if pdf_path.exists():
                with open(pdf_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")

                attachment = {
                    "filename": pdf_filename,
                    "content": encoded,
                    "content_type": "application/pdf",
                }
            else:
                print(f"Missing file: {pdf_filename}")

        try:
            resend.Emails.send({
                "from": "Driver Portal <DriverPortal@changingform.com>",
                "to": [to_email],
                "subject": f"[RESEND] {subject}",
                "html": "<p>Re-sent submission (previous attempt failed).</p>",
                "attachments": [attachment] if attachment else [],
            })

            print(f"Resent email_id: {email_id} to {to_email}")
            return True

        except Exception as e:
            print(f"FAILED AGAIN: {email_id} -> {e}")
            return False

    print(f"Email ID not found: {email_id}")
    return False

def build_security_log_csv_attachment():
    log_path = SECURITY_LOG_FILE

    if not log_path.exists():
        raise FileNotFoundError("No security log file found yet.")

    rows = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

    if not rows:
        raise ValueError("Security log exists but has no entries.")

    timestamp = datetime.now(eastern).strftime("%Y%m%d_%H%M%S")
    csv_filename = f"security_log_export_{timestamp}.csv"
    csv_path = LOG_FOLDER / csv_filename

    fieldnames = [
        "timestamp",
        "timestamp_iso",
        "reason",
        "email",
        "form_slug",
        "ip",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({
                "timestamp": row.get("timestamp", ""),
                "timestamp_iso": row.get("timestamp_iso", ""),
                "reason": row.get("reason", ""),
                "email": row.get("email", ""),
                "form_slug": row.get("form_slug", ""),
                "ip": row.get("ip", ""),
            })

    with open(csv_path, "rb") as f:
        encoded_csv = base64.b64encode(f.read()).decode("utf-8")

    return {
        "filename": csv_filename,
        "content": encoded_csv,
        "content_type": "text/csv",
    }

def log_security_event(reason, email=None, form_slug=None):
    now = datetime.now(eastern)

    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)

    record = {
        "timestamp": now.strftime("%Y-%m-%d %I:%M %p %Z"),
        "timestamp_iso": now.isoformat(),
        "reason": reason,
        "email": email,
        "form_slug": form_slug,
        "ip": ip_address,  # 👈 ADD THIS
    }

    with open(SECURITY_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

def format_accident_sketch_data(sketch_data_raw):
    if not sketch_data_raw:
        return "No sketch items placed."

    try:
        items = json.loads(sketch_data_raw)
    except Exception:
        return f"Sketch data: {sketch_data_raw}"

    if not items:
        return "No sketch items placed."

    lines = []
    for i, item in enumerate(items, start=1):
        tool = item.get("tool", "")
        x = item.get("x", "")
        y = item.get("y", "")
        direction = item.get("direction", "")

        tool_label = tool.replace("_", " ").title()

        line = f"{i}. {tool_label} | X: {x} | Y: {y}"
        if direction:
            line += f" | Direction: {direction}"

        lines.append(line)

    return "\n".join(lines)

def cleanup_old_files(folder, days=7):
    cutoff = time.time() - (days * 24 * 60 * 60)

    for file_path in folder.glob("*"):
        try:
            if file_path.is_file() and file_path.stat().st_mtime < cutoff:
                file_path.unlink()
                print(f"Deleted old file: {file_path.name}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

def run_storage_cleanup():
    cleanup_old_files(POSTING_PHOTO_FOLDER, days=7)
    cleanup_old_files(UCR_PHOTO_FOLDER, days=14)
    cleanup_old_files(PDF_FOLDER, days=30)

def generate_accident_report_id():
    now = datetime.now(eastern)
    return f"ACC-{now.strftime('%Y%m%d-%H%M%S')}"

def log_accident_report(report_id, form_data, pdf_filename=None):
    now = datetime.now(eastern)
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)

    record = {
        "report_id": report_id,
        "timestamp": now.strftime("%Y-%m-%d %I:%M %p %Z"),
        "timestamp_iso": now.isoformat(),
        "driver_name": form_data.get("name", ""),
        "accident_date": form_data.get("accident_date", ""),
        "accident_time": form_data.get("accident_time", ""),
        "location": form_data.get("city_county_state", ""),
        "pdf_filename": pdf_filename,
        "ip": ip_address,
        "form_data": form_data,
    }

    with open(ACCIDENT_REPORT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def find_accident_report_by_id(report_id):
    log_path = LOG_FOLDER / "accident_reports.jsonl"

    if not log_path.exists():
        return None

    report_id = str(report_id or "").strip()
    found_report = None

    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            if row.get("report_id") == report_id:
                found_report = row

    return found_report