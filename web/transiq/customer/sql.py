from django.db import connection


def get_ranking_results(user_id):
    addr_rank_sql = address_ranking_sql(user_id)
    city_rank_sql = city_ranking_sql(user_id)
    cursor = connection.cursor()

    cursor.execute(addr_rank_sql)
    address_scores = cursor.fetchall()

    cursor.execute(city_rank_sql)
    city_scores = cursor.fetchall()

    return city_scores, address_scores


def address_ranking_sql(user_id):
    return """
        SELECT lua.address, lua.city_id, SUM(1.0 / (EXTRACT(EPOCH FROM (NOW() - lua.created_on)) / (3600 * 24) + 1.0)) AS score
            FROM transaction_loadingunloadingaddress lua
            JOIN transaction_transaction tra ON lua.transaction_id = tra.id
            WHERE tra.booking_agent_id = {user_id}
            GROUP BY lua.address, lua.city_id
            ORDER BY score DESC;
    """.format(user_id=user_id)


def city_ranking_sql(user_id):
    return """
        SELECT lua.city_id, SUM(1.0 / (EXTRACT(EPOCH FROM (NOW() - lua.created_on)) / (3600 * 24) + 1.0)) AS score
            FROM transaction_loadingunloadingaddress lua
            JOIN transaction_transaction tra ON lua.transaction_id = tra.id
            WHERE tra.booking_agent_id = {user_id}
            GROUP BY lua.city_id
            ORDER BY score DESC;
    """.format(user_id=user_id)


"""
-- run this, to see how ranking works
-- score = SUM of [1 / (age_in_days + 1)]

SELECT
    city_id,
    SUM(1.0 / (EXTRACT(EPOCH FROM (NOW() - created_on)) / (3600 * 24) + 1.0)) AS score,
    COUNT(city_id) AS frequency,
    MAX(created_on) AS last_used
FROM transaction_loadingunloadingaddress
GROUP BY city_id ORDER BY score DESC;
"""
