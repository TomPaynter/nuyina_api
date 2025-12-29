import socket
import pynmea2
import psycopg2
import datetime
import os
import logging
import sys

# -----------------------
# Logging → Docker logs
# -----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

UDP_IP = "0.0.0.0"
UDP_PORT = 1234

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "app_db")
DB_USER = os.getenv("DB_USER", "app_user")
DB_PASS = os.getenv("DB_PASS", "password")

conn = psycopg2.connect(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)
conn.autocommit = True
cur = conn.cursor()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind((UDP_IP, UDP_PORT))

log.info("NMEA ingest started, listening on UDP %s", UDP_PORT)

state = {
    "lat": None,
    "lon": None,
    "sog": None,
    "cog": None,
    "heading": None,
    "roll": None,
    "pitch": None,
    "heave": None,
}

def insert_row():
    ts = datetime.datetime.now(datetime.timezone.utc)

    cur.execute("""
        INSERT INTO elog.shipnav (
            timestamp,
            shipnav_timestamp,
            shipnav_latitude,
            shipnav_longitude,
            shipnav_heading_true,
            shipnav_ground_speed,
            shipnav_ground_course,
            shipnav_roll,
            shipnav_pitch,
            shipnav_heave,
            shipnav_depth,
            shipnav_draught_jet,
            shipnav_draught_prop,
            shipnav_transducer_offset,
            shipnav_depth_from_waterline
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            -999, -999, -999, -999, -999
        )
    """, (
        ts,
        ts.timestamp(),
        state["lat"],
        state["lon"],
        state["heading"],
        state["sog"],
        state["cog"],
        state["roll"],
        state["pitch"],
        state["heave"],
    ))

    log.info(
        "Inserted shipnav lat=%.6f lon=%.6f sog=%s cog=%s hdg=%s",
        state["lat"] or -999,
        state["lon"] or -999,
        state["sog"],
        state["cog"],
        state["heading"],
    )

while True:
    data, addr = sock.recvfrom(4096)
    line = data.decode("ascii", errors="ignore").strip()

    if not line.startswith("$"):
        continue

    try:
        msg = pynmea2.parse(line)

        log.debug("Received %s from %s", msg.sentence_type, addr)

        if isinstance(msg, pynmea2.types.talker.GGA):
            state["lat"] = msg.latitude
            state["lon"] = msg.longitude
            insert_row()

        elif isinstance(msg, pynmea2.types.talker.RMC):
            state["lat"] = msg.latitude
            state["lon"] = msg.longitude
            state["sog"] = msg.spd_over_grnd
            state["cog"] = msg.true_course
            insert_row()

        elif msg.sentence_type == "HDT":
            state["heading"] = float(msg.heading)

        elif msg.sentence_type == "VTG":
            state["cog"] = msg.true_track
            state["sog"] = msg.spd_over_grnd_kts

    except Exception as e:
        log.warning("NMEA parse error: %s | %s", e, line)
