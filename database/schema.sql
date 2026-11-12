CREATE DATABASE IF NOT EXISTS campusfind
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE campusfind;

CREATE TABLE IF NOT EXISTS found_items (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  reference_code VARCHAR(40) NOT NULL,
  item_name VARCHAR(150) NOT NULL,
  category VARCHAR(80) NOT NULL,
  color VARCHAR(80) NOT NULL,
  found_location VARCHAR(150) NOT NULL,
  found_date DATE NOT NULL,
  description TEXT NULL,
  status ENUM('available', 'returned') NOT NULL DEFAULT 'available',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_found_items_reference_code (reference_code),
  KEY idx_found_items_status_date (status, found_date, id)
) ENGINE=InnoDB
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
