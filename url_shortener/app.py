from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, URL
from config import Config
from utils import (
    is_valid_url_format,
    is_url_reachable,
    canonicalize_url,
    md5_short_code,
    random_short_code
)

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/", methods=["GET", "POST"])
    def index():
        short_full_url = None

        if request.method == "POST":
            original_url = request.form.get("original_url", "").strip()
            use_random = bool(request.form.get("use_random"))

            # Validate format
            if not is_valid_url_format(original_url):
                flash("Please enter a valid URL with http:// or https://", "danger")
                return render_template("index.html", short_full_url=None)

            # Canonicalize
            original_url = canonicalize_url(original_url)

            # Reachability check
            if not is_url_reachable(original_url):
                flash("The URL appears unreachable. Please check and try again.", "warning")
                return render_template("index.html", short_full_url=None)

            # Generate short code
            short_code = md5_short_code(original_url, length=6) if not use_random else random_short_code(6)

            # Handle collisions: if code exists but points to different URL, regenerate randomly
            existing = URL.query.filter_by(short_code=short_code).first()
            if existing and existing.original_url != original_url:
                # regenerate random until unique
                attempts = 0
                while existing and attempts < 5:
                    short_code = random_short_code(6)
                    existing = URL.query.filter_by(short_code=short_code).first()
                    attempts += 1

            # Upsert: if same original exists with same code, reuse; else create new
            record = URL.query.filter_by(short_code=short_code).first()
            if record is None:
                record = URL(original_url=original_url, short_code=short_code)
                db.session.add(record)
                db.session.commit()

            # Build full short URL
            try:
                short_full_url = url_for("redirect_short", short_code=record.short_code, _external=True)
            except RuntimeError:
                # Fallback if SERVER_NAME not set—use BASE_URL if provided
                base = app.config.get("BASE_URL", "")
                if base:
                    short_full_url = f"{base}/{record.short_code}"
                else:
                    short_full_url = f"/{record.short_code}"

            flash("URL shortened successfully!", "success")

        return render_template("index.html", short_full_url=short_full_url)

    @app.route("/history", methods=["GET"])
    def history():
        urls = URL.query.order_by(URL.created_at.desc()).all()
        return render_template("history.html", urls=urls)

    @app.route("/<string:short_code>", methods=["GET"])
    def redirect_short(short_code):
        record = URL.query.filter_by(short_code=short_code).first()
        if not record:
            flash("Short URL not found.", "danger")
            return redirect(url_for("index"))
        return redirect(record.original_url, code=302)

    # Optional API endpoint for AJAX shortening
    @app.route("/api/shorten", methods=["POST"])
    def api_shorten():
        data = request.get_json(silent=True) or {}
        original_url = (data.get("original_url") or "").strip()
        use_random = bool(data.get("use_random"))

        if not is_valid_url_format(original_url):
            return jsonify({"error": "Invalid URL format"}), 400

        if not is_url_reachable(original_url):
            return jsonify({"error": "URL unreachable"}), 400

        short_code = md5_short_code(original_url, length=6) if not use_random else random_short_code(6)
        existing = URL.query.filter_by(short_code=short_code).first()
        if existing and existing.original_url != original_url:
            attempts = 0
            while existing and attempts < 5:
                short_code = random_short_code(6)
                existing = URL.query.filter_by(short_code=short_code).first()
                attempts += 1

        record = URL.query.filter_by(short_code=short_code).first()
        if record is None:
            record = URL(original_url=original_url, short_code=short_code)
            db.session.add(record)
            db.session.commit()

        short_full_url = url_for("redirect_short", short_code=record.short_code, _external=True)
        return jsonify({"short_url": short_full_url}), 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)