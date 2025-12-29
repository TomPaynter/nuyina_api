CREATE TABLE elog.shipnav (
    timestamp TIMESTAMPTZ NOT NULL,
    message_type TEXT DEFAULT 'shipnav',

    shipnav_timestamp DOUBLE PRECISION,

    shipnav_latitude DOUBLE PRECISION,
    shipnav_longitude DOUBLE PRECISION,

    shipnav_heading_true DOUBLE PRECISION,
    shipnav_ground_speed DOUBLE PRECISION,
    shipnav_ground_course DOUBLE PRECISION,

    shipnav_roll DOUBLE PRECISION,
    shipnav_pitch DOUBLE PRECISION,

    shipnav_depth DOUBLE PRECISION,
    shipnav_heave DOUBLE PRECISION,

    shipnav_draught_jet DOUBLE PRECISION,
    shipnav_draught_prop DOUBLE PRECISION,

    shipnav_cruise_id INTEGER,
    shipnav_transducer_offset DOUBLE PRECISION,
    shipnav_depth_from_waterline DOUBLE PRECISION
);

SELECT create_hypertable('elog.shipnav', 'timestamp', if_not_exists => TRUE);

GRANT SELECT ON elog.shipnav TO nuyinapi_ro;
SELECT add_retention_policy('elog.shipnav', INTERVAL '90 days');
