"""Read-only release inventory; intentionally contains no user-supplied SQL."""

import json
import logging
import os
import uuid

import psycopg
from flask import Flask, g, jsonify, request


def query_releases():
    # The application role has SELECT only; migrations use a separate identity.
    with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=3) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version, description FROM releases ORDER BY id DESC LIMIT 20")
            return [{"version": row[0], "description": row[1]} for row in cursor.fetchall()]


def create_app():
    application = Flask(__name__)
    application.config.update(MAX_CONTENT_LENGTH=4096)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    @application.before_request
    def start_request():
        g.request_id = str(uuid.uuid4())

    @application.after_request
    def secure_response(response):
        response.headers.update(
            {
                "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "no-referrer",
                "Cache-Control": "no-store",
                "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
                "X-Request-ID": g.request_id,
            }
        )
        # Do not log URLs, query strings, headers, request bodies, or credentials.
        application.logger.info(
            json.dumps(
                {
                    "event": "http_request",
                    "request_id": g.request_id,
                    "method": request.method,
                    "route": request.url_rule.rule if request.url_rule else "unmatched",
                    "status": response.status_code,
                }
            )
        )
        return response

    @application.get("/")
    def index():
        return jsonify(service="secure-delivery", version="0.1.1", api="/api/releases")

    @application.get("/health/live")
    def live():
        return jsonify(status="alive")

    @application.get("/health/ready")
    def ready():
        try:
            query_releases()
        except (psycopg.Error, KeyError):
            return jsonify(status="not_ready"), 503
        return jsonify(status="ready")

    @application.get("/api/releases")
    def releases():
        try:
            return jsonify(releases=query_releases())
        except (psycopg.Error, KeyError):
            return jsonify(error="database_unavailable"), 503

    @application.errorhandler(404)
    def missing(_error):
        return jsonify(error="not_found"), 404

    @application.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify(error="method_not_allowed"), 405

    return application
