from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path
import sys
import secrets
from typing import List, Dict

from flask import Flask, render_template, request, redirect, url_for, send_file


if getattr(sys, "frozen", False):
    APP_DIR = Path.home() / "AppData" / "Local" / "JobTracker"
    TEMPLATE_DIR = Path(sys._MEIPASS)
else:
    APP_DIR = Path(__file__).resolve().parent
    TEMPLATE_DIR = APP_DIR

DATA_DIR = APP_DIR / "data"
DATA_PATH = DATA_DIR / "jobs.csv"

app = Flask(
    __name__,
    template_folder=str(TEMPLATE_DIR / "templates"),
    static_folder=str(TEMPLATE_DIR / "static")
)

FIELDS = [
    "id",
    "company",
    "role",
    "date_added",
    "status",
    "salary",
    "location",
    "notes",
    "color",
    "archived",
]

STATUS_ORDER = ["QUEUED", "APPLIED", "INTERVIEWING", "OFFERED", "REJECTED"]


@app.context_processor
def inject_globals() -> dict:
    return {"status_order": STATUS_ORDER}


def ensure_data_file() -> None:
    if DATA_PATH.exists():
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(
            [
                {
                    "id": "0x8F2C4A",
                    "company": "NEURAL_DYNAMICS_INC",
                    "role": "SR_PLATFORM_ENGINEER",
                    "date_added": "2023-10-24",
                    "status": "INTERVIEWING",
                    "salary": "130k-160k",
                    "location": "REMOTE",
                    "notes": "Panel round pending",
                    "color": "blue",
                    "archived": "false",
                },
                {
                    "id": "0xA14E99",
                    "company": "QUANTUM_LOGIC_LABS",
                    "role": "INFRA_ARCHITECT_L6",
                    "date_added": "2023-10-22",
                    "status": "APPLIED",
                    "salary": "150k-180k",
                    "location": "AUSTIN_TX",
                    "notes": "Referral sent",
                    "color": "green",
                    "archived": "false",
                },
                {
                    "id": "0xD77B21",
                    "company": "VOID_PROTOCOLS",
                    "role": "SECURITY_RESEARCHER",
                    "date_added": "2023-10-20",
                    "status": "REJECTED",
                    "salary": "120k-150k",
                    "location": "NYC_NY",
                    "notes": "Reapply after 6 months",
                    "color": "red",
                    "archived": "false",
                },
            ]
        )


def read_jobs() -> List[Dict[str, str]]:
    ensure_data_file()
    with DATA_PATH.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [row for row in reader]


def write_jobs(rows: List[Dict[str, str]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def generate_id(existing: set[str]) -> str:
    while True:
        candidate = f"0x{secrets.token_hex(3).upper()}"
        if candidate not in existing:
            return candidate


def normalize_status(raw_status: str) -> str:
    candidate = raw_status.strip().upper()
    return candidate if candidate in STATUS_ORDER else "QUEUED"


def parse_date(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return datetime.min


def days_since(value: str) -> int:
    parsed = parse_date(value)
    if parsed == datetime.min:
        return 0
    return (date.today() - parsed.date()).days


@app.get("/")
def root() -> str:
    return redirect(url_for("dashboard"))


@app.get("/dashboard")
def dashboard() -> str:
    jobs = read_jobs()
    active = [job for job in jobs if job.get("archived") != "true"]
    total = len(active)
    interviews = sum(1 for job in active if job.get("status") == "INTERVIEWING")
    offers = sum(1 for job in active if job.get("status") == "OFFERED")
    success_rate = (offers / total * 100) if total else 0
    latest = sorted(active, key=lambda job: parse_date(job.get("date_added", "")), reverse=True)[:8]
    for job in latest:
        job["days_since"] = days_since(job.get("date_added", ""))

    return render_template(
        "dashboard.html",
        jobs=latest,
        total=total,
        interviews=interviews,
        success_rate=success_rate,
        uptime=99.9,
    )


@app.get("/applications")
def applications() -> str:
    jobs = read_jobs()
    active = [job for job in jobs if job.get("archived") != "true"]
    active.sort(key=lambda job: parse_date(job.get("date_added", "")), reverse=True)
    for job in active:
        job["days_since"] = days_since(job.get("date_added", ""))
    return render_template("applications.html", jobs=active, status_order=STATUS_ORDER)


@app.route("/entry", methods=["GET", "POST"])
def entry() -> str:
    if request.method == "POST":
        jobs = read_jobs()
        existing_ids = {job["id"] for job in jobs}
        new_job = {
            "id": generate_id(existing_ids),
            "company": request.form.get("company", "").strip().upper(),
            "role": request.form.get("role", "").strip().upper(),
            "date_added": date.today().isoformat(),
            "status": normalize_status(request.form.get("status", "QUEUED")),
            "salary": request.form.get("salary", "").strip(),
            "location": request.form.get("location", "").strip().upper(),
            "notes": request.form.get("notes", "").strip(),
            "color": request.form.get("color", "").strip().lower(),
            "archived": "false",
        }
        jobs.append(new_job)
        write_jobs(jobs)
        return redirect(url_for("applications"))

    return render_template("entry.html", status_order=STATUS_ORDER)


@app.get("/analytics")
def analytics() -> str:
    jobs = read_jobs()
    active = [job for job in jobs if job.get("archived") != "true"]

    by_status = {status: 0 for status in STATUS_ORDER}
    for job in active:
        status = job.get("status", "QUEUED")
        by_status[status] = by_status.get(status, 0) + 1

    monthly_counts: Dict[str, int] = {}
    for job in active:
        month = job.get("date_added", "")[:7]
        if month:
            monthly_counts[month] = monthly_counts.get(month, 0) + 1

    months = sorted(monthly_counts)
    month_pairs = [(month, monthly_counts[month]) for month in months]

    avg_days = 0
    if active:
        avg_days = round(sum(days_since(job.get("date_added", "")) for job in active) / len(active))

    top_locations: Dict[str, int] = {}
    for job in active:
        location = (job.get("location") or "UNKNOWN").strip().upper() or "UNKNOWN"
        top_locations[location] = top_locations.get(location, 0) + 1
    location_pairs = sorted(top_locations.items(), key=lambda item: item[1], reverse=True)[:5]

    return render_template(
        "analytics.html",
        by_status=by_status,
        month_pairs=month_pairs,
        avg_days=avg_days,
        total_active=len(active),
        location_pairs=location_pairs,
    )


@app.get("/archived")
def archived() -> str:
    jobs = read_jobs()
    archived_jobs = [job for job in jobs if job.get("archived") == "true"]
    archived_jobs.sort(key=lambda job: parse_date(job.get("date_added", "")), reverse=True)
    for job in archived_jobs:
        job["days_since"] = days_since(job.get("date_added", ""))
    return render_template("archived.html", jobs=archived_jobs)


@app.post("/update-status/<job_id>")
def update_status(job_id: str) -> str:
    new_status = normalize_status(request.form.get("status", "QUEUED"))
    jobs = read_jobs()
    for job in jobs:
        if job.get("id") == job_id:
            job["status"] = new_status
            break
    write_jobs(jobs)
    return redirect(request.referrer or url_for("applications"))


@app.post("/archive/<job_id>")
def archive(job_id: str) -> str:
    jobs = read_jobs()
    for job in jobs:
        if job.get("id") == job_id:
            job["archived"] = "true"
            break
    write_jobs(jobs)
    return redirect(request.referrer or url_for("applications"))


@app.post("/unarchive/<job_id>")
def unarchive(job_id: str) -> str:
    jobs = read_jobs()
    for job in jobs:
        if job.get("id") == job_id:
            job["archived"] = "false"
            break
    write_jobs(jobs)
    return redirect(request.referrer or url_for("archived"))


@app.get("/export.csv")
def export_csv() -> str:
    ensure_data_file()
    return send_file(DATA_PATH, as_attachment=True, download_name="jobs.csv")


if __name__ == "__main__":
    ensure_data_file()
    app.run(debug=True)
