PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS locations (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT,
    district TEXT,
    ward TEXT,
    name TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS property_types (
    type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS properties (
    property_id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    current_price REAL,
    area REAL,
    bedrooms INTEGER DEFAULT 0,
    bathrooms INTEGER DEFAULT 0,
    listing_url TEXT UNIQUE,
    listing_date TEXT,
    first_seen TEXT,
    last_seen TEXT,
    type_id INTEGER,
    location_id INTEGER,
    address TEXT,
    price REAL,
    area_sq_m REAL,
    property_type_id INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(type_id) REFERENCES property_types(type_id),
    FOREIGN KEY(location_id) REFERENCES locations(location_id),
    FOREIGN KEY(property_type_id) REFERENCES property_types(type_id)
);

CREATE TABLE IF NOT EXISTS price_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    session_id INTEGER,
    price REAL NOT NULL,
    captured_at TEXT DEFAULT CURRENT_TIMESTAMP,
    recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(property_id) REFERENCES properties(property_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scrape_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_website TEXT NOT NULL,
    started_at TEXT DEFAULT CURRENT_TIMESTAMP,
    finished_at TEXT,
    status TEXT DEFAULT 'running',
    source TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
