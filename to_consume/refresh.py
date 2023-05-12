def get_stale_records(conn, stale_threshold=0.1) -> list[str]:
    query = """
        WITH dates AS (
            SELECT
                imdb_id,
                updated_at :: DATE,
                date_released
            FROM
                titles
            UNION
            SELECT
                title_imdb_id imdb_id,
                updated_at :: DATE,
                date_released
            FROM
                title_episodes
        ),
        dates2 AS (
            SELECT
                imdb_id,
                updated_at,
                COALESCE(date_released, CURRENT_DATE) date_released
            FROM
                dates
        ),
        stale AS (
            SELECT
                DISTINCT ON (imdb_id) imdb_id,
                (CURRENT_DATE - updated_at) :: FLOAT / GREATEST((CURRENT_DATE - date_released) :: FLOAT, 1.0) staleness
            FROM
                dates2
            ORDER BY
                imdb_id,
                updated_at DESC
        )
        SELECT
            imdb_id
        FROM
            stale
        WHERE
            staleness > %s;
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (stale_threshold,))
        res = cursor.fetchall()
    return [r[0] for r in res]
