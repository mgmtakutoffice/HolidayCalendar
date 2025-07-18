import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
###creds = ServiceAccountCredentials.from_json_keyfile_name(r"D:\Kalyani\Office\Development\Leave_Calender\credentials.json", scope)
import os

creds_path = os.environ.get("GOOGLE_CREDS_PATH", "credentials.json")
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)

client = gspread.authorize(creds)

# Replace with your sheet name
spreadsheet = client.open("Leave Application (Responses)")
leave_sheet = spreadsheet.worksheet("Form Responses 1")
holiday_sheet = spreadsheet.worksheet("Holidays")


@app.route('/')
def index():
    return render_template("calendar.html")

@app.route('/api/leaves')
def get_leaves():
    records = leave_sheet.get_all_records()
    events = []

    for row in records:
        status = row.get("Apprved/Rejected by Anand Akut", "").strip().lower()
        if status in ["rejected", "cancelled"]:
            continue
        
        full_name = row.get("Name", "").strip()
       #name = row.get("Name", "").split(" ")[1]
        name_parts = full_name.strip().split()

        # Get all words except the last
        name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else full_name
        start_str = row.get("Leave From Date")
        end_str = row.get("Leave To Date")
        leave_type = row.get("Half Day / Full Day", "Full Day")

        try:
            start_date = datetime.strptime(start_str, "%m/%d/%Y").date()
            end_date = datetime.strptime(end_str, "%m/%d/%Y").date()

        except:
            continue

        delta = (end_date - start_date).days + 1
        for i in range(delta):
            leave_date = start_date + timedelta(days=i)
            events.append({
                "title": f"{name} ({leave_type})",
                "start": leave_date.isoformat()
            })


    holiday_rows = holiday_sheet.get_all_records()
    for row in holiday_rows:
        holiday_name = row.get("Occasion", "").strip()
        date_str = row.get("Date", "").strip()

        try:
            holiday_date = datetime.strptime(date_str, "%d-%b-%Y").date()
        except:
            continue

        events.append({
            "title": f"{holiday_name}\n(Holiday)",
            "start": holiday_date.isoformat(),
            "allDay": True,
            "color": "#FF9999"  # Light red color for holidays
        })


    return jsonify(events)

#if __name__ == '__main__':
 #   app.run(debug=True, port=5050)

if __name__ == "__main__":
    from waitress import serve
    print("▶️ Starting server on port 8000…")  
    serve(app, host="0.0.0.0", port=8000)
