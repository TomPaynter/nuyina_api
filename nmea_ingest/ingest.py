import socket
import pynmea2
import psycopg2
import datetime
import os

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
sock.bind((UDP_IP, UDP_PORT))

print("Listening for NMEA on UDP 1234")

# rolling state so different NMEA sentences can combine
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

while True:
    data, _ = sock.recvfrom(4096)
    line = data.decode("ascii", errors="ignore").strip()

    if not line.startswith("$"):
        continue

    try:
        msg = pynmea2.parse(line)

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

        # Proprietary examples (vendor-specific)
        elif msg.sentence_type == "ASHR":  # $PASHR
            state["heading"] = msg.heading
            state["roll"] = msg.roll
            state["pitch"] = msg.pitch
            state["heave"] = msg.heave

    except Exception as e:
        print("Parse error:", e, line)
