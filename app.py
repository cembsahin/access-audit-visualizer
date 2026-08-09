"""
Access Review / Audit Log Visualizer
A Flask app that ingests identity/access export CSVs (Okta-style) and
visualizes stale accounts, access by department, and risk flags.
"""
import os
from datetime import datetime, timedelta

import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

from models import db, AccessRecord

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"csv"}
STALE_DAYS_THRESHOLD = 90

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "audit.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
db.init_app(app)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def compute_risk_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived risk columns to an access-log dataframe."""
    df["last_login"] = pd.to_datetime(df["last_login"], errors="coerce")
    cutoff = datetime.utcnow() - timedelta(days=STALE_DAYS_THRESHOLD)

    df["is_stale"] = df["last_login"].isna() | (df["last_login"] < cutoff)
    df["is_admin_role"] = df["role"].str.contains("admin", case=False, na=False)
    df["risk_flag"] = df["is_stale"] & df["is_admin_role"]
    return df


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        flash("Please choose a CSV file to upload.")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Only .csv files are supported.")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        df = pd.read_csv(filepath)
        required_cols = {"username", "department", "role", "status", "last_login"}
        missing = required_cols - set(df.columns)
        if missing:
            flash(f"CSV is missing required columns: {', '.join(sorted(missing))}")
            return redirect(url_for("index"))

        df = compute_risk_flags(df)

        # Replace prior import (demo app: single dataset at a time)
        AccessRecord.query.delete()
        for _, row in df.iterrows():
            record = AccessRecord(
                username=row["username"],
                department=row["department"],
                role=row["role"],
                status=row["status"],
                last_login=None if pd.isna(row["last_login"]) else row["last_login"].to_pydatetime(),
                is_stale=bool(row["is_stale"]),
                risk_flag=bool(row["risk_flag"]),
            )
            db.session.add(record)
        db.session.commit()

    except Exception as exc:  # noqa: BLE001 - surface parse errors to the user
        flash(f"Could not process file: {exc}")
        return redirect(url_for("index"))

    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    records = AccessRecord.query.all()
    total = len(records)
    stale_count = sum(1 for r in records if r.is_stale)
    risk_count = sum(1 for r in records if r.risk_flag)

    return render_template(
        "dashboard.html",
        records=records,
        total=total,
        stale_count=stale_count,
        risk_count=risk_count,
    )


@app.route("/api/department-breakdown")
def department_breakdown():
    records = AccessRecord.query.all()
    counts: dict[str, int] = {}
    for r in records:
        counts[r.department] = counts.get(r.department, 0) + 1
    return jsonify({"labels": list(counts.keys()), "values": list(counts.values())})


@app.route("/api/stale-vs-active")
def stale_vs_active():
    records = AccessRecord.query.all()
    stale = sum(1 for r in records if r.is_stale)
    active = len(records) - stale
    return jsonify({"labels": ["Active", "Stale (90+ days)"], "values": [active, stale]})


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
