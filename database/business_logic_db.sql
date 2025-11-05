-- ===========================================
-- DATABASE: proticket_business
-- DESCRIPTION: Event, Order, Payment, and Ticket Management
-- ===========================================

-- Create the database
CREATE DATABASE proticket_business
  WITH ENCODING 'UTF8'
  LC_COLLATE = 'en_US.UTF-8'
  LC_CTYPE = 'en_US.UTF-8'
  TEMPLATE template0;

\c proticket_business;

-- UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===========================================
-- 1. ORGANIZERS
-- ===========================================

CREATE TABLE organizers (
  id_organizer SERIAL PRIMARY KEY,
  user_id UUID NOT NULL,
  organization_name VARCHAR(100) NOT NULL,
  status VARCHAR(20) DEFAULT 'draft',         -- draft | approved
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_organizers_user_id ON organizers (user_id);

-- ===========================================
-- 2. EVENTS
-- ===========================================

CREATE TABLE events (
  id_event SERIAL PRIMARY KEY,
  organizer_id INT NOT NULL,
  title VARCHAR(150) NOT NULL,
  description TEXT,
  location VARCHAR(150),
  start_datetime TIMESTAMP NOT NULL,
  price NUMERIC(12,2) NOT NULL CHECK (price >= 0),
  capacity INT NOT NULL CHECK (capacity >= 0),
  status VARCHAR(20) DEFAULT 'draft',         -- draft | published
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_events_organizer
    FOREIGN KEY (organizer_id) REFERENCES organizers (id_organizer)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX idx_events_status_date ON events (status, start_datetime);
CREATE INDEX idx_events_title ON events (title);

-- ===========================================
-- 3. ORDERS
-- ===========================================

CREATE TABLE orders (
  id_order SERIAL PRIMARY KEY,
  buyer_id UUID NOT NULL,
  event_id INT NOT NULL,
  quantity INT NOT NULL CHECK (quantity > 0),
  total_price NUMERIC(12,2) NOT NULL CHECK (total_price >= 0),
  status VARCHAR(20) DEFAULT 'pending',       -- pending | paid | failed
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_orders_event
    FOREIGN KEY (event_id) REFERENCES events (id_event)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX idx_orders_event_status ON orders (event_id, status);
CREATE INDEX idx_orders_buyer ON orders (buyer_id);

-- ===========================================
-- 4. PAYMENTS
-- ===========================================

CREATE TABLE payments (
  id_payment UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id INT NOT NULL UNIQUE,
  provider_txn_id VARCHAR(100) UNIQUE NOT NULL,
  status VARCHAR(20) DEFAULT 'pending',       -- pending | success | failed
  amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_payments_order
    FOREIGN KEY (order_id) REFERENCES orders (id_order)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX idx_payments_status ON payments (status);
CREATE INDEX idx_payments_provider_txn ON payments (provider_txn_id);

-- ===========================================
-- 5. TICKETS
-- ===========================================

CREATE TABLE tickets (
  id_ticket UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id INT NOT NULL,
  ticket_code UUID UNIQUE DEFAULT uuid_generate_v4(),
  pdf_url VARCHAR(255),
  qr_code TEXT,
  issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_tickets_order
    FOREIGN KEY (order_id) REFERENCES orders (id_order)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX idx_tickets_order ON tickets (order_id);
CREATE INDEX idx_tickets_code ON tickets (ticket_code);

-- ===========================================
-- 6. MATERIALIZED VIEW: SALES REPORTS
-- ===========================================
CREATE MATERIALIZED VIEW sales_reports AS
SELECT 
    e.id_event,
    e.title,
    e.capacity,
    COUNT(t.id_ticket) AS sold_tickets,
    COALESCE(SUM(p.amount), 0) AS gross_revenue,
    (e.capacity - COUNT(t.id_ticket)) AS remaining_capacity
FROM events e
LEFT JOIN orders o ON o.event_id = e.id_event
LEFT JOIN payments p ON p.order_id = o.id_order AND p.status = 'success'
LEFT JOIN tickets t ON t.order_id = o.id_order
GROUP BY e.id_event, e.title, e.capacity
ORDER BY e.id_event;