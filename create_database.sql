-- ============================================
-- SAVING_SERVER Database Creation Script
-- PostgreSQL Database Schema
-- ============================================

-- Create database (run this separately as postgres superuser)
-- CREATE DATABASE savingdb;
-- CREATE USER admin WITH PASSWORD 'password';
-- GRANT ALL PRIVILEGES ON DATABASE savingdb TO admin;

-- Connect to savingdb before running the following
-- \c savingdb;

-- ============================================
-- Drop existing tables (if recreating)
-- ============================================
DROP TABLE IF EXISTS meetings CASCADE;
DROP TABLE IF EXISTS files CASCADE;
DROP TABLE IF EXISTS invites CASCADE;
DROP TABLE IF EXISTS invite_codes CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================
-- Table: users
-- ============================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255),
    
    -- Personal information
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    address TEXT,
    
    -- Work information
    role VARCHAR(50) NOT NULL CHECK (role IN ('hr', 'manager', 'employee', 'guest')),
    department VARCHAR(100),
    employees_list JSONB DEFAULT '[]'::JSONB,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_users_role ON users(role);

-- ============================================
-- Table: files
-- ============================================
CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(255) UNIQUE NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    size BIGINT NOT NULL,
    content_type VARCHAR(100),
    
    uploaded_by VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    file_path TEXT NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    download_count INTEGER DEFAULT 0,
    
    CONSTRAINT fk_files_uploaded_by FOREIGN KEY (uploaded_by) 
        REFERENCES users(email) ON DELETE CASCADE
);

-- Create indexes for files table
CREATE INDEX idx_files_file_id ON files(file_id);
CREATE INDEX idx_files_filename ON files(filename);
CREATE INDEX idx_files_uploaded_by ON files(uploaded_by);
CREATE INDEX idx_files_uploaded_at ON files(uploaded_at);

-- ============================================
-- Table: invites
-- ============================================
CREATE TABLE invites (
    id SERIAL PRIMARY KEY,
    manager_id VARCHAR(255) NOT NULL,
    code VARCHAR(8) UNIQUE NOT NULL,
    max_uses INTEGER DEFAULT 1 NOT NULL,
    current_uses INTEGER DEFAULT 0 NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    used_by JSONB DEFAULT '[]'::JSONB,
    
    CONSTRAINT fk_invites_manager_id FOREIGN KEY (manager_id) 
        REFERENCES users(user_id) ON DELETE CASCADE
);

-- Create indexes for invites table
CREATE INDEX idx_invites_code ON invites(code);
CREATE INDEX idx_invites_manager_id ON invites(manager_id);
CREATE INDEX idx_invites_is_active ON invites(is_active);

-- ============================================
-- Table: invite_codes
-- ============================================
CREATE TABLE invite_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    manager_id INTEGER NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    max_uses INTEGER DEFAULT 1,
    used_count INTEGER DEFAULT 0,
    used_by INTEGER,
    used_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    
    CONSTRAINT fk_invite_codes_manager_id FOREIGN KEY (manager_id) 
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_invite_codes_used_by FOREIGN KEY (used_by) 
        REFERENCES users(id) ON DELETE SET NULL
);

-- Create indexes for invite_codes table
CREATE INDEX idx_invite_codes_code ON invite_codes(code);
CREATE INDEX idx_invite_codes_manager_id ON invite_codes(manager_id);
CREATE INDEX idx_invite_codes_is_active ON invite_codes(is_active);

-- ============================================
-- Table: meetings
-- ============================================
CREATE TABLE meetings (
    id SERIAL PRIMARY KEY,
    meeting_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    object VARCHAR(255),
    description TEXT,
    invitation_link VARCHAR(500),
    password VARCHAR(255),
    
    log_path TEXT,
    invited_employees_list JSONB DEFAULT '[]'::JSONB,
    
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    is_active BOOLEAN DEFAULT TRUE,
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT fk_meetings_created_by FOREIGN KEY (created_by) 
        REFERENCES users(email) ON DELETE CASCADE
);

-- Create indexes for meetings table
CREATE INDEX idx_meetings_meeting_id ON meetings(meeting_id);
CREATE INDEX idx_meetings_created_by ON meetings(created_by);
CREATE INDEX idx_meetings_is_active ON meetings(is_active);
CREATE INDEX idx_meetings_created_at ON meetings(created_at);

-- ============================================
-- Table: activities
-- ============================================
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    activity_id VARCHAR(255) UNIQUE NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    type VARCHAR(100) NOT NULL,
    title VARCHAR(255),
    description TEXT,
    
    creator VARCHAR(255) NOT NULL,
    employees_joined JSONB DEFAULT '[]'::JSONB,
    status VARCHAR(50) DEFAULT 'scheduled',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_activities_creator FOREIGN KEY (creator) 
        REFERENCES users(email) ON DELETE CASCADE
);

-- Create indexes for activities table
CREATE INDEX idx_activities_activity_id ON activities(activity_id);
CREATE INDEX idx_activities_creator ON activities(creator);
CREATE INDEX idx_activities_type ON activities(type);
CREATE INDEX idx_activities_date ON activities(date);
CREATE INDEX idx_activities_status ON activities(status);

-- ============================================
-- Triggers for updated_at
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_meetings_updated_at 
    BEFORE UPDATE ON meetings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Grant permissions to admin user
-- ============================================
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;

-- ============================================
-- Sample data (optional)
-- ============================================
-- Insert a sample HR user
INSERT INTO users (email, user_id, password, first_name, last_name, role, department, employees_list)
VALUES 
    ('hr@example.com', 'hr_001', 'placeholder', 'HR', 'Admin', 'hr', 'Human Resources', '[]'),
    ('manager@example.com', 'mgr_001', 'placeholder', 'John', 'Manager', 'manager', 'Engineering', '["emp_001", "emp_002"]'),
    ('employee@example.com', 'emp_001', 'placeholder', 'Jane', 'Employee', 'employee', 'Engineering', '[]');

-- Insert a sample invite
INSERT INTO invites (manager_id, code, max_uses, expires_at)
VALUES ('mgr_001', 'TEST1234', 5, CURRENT_TIMESTAMP + INTERVAL '7 days');

-- ============================================
-- Verification Queries
-- ============================================
-- SELECT * FROM users;
-- SELECT * FROM files;
-- SELECT * FROM invites;
-- SELECT * FROM invite_codes;

-- Check table sizes
-- SELECT 
--     schemaname,
--     tablename,
--     pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
-- FROM pg_tables
-- WHERE schemaname = 'public'
-- ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
