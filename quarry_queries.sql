-- ============================================================================
-- WIKIPEDIA MOBILE VISUAL EDITOR ARTICLE CREATION ANALYSIS
-- SQL Queries for Wikimedia Quarry (https://quarry.wmcloud.org/)
-- ============================================================================

-- QUERY 1: Find articles created in last 30 days with mobile visual editor
-- ============================================================================
-- This query identifies new articles (pages) created using mobile visual editor
-- by checking for both 'mobile edit' and 'visualeditor' tags on the first revision

SELECT
    p.page_id,
    p.page_title,
    p.page_namespace,
    r.rev_id as first_revision_id,
    r.rev_timestamp as creation_timestamp,
    r.rev_user_text as creator,
    r.rev_len as initial_length,
    GROUP_CONCAT(DISTINCT ct.ct_tag SEPARATOR ', ') as tags
FROM
    page p
    INNER JOIN revision r ON p.page_id = r.rev_page
    INNER JOIN change_tag ct ON r.rev_id = ct.ct_rev_id
    INNER JOIN change_tag_def ctd ON ct.ct_tag_id = ctd.ctd_id
WHERE
    p.page_namespace = 0  -- Main namespace (articles only)
    AND r.rev_parent_id = 0  -- First revision (article creation)
    AND r.rev_timestamp >= DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 30 DAY), '%Y%m%d%H%i%s')
    AND p.page_id IN (
        -- Subquery to find pages with BOTH mobile and visualeditor tags
        SELECT DISTINCT ct1.ct_rev_id
        FROM change_tag ct1
        INNER JOIN change_tag_def ctd1 ON ct1.ct_tag_id = ctd1.ctd_id
        WHERE ctd1.ctd_name LIKE '%mobile%'
        INTERSECT
        SELECT DISTINCT ct2.ct_rev_id
        FROM change_tag ct2
        INNER JOIN change_tag_def ctd2 ON ct2.ct_tag_id = ctd2.ctd_id
        WHERE ctd2.ctd_name LIKE '%visual%'
    )
GROUP BY
    p.page_id, p.page_title, r.rev_id, r.rev_timestamp, r.rev_user_text, r.rev_len
ORDER BY
    r.rev_timestamp DESC
LIMIT 1000;


-- QUERY 2: Get all available tags (to identify exact tag names)
-- ============================================================================
SELECT
    ctd.ctd_id,
    ctd.ctd_name,
    COUNT(ct.ct_tag_id) as usage_count
FROM
    change_tag_def ctd
    LEFT JOIN change_tag ct ON ctd.ctd_id = ct.ct_tag_id
GROUP BY
    ctd.ctd_id, ctd.ctd_name
HAVING
    ctd_name LIKE '%mobile%'
    OR ctd_name LIKE '%visual%'
    OR ctd_name LIKE '%editor%'
ORDER BY
    usage_count DESC;


-- QUERY 3: Detailed revision history for a specific article
-- ============================================================================
-- Replace 'ARTICLE_TITLE_HERE' with the actual article title
-- This gets all revisions with their tags to analyze editing patterns

SELECT
    r.rev_id,
    r.rev_timestamp,
    r.rev_user_text,
    r.rev_len,
    r.rev_comment,
    r.rev_minor_edit,
    GROUP_CONCAT(DISTINCT ctd.ctd_name SEPARATOR ', ') as tags
FROM
    page p
    INNER JOIN revision r ON p.page_id = r.rev_page
    LEFT JOIN change_tag ct ON r.rev_id = ct.ct_rev_id
    LEFT JOIN change_tag_def ctd ON ct.ct_tag_id = ctd.ctd_id
WHERE
    p.page_title = 'ARTICLE_TITLE_HERE'  -- Replace with actual title
    AND p.page_namespace = 0
GROUP BY
    r.rev_id, r.rev_timestamp, r.rev_user_text, r.rev_len, r.rev_comment, r.rev_minor_edit
ORDER BY
    r.rev_timestamp ASC;


-- QUERY 4: Statistics on mobile visual editor article creations
-- ============================================================================
-- Get aggregate statistics about articles created with mobile VE

SELECT
    DATE(r.rev_timestamp) as creation_date,
    COUNT(DISTINCT p.page_id) as articles_created,
    AVG(r.rev_len) as avg_initial_length,
    MIN(r.rev_len) as min_initial_length,
    MAX(r.rev_len) as max_initial_length,
    COUNT(DISTINCT r.rev_user_text) as unique_creators
FROM
    page p
    INNER JOIN revision r ON p.page_id = r.rev_page
    INNER JOIN change_tag ct ON r.rev_id = ct.ct_rev_id
    INNER JOIN change_tag_def ctd ON ct.ct_tag_id = ctd.ctd_id
WHERE
    p.page_namespace = 0
    AND r.rev_parent_id = 0
    AND r.rev_timestamp >= DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 30 DAY), '%Y%m%d%H%i%s')
    AND ctd.ctd_name IN ('mobile edit', 'mobile web edit', 'visualeditor', 'visualeditor-wikitext')
GROUP BY
    DATE(r.rev_timestamp)
ORDER BY
    creation_date DESC;


-- QUERY 5: Find mobile VE created articles with their revision counts
-- ============================================================================
-- This helps identify which articles had multiple editing sessions

SELECT
    p.page_id,
    p.page_title,
    r.rev_timestamp as created_at,
    r.rev_user_text as creator,
    COUNT(r2.rev_id) as total_revisions,
    r.rev_len as initial_length,
    MAX(r2.rev_len) as current_length,
    MAX(r2.rev_len) - r.rev_len as length_growth
FROM
    page p
    INNER JOIN revision r ON p.page_id = r.rev_page AND r.rev_parent_id = 0
    LEFT JOIN revision r2 ON p.page_id = r2.rev_page
    INNER JOIN change_tag ct ON r.rev_id = ct.ct_rev_id
    INNER JOIN change_tag_def ctd ON ct.ct_tag_id = ctd.ctd_id
WHERE
    p.page_namespace = 0
    AND r.rev_timestamp >= DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 30 DAY), '%Y%m%d%h%i%s')
    AND (ctd.ctd_name LIKE '%mobile%' OR ctd.ctd_name LIKE '%visual%')
GROUP BY
    p.page_id, p.page_title, r.rev_timestamp, r.rev_user_text, r.rev_len
HAVING
    total_revisions > 0
ORDER BY
    total_revisions DESC
LIMIT 100;


-- QUERY 6: User contribution patterns - mobile VE article creators
-- ============================================================================
-- Analyze which users are creating articles with mobile VE

SELECT
    r.rev_user_text as username,
    COUNT(DISTINCT p.page_id) as articles_created,
    AVG(r.rev_len) as avg_article_length,
    MIN(r.rev_timestamp) as first_article,
    MAX(r.rev_timestamp) as latest_article
FROM
    page p
    INNER JOIN revision r ON p.page_id = r.rev_page
    INNER JOIN change_tag ct ON r.rev_id = ct.ct_rev_id
    INNER JOIN change_tag_def ctd ON ct.ct_tag_id = ctd.ctd_id
WHERE
    p.page_namespace = 0
    AND r.rev_parent_id = 0
    AND r.rev_timestamp >= DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 30 DAY), '%Y%m%d%H%i%s')
    AND (ctd.ctd_name LIKE '%mobile%' AND ctd.ctd_name LIKE '%visual%')
GROUP BY
    r.rev_user_text
HAVING
    articles_created >= 1
ORDER BY
    articles_created DESC
LIMIT 50;


-- ============================================================================
-- INSTRUCTIONS FOR USE:
-- ============================================================================
-- 1. Go to https://quarry.wmcloud.org/
-- 2. Create a new query
-- 3. Select "enwiki_p" as the database (English Wikipedia)
-- 4. Copy and paste each query above
-- 5. Run the query to get results
-- 6. Export results as CSV for further analysis
--
-- Note: Some queries may need adjustment based on exact tag names in use.
-- Run QUERY 2 first to identify the exact tag names currently in use.
-- ============================================================================
