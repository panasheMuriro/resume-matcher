CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT,
    embedding vector(768)
);

CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    name TEXT,
    resume_text TEXT,
    embedding vector(768)
);

-- Insert sample jobs with empty embeddings
INSERT INTO jobs (title, description) VALUES
('Backend Python Developer', 'Looking for Python + FastAPI experience, Postgres, Docker'),
('Frontend React Engineer', 'Seeking React, TypeScript, TailwindCSS experience'),
('Data Scientist', 'Machine learning, data analysis, Python, TensorFlow');
