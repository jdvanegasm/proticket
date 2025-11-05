-- ===========================================
-- DATABASE: proticket_auth
-- DESCRIPTION: Authentication and User Management
-- ===========================================

CREATE DATABASE IF NOT EXISTS proticket_auth
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE proticket_auth;

-- ===========================================
-- 1. ROLES
-- ===========================================

CREATE TABLE roles (
  id_role INT AUTO_INCREMENT PRIMARY KEY,
  role_name VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

INSERT INTO roles (role_name) VALUES
('buyer'),
('organizer'),
('admin');

-- ===========================================
-- 2. USERS
-- ===========================================

CREATE TABLE users (
  id_user CHAR(36) PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role_id INT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_login DATETIME DEFAULT NULL,
  CONSTRAINT fk_users_role
    FOREIGN KEY (role_id) REFERENCES roles (id_role)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB;

-- INDEXES
CREATE INDEX idx_users_role ON users (role_id);

-- ===========================================
-- 3. PASSWORD RESET TOKENS
-- ===========================================

CREATE TABLE password_reset_tokens (
  id_token CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  token_hash VARCHAR(255) NOT NULL,
  expires_at DATETIME NOT NULL,
  used BOOLEAN DEFAULT FALSE,
  CONSTRAINT fk_tokens_user
    FOREIGN KEY (user_id) REFERENCES users (id_user)
    ON DELETE CASCADE
) ENGINE=InnoDB;

-- INDEXES
CREATE INDEX idx_tokens_user ON password_reset_tokens (user_id);
CREATE INDEX idx_tokens_expires ON password_reset_tokens (expires_at);

-- ===========================================
-- DEFAULT CHARACTERISTICS
-- ===========================================
ALTER DATABASE proticket_auth CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;