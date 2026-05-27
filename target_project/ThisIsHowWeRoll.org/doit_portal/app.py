from flask import session, Flask, render_template, request, redirect, url_for, flash, send_file, send_from_directory, abort
from datetime import datetime
import pytz
import resend
import os
import base64
import json
import re
from pathlib import Path

from io import BytesIO
from pypdf import PdfWriter
import cryptography
import uuid
import tempfile

from email_config import FORM_EMAIL_MAP

from helpers import (
    send_form_email, render_form,
    save_signature_image, build_uploaded_file_attachment,
    build_uploaded_file_attachments, build_latest_log_csv_attachment,
    clean_form_data, get_log_summary,
    log_monthly_quiz_submission, LOG_FOLDER,
    QUIZ_LOG_FOLDER, SIGNATURE_FOLDER,
    maps_link, resend_failed_email_by_id,
    save_uploaded_file, build_security_log_csv_attachment,
    format_accident_sketch_data, POSTING_PHOTO_FOLDER,
    run_storage_cleanup, generate_accident_report_id,
    log_accident_report, find_accident_report_by_id,
    build_accident_report_log_csv_attachment, UCR_PHOTO_FOLDER,
    download_return_checklist_log_csv,log_security_event,
)

from custom_form_helpers import (
    build_accident_report_pdf,
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024  # 30MB upload limit

eastern = pytz.timezone("America/New_York")

resend.api_key = os.getenv("RESEND_API_KEY")
app.secret_key = os.getenv("SECRET_KEY", "dev-only-secret")

LEAD_PASSWORD = "outdoors"   # change this to your real password
OR_TEST_PASSWORD = "test123"  # change this later

RECENT_POSTING_SUBMISSIONS = {}

@app.route("/")
def index():
    # Put your real incident start timestamps here later (ISO format)
    # Example: "2026-02-20T14:30:00"
    # /?resetReferral=1
    last_accident = eastern.localize(
        datetime(2025, 10, 29, 14, 15, 0)
    ).isoformat()
    last_incident = eastern.localize(
        datetime(2026, 4, 24, 16, 0, 0)
    ).isoformat()
    return render_template(
        "index.html",
        incident_a_start=last_accident,
        incident_b_start=last_incident,
    )

@app.route("/payroll-hr")
def payroll_hr():
    return render_template("payroll_hr.html")

@app.route("/benefits")
def benefits():
    return render_template("benefits.html")

@app.route("/benefit-info")
def benefit_info():
    return render_template("benefit_info.html")

@app.route("/dresscode")
def dresscode():
    return render_template("dresscode.html")

@app.route("/gettingpaid")
def gettingpaid():
    return render_template("gettingpaid.html")

@app.route("/labor-law-posters")
def labor_law_posters():
    return render_template("labor_law_posters.html")

@app.route("/comdata")
def comdata():
    return render_template("comdata.html")

@app.route("/employee-navigator")
def employee_navigator():
    return render_template("employee_navigator.html")

@app.route("/perdiem")
def perdiem():
    return render_template("perdiem.html")

@app.route("/photos")
def photos():
    return render_template("photos.html")

@app.route("/photoexamples")
def photoexamples():
    return render_template("photoexamples.html")

@app.route("/pops")
def pops():
    return render_template("pops.html")

@app.route("/dankellyaward")
def dankellyaward():
    return render_template("dankellyaward.html")

@app.route("/contestwinners")
def contestwinners():
    return render_template("contestwinners.html")

# Year pages (create templates for these)
@app.route("/contestwinners/<year>")
def contest_winners(year):

    template_map = {
        "2023": "cw_2023.html",
        "2022": "cw_2022.html",
        "2021": "cw_2021.html",
        "2020": "cw_2020.html",
        "2019": "cw_2019.html",
        "2018": "cw_2018.html",
        "2017": "cw_2017.html",
        "2016": "cw_2016.html",
        "2014-2015": "cw_2014_2015.html"
    }

    if year not in template_map:
        return "Not Found", 404

    return render_template(template_map[year])

@app.route("/contestrules")
def contestrules():
    return render_template("contestrules.html")

@app.route("/tipsandtricks")
def tipsandtricks():
    return render_template("tipsandtricks.html")

@app.route("/videos")
def videos():
    return render_template("videos.html")

@app.route("/new-hires")
def new_hires():
    return render_template("new_hires.html")

@app.route("/dot")
def dot():
    return render_template("dot.html")

@app.route("/temp-driver")
def temp_driver():
    return render_template("temp_driver.html")

@app.route("/forms")
def forms():
    return render_template("forms.html")

@app.route("/accident-forms")
def accident_forms():
    return render_template("accident_forms.html")

@app.route("/driver-expense")
def driver_expense():
    return render_template("driver_expense.html")

@app.route("/expense-form")
def expense_form():
    return render_template("expense_form.html")

@app.route("/vehicleinfo")
def vehicleinfo():
    return render_template("vehicleinfo.html")

@app.route("/insurance")
def insurance():
    return render_template("insurance.html")

@app.route("/maintenance")
def maintenance():
    return render_template("maintenance.html")

@app.route("/gas-air-cabin-filter")
def gas_air_cabin_filter():
    return render_template("gas_air_cabin_filter.html")

@app.route("/healthandsafety")
def healthandsafety():
    return render_template("healthandsafety.html")

@app.route("/safetyfirst")
def safetyfirst():
    return render_template("safetyfirst.html")

@app.route("/healthandfitness")
def healthandfitness():
    return render_template("healthandfitness.html")

@app.route("/safetyvideos")
def safetyvideos():
    return render_template("safetyvideos.html")

@app.route("/2020-health-crisis")
def health_crisis_2020():
    return render_template("health_crisis_2020.html")

@app.route("/vinyls")
def vinyls():
    return render_template("vinyls.html")

@app.route("/ourvinylsystem")
def ourvinylsystem():
    return render_template("ourvinylsystem.html")

@app.route("/vinyltroubleshooting")
def vinyltroubleshooting():
    return render_template("vinyltroubleshooting.html")

@app.route("/perfectvinyls")
def perfectvinyls():
    return render_template("perfectvinyls.html")

@app.route("/contacts")
def contacts():
    return render_template("contacts.html")

@app.route("/preferred-shops")
def preferred_shops():
    data_path = Path(app.static_folder) / "data" / "preferred_shops.json"

    with open(data_path, "r", encoding="utf-8") as f:
        states_data = json.load(f)

    for state in states_data:
        state["anchor"] = state["state"].lower().replace(" ", "-").replace("&", "and")

        for section_name in ["shops", "washes"]:
            for place in state.get(section_name, []):
                place["maps_url"] = maps_link(place["address"])

    return render_template("preferred_shops.html", states_data=states_data)

@app.route("/lead-login", methods=["GET", "POST"])
def lead_login():
    if request.method == "POST":
        entered_pw = request.form.get("password")

        if entered_pw == LEAD_PASSWORD:
            session["lead_access"] = True
            return redirect(url_for("leads"))  # your lead hub page route
        else:
            return render_template("lead_login.html", error="Incorrect password")

    return render_template("lead_login.html")

@app.route("/leads")
def leads():
    if not session.get("lead_access"):
        return redirect(url_for("lead_login"))
    return render_template("leads.html")  # your hub page

@app.route("/or-login", methods=["GET", "POST"])
def or_login():
    if request.method == "POST":
        entered_pw = request.form.get("password")

        if entered_pw == OR_TEST_PASSWORD:
            session["or_access"] = True
            return redirect(url_for("or_dashboard"))
        else:
            return render_template("or_login.html", error="Incorrect password")

    return render_template("or_login.html")


@app.route("/OR-Dashboard")
def or_dashboard():
    if not session.get("or_access"):
        return redirect(url_for("or_login"))

    today = datetime.now(eastern).strftime("%B %d, %Y")

    schedule_path = Path(app.static_folder) / "data" / "or_campaigns.json"

    with open(schedule_path, "r", encoding="utf-8") as f:
        schedule_rows = json.load(f)

    return render_template(
        "or_dashboard.html",
        schedule_rows=schedule_rows,
        today=today
    )

@app.route("/OR-Calendar")
def or_calendar():
    if not session.get("or_access"):
        return redirect(url_for("or_login"))

    campaign_path = Path(app.static_folder) / "data" / "or_campaigns.json"

    with open(campaign_path, "r", encoding="utf-8") as f:
        calendar_rows = json.load(f)

    return render_template(
        "or_calendar.html",
        calendar_rows=calendar_rows
    )

@app.route("/OR-Codes")
def or_codes():
    if not session.get("or_access"):
        return redirect(url_for("or_login"))

    return render_template("or_codes.html")

@app.route("/OR-Units")
def or_units():
    if not session.get("or_access"):
        return redirect(url_for("or_login"))

    units_path = Path(app.static_folder) / "data" / "or_units.json"
    storage_path = Path(app.static_folder) / "data" / "or_storage_locations.json"

    with open(units_path, "r", encoding="utf-8") as f:
        unit_rows = json.load(f)

    with open(storage_path, "r", encoding="utf-8") as f:
        storage_locations = json.load(f)

    return render_template(
        "or_units.html",
        unit_rows=unit_rows,
        storage_locations=storage_locations
    )

@app.route("/or-add-unit", methods=["POST"])
def or_add_unit():
    if not session.get("or_access"):
        return redirect(url_for("or_login"))

    units_path = Path(app.static_folder) / "data" / "or_units.json"

    with open(units_path, "r", encoding="utf-8") as f:
        units = json.load(f)

    new_unit = {
        "unit_id": f"unit_{request.form.get('unit_number', '').strip()}",
        "unit_number": request.form.get("unit_number", "").strip(),
        "status": request.form.get("status", "").strip(),
        "city": request.form.get("city", "").strip(),
        "state": request.form.get("state", "").strip().upper(),
        "storage_location": request.form.get("storage_location", "").strip(),
        "current_driver": "",
        "notes": request.form.get("notes", "").strip(),
    }

    units.append(new_unit)

    with open(units_path, "w", encoding="utf-8") as f:
        json.dump(units, f, indent=2)

    return redirect(url_for("or_units"))

@app.route("/or-add-campaign", methods=["POST"])
def or_add_campaign():
    if not session.get("or_access"):
        return redirect(url_for("or_login"))

    campaign_path = Path(app.static_folder) / "data" / "or_campaigns.json"

    with open(campaign_path, "r", encoding="utf-8") as f:
        campaigns = json.load(f)

    campaign_id = request.form.get("campaign_id", "").strip()

    if campaign_id:
        # EDIT existing
        for campaign in campaigns:
            if campaign.get("campaign_id") == campaign_id:
                campaign["contract_number"] = request.form.get("contract_number", "").strip()
                campaign["campaign"] = request.form.get("campaign", "").strip()
                campaign["city"] = request.form.get("city", "").strip()
                campaign["state"] = request.form.get("state", "").strip().upper()
                campaign["start_date"] = request.form.get("start_date", "").strip()
                campaign["end_date"] = request.form.get("end_date", "").strip()
                campaign["notes"] = request.form.get("notes", "").strip()
                break

    else:
        # CREATE new
        new_campaign = {
            "campaign_id": uuid.uuid4().hex[:8],
            "contract_number": request.form.get("contract_number", "").strip(),
            "campaign": request.form.get("campaign", "").strip(),
            "city": request.form.get("city", "").strip(),
            "state": request.form.get("state", "").strip().upper(),
            "start_date": request.form.get("start_date", "").strip(),
            "end_date": request.form.get("end_date", "").strip(),
            "notes": request.form.get("notes", "").strip(),
            "day_codes": {},
        }

        campaigns.append(new_campaign)

    with open(campaign_path, "w", encoding="utf-8") as f:
        json.dump(campaigns, f, indent=2)

    return redirect(url_for("or_calendar"))

@app.route("/or-save-day-code", methods=["POST"])
def or_save_day_code():
    if not session.get("or_access"):
        return {"success": False}, 403

    data = request.get_json()

    campaign_id = data.get("campaign_id")
    date = data.get("date")
    code = data.get("code", "").strip()

    campaign_path = Path(app.static_folder) / "data" / "or_campaigns.json"

    with open(campaign_path, "r", encoding="utf-8") as f:
        campaigns = json.load(f)

    for campaign in campaigns:
        if campaign.get("campaign_id") == campaign_id:

            if "day_codes" not in campaign:
                campaign["day_codes"] = {}

            if code:
                campaign["day_codes"][date] = code
            else:
                campaign["day_codes"].pop(date, None)

            break

    with open(campaign_path, "w", encoding="utf-8") as f:
        json.dump(campaigns, f, indent=2)

    return {"success": True}

@app.route("/or-delete-campaign", methods=["POST"])
def or_delete_campaign():
    if not session.get("or_access"):
        return redirect(url_for("or_login"))

    campaign_id = request.form.get("campaign_id", "").strip()

    if not campaign_id:
        return redirect(url_for("or_calendar"))

    campaign_path = Path(app.static_folder) / "data" / "or_campaigns.json"

    with open(campaign_path, "r", encoding="utf-8") as f:
        campaigns = json.load(f)

    campaigns = [
        campaign for campaign in campaigns
        if campaign.get("campaign_id") != campaign_id
    ]

    with open(campaign_path, "w", encoding="utf-8") as f:
        json.dump(campaigns, f, indent=2)

    return redirect(url_for("or_calendar"))

@app.route("/lead-shop", methods=["GET", "POST"])
def lead_shop():
    if request.method == "POST":
        form_data = request.form.to_dict()
        to_email = FORM_EMAIL_MAP["lead_shop"]

        name = (form_data.get("name") or "").strip()
        email = (form_data.get("email") or "").strip()
        size = (form_data.get("size") or "").strip()
        quantity = (form_data.get("quantity") or "").strip()

        if not name or not email or not size or not quantity:
            flash("Please complete all fields.", "error")
            return render_template("lead_shop.html", submitted=False)

        field_map = {
            "name": "Your Name",
            "email": "Email Address",
            "size": "Size",
            "quantity": "Quantity",
        }

        try:
            send_form_email(
                subject="Lead Polo Shirt Order Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                form_slug="lead_shop",
                submitter_name=form_data.get("name"),
                submitter_email=form_data.get("email"),
                route_name="lead_shop",
            )

            return redirect(url_for("lead_shop", submitted="1"))

        except Exception as e:
            print("LEAD SHOP EMAIL ERROR:", e)
            flash("Order submitted, but email failed to send.", "error")
            return render_template("lead_shop.html", submitted=False)

    submitted = request.args.get("submitted") == "1"
    return render_template("lead_shop.html", submitted=submitted)

@app.route("/lead-applicant-feedback", methods=["GET", "POST"])
def lead_applicant_feedback():
    if request.method == "POST":
        form_data = request.form.to_dict()
        to_email = FORM_EMAIL_MAP["lead_applicant_feedback"]
        print("LEAD DRIVER FEEDBACK submitted:", form_data)

        field_map = {
            "your_name": "Your Name",
            "applicant": "Applicant Name",
            "date": "Date",

            "understands_business": "Communication",
            "meaningful_questions": "Adaptability",
            "accepts_coaching": "Problem Solving Skills",
            "technological_expertise": "Self-confidence",
            "printed_route": "Patience",
            "retains_information": "Job Knowledge",
            "sense_of_urgency": "Company Knowledge",
            "chain_of_command": "DOT Knowledge",
            "client_interest": "Team Player",

            "comments": "Additional Comments",
        }

        try:
            send_form_email(
                subject="Lead Driver Applicant Feedback Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                form_slug="lead_applicant_feedback",
                submitter_name=form_data.get("your_name"),
                route_name="lead_applicant_feedback",
            )

            return render_template("lead_applicant_feedback.html", submitted=True)

        except Exception as e:
            print("LEAD DRIVER FEEDBACK EMAIL ERROR:", e)
            flash("Form submitted but email failed.", "error")
            return render_template("lead_applicant_feedback.html", submitted=False)

    return render_template("lead_applicant_feedback.html", submitted=False)

@app.route("/contactreport", methods=["GET", "POST"])
def contactreport():
    if request.method == "POST":
        form_data = request.form.to_dict()
        to_email = FORM_EMAIL_MAP["contactreport"]
        print("CONTACT REPORT submitted:", form_data)

        field_map = {
            "your_name": "Your Name",
            "email": "Email Address",
            "date_discussion": "Date of Discussion",
            "driver_name": "Driver Name",
            "unit_number": "Unit Number",
            "campaign": "Campaign / Market",
            "drivers_lead": "Driver's Lead",
            "performance_concern": "Performance Concern / Issue",
            "solution_action": "Agreed Upon Solution / Course of Action",
            "rating_value": "Overall Performance Rating",
            "date_submitted": "Date Submitted",
        }

        attachments = []
        extra_html = ""

        try:
            signature_data = form_data.get("signature_data")
            signature_path, signature_filename = save_signature_image(
                signature_data,
                SIGNATURE_FOLDER,
                prefix="contactreport_signature"
            )

            if signature_path:
                with open(signature_path, "rb") as f:
                    signature_base64 = base64.b64encode(f.read()).decode("utf-8")

                attachments.append({
                    "filename": signature_filename,
                    "content": signature_base64,
                    "content_type": "image/png",
                    "content_id": "contactreport-signature"
                })

                extra_html = """
                <hr>
                <p><strong>Signature:</strong></p>
                <img src="cid:contactreport-signature" alt="Signature" style="max-width: 320px; border: 1px solid #ccc; padding: 6px;">
                """

                print("SIGNATURE INLINE IMAGE ADDED:", signature_filename)

            send_form_email(
                subject="Driver Contact Report Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                attachments=attachments,
                extra_html=extra_html,
                form_slug="contactreport",
                submitter_name=form_data.get("your_name"),
                submitter_email=form_data.get("email"),
                route_name="contactreport",
            )

            return render_template("contactreport.html", submitted=True)

        except Exception as e:
            print("CONTACT REPORT EMAIL ERROR:", e)
            flash("Form submitted, but email failed to send.", "error")
            return render_template("contactreport.html", submitted=False)

    return render_template("contactreport.html", submitted=False)

@app.route("/postingphotos", methods=["GET", "POST"])
def postingphotos():
    if request.method == "POST":
        run_storage_cleanup()
        form_data = request.form.to_dict()
        driver_side_file = request.files.get("driver_side_photo")
        passenger_side_file = request.files.get("passenger_side_photo")
        to_email = FORM_EMAIL_MAP["postingphotos"]
        submission_id = form_data.get("submission_id")

        now = datetime.now(eastern)

        # Remove old submission IDs after 1 minutes
        for old_id, old_time in list(RECENT_POSTING_SUBMISSIONS.items()):
            if (now - old_time).total_seconds() > 60:
                del RECENT_POSTING_SUBMISSIONS[old_id]

        if submission_id and submission_id in RECENT_POSTING_SUBMISSIONS:
            print("DUPLICATE POSTING PHOTO SUBMISSION BLOCKED:", submission_id)
            return redirect(url_for("postingphotos", submitted="1"))

        if submission_id:
            RECENT_POSTING_SUBMISSIONS[submission_id] = now

        print("POSTING PHOTOS submitted:", form_data)
        print("DRIVER SIDE FILE:", driver_side_file.filename if driver_side_file and driver_side_file.filename else "No file uploaded")
        print("PASSENGER SIDE FILE:", passenger_side_file.filename if passenger_side_file and passenger_side_file.filename else "No file uploaded")

        field_map = {
            "driver_name": "Driver Name",
            "email": "Email",
            "unit": "Unit #",
            "campaign_city": "Campaign / City",
            "notes": "Notes",
        }

        attachments = []
        uploaded_names = []
        # (we will not use attachments for this form anymore)

        if driver_side_file and driver_side_file.filename:
            saved_driver_path, saved_driver_name = save_uploaded_file(
                driver_side_file,
                POSTING_PHOTO_FOLDER,
                driver_name=form_data.get("driver_name"),
                form_name="posting_driver_side"
            )
            driver_side_file.stream.seek(0)

        if passenger_side_file and passenger_side_file.filename:
            saved_passenger_path, saved_passenger_name = save_uploaded_file(
                passenger_side_file,
                POSTING_PHOTO_FOLDER,
                driver_name=form_data.get("driver_name"),
                form_name="posting_passenger_side"
            )
            passenger_side_file.stream.seek(0)

        try:
            uploaded_links = []

            if driver_side_file and driver_side_file.filename:
                driver_url = url_for("postingphotos_file", filename=saved_driver_name, _external=True)
                uploaded_links.append(f'<li><a href="{driver_url}">{saved_driver_name}</a></li>')

            if passenger_side_file and passenger_side_file.filename:
                passenger_url = url_for("postingphotos_file", filename=saved_passenger_name, _external=True)
                uploaded_links.append(f'<li><a href="{passenger_url}">{saved_passenger_name}</a></li>')

            extra_html = ""
            if uploaded_links:
                file_list_html = "".join(uploaded_links)
                extra_html = f"""
                <hr>
                <p><strong>Photo Links:</strong></p>
                <ul>{file_list_html}</ul>
                """

            send_form_email(
                subject="Posting Photos Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                attachments=[],
                extra_html=extra_html,
                form_slug="postingphotos",
                submitter_name=form_data.get("driver_name"),
                submitter_email=form_data.get("email"),
                route_name="postingphotos",
                include_pdf=False,
            )

            return redirect(url_for("postingphotos", submitted="1"))

        except Exception as e:
            print("POSTING PHOTOS EMAIL ERROR:", e)
            flash("Form submitted, but email failed to send.", "error")
            return render_form("postingphotos.html")

    return render_form("postingphotos.html")

@app.route("/postingphotos/file/<filename>")
def postingphotos_file(filename):
    file_path = POSTING_PHOTO_FOLDER / filename

    if not file_path.exists():
        abort(404)

    return send_from_directory(POSTING_PHOTO_FOLDER, filename)

@app.route("/photo-quiz", methods=["GET", "POST"])
def photo_quiz():
    questions = [
        {"id": 1, "img": "img/photo_quiz/photo_quiz1.jpg"},
        {"id": 2, "img": "img/photo_quiz/photo_quiz2.jpg"},
        {"id": 3, "img": "img/photo_quiz/photo_quiz3.jpg"},
        {"id": 4, "img": "img/photo_quiz/photo_quiz4.jpg"},
        {"id": 5, "img": "img/photo_quiz/photo_quiz5.jpg"},
        {"id": 6, "img": "img/photo_quiz/photo_quiz6.jpg"},
        {"id": 7, "img": "img/photo_quiz/photo_quiz7.jpg"},
        {"id": 8, "img": "img/photo_quiz/photo_quiz8.jpg"},
        {"id": 9, "img": "img/photo_quiz/photo_quiz9.jpg"},
        {"id": 10, "img": "img/photo_quiz/photo_quiz10.jpg"},
    ]

    if request.method == "POST":
        form_data = request.form.to_dict()
        to_email = FORM_EMAIL_MAP["photo_quiz"]
        print("PHOTO QUIZ:", form_data)

        field_map = {
            "your_name": "Name",
            "email": "Email Address",
            "q1_rating": "1. Image 1 Rating",
            "q1_why": "1. Why?",
            "q2_rating": "2. Image 2 Rating",
            "q2_why": "2. Why?",
            "q3_rating": "3. Image 3 Rating",
            "q3_why": "3. Why?",
            "q4_rating": "4. Image 4 Rating",
            "q4_why": "4. Why?",
            "q5_rating": "5. Image 5 Rating",
            "q5_why": "5. Why?",
            "q6_rating": "6. Image 6 Rating",
            "q6_why": "6. Why?",
            "q7_rating": "7. Image 7 Rating",
            "q7_why": "7. Why?",
            "q8_rating": "8. Image 8 Rating",
            "q8_why": "8. Why?",
            "q9_rating": "9. Image 9 Rating",
            "q9_why": "9. Why?",
            "q10_rating": "10. Image 10 Rating",
            "q10_why": "10. Why?",
        }

        try:
            send_form_email(
                subject="Photo Quality Quiz Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                form_slug="photo_quiz",
                submitter_name=form_data.get("your_name"),
                submitter_email=form_data.get("email"),
                route_name="photo_quiz",
            )

            return redirect(url_for("photo_quiz", submitted="1"))

        except Exception as e:
            print("PHOTO QUIZ EMAIL ERROR:", e)
            flash("Form submitted, but email failed to send.", "error")
            return render_template("photo_quiz.html", submitted=False, questions=questions)

    submitted = request.args.get("submitted") == "1"
    return render_template("photo_quiz.html", submitted=submitted, questions=questions)

@app.route("/dan-kelly-voting", methods=["GET", "POST"])
def dan_kelly_voting():

    photos = [
        {"id": "1", "src": "img/dk_voting/dk_vote1.jpeg"},
        {"id": "2", "src": "img/dk_voting/dk_vote2.jpeg"},
        {"id": "3", "src": "img/dk_voting/dk_vote3.jpeg"},
        {"id": "4", "src": "img/dk_voting/dk_vote4.jpeg"},
        {"id": "5", "src": "img/dk_voting/dk_vote5.jpeg"},
    ]

    if request.method == "POST":
        form_data = request.form.to_dict()
        to_email = FORM_EMAIL_MAP["dan_kelly_voting"]

        print("DAN KELLY VOTE:", form_data)

        field_map = {
            "your_name": "Voter Name",
            "email": "Email",
            "vote_choice": "Selected Photo",
        }

        try:
            send_form_email(
                subject="Dan Kelly Award Vote Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                form_slug="dan_kelly_voting",
                submitter_name=form_data.get("your_name"),
                submitter_email=form_data.get("email"),
                route_name="dan_kelly_voting",
            )

            return redirect(url_for("dan_kelly_voting", submitted="1"))

        except Exception as e:
            print("DAN KELLY VOTE EMAIL ERROR:", e)
            flash("Vote submitted, but email failed to send.", "error")

    submitted = request.args.get("submitted") == "1"

    return render_template(
        "dan_kelly_voting.html",
        photos=photos,
        submitted=submitted,
        page_title="Dan Kelly Award Voting",
        page_subtitle_1="Select the photo that best represents the Dan Kelly Award.",
        page_subtitle_2="Each person may vote once."
    )

@app.route("/harassment-training/<role>", methods=["GET", "POST"])
def harassment_training(role):
    config = {
        "drivers": "harassment_quiz.html",
        "leads": "harassment_training_leads.html",
        "managers": "harassment_training_managers.html",
    }

    if role not in config:
        return "Not Found", 404

    template_name = config[role]
    ack_submitted = request.args.get("ack_submitted") == "1"
    quiz_submitted = request.args.get("quiz_submitted") == "1"

    if request.method == "POST":
        form_name = request.form.get("form_name")
        form_data = request.form.to_dict()
        to_email = FORM_EMAIL_MAP["harassment_training"]

        print(f"HARASSMENT {role.upper()} {form_name.upper()}:", form_data)

        try:
            if role == "drivers":
                if form_name == "ack":
                    field_map = {
                        "ack_name": "Your Name",
                        "ack_complete": "Acknowledgement Complete",
                    }

                    send_form_email(
                        subject="Harassment Training - Drivers Acknowledgement Submitted",
                        form_data=form_data,
                        field_map=field_map,
                        to_email=to_email,
                        form_slug="harassment_training_driver",
                        submitter_name=form_data.get("ack_name"),
                        route_name="harassment_training",
                    )

                    return redirect(url_for("harassment_training", role=role, ack_submitted="1"))

                elif form_name == "quiz":
                    field_map = {
                        "your_name": "Your Name",
                        "email": "Email",
                        "q1": "Question 1",
                        "q2": "Question 2",
                        "q3": "Question 3",
                        "q4": "Question 4",
                        "q5": "Question 5",
                        "q6": "Question 6",
                        "q7": "Question 7",
                        "q8": "Question 8",
                        "q9": "Question 9",
                        "q10": "Question 10",
                        "q11": "Question 11",
                        "q12": "Question 12",
                        "q13": "Question 13",
                        "q14": "Question 14",
                        "q15": "Question 15",
                        "q16": "Question 16",
                        "q17": "Question 17",
                        "q18": "Question 18",
                        "q19": "Question 19",
                        "q20": "Question 20",
                    }

                    send_form_email(
                        subject="Harassment Training - Drivers Quiz Submitted",
                        form_data=form_data,
                        field_map=field_map,
                        to_email=to_email,
                        form_slug="harassment_training_driver",
                        submitter_name=form_data.get("your_name"),
                        submitter_email=form_data.get("email"),
                        route_name="harassment_training",
                    )

                    return redirect(url_for("harassment_training", role=role, quiz_submitted="1"))

            elif role == "leads":
                if form_name == "ack":
                    field_map = {
                        "ack_name": "Your Name",
                        "ack_complete": "Acknowledgement Complete",
                    }

                    send_form_email(
                        subject="Harassment Training - Leads Acknowledgement Submitted",
                        form_data=form_data,
                        field_map=field_map,
                        to_email=to_email,
                        form_slug="harassment_training_lead",
                        submitter_name=form_data.get("ack_name"),
                        route_name="harassment_training",
                    )

                    return redirect(url_for("harassment_training", role=role, ack_submitted="1"))

                elif form_name == "quiz":
                    field_map = {
                        "your_name": "Your Name",
                        "email": "Email",
                        "q1": "Question 1",
                        "q2": "Question 2",
                        "q3": "Question 3",
                        "q4": "Question 4",
                        "q5": "Question 5",
                        "q6": "Question 6",
                        "q7": "Question 7",
                        "q8": "Question 8",
                        "q9": "Question 9",
                        "q10": "Question 10",
                        "q11": "Question 11",
                        "q12": "Question 12",
                        "q13": "Question 13",
                        "q14": "Question 14",
                        "q15": "Question 15",
                        "q16": "Question 16",
                        "q17": "Question 17",
                        "q18": "Question 18",
                        "q19": "Question 19",
                        "q20": "Question 20",
                        "q21": "Question 21",
                        "q22": "Question 22",
                        "q23": "Question 23",
                        "q24": "Question 24",
                        "q25": "Question 25",
                        "q26": "Question 26",
                        "q27": "Question 27",
                        "q28": "Question 28",
                    }

                    send_form_email(
                        subject="Harassment Training - Leads Quiz Submitted",
                        form_data=form_data,
                        field_map=field_map,
                        to_email=to_email,
                        form_slug="harassment_training_lead",
                        submitter_name=form_data.get("your_name"),
                        submitter_email=form_data.get("email"),
                        route_name="harassment_training",
                    )

                    return redirect(url_for("harassment_training", role=role, quiz_submitted="1"))

            elif role == "managers":
                if form_name == "ack":
                    field_map = {
                        "ack_name": "Your Name",
                        "ack_complete": "Acknowledgement Complete",
                    }

                    send_form_email(
                        subject="Harassment Training - Managers Acknowledgement Submitted",
                        form_data=form_data,
                        field_map=field_map,
                        to_email=to_email,
                        form_slug="harassment_training_manager",
                        submitter_name=form_data.get("ack_name"),
                        route_name="harassment_training",
                    )

                    return redirect(url_for("harassment_training", role=role, ack_submitted="1"))

                elif form_name == "quiz":
                    field_map = {
                        "your_name": "Your Name",
                        "email": "Email",
                        "q1": "Question 1",
                        "q2": "Question 2",
                        "q3": "Question 3",
                        "q4": "Question 4",
                        "q5": "Question 5",
                        "q6": "Question 6",
                        "q7": "Question 7",
                        "q8": "Question 8",
                        "q9": "Question 9",
                        "q10": "Question 10",
                        "q11": "Question 11",
                        "q12": "Question 12",
                        "q13": "Question 13",
                        "q14": "Question 14",
                        "q15": "Question 15",
                        "q16": "Question 16",
                        "q17": "Question 17",
                        "q18": "Question 18",
                        "q19": "Question 19",
                        "q20": "Question 20",
                        "q21": "Question 21",
                        "q22": "Question 22",
                        "q23": "Question 23",
                        "q24": "Question 24",
                        "q25": "Question 25",
                        "q26": "Question 26",
                        "q27": "Question 27",
                    }

                    send_form_email(
                        subject="Harassment Training - Managers Quiz Submitted",
                        form_data=form_data,
                        field_map=field_map,
                        to_email=to_email,
                        form_slug="harassment_training_manager",
                        submitter_name=form_data.get("your_name"),
                        submitter_email=form_data.get("email"),
                        route_name="harassment_training",
                    )

                    return redirect(url_for("harassment_training", role=role, quiz_submitted="1"))

        except Exception as e:
            print(f"HARASSMENT {role.upper()} EMAIL ERROR:", e)
            flash("Form submitted, but email failed to send.", "error")

    return render_template(
        template_name,
        ack_submitted=ack_submitted,
        quiz_submitted=quiz_submitted
    )

@app.route("/dotcompliancetest", methods=["GET", "POST"])
def dot_compliance_test():
    if request.method == "POST":
        form_data = request.form.to_dict()
        uploaded_file = request.files.get("q22_file")
        to_email = FORM_EMAIL_MAP["dot_compliance_test"]

        print("DOT TEST submitted:", form_data)
        print("DOT TEST file:", uploaded_file.filename if uploaded_file and uploaded_file.filename else "No file uploaded")

        field_map = {
            "your_name": "Your Name",
            "new_hire": "New Hire",
            "date_time": "Date and Time",
            "q1": "1. Must fill out a DOT Log",
            "q2": "2. DOT Log must account for all time",
            "q3": "3. Fill out DOT Log at end of day",
            "q4": "4. Consecutive hours allowed ON DUTY",
            "q5": "5. Required OFF DUTY time before operating DOT vehicle",
            "q6": "6. Stop after 11 hours driving and reset 10 hours OFF DUTY",
            "q7": "7. Vehicle use while OFF DUTY",
            "q8": "8. What to write in 'Shipper & Commodity'",
            "q9": "9. What to write in 'Home Terminal Address'",
            "q10": "10. To/From on multiple day trip",
            "q11": "11. When to add Remarks",
            "q12": "12. What Remarks should include",
            "q13": "13. Pre-Trip and Post-Trip Inspections are considered",
            "q14": "14. Restaurant break while market-to-market is considered",
            "q15": "15. Fuel stop is considered",
            "q16": "16. Break to make phone calls in vehicle is considered",
            "q17": "17. Total hours for the day should equal",
            "q18": "18. Which copy of the DOT Log gets mailed in",
            "q19": "19. How long must you retain your copy of the DOT Log",
            "q20": "20. On a four day trip, when must you sign the DOT log",
            "q21_notes": "21. Mock Trip Notes / Confirmation",
        }

        attachments = []
        extra_html = ""

        try:
            uploaded_attachment = build_uploaded_file_attachment(
                uploaded_file,
                driver_name=form_data.get("your_name"),
                form_name="dot_compliance_test"
            )
            if uploaded_attachment:
                attachments.append(uploaded_attachment)
                extra_html = f"""
                <hr>
                <p><strong>Uploaded File Attached:</strong> {uploaded_attachment['filename']}</p>
                """

            send_form_email(
                subject="DOT Compliance Test Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                attachments=attachments,
                extra_html=extra_html,
                form_slug="dot_compliance_test",
                submitter_name=form_data.get("your_name"),
                route_name="dot_compliance_test",
            )

            return redirect(url_for("dot_compliance_test", submitted="1"))

        except Exception as e:
            print("DOT TEST EMAIL ERROR:", e)
            flash("Form submitted, but email failed to send.", "error")
            return render_form("dot_compliance_test.html")

    return render_form("dot_compliance_test.html")

@app.route("/acknowledgement-form", methods=["GET", "POST"])
def acknowledgement_form():
    if request.method == "POST":
        form_data = request.form.to_dict()
        to_email = FORM_EMAIL_MAP["acknowledgement_form"]
        print("TEMP ACKNOWLEDGEMENT submitted:", form_data)

        field_map = {
            "q1_questions": "1. Your Full Name",
            "q2_questions": "2. What is your phone number?",
            "q3_questions": "3. Who did your initial training?",
            "q4_questions": "4. Who is your Lead Driver?",
            "q5_questions": "5. What campaign will you be running?",
            "q6_questions": "6. What unit # will you be driving?",
            "keys_understanding": "7. Do you understand how to find, and where to leave the keys for the vehicle?",
            "routing_printed": "8. Do you have your routing printed out?",
            "review_handbook": "9. Did you review the handbook?",
            "q10_questions": "10. I understand that the tablets are for business purposes only... (Initials)",
            "q11_questions": "11. I will keep the truck clean - inside and out. (Initials)",
            "q12_questions": "12. I will not smoke in or around the truck. (Initials)",
            "q13_questions": "13. I will not use my cellphone while driving. (Initials)",
            "q14_questions": "14. I will not exceed 55 MPH while driving. (Initials)",
            "q15_questions": "15. I will keep work to an 8 hour day. (Initials)",
            "q16_questions": "16. I will work the hours listed in my routing. (Initials)",
            "q17_questions": "17. I am allowed ONE 30 minute break. (Initials)",
            "q18_questions": "18. Stops over 15 minutes must be reported. (Initials)",
            "q19_questions": "19. I will alert my lead driver of any stops longer than 15 minutes (Initials)",
            "fuel_card": "20. I understand the fuel card must remain with the truck.",
            "q21_questions": "21. Tablet use is required. (Initials)",
            "q22_questions": "22. Tablet remains inside vehicle. (Initials)",
            "q23_questions": "23. Photos must be uploaded regularly. (Initials)",
            "q24_questions": "24. Do you understand what type of photos and how many we are looking for?",
            "q25_questions": "25. Tablet and keys must remain with vehicle (Initials)",
        }

        try:
            send_form_email(
                subject="Temp Driver Acknowledgement Form Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                form_slug="Temp_acknowledgement_form",
                submitter_name=form_data.get("q1_questions"),
                route_name="acknowledgement_form",
            )

            return render_template("temp_acknowledgement_form.html", submitted=True)

        except Exception as e:
            print("TEMP ACKNOWLEDGEMENT EMAIL ERROR:", e)
            flash("Form submitted, but email failed to send.", "error")
            return render_template("temp_acknowledgement_form.html", submitted=False)

    return render_template("temp_acknowledgement_form.html", submitted=False)

@app.route("/samsaranotice", methods=["GET", "POST"])
def samsara_notice():
    if request.method == "POST":
        form_data = request.form.to_dict()
        to_email = FORM_EMAIL_MAP["samsara_notice"]
        print("SAMSARA NOTICE submitted:", form_data)

        field_map = {
            "your_name": "Your Name",
            "email": "Email",
            "q1": "1. The purpose of the Samsara AI dashcam is to promote safe driving habits.",
            "q2": "2. Samsara's distracted driving detection can identify cell phone use.",
            "q3": "3. The Following Distance Violation feature detects tailgating.",
            "q4": "4. Drivers may receive real-time in-cab audio alerts.",
            "q5": "5. Have you read and understood all of the information provided?",
        }

        try:
            send_form_email(
                subject="Samsara Notice Acknowledgement Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                form_slug="samsara_notice",
                submitter_name=form_data.get("your_name"),
                submitter_email=form_data.get("email"),
                route_name="samsara_notice",
            )

            return render_template("samsara_notice.html", submitted=True)

        except Exception as e:
            print("SAMSARA NOTICE EMAIL ERROR:", e)
            flash("Form submitted, but email failed to send.", "error")
            return render_template("samsara_notice.html", submitted=False)

    return render_template("samsara_notice.html", submitted=False)

@app.route("/near-miss-reporting", methods=["GET", "POST"])
def near_miss_reporting():
    if request.method == "POST":
        form_data = request.form.to_dict()
        to_email = FORM_EMAIL_MAP["near_miss_reporting"]

        field_map = {
            "date": "Date of Occurrence",
            "time": "Time of Occurrence",
            "description": "Description",
        }

        try:
            send_form_email(
                subject="Near Miss Report Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                form_slug="near_miss_reporting",
                route_name="near_miss_reporting",
            )
            return render_template("near_miss_reporting.html", submitted=True)

        except Exception as e:
            print("NEAR MISS EMAIL ERROR:", e)
            flash("Form submitted, but email failed to send.", "error")

    return render_template("near_miss_reporting.html", submitted=False)

@app.route("/quiz-<month>", methods=["GET", "POST"])
def monthly_quiz(month):
    template_map = {
        "january": "quiz_january_26.html",
        "february": "quiz_february_26.html",
        "march": "quiz_march_26.html",
        "april": "quiz_april_26.html",
        "may": "quiz_may_26.html",
        # "june": "quiz_june_26.html",
        # "july": "quiz_july_26.html",
    }

    quiz_id_map = {
        "january": "2026_01",
        "february": "2026_02",
        "march": "2026_03",
        "april": "2026_04",
        "may": "2026_05",
        # "june": "2026_05",
        # "july": "2026_05",
    }

    if month not in template_map:
        return "Not Found", 404

    template_name = template_map[month]
    quiz_id = quiz_id_map[month]

    if request.method == "POST":
        form_data = request.form.to_dict()
        to_email = FORM_EMAIL_MAP["monthly_quiz"]
        print(f"{month.upper()} QUIZ Submitted:", form_data)

        field_map = {
            "your_name": "Your Name",
            "email": "Email",
            "q1": "Question 1",
            "q2": "Question 2",
            "q3": "Question 3",
            "q4": "Question 4",
            "q5": "Question 5",
            "q6": "Question 6",
            "q7": "Question 7",
            "q8": "Question 8",
            "q9": "Question 9",
            "q10": "Question 10",
            "q11": "Question 11",
            "q12": "Question 12",
        }

        try:
            employee_name = form_data.get("your_name", "").strip()

            answers = [
                form_data.get("q1", "").strip(),
                form_data.get("q2", "").strip(),
                form_data.get("q3", "").strip(),
                form_data.get("q4", "").strip(),
                form_data.get("q5", "").strip(),
                form_data.get("q6", "").strip(),
                form_data.get("q7", "").strip(),
                form_data.get("q8", "").strip(),
                form_data.get("q9", "").strip(),
                form_data.get("q10", "").strip(),
                form_data.get("q11", "").strip(),
                form_data.get("q12", "").strip(),
            ]

            log_monthly_quiz_submission(
                quiz_id=quiz_id,
                employee_name=employee_name,
                answers=answers,
            )

            send_form_email(
                subject=f"{month.title()} Safety Quiz Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                form_slug="monthly_quiz",
                submitter_name=form_data.get("your_name"),
                submitter_email=form_data.get("email"),
                route_name="monthly_quiz",
            )

            return redirect(url_for("monthly_quiz", month=month, submitted="1"))

        except Exception as e:
            print(f"{month.upper()} QUIZ EMAIL ERROR:", e)
            flash("Quiz submitted, but email failed to send.", "error")
            return render_template(template_name, submitted=False)

    submitted = request.args.get("submitted") == "1"
    return render_template(template_name, submitted=submitted)

@app.route("/<int:week>-week-test", methods=["GET", "POST"])
def week_test(week):
    allowed_weeks = [2, 4, 6, 8, 10, 12]
    if week not in allowed_weeks:
        return "Not Found", 404

    template_map = {
        2: "week_two_test.html",
        4: "week_four_test.html",
        6: "week_six_test.html",
        8: "week_eight_test.html",
        10: "week_ten_test.html",
        12: "week_twelve_test.html",
    }

    template_name = template_map[week]

    if request.method == "POST":
        form_data = request.form.to_dict()
        to_email = FORM_EMAIL_MAP["week_test"]
        print(f"{week} WEEK TEST:", form_data)

        field_map = {
            "your_name": "Your Name",
            "email": "Email",
            "mentor": 'Mentor Lead Driver',
            "q1": "Question 1",
            "q2": "Question 2",
            "q3": "Question 3",
            "q4": "Question 4",
            "q5": "Question 5",
            "q6": "Question 6",
            "q7": "Question 7",
            "q8": "Question 8",
            "q9": "Question 9",
            "q10": "Question 10",
            "q11": "Question 11",
            "q12": "Question 12",
        }

        try:
            send_form_email(
                subject=f"Week {week} Post Hire Test Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                form_slug="week_test",
                submitter_name=form_data.get("your_name"),
                submitter_email=form_data.get("email"),
                route_name="week_test",
            )

            return redirect(url_for("week_test", week=week, submitted="1"))

        except Exception as e:
            print(f"{week} WEEK TEST EMAIL ERROR:", e)
            flash("Form submitted, but email failed to send.", "error")
            return render_template(template_name, submitted=False)

    submitted = request.args.get("submitted") == "1"
    return render_template(template_name, submitted=submitted)

@app.route("/ojt-checklist", methods=["GET", "POST"])
def ojt_checklist():
    if request.method == "POST":
        raw_form_data = request.form.to_dict(flat=False)
        to_email = FORM_EMAIL_MAP["ojt_checklist"]
        print("OJT CHECKLIST submitted:", raw_form_data)

        form_data = {}

        for key, value in raw_form_data.items():

            # convert checkbox values to Yes
            if key.startswith("q16_"):
                form_data[key] = "Yes"

            # normal fields
            else:
                form_data[key] = value[0] if isinstance(value, list) and value else value

        field_map = {
            "your_name": "1. Your Name",
            "new_hire": "2. New Hire",
            "date_time": "3. Date and Time",
            "q4_prepost": "4. Does driver know how to complete a proper pre/post inspection?",
            "q5_ucr": "5. Does driver know how to complete a UCR? Did they submit one for your vehicle?",
            "q6_attire": "6. Is driver wearing proper work attire? Does driver understand our dress code?",
            "q7_fuel_sep": "7. Does driver know where to locate the fuel separator, and how to drain it properly?",
            "q8_air_filter": "8. Does driver know where the in-cabin air filter is and how to check/clean it?",
            "q9_clips": "9. How many clips does driver think need to be with the unit? Do they understand why we need the proper amount?",
            "q10_install_clips": "10. Can driver successfully install vinyl clips, without struggle?",
            "q11_hang_vinyls": "11. Can driver successfully hang vinyls on their own?",
            "q12_troubleshoot": "12. Did you cover troubleshooting issues with vinyls? How to re-tighten, check pulleys, etc.",
            "q13_xrs": "13. Does driver know how to log in and properly use XRS, including changing rulesets and using personal conveyance?",
            "q14_roadnet": "14. Does driver know how to log-in and use Roadnet?",
            "q15_paylocity": "15. Does driver know how to log into and properly use the Paylocity app (including using proper labor codes)?",
            "q16_safe_backing": "16a. Safe backing skills",
            "q16_height_clearance": "16b. Watching height clearance",
            "q16_tail_swing": "16c. Watching for tail swing on turns",
            "q16_speed_limits": "16d. Obey speed limits",
            "q17_concerns": "17. Do you have any concerns about their driving?",
            "q18_max_speed": "18. Does driver know and understand company max speed limits with/without vinyls?",
            "q19_lead_driver": "19. Does driver know who their Lead Driver is, and have all of their contact info?",
            "q20_ppe": "20. Does driver have their P.P.E. (personal protective equipment) Safety hat or vest?",
            "q21_posting_photos": "21. Does driver know what posting photos are, and when/where to send them?",
            "q22_campaign_photos": "22. Does driver know when/where to send campaign photos?",
            "q23_photo_tips": "23. What good photo taking tips did you give to the driver?",
            "q24_clean_unit": "24. Did you cover the importance of keeping a clean unit at all times?",
            "q25_breakdown": "25. Does driver know what to do, and who to call if their unit breaks down?",
            "q26_accident": "26. Does driver understand the accident protocol? importance of taking photos, etc",
            "q27_routing_printed": "27. Does driver understand that they MUST have their routing printed out at all times?",
            "q28_geofence": "28. Does driver understand what their geofence (overview) is?",
            "q29_schedule": "29. Does driver understand the importance of checking their schedule every day, and why it's so important to start/stop on time?",
            "q30_extended_stops": "30. Does driver know what extended stops are? and the importance of not having them/who to contact?",
            "q31_weather": "31. Does driver know/understand weather policy?",
            "q32_cards": "32. Does driver know the difference between the red and blue Comdata and OnRoad cards?",
            "q33_expense": "33. Does driver know how to fill out expense report, and when/where to submit it along with receipts?",
            "q34_fuel_card": "34. Does driver know how to use the fuel card, and the importance of entering the correct mileage?",
            "q35_no_ladder": "35. Does driver know not to be on a ladder, rear deck, or inside the box?",
            "q36_paper_log": "36. Does driver have a paper log book as required back up?",
            "q37_questionnaire": "37. Did you remind the driver to complete the upcoming campaign questionnaire?",
            "q38_confidence": "38. Confidence level for first campaign",
            "q39_comments": "39. Additional comments",
        }

        try:
            send_form_email(
                subject="O.J.T. Checklist Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                form_slug="ojt_checklist",
                submitter_name=form_data.get("your_name"),
                route_name="ojt_checklist",
            )

            return redirect(url_for("ojt_checklist", submitted="1"))

        except Exception as e:
            print("OJT CHECKLIST EMAIL ERROR:", e)
            flash("Form submitted, but email failed to send.", "error")
            return render_form("ojt_checklist.html")

    return render_form("ojt_checklist.html")

@app.route("/post-training-recap", methods=["GET", "POST"])
def post_training_recap():
    if request.method == "POST":
        raw_form_data = request.form.to_dict(flat=False)
        to_email = FORM_EMAIL_MAP["post_training_recap"]
        print("POST TRAINING RECAP:", raw_form_data)

        form_data = {}
        for key, value in raw_form_data.items():
            if key.startswith("q88_"):
                form_data[key] = value
            else:
                form_data[key] = value[0] if isinstance(value, list) and value else value

        field_map = {
            "your_name": "1. Your Name",
            "email": "2. Email",
            "date_time": "3. Date and Time",

            "q1": "1) What is the number one goal of do it outdoors?",
            "q2": "2) Drivers are guaranteed hours every week.",
            "q3": "3) The do it outdoors dress code calls for:",
            "q4": "4) Being drug free is a condition of employment.",
            "q5": "5) When do you use the Paylocity payroll app?",
            "q6": "6) You are required to stop at open weigh stations/port of entries when……",
            "q7": "7) When stopping at a weigh station, you are required to have with you:",
            "q8": "8) Where do you send Receipts? (email or location)",
            "q9": "9) Where do you send Posting Photos? (email or location)",
            "q10": "10) Where do you send DOT Logs? (email or location)",
            "q11": "11) Where do you send Campaign Photos? (email or location)",
            "q12": "12) Where do you send UCR’s & Hotel Folios? (email or location)",
            "q13": "13) If you forget where to send items, where do you go to find this info?",
            "q14": "14) If a police officer or security personnel tell you to move the mobile billboard, you should:",
            "q15": "15) Good attendance and punctuality are important to the efficient operation of the company",
            "q16": "16) When you need to be off the schedule, it’s ok to inform OMT the day before?",
            "q17": "17) I can drive market to market with my vinyls on?",
            "q18": "18) Once you are hired, it doesn’t matter if you receive any moving traffic violations",
            "q19": "19) do it outdoors will pay for the following moving violations when you are running behind for a campaign:",
            "q20": "20) When should you arrive at the airport for a departing flight?",
            "q21": "21) How many miles are you permitted to drive per day during an average campaign?",
            "q22": "22) When I am notified that my vinyls are delivering to my campaign hotel, I must call the hotel before arriving and confirm that my vinyls have delivered.",
            "q23": "23) It is against company policy to drive between the hours of midnight and 5:00am.",
            "q24": "24) When do you clock out for lunch?",
            "q25": "25) If your Lead Driver or Ops needs to get in touch with you while you are driving, how will this be accomplished?",
            "q26": "26) If you are notified that you have been selected for random drug testing, what must you do?",
            "q27": "27) It’s okay to use the company Uber account for personal use, do it outdoors will just deduct the amount from your pay.",
            "q28": "28) You are allowed to use the company Uber account when in your home market.",
            "q29": "29) When are Drivers eligible to receive per diem? And when are OnRoad cards loaded?",
            "q30": "30) How do you know that funds have been loaded to your Blue Comdata card?",
            "q31": "31) The best thing to do with leftover Blue Card Comdata funds is:",
            "q32": "32) I can call Operations anytime of the day or any day I please to have Comdata funds added to my account.",
            "q33": "33) When turning in receipts, you must do the following:",
            "q34": "34) Misuse of Comdata funds may lead to payroll deductions, disciplinary action and even termination.",
            "q35": "35) If I leave a market unexpectedly during the week and have already received my per diem, I get to keep the unearned funds.",
            "q36": "36) What is the OnRoad Comdata card for?",
            "q37": "37) What is the BLUE Comdata card for?",
            "q38": "38) Drivers should never be:",
            "q39": "39) Why is the use of electronic devices prohibited while driving?",
            "q40": "40) What is the #1 job priority while working for do it outdoors?",
            "q41": "41) When your phone rings while you are driving, the best thing for you to do is:",
            "q42": "42) What is the recommended height clearance for ALL of our mobiles?",
            "q43": "43) If you pull up to a bridge or overpass and can’t go under it. What should you do?",
            "q44": "44) How many points of contact are you required to use when entering a mobile & what does it mean?",
            "q45": "45) If you are involved in an accident, you must do the following:",
            "q46": "46) What is the companywide MAX speed limit without vinyls and what is the MAX speed limit if your unit has vinyls on?",
            "q47": "47) When you need to use the safety triangles for a vehicle breakdown, what is the recommended distance between the rear of our unit and the placement of each triangle (1st, 2nd, 3rd)?",
            "q48": "48) If you get lost on your campaign, you should:",
            "q49": "49) When should you be within your route area (geofence)?",
            "q50": "50) I can run any days of the week and any hours of the day I prefer. What is listed on my routing are just loose guidelines.",
            "q51": "51) If I have any questions on my route, whom do I contact?",
            "q52": "52) When running a campaign, if you are going off route or are going to stop for more than thirty minutes, you should:",
            "q53": "53) If you are late or going to be late starting your route while on campaign you should...",
            "q54": "54) Stops while driving a campaign should be no more than 15 minutes except when?",
            "q55": "55) If I have an extended stop/late start/early out, I do not have to report this, especially on the weekends.",
            "q56": "56) If you’re running late due to traffic and there’s an event that starts in 20 minutes and you’re 15 minutes from the location what should you do?",
            "q57": "57) What should you do if you’re not sure if a store is a competitor or not?",
            "q58": "58) I have to follow Roadnet routing turn by turn on every campaign I’m on?",
            "q59": "59) If I’m not sure if I run today or not sure what time I start, how do I find out this information?",
            "q60": "60) If I encounter some inclement weather (high winds, snow, ice, severe t-storms, etc.) during the day, what should I do?",
            "q61": "61) Who is our fleet maintenance provider and how do I find their contact information?",
            "q62": "62) On a regular basis (as often as needed) I must clean the inside, outside and vinyls on my mobile and wipe it down daily during my stops.",
            "q63": "63) I can purchase fuel at fuel stations with the following:",
            "q64": "64) Smoking/using tobacco products/vaping is allowed in or around the vehicle",
            "q65": "65) If XRS on the tablet will not let me log a pre-trip, what is the first thing to check?",
            "q66": "66) Fuel additive should be used ONLY in cold weather.",
            "q67": "67) How often do I need to make sure my vinyls are still stretched properly, and if not, fix them?",
            "q68": "68) What three basic safety items are required to be in your mobile at all times?",
            "q69": "69) Your vehicle suddenly breaks down. Who do you call?",
            "q70": "70) Vehicle clearance refers to:",
            "q71": "71) When do you perform a post-trip Inspection?",
            "q72": "72) What are the three instances when you need to fill out a Unit Condition Report (UCR)?",
            "q73": "73) During your post-trip inspection, you notice body damage. You should:",
            "q74": "74) Whenever I park my mobile, I should:",
            "q75": "75) Other than the pre-trip and post-trip inspections, what other maintenance am I responsible to perform?",
            "q76": "76) When do I need to unplug the OBD (On Board Diagnostic) port?",
            "q77": "77) If driving a diesel unit, when should you drain your fuel separator regardless of the weather conditions?",
            "q78": "78) If you accidentally fill your mobile with the wrong fuel type, what should you NOT do?",
            "q79": "79) As long as I log into XRS on the tablet at the start of my shift, I do not have to upload my Roadnet route.",
            "q80": "80) When driving one of the gasoline powered MBBs (units 104 and up), I must make sure the hotspot on the tablet is turned on daily to activate the MDVR Camera system?",
            "q81": "81) On an average campaign you only need to take photos if instructed to do so.",
            "q82": "82) When taking campaign photographs, the Driver should:",
            "q83": "83) What are the circumstances when I send in posting photos and when should I send them in?",
            "q84": "84) It is acceptable to only upload 5 photos in a batch as long as they are good quality.",
            "q85": "85) Campaign photos are required for any targeted events on your route.",
            "q86": "86) For a 5 day campaign, how many total batches of photos should you upload?",
            "q87": "87) T/F – Shorter campaigns require more photos. Please explain why.",
            "q88_a": "88a) It’s okay if the vinyls are loose as long as there are people in your photos",
            "q88_b": "88b) Vinyls should be checked throughout the day to make sure they look good every campaign day",
            "q88_c": "88c) People and/or traffic are required in all photos",
            "q88_d": "88d) The entire mobile must be within the frame of all photos",
            "q88_e": "88e) It’s okay to target schools as long as you are not advertising for alcohol/tobacco/marijuana",
            "q88_f": "88f) It’s okay to veer from Roadnet to find good photo opportunities",
        }

        link_pattern = re.compile(
            r"(https?://|www\.|\.com|\.net|\.org|\.ru|\.cn|\.xyz)",
            re.IGNORECASE
        )

        for key, value in form_data.items():
            values = value if isinstance(value, list) else [value]

            for item in values:
                if item and link_pattern.search(str(item)):
                    print("POST TRAINING RECAP BLOCKED - LINK DETECTED:", key, item)

                    log_security_event(
                        reason="link_detected",
                        email=form_data.get("email"),
                        form_slug="post_training_recap"
                    )

                    return redirect(url_for("post_training_recap", submitted="1"))

        try:
            send_form_email(
                subject="Post-Training Recap Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                form_slug="post_training_recap",
                submitter_name=form_data.get("your_name"),
                route_name="post_training_recap",
            )

            return redirect(url_for("post_training_recap", submitted="1"))

        except Exception as e:
            print("POST TRAINING RECAP EMAIL ERROR:", e)
            flash("Form submitted, but email failed to send.", "error")
            return render_form("post_training_recap.html")

    return render_form("post_training_recap.html")

@app.route("/return-to-work-quiz", methods=["GET", "POST"])
def return_to_work_quiz():
    if request.method == "POST":
        form_data = request.form.to_dict()
        to_email = FORM_EMAIL_MAP["return_to_work_quiz"]
        print("RETURN TO WORK QUIZ:", form_data)

        field_map = {
            "your_name": "Your Name",
            "date": "Date",
            "q1_first_contact": "1. Who is your first point of contact?",
            "q2_batch_count": '2. How many campaign photos should be included in each "batch"?',
            "q3_campaign_speed": "3. Maximum speed limit while driving on campaign time",
            "q4_missing_target": "4. What do you do if you can't find one of your target locations?",
            "q5_start_time": "5. How early should you start?",
            "q6_shadowfencing": "6. What is required of you if on a shadowfencing campaign?",
            "q7_tablet_excuse": "7. Is tablet login trouble a valid excuse for a late start?",
            "q8_mechanical": "8. Who do you call if your truck has mechanical issues?",
            "q9_printed_routing": "9. Required to have routing printed out at all times",
            "q10_labor_codes": "10. What are labor codes used for?",
            "q11_prepost_min": "11. Minimum minutes for pre/post trip inspection",
            "q12_campaign_upload": "12. Where do you upload your campaign photos?",
            "q13_posting_when": "13. Where do you send posting photos, and when?",
            "q14_do_not": "14. If involved in an incident/accident, what should you NOT do?",
            "q15_ucr_instances": "15. What 3 instances do UCR’s need to be completed?",
            "q16_xrs_userid": "16. What is your specific user id for XRS?",
            "q17_expenses": "17. When and where do you submit expenses?",
            "q18_onroad_card": "18. What is your OnRoad card used for?",
            "q19_merchants_packet": "19. What 3 main items should you find in the Merchants Packet?",
            "q20_m2m_speed": "20. Maximum speed limit while driving market-to-market",
            "q21_clips": "21. How many clips go on one vinyl, and how many total clips should you have with your unit?",
        }

        try:
            send_form_email(
                subject="Return to Work Questionnaire Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                form_slug="return_to_work_quiz",
                submitter_name=form_data.get("your_name"),
                route_name="return_to_work_quiz",
            )

            return redirect(url_for("return_to_work_quiz", submitted="1"))

        except Exception as e:
            print("RETURN TO WORK QUIZ EMAIL ERROR:", e)
            flash("Form submitted, but email failed to send.", "error")
            return render_form("return_to_work_quiz.html")

    return render_form("return_to_work_quiz.html")

@app.route("/driver-questions", methods=["GET", "POST"])
def driver_questions():
    if request.method == "POST":
        form_data = clean_form_data(request.form)
        uploaded_file = request.files.get("favorite_photo")
        to_email = FORM_EMAIL_MAP["driver_questions"]

        print("DRIVER SURVEY submitted:", form_data)
        print(
            "DRIVER SURVEY file:",
            uploaded_file.filename if uploaded_file and uploaded_file.filename else "No file uploaded"
        )

        field_map = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "favorite_campaign": "What has been your favorite campaign or location? Why?",
            "most_unique": "What has been the most unique thing you have seen or done on a campaign or in a campaign location?",
        }

        attachments = []
        extra_html = ""

        try:
            uploaded_attachment = build_uploaded_file_attachment(
                uploaded_file,
                driver_name=f"{form_data.get('first_name', '')}_{form_data.get('last_name', '')}",
                form_name="driver_survey_photo"
            )

            if uploaded_attachment:
                attachments.append(uploaded_attachment)
                extra_html = f"""
                <hr>
                <p><strong>Uploaded File Attached:</strong> {uploaded_attachment['filename']}</p>
                """

            submitter_name = f"{form_data.get('first_name', '')} {form_data.get('last_name', '')}".strip()

            send_form_email(
                subject="Driver Survey Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                attachments=attachments,
                extra_html=extra_html,
                form_slug="driver_survey",
                submitter_name=submitter_name,
                route_name="driver_questions",
            )

            return redirect(url_for("driver_questions", submitted="1"))

        except Exception as e:
            print("DRIVER SURVEY EMAIL ERROR:", e)
            flash("Survey submitted, but email failed to send.", "error")
            return render_form("driver_questions.html")

    return render_form("driver_questions.html")

@app.route("/driver-feedback", methods=["GET", "POST"])
def driver_feedback():
    if request.method == "POST":
        form_data = request.form.to_dict()
        to_email = FORM_EMAIL_MAP["driver_feedback"]
        print("DRIVER FEEDBACK submitted:", form_data)

        field_map = {
            "your_name": "Your Name",
            "driver_name": "Driver Name",
            "quality_of_work": "Quality of Work",
            "safety": "Safety",
            "communication": "Communication",
            "dependability": "Dependability",
            "professionalism": "Professionalism",
            "team_player": "Team Player",
            "vehicle_condition": "Vehicle Condition",
            "dress_code": "Adheres to Dress Code",
            "understands_business": "Understands the Business",
            "meaningful_questions": "Asks Meaningful Questions",
            "accepts_coaching": "Accepts Coaching Well",
            "technological_expertise": "Technological Expertise",
            "printed_route": "Has Printed Copy of Route",
            "retains_information": "Retains Information",
            "sense_of_urgency": "Has Sense of Urgency",
            "chain_of_command": "Follows Chain of Command",
            "client_interest": "Keeps Best Interest of Client in Mind",
            "comments": "Additional Comments",
        }

        try:
            send_form_email(
                subject="Driver Evaluation Feedback Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                form_slug="driver_feedback",
                submitter_name=form_data.get("your_name"),
                route_name="driver_feedback",
            )

            return render_template("driver_feedback.html", submitted=True)

        except Exception as e:
            print("DRIVER FEEDBACK EMAIL ERROR:", e)
            flash("Form submitted, but email failed to send.", "error")
            return render_template("driver_feedback.html", submitted=False)

    return render_template("driver_feedback.html", submitted=False)

@app.route("/upcoming-campaign", methods=["GET", "POST"])
def upcoming_campaign():
    if request.method == "POST":
        form_data = request.form.to_dict()
        to_email = FORM_EMAIL_MAP["upcoming_campaign"]
        print("UPCOMING CAMPAIGN submitted:", form_data)

        field_map = {
            "your_name": "Your Name",
            "email": "Email Address",
            "q0_questions": "Lead Driver",
            "q1_questions": "1. Campaign (Client) Name",
            "q2_questions": "2. Campaign Location (City and State)",
            "q3_questions": "3. Campaign Start Date and Time",
            "q4_questions": "4. Travel Method",
            "q5_m2m_hotel": "5. Need a Market 2 Market (Travel) Hotel?",
            "q6_questions": "6. Unit Number",
            "q7_questions": "7. Know Where the Unit Is Located / How to Access It?",
            "q8_questions": "8. Know How to Log Into the Tablet, XRS, and RoadNet?",
            "q9_questions": "9. Have Routing Information?",
            "q10_questions": "10. Have Hotel Information? (If Applicable)",
            "q11_questions": "11. Know When/Where Vinyls Are Being Delivered?",
            "q12_questions": "12. When and Where Do You Need to Send Posting Photos?",
            "q13_questions": "13. When Are Your First Campaign Photos Due?",
            "q14_questions": "14. Questions Regarding Upcoming Campaign",
            "q15_excited": "15. What Excites You Most About Your Upcoming Campaign?",
        }

        try:
            send_form_email(
                subject="Upcoming Campaign Questionnaire Submitted",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                form_slug="upcoming_campaign_questionnaire",
                submitter_name=form_data.get("your_name"),
                submitter_email=form_data.get("email"),
                route_name="upcoming_campaign",
            )

            return render_template("upcoming_campaign.html", submitted=True)

        except Exception as e:
            print("UPCOMING CAMPAIGN EMAIL ERROR:", e)
            flash("Form submitted, but email failed to send.", "error")
            return render_template("upcoming_campaign.html", submitted=False)

    return render_template("upcoming_campaign.html", submitted=False)

@app.route("/ucr", methods=["GET", "POST"])
def ucr():
    if request.method == "POST":
        run_storage_cleanup()
        form_data = clean_form_data(request.form)
        uploaded_files = request.files.getlist("ucr_photos")
        to_email = FORM_EMAIL_MAP["ucr"]

        print("UCR submitted:", form_data)
        print("UCR file count:", len([f for f in uploaded_files if f and f.filename]))

        # flatten single-value lists for most fields, but keep checkbox list(s)
        cleaned_form_data = {}
        for key, value in form_data.items():
            if key == "missing_items":
                cleaned_form_data[key] = value
            else:
                cleaned_form_data[key] = value[0] if isinstance(value, list) and value else value

        field_map = {
            "name": "Name",
            "date_time": "Date and Time",
            "unit_number": "Unit Number",
            "current_mileage": "Current Mileage",
            "email": "Email",
            "lead_driver": 'Home Based Lead Driver',
            "unit_action": "What Are You Doing With This Unit?",
            "inspection_exp": "DOT/PA Inspection Expiration Date",
            "dot_credential_type": "DOT Credential Type",
            "exterior_ok": "Exterior in Good Condition?",
            "interior_ok": "Interior in Good Condition / Clearance Sticker / No Smoking Sticker?",
            "rear_ok": "Rear of Unit in Good Condition / Door / Floor / Sign?",
            "frame_doors_ok": "Vinyl Frame Doors in Good Condition?",
            "pulleys_ok": "Vinyl System Pulleys and Brackets in Good Condition?",
            "cable_ok": "Vinyl Cable in Good Condition?",
            "pole_ok": "Vinyl Pole / Flashlight in Good Working Condition?",
            "corner_caps_ok": "Corner Caps / Billboard Box Integrity Good?",
            "vinyl_clips": "How Many Vinyl Clips Are With the Unit?",
            "tools_ok": "Required Tools Present?",
            "safety_ok": "All 3 Required Safety Items Present?",
            "cleaning_ok": "Sufficient Cleaning Supplies?",
            "bins_ok": "Clean, Solid, Separate Supply Bins?",
            "missing_items": "Merchants Packet Missing Items",
            "reg_exp": "Registration Expiration",
            "ins_exp": "Insurance Expiration",
            "tablet_ok": "Tablet in Good Condition?",
            "obd_ok": "OBD Port Correctly Handled?",
            "spare_key_ok": "Additional Spare Key in Appropriate Spot?",
            "sanitized": "Fully Sanitized Unit?",
            "comments": "Comments",
        }

        attachments = []
        extra_html = ""

        try:
            for uploaded_file in uploaded_files:
                if uploaded_file and uploaded_file.filename:
                    save_uploaded_file(
                        uploaded_file,
                        UCR_PHOTO_FOLDER,
                        driver_name=cleaned_form_data.get("name"),
                        form_name="ucr_photo"
                    )
                    uploaded_file.stream.seek(0)

            attachments = build_uploaded_file_attachments(
                uploaded_files,
                driver_name=cleaned_form_data.get("name"),
                form_name="ucr_photo"
            )

            if attachments:
                file_list_html = "".join(
                    f"<li>{attachment['filename']}</li>" for attachment in attachments
                )

                extra_html = f"""
                <hr>
                <p><strong>Attached Photo Count:</strong> {len(attachments)}</p>
                <p><strong>Attached Files:</strong></p>
                <ul>{file_list_html}</ul>
                """

            send_form_email(
                subject="UCR - Unit Condition Report Submitted",
                form_data=cleaned_form_data,
                field_map=field_map,
                to_email=to_email,
                attachments=attachments,
                extra_html=extra_html,
                form_slug="ucr",
                submitter_name=form_data.get("name"),
                submitter_email=form_data.get("email"),
                route_name="ucr",
            )

            return redirect(url_for("ucr", submitted="1"))

        except Exception as e:
            print("UCR EMAIL ERROR:", e)
            flash("Form submitted, but email failed to send.", "error")
            return render_form("ucr.html")

    return render_form("ucr.html")

@app.route("/truck-return-checklist", methods=["GET", "POST"])
def truck_return_checklist():
    if request.method == "POST":

        entry = {
            "timestamp_iso": datetime.now(eastern).isoformat(),

            "unit_number": request.form.get("unit_number"),
            "checklist_date": request.form.get("checklist_date"),

            "does_unit_have": request.form.getlist("does_unit_have"),
            "comment_1": request.form.get("comment_1"),
            "working_components": request.form.getlist("working_components"),
            "comment_2": request.form.get("comment_2"),
            "paperwork": request.form.getlist("paperwork"),
            "comment_3": request.form.get("comment_3"),
            "bin_1": request.form.getlist("bin_1"),
            "comment_4": request.form.get("comment_4"),
            "bin_2_all_trucks": request.form.getlist("bin_2_all_trucks"),
            "comment_5": request.form.get("comment_5"),
            "bin_2_new_gas": request.form.getlist("bin_2_new_gas"),
            "comment_6": request.form.get("comment_6"),
            "bin_2_new_diesel": request.form.getlist("bin_2_new_diesel"),
            "comment_7": request.form.get("comment_7"),
            "bin_2_old_diesel": request.form.getlist("bin_2_old_diesel"),
            "comment_8": request.form.get("comment_8"),

            "completed_by": request.form.get("completed_by"),
            "timestamp": datetime.now(eastern).strftime("%Y-%m-%d %I:%M %p %Z"),
        }

        log_path = os.path.join(LOG_FOLDER, "return_checklist_log.jsonl")

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        return render_template("truck_return_checklist.html", submitted=True)

    return render_template("truck_return_checklist.html")

@app.route("/vehicle-accident-report", methods=["GET", "POST"])
def vehicle_accident_report():
    to_email = FORM_EMAIL_MAP["vehicle_accident_report"]
    submitted = False

    other_injuries = []
    for i in range(1, 7):
        name = request.form.get(f"other_name_{i}", "").strip()
        injury = request.form.get(f"other_injury_{i}", "").strip()
        if name or injury:
            other_injuries.append({
                "name": name,
                "injury": injury
            })

    witnesses = []
    for i in range(1, 7):
        name = request.form.get(f"witness_{i}_name", "").strip()
        phone = request.form.get(f"witness_{i}_phone", "").strip()
        address = request.form.get(f"witness_{i}_address", "").strip()
        if name or phone or address:
            witnesses.append({
                "name": name,
                "phone": phone,
                "address": address
            })

    if request.method == "POST":
        report_id = request.form.get("report_id", "").strip() or generate_accident_report_id()
        form_data = {
            "report_id": report_id,
            "edit_resubmitter_name": request.form.get("edit_resubmitter_name", "").strip(),
            "edit_resubmitter_comment": request.form.get("edit_resubmitter_comment", "").strip(),

            "name": request.form.get("name", "").strip(),
            "age": request.form.get("age", "").strip(),
            "address": request.form.get("address", "").strip(),
            "city_state_zip": request.form.get("city_state_zip", "").strip(),
            "drivers_license": request.form.get("drivers_license", "").strip(),
            "license_state": request.form.get("license_state", "").strip(),
            "license_plate": request.form.get("license_plate", "").strip(),
            "plate_state": request.form.get("plate_state", "").strip(),

            "driver_injury": request.form.get("driver_injury", "").strip(),
            "passenger_name": request.form.get("passenger_name", "").strip(),
            "passenger_injury": request.form.get("passenger_injury", "").strip(),
            "other_driver_name": request.form.get("other_driver_name", "").strip(),
            "other_driver_injury": request.form.get("other_driver_injury", "").strip(),
            "other_passenger_name": request.form.get("other_passenger_name", "").strip(),
            "other_passenger_injury": request.form.get("other_passenger_injury", "").strip(),
            "other_injuries": other_injuries,

            "officer_name": request.form.get("officer_name", "").strip(),
            "police_report_made": request.form.get("police_report_made", "").strip(),
            "headquarters": request.form.get("headquarters", "").strip(),
            "badge_number": request.form.get("badge_number", "").strip(),
            "driver_citation_issued": request.form.get("driver_citation_issued", "").strip(),
            "driver_citation_reason": request.form.get("driver_citation_reason", "").strip(),
            "other_driver_citation_issued": request.form.get("other_driver_citation_issued", "").strip(),
            "other_driver_citation_reason": request.form.get("other_driver_citation_reason", "").strip(),

            "driver_vehicle_damage": request.form.get("driver_vehicle_damage", "").strip(),
            "other_vehicle_damage": request.form.get("other_vehicle_damage", "").strip(),
            "other_driver_contact_name": request.form.get("other_driver_contact_name", "").strip(),
            "other_driver_phone": request.form.get("other_driver_phone", "").strip(),
            "other_driver_license": request.form.get("other_driver_license", "").strip(),
            "other_vehicle_owner": request.form.get("other_vehicle_owner", "").strip(),
            "other_owner_phone": request.form.get("other_owner_phone", "").strip(),
            "other_vehicle_make": request.form.get("other_vehicle_make", "").strip(),
            "insurance_company": request.form.get("insurance_company", "").strip(),
            "insurance_phone": request.form.get("insurance_phone", "").strip(),
            "other_property_damage": request.form.get("other_property_damage", "").strip(),
            "property_owner": request.form.get("property_owner", "").strip(),
            "property_owner_phone": request.form.get("property_owner_phone", "").strip(),

            "witnesses": witnesses,

            "accident_date": request.form.get("accident_date", "").strip(),
            "accident_time": request.form.get("accident_time", "").strip(),
            "am_pm": request.form.get("am_pm", "").strip(),
            "light_condition": request.form.get("light_condition", "").strip(),
            "your_direction": request.form.get("your_direction", "").strip(),
            "other_direction": request.form.get("other_direction", "").strip(),
            "street_or_highway": request.form.get("street_or_highway", "").strip(),
            "closest_intersection": request.form.get("closest_intersection", "").strip(),
            "city_county_state": request.form.get("city_county_state", "").strip(),
            "driver_speed_posted": request.form.get("driver_speed_posted", "").strip(),
            "driver_speed_actual": request.form.get("driver_speed_actual", "").strip(),
            "other_speed_posted": request.form.get("other_speed_posted", "").strip(),
            "other_speed_actual": request.form.get("other_speed_actual", "").strip(),

            "weather": request.form.getlist("weather"),
            "area": request.form.get("area", "").strip(),
            "pavement": request.form.get("pavement", "").strip(),
            "traffic_control": request.form.getlist("traffic_control"),
            "conditions": request.form.getlist("conditions"),

            "seat_belt_used": request.form.get("seat_belt_used", "").strip(),
            "air_bag_inflated": request.form.get("air_bag_inflated", "").strip(),

            "accident_description": request.form.get("accident_description", "").strip(),

            "accident_sketch_data": request.form.get("accident_sketch_data", "").strip(),
            "accident_sketch_image": request.form.get("accident_sketch_image", "").strip(),
        }

        form_data["accident_sketch_summary"] = format_accident_sketch_data(
            form_data.get("accident_sketch_data", "")
        )

        pdf_attachment, pdf_filename = build_accident_report_pdf(form_data)

        log_accident_report(
            report_id=report_id,
            form_data=form_data,
            pdf_filename=pdf_filename
        )

        send_form_email(
            subject="Vehicle Accident Report",
            form_data=form_data,
            field_map={},
            to_email=to_email,
            attachments=[pdf_attachment],
            form_slug="vehicle_accident_report",
            submitter_name=form_data.get("name"),
            submitter_email=None,
            route_name="vehicle_accident_report",
            include_pdf=False,
        )

        #print("HAS SKETCH IMAGE:", bool(request.form.get("accident_sketch_image")))
        # log_email_result(...)
        # save attachments later when sketch/uploads are added

        submitted = True

    return render_template(
        "vehicle_accident_report.html",
        submitted=submitted,
        form_data=None,
        view_mode=False,
    )

@app.route("/accident-report-lookup", methods=["GET", "POST"])
def accident_report_lookup():
    report_id = request.form.get("report_id", "").strip()

    report = find_accident_report_by_id(report_id)

    if not report:
        return f"Accident Report ID not found: {report_id}", 404

    form_data = report.get("form_data", {})

    return render_template(
        "vehicle_accident_report.html",
        submitted=False,
        form_data=form_data,
        view_mode=True
    )

@app.route("/unlock-accident-report", methods=["POST"])
def unlock_accident_report():
    pw = request.json.get("password", "")

    if pw == LEAD_PASSWORD:
        return {"success": True}
    else:
        return {"success": False}, 401

@app.route("/driver_introduction", methods=["GET", "POST"])
def driver_intro():
    if request.method == "POST":
        form_data = request.form.to_dict()
        to_email = FORM_EMAIL_MAP["driver_intro"]

        field_map = {
            "your_name": "Your Name",
            "email": "Email",
            "q1": "Do you currently hold a valid Commercial Driver License (CDL)?",
            "q2": "If yes, what year did you obtain your CDL?",
            "q3": "Do you currently have a valid DOT Medical Certificate?",
            "q4": "If yes, what is the expiration date of your DOT Medical Certificate?",
            "q5": "Are you able to lift 35 pounds to waist level as part of the job duties?",
            "q6": "Are you able to comply with the professional dress code?",
            "q7": "Do you agree to comply with the tobacco/vaping policy?",
            "q8": "Are you able and willing to travel by air?",
            "q9": "Do you currently have a REAL ID or a passport?",
            "q10": "Are you able to perform the essential functions of the position with or without reasonable accommodation?",
            "q11": "Are you able to meet the DOT Medical Certificate requirement?",
            "q12": "Please confirm you are still available for your scheduled interview?",
            "add_comments": "Any Additional Comments or Questions?"
        }

        try:
            send_form_email(
                subject=f"Driver Introduction - {form_data.get('your_name')}",
                form_data=form_data,
                field_map=field_map,
                to_email=to_email,
                form_slug="driver_introduction",
                submitter_name=form_data.get("your_name"),
                submitter_email=form_data.get("email"),
                route_name="driver_intro",
            )

            flash("Form submitted successfully!", "success")
            return redirect(url_for("driver_intro"))

        except Exception as e:
            print("DRIVER INTRO ERROR:", e)
            flash("There was an issue submitting the form.", "error")
            return redirect(url_for("driver_intro"))

    return render_template("driver_intro.html")

@app.route('/planning-practice-assignment', methods=['GET', 'POST'])
def planning_practice_assignment():
    to_email = FORM_EMAIL_MAP["planning_practice_assignment"]
    submitted = False

    if request.method == 'POST':

        # Honeypot check
        if request.form.get("do_not_fill"):
            return render_template("planning_practice_assignment.html", submitted=True)

        cleaned_data = clean_form_data(request.form)

        # Send email (no PDF for this one — simple form)
        send_form_email(
            subject="M-M Planning Practice Assignment Submission",
            form_data=cleaned_data,
            field_map={
                "your_name": "Your Name",
                "email": "Email Address",
                "monday_leave_hotel": "Monday - What time do you leave the hotel?",
                "monday_travel_to_bwi": "Monday - How are you traveling to BWI?",
                "monday_ride_time_bwi": "Monday - What time will you arrange your ride?",
                "monday_rdu_to_storage": "Monday - How are you getting to storage from RDU?",
                "monday_ride_time_rdu": "Monday - When will you arrange your ride?",
                "monday_hotel_who_books": "Monday - Who books your hotel in Raleigh for Monday night?",
                "monday_hotel_when_request": "Monday - When will you request your hotel?",
                "tuesday_depart_raleigh": "Tuesday - What time will you depart your hotel in Raleigh?",
                "tuesday_hotel_who_books": "Tuesday - Who books hotel for tonight?",
                "wednesday_checkout_time": "Wednesday - What time will you check out?",
            },
            to_email=to_email,  # swap this
            include_pdf=False
        )

        submitted = True

    return render_template("planning_practice_assignment.html", submitted=submitted)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    quiz_options = [
        # {"value": "2026_01", "label": "January 2026"},
        # {"value": "2026_02", "label": "February 2026"},
        {"value": "2026_03", "label": "March 2026"},
        {"value": "2026_04", "label": "April 2026"},
        {"value": "2026_05", "label": "May 2026"},
        # {"value": "2026_06", "label": "June 2026"},
        # {"value": "2026_07", "label": "July 2026"},
    ]

    if request.method == "POST":
        action = request.form.get("action")

        if action == "download_main_log":
            return redirect(url_for("download_main_log"))

        elif action == "download_quiz_log":
            quiz_id = request.form.get("quiz_id", "").strip()

            if not quiz_id:
                flash("Please select a quiz month.", "error")
                return redirect(url_for("admin"))

            return redirect(url_for("download_quiz_log", quiz_id=quiz_id))

        elif action == "download_security_log":
            return redirect(url_for("download_security_log"))

        elif action == "download_return_checklist_log":
            return redirect(url_for("download_return_checklist_log"))

        elif action == "resend_failed":
            email_id = request.form.get("email_id", "").strip()

            if not email_id:
                flash("Email ID is required.", "error")
                return redirect(url_for("admin"))

            success = resend_failed_email_by_id(email_id)

            if success:
                flash(f"Re-send complete for {email_id}.", "success")
            else:
                flash(f"Could not re-send email for {email_id}.", "error")

            return redirect(url_for("admin"))

    summary = get_log_summary()
    return render_template("admin.html", summary=summary, quiz_options=quiz_options)

@app.route("/admin/download-main-log")
def download_main_log():
    try:
        csv_attachment = build_latest_log_csv_attachment()

        file_path = LOG_FOLDER / csv_attachment["filename"]

        if not file_path.exists():
            flash("Log CSV could not be found.", "error")
            return redirect(url_for("admin"))

        return send_file(
            file_path,
            as_attachment=True,
            download_name=csv_attachment["filename"],
            mimetype="text/csv",
        )

    except Exception as e:
        print("DOWNLOAD MAIN LOG ERROR:", e)
        flash("Could not generate log CSV.", "error")
        return redirect(url_for("admin"))

@app.route("/admin/download-security-log")
def download_security_log():
    try:
        csv_attachment = build_security_log_csv_attachment()

        file_path = LOG_FOLDER / csv_attachment["filename"]

        if not file_path.exists():
            flash("Security log CSV could not be found.", "error")
            return redirect(url_for("admin"))

        return send_file(
            file_path,
            as_attachment=True,
            download_name=csv_attachment["filename"],
            mimetype="text/csv",
        )

    except Exception as e:
        print("DOWNLOAD SECURITY LOG ERROR:", e)
        flash("Could not generate security log CSV.", "error")
        return redirect(url_for("admin"))

@app.route("/admin/download-quiz-log")
def download_quiz_log():
    quiz_id = request.args.get("quiz_id", "").strip()

    if not quiz_id:
        flash("No quiz month selected.", "error")
        return redirect(url_for("admin"))

    file_path = QUIZ_LOG_FOLDER / f"quiz_log_{quiz_id}.csv"

    if not file_path.exists():
        flash(f"No quiz log found for {quiz_id}.", "error")
        return redirect(url_for("admin"))

    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"quiz_log_{quiz_id}.csv",
        mimetype="text/csv",
    )

@app.route("/admin/download-accident-report-log")
def download_accident_report_log():
    try:
        attachment = build_accident_report_log_csv_attachment()
        file_path = LOG_FOLDER / attachment["filename"]

        if not file_path.exists():
            flash("Accident report CSV could not be found.", "error")
            return redirect(url_for("admin"))

        return send_file(
            file_path,
            as_attachment=True,
            download_name=attachment["filename"],
            mimetype="text/csv",
        )

    except Exception as e:
        print("DOWNLOAD ACCIDENT REPORT LOG ERROR:", e)
        flash("Could not generate accident report log CSV.", "error")
        return redirect(url_for("admin"))

@app.route("/merge-pdfs", methods=["GET", "POST"])
def merge_pdfs():
    if request.method == "POST":
        uploaded_files = request.files.getlist("pdf_files")
        file_order_raw = request.form.get("file_order", "")

        pdf_files = [
            f for f in uploaded_files
            if f and f.filename and f.filename.lower().endswith(".pdf")
        ]

        if len(pdf_files) < 2:
            return render_template(
                "merge_pdfs.html",
                error="Please upload at least 2 PDF files."
            )

        ordered_files = pdf_files

        if file_order_raw:
            try:
                indices = [int(x) for x in file_order_raw.split(",") if x.strip() != ""]
                if len(indices) == len(pdf_files):
                    ordered_files = [pdf_files[i] for i in indices]
            except Exception:
                pass

        writer = PdfWriter()

        try:
            for pdf_file in ordered_files:
                writer.append(pdf_file)

            temp_dir = os.path.join(tempfile.gettempdir(), "doit_merge_pdfs")
            os.makedirs(temp_dir, exist_ok=True)

            token = f"{uuid.uuid4().hex}.pdf"
            output_path = os.path.join(temp_dir, token)

            with open(output_path, "wb") as f:
                writer.write(f)

            session["merged_pdf_token"] = token

            return redirect(url_for("merge_pdfs", ready=1))

        except Exception as e:
            if "cryptography" in str(e).lower():
                error_msg = "One or more PDFs may be protected or encrypted. Try re-saving the PDF and uploading it again."
            else:
                error_msg = f"Could not merge PDFs: {e}"

            return render_template("merge_pdfs.html", error=error_msg)

    download_token = session.get("merged_pdf_token")
    ready = request.args.get("ready")

    return render_template(
        "merge_pdfs.html",
        ready=ready,
        download_token=download_token
    )

@app.route("/merge-pdfs/download")
def download_merged_pdf():
    token = session.get("merged_pdf_token")
    if not token:
        abort(404)

    temp_dir = os.path.join(tempfile.gettempdir(), "doit_merge_pdfs")
    file_path = os.path.join(temp_dir, token)

    if not os.path.exists(file_path):
        abort(404)

    return send_file(
        file_path,
        as_attachment=True,
        download_name="merged.pdf",
        mimetype="application/pdf"
    )

@app.route("/admin/download-return-checklist-log")
def download_return_checklist_log():
    return download_return_checklist_log_csv()

@app.route("/resend-failed/<email_id>")
def resend_failed(email_id):
    success = resend_failed_email_by_id(email_id)

    if success:
        return f"Resent {email_id}"
    return f"Failed or not found: {email_id}"

@app.route("/download-pdf-file")
def download_pdf_file():
    return send_from_directory(
        "/var/data/email_pdfs",
        "mark_hooper_ucr_-_unit_condition_report_submitted_20260401_153040.pdf",
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)
