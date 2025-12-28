-- CE49X Final Project Database Schema
-- PostgreSQL initialization script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text similarity searches

-- Articles table - main storage for collected articles
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    published_at TIMESTAMP,
    source TEXT,
    url TEXT UNIQUE NOT NULL,
    content TEXT,
    description TEXT,
    full_text TEXT,
    processed_text TEXT,
    retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Classification results table - stores LLM-based classifications
CREATE TABLE IF NOT EXISTS classifications (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    ce_areas TEXT[], -- Array of CE area classifications
    ai_technologies TEXT[], -- Array of AI technology classifications
    classification_method TEXT DEFAULT 'llm', -- 'llm' or 'keyword'
    llm_model TEXT, -- Which LLM was used (e.g., 'gpt-4', 'claude-3')
    confidence_score FLOAT, -- Confidence score from LLM (0-1)
    raw_llm_response JSONB, -- Store full LLM response for analysis
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Co-occurrence matrix cache table
CREATE TABLE IF NOT EXISTS cooccurrence_matrix (
    id SERIAL PRIMARY KEY,
    ce_area TEXT NOT NULL,
    ai_technology TEXT NOT NULL,
    count INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ce_area, ai_technology)
);

-- Temporal trends table
CREATE TABLE IF NOT EXISTS temporal_trends (
    id SERIAL PRIMARY KEY,
    period DATE NOT NULL,
    ce_area TEXT,
    ai_technology TEXT,
    article_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(period, ce_area, ai_technology)
);

-- Sources metadata table
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    source_name TEXT UNIQUE NOT NULL,
    source_type TEXT, -- 'rss', 'api', 'sitemap', 'serpapi'
    last_scraped TIMESTAMP,
    article_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url);
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at);
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at);
CREATE INDEX IF NOT EXISTS idx_classifications_article_id ON classifications(article_id);
CREATE INDEX IF NOT EXISTS idx_classifications_ce_areas ON classifications USING GIN(ce_areas);
CREATE INDEX IF NOT EXISTS idx_classifications_ai_technologies ON classifications USING GIN(ai_technologies);
CREATE INDEX IF NOT EXISTS idx_cooccurrence_matrix_ce_area ON cooccurrence_matrix(ce_area);
CREATE INDEX IF NOT EXISTS idx_cooccurrence_matrix_ai_tech ON cooccurrence_matrix(ai_technology);
CREATE INDEX IF NOT EXISTS idx_temporal_trends_period ON temporal_trends(period);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_articles_content_fts ON articles USING GIN(to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(content, '') || ' ' || COALESCE(description, '')));

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at
CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- View for articles with classifications
CREATE OR REPLACE VIEW articles_with_classifications AS
SELECT 
    a.id,
    a.title,
    a.published_at,
    a.source,
    a.url,
    a.content,
    a.retrieved_at,
    c.ce_areas,
    c.ai_technologies,
    c.classification_method,
    c.confidence_score,
    c.created_at as classified_at
FROM articles a
LEFT JOIN LATERAL (
    SELECT * FROM classifications 
    WHERE article_id = a.id 
    ORDER BY created_at DESC 
    LIMIT 1
) c ON TRUE;

-- View for statistics
CREATE OR REPLACE VIEW classification_statistics AS
SELECT 
    COUNT(DISTINCT a.id) as total_articles,
    COUNT(DISTINCT CASE WHEN c.ce_areas IS NOT NULL THEN a.id END) as articles_with_ce,
    COUNT(DISTINCT CASE WHEN c.ai_technologies IS NOT NULL THEN a.id END) as articles_with_ai,
    COUNT(DISTINCT CASE WHEN c.ce_areas IS NOT NULL AND c.ai_technologies IS NOT NULL THEN a.id END) as articles_with_both,
    COUNT(DISTINCT c.id) as total_classifications
FROM articles a
LEFT JOIN classifications c ON a.id = c.article_id;

