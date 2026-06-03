-- AI-Powered Smart Agriculture System Database Schema

-- Create Database
CREATE DATABASE IF NOT EXISTS smart_agriculture;
USE smart_agriculture;

-- Farmers Table
CREATE TABLE IF NOT EXISTS farmers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    location VARCHAR(255) NOT NULL,
    farm_size FLOAT DEFAULT 0,
    soil_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_location (location)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Predictions Table (stores all prediction history)
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    prediction_type ENUM('crop_recommendation', 'fertilizer_recommendation', 'yield_prediction') NOT NULL,
    input_data TEXT NOT NULL,
    result VARCHAR(500) NOT NULL,
    confidence FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE,
    INDEX idx_farmer_id (farmer_id),
    INDEX idx_prediction_type (prediction_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Crops Table
CREATE TABLE IF NOT EXISTS crops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crop_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    best_season VARCHAR(50),
    water_requirement FLOAT,
    nitrogen_requirement FLOAT,
    phosphorus_requirement FLOAT,
    potassium_requirement FLOAT,
    ideal_temperature_min FLOAT,
    ideal_temperature_max FLOAT,
    ideal_ph_min FLOAT,
    ideal_ph_max FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Fertilizers Table
CREATE TABLE IF NOT EXISTS fertilizers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fertilizer_name VARCHAR(100) UNIQUE NOT NULL,
    fertilizer_type ENUM('Organic', 'Inorganic', 'Mixed') NOT NULL,
    nitrogen_content FLOAT,
    phosphorus_content FLOAT,
    potassium_content FLOAT,
    description TEXT,
    price_per_unit FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Soil Types Table
CREATE TABLE IF NOT EXISTS soil_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    soil_type_name VARCHAR(100) UNIQUE NOT NULL,
    ph_range_min FLOAT,
    ph_range_max FLOAT,
    nitrogen_level VARCHAR(50),
    phosphorus_level VARCHAR(50),
    potassium_level VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Farm Data Table (for tracking farm metrics over time)
CREATE TABLE IF NOT EXISTS farm_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    crop_name VARCHAR(100),
    area_planted FLOAT,
    planting_date DATE,
    soil_type VARCHAR(100),
    ph_level FLOAT,
    nitrogen_level FLOAT,
    phosphorus_level FLOAT,
    potassium_level FLOAT,
    rainfall FLOAT,
    temperature FLOAT,
    humidity FLOAT,
    yield FLOAT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE,
    INDEX idx_farmer_id (farmer_id),
    INDEX idx_crop_name (crop_name),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Weather History Table
CREATE TABLE IF NOT EXISTS weather_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    location VARCHAR(255),
    temperature FLOAT,
    humidity FLOAT,
    rainfall FLOAT,
    weather_condition VARCHAR(100),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE,
    INDEX idx_farmer_id (farmer_id),
    INDEX idx_recorded_at (recorded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==================== Sample Data ====================

-- Insert Sample Crops
INSERT INTO crops (crop_name, description, best_season, water_requirement, nitrogen_requirement, phosphorus_requirement, potassium_requirement, ideal_temperature_min, ideal_temperature_max, ideal_ph_min, ideal_ph_max) VALUES
('Rice', 'Major staple crop', 'Monsoon', 1200, 60, 30, 40, 20, 30, 6.0, 7.0),
('Wheat', 'Winter crop', 'Winter', 450, 100, 50, 50, 15, 25, 6.5, 7.5),
('Maize', 'Versatile crop', 'Summer', 500, 120, 60, 40, 25, 35, 6.0, 7.5),
('Cotton', 'Cash crop', 'Summer', 800, 120, 50, 50, 28, 35, 6.0, 7.0),
('Sugarcane', 'Cash crop', 'Winter', 1500, 120, 60, 60, 20, 30, 6.0, 8.0),
('Potato', 'Vegetable crop', 'Winter', 600, 100, 50, 120, 18, 25, 5.5, 7.0),
('Tomato', 'Vegetable crop', 'Summer', 600, 80, 40, 80, 25, 35, 6.0, 7.0),
('Onion', 'Vegetable crop', 'Winter', 400, 80, 40, 80, 15, 25, 6.0, 7.0);

-- Insert Sample Fertilizers
INSERT INTO fertilizers (fertilizer_name, fertilizer_type, nitrogen_content, phosphorus_content, potassium_content, description, price_per_unit) VALUES
('Urea', 'Inorganic', 46, 0, 0, 'High nitrogen content fertilizer', 500),
('DAP (Di-ammonium phosphate)', 'Inorganic', 18, 46, 0, 'High phosphorus content', 1200),
('MOP (Muriate of Potash)', 'Inorganic', 0, 0, 60, 'High potassium content', 1000),
('NPK 10-10-10', 'Inorganic', 10, 10, 10, 'Balanced fertilizer', 700),
('Cow Manure', 'Organic', 3, 1, 1, 'Organic fertilizer from cow dung', 300),
('Compost', 'Organic', 2, 1, 1, 'Well-decomposed organic matter', 400),
('Vermicompost', 'Organic', 1.5, 1.5, 1, 'Worm-processed organic waste', 800),
('Fish Emulsion', 'Organic', 5, 2, 1, 'Liquid organic fertilizer', 600);

-- Insert Sample Soil Types
INSERT INTO soil_types (soil_type_name, ph_range_min, ph_range_max, nitrogen_level, phosphorus_level, potassium_level, description) VALUES
('Loamy', 6.0, 7.0, 'Medium', 'Medium', 'Medium', 'Ideal for most crops, good drainage'),
('Clay', 5.5, 7.5, 'Low', 'Medium', 'High', 'Retains moisture, poor drainage'),
('Sandy', 5.5, 7.0, 'Low', 'Low', 'Medium', 'Good drainage, low water retention'),
('Silt', 6.0, 8.0, 'High', 'Medium', 'Medium', 'Fine particles, good fertility'),
('Peat', 4.0, 6.5, 'Low', 'Low', 'Low', 'High organic matter, acidic'),
('Alluvial', 6.0, 7.5, 'High', 'Medium', 'High', 'Fertile, good for crops');
