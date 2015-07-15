CREATE DATABASE IF NOT EXISTS WallhavenGallery;

GRANT ALL ON WallhavenGallery.* TO 'wallhaven_user'@'localhost' IDENTIFIED BY 'wallhaven';

USE WallhavenGallery;

CREATE TABLE IF NOT EXISTS Image(
    Name VARCHAR(50) PRIMARY KEY,
    Width INT,
    Height INT,
    Format VARCHAR(10),
    Url VARCHAR(150),
    Query VARCHAR(500),
    Local_path VARCHAR(1000)
);

COMMIT;
