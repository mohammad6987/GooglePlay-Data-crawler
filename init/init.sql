CREATE TABLE IF NOT EXISTS apps_info (
    app_id VARCHAR PRIMARY KEY,
    app_name VARCHAR,
    min_installs BIGINT,
    score REAL, 
    ratings INT,
    reviews_count INT,
    updated INT,
    version VARCHAR,
    ad_supported BOOLEAN
);

CREATE TABLE IF NOT EXISTS apps_info_history (
    id SERIAL PRIMARY KEY,
    app_id VARCHAR,
    title VARCHAR,
    min_installs BIGINT,
    score REAL, 
    ratings INT,
    reviews_count INT,
    updated INT,
    version VARCHAR,
    ad_supported BOOLEAN,
    time_stamp TIMESTAMP
);

INSERT INTO apps_info (app_id, app_name)
VALUES 
       ('com.instagram.android' , 'Instagram'),
       ('org.telegram.messenger', 'Telegram'),
       ('com.whatsapp' , 'WhatsApp Messenger'),
       ('ir.mci.ecareapp' , 'MyMCI')
ON CONFLICT (app_id) DO NOTHING;       

