#!/usr/bin/env python3
import base64
import datetime
import json
import sqlite3

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
CORS(app)

limiter = Limiter(
    app=app, key_func=get_remote_address, default_limits=["100 per 5 minutes"]
)


def format_datetime(dateTime, options=None):
    """Format datetime to ISO format"""
    if options is None:
        options = {
            "year": "numeric",
            "month": "2-digit",
            "day": "2-digit",
            "hour": "2-digit",
            "minute": "2-digit",
            "second": "2-digit",
            "hour12": False,
        }

    dt = datetime.datetime.fromisoformat(dateTime.replace("Z", "+00:00"))
    formatted = dt.strftime("%Y-%m-%dT%H:%M:%S")
    return formatted


def utc_to_iso_format(dateTimeRange):
    """Convert UTC datetime range to local ISO format"""
    if not dateTimeRange or "start" not in dateTimeRange or "end" not in dateTimeRange:
        return {"startLocalISO": None, "endLocalISO": None}

    startLocalISO = format_datetime(dateTimeRange["start"])
    endLocalISO = format_datetime(dateTimeRange["end"])
    return {"startLocalISO": startLocalISO, "endLocalISO": endLocalISO}


def decode_base64_payload(base64Payload):
    """Decode Base64 payload to JSON object"""
    try:
        # Decode Base64 string to bytes
        decoded_bytes = base64.b64decode(base64Payload)

        # Convert bytes to UTF-8 string
        json_string = decoded_bytes.decode("utf-8")

        # Parse JSON string to Python object
        return json.loads(json_string)
    except Exception as error:
        print(f"Base64 decode error: {error}")
        raise ValueError("Invalid Base64 format")


def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect("./reports.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/query", methods=["POST"])
@limiter.limit("100 per 5 minutes")
def query_reports():
    """Query reports endpoint"""
    try:
        if not request.json or "data" not in request.json:
            return jsonify(
                {"error": "Invalid request format, expected {data: base64String}"}
            ), 400

        decoded_data = decode_base64_payload(request.json["data"])

        id_array = decoded_data.get("idArray", [])
        date_time_range = decoded_data.get("dateTimeRange")
        mode = decoded_data.get("mode")

        if not id_array or not mode:
            return jsonify({"error": "Invalid request body"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Step 1: Query keyMap table to get hashed_adv_key for each private_key
        key_map_query = """
            SELECT private_key, hashed_adv_key
            FROM keyMap 
            WHERE private_key IN ({})
        """.format(",".join(["?" for _ in id_array]))

        cursor.execute(key_map_query, id_array)
        key_map_rows = cursor.fetchall()

        # Build bidirectional mapping
        priv_to_hashed = {}
        hashed_to_priv = {}

        for row in key_map_rows:
            priv_to_hashed[row["private_key"]] = row["hashed_adv_key"]
            hashed_to_priv[row["hashed_adv_key"]] = row["private_key"]

        # Get hashed_adv_keys for query
        hashed_adv_keys = list(priv_to_hashed.values())
        if not hashed_adv_keys:
            conn.close()
            return jsonify({"error": "No matching keys found"}), 404

        # Step 2: Query reports_detail table based on mode
        if mode == "realtime":
            query = """
                SELECT t.*
                FROM reports_detail t
                JOIN (
                    SELECT id, MAX(isodatetime) AS latest_isodatetime
                    FROM reports_detail
                    WHERE id IN ({})
                    GROUP BY id
                ) sub
                ON t.id = sub.id AND t.isodatetime = sub.latest_isodatetime
                WHERE t.id IN ({})
            """.format(
                ",".join(["?" for _ in hashed_adv_keys]),
                ",".join(["?" for _ in hashed_adv_keys]),
            )

            params = hashed_adv_keys + hashed_adv_keys
            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Convert rows to dictionaries
            result = [dict(row) for row in rows]

            conn.close()
            return jsonify({"data": result})

        elif mode == "timerange":
            if (
                not date_time_range
                or "start" not in date_time_range
                or "end" not in date_time_range
            ):
                conn.close()
                return jsonify({"error": "Invalid dateTimeRange"}), 400

            iso_format = utc_to_iso_format(date_time_range)
            query = """
                SELECT * 
                FROM reports_detail 
                WHERE id IN ({}) 
                AND isodatetime BETWEEN ? AND ?
            """.format(",".join(["?" for _ in hashed_adv_keys]))

            params = hashed_adv_keys + [
                iso_format["startLocalISO"],
                iso_format["endLocalISO"],
            ]
            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Convert rows to dictionaries
            result = [dict(row) for row in rows]

            conn.close()
            return jsonify({"data": result})

        else:
            conn.close()
            return jsonify({"error": "Invalid mode"}), 400

    except Exception as err:
        return jsonify({"error": str(err)}), 500


if __name__ == "__main__":
    # Initialize database connection and verify table structure
    conn = get_db_connection()
    cursor = conn.cursor()

    # Turn off foreign keys
    cursor.execute("PRAGMA foreign_keys=OFF")
    print("Foreign keys off for SQLite3")

    # Verify reports_detail table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='reports_detail'"
    )
    table = cursor.fetchone()
    if not table:
        print("Table 'reports_detail' does not exist in the database.")
    else:
        print("Table 'reports_detail' exists in the database.")

    conn.close()

    # Start the Flask server
    app.run(host="0.0.0.0", port=3001, debug=True)
