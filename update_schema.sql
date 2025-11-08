-- First, add the new columns if they don't exist
PRAGMA foreign_keys=off;
BEGIN TRANSACTION;

-- Create a new table with the updated schema
CREATE TABLE IF NOT EXISTS service_new (
    id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    content TEXT,
    icon VARCHAR(50),
    image_path VARCHAR(200),
    is_featured BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    order_position INTEGER DEFAULT 0,
    created_at DATETIME,
    updated_at DATETIME,
    PRIMARY KEY (id)
);

-- Copy data from old table to new table
INSERT INTO service_new (id, title, slug, description, content, icon, image_path, is_featured, is_active, order_position, created_at, updated_at)
SELECT 
    id, 
    title, 
    LOWER(REPLACE(title, ' ', '-')) as slug,
    description,
    description as content,
    icon,
    NULL as image_path,
    0 as is_featured,
    is_active,
    id as order_position,
    created_at,
    datetime('now') as updated_at
FROM service;

-- Drop the old table
DROP TABLE service;

-- Rename the new table
ALTER TABLE service_new RENAME TO service;

COMMIT;
PRAGMA foreign_keys=on;
