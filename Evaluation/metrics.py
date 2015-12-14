# Takes in two lists in the following form:
# [[URLs for query1], [URLS for query2], ...
# Measure distance normalized distance between our rank and google's rank.
def mean_percentile_rank(expected, actual):
    score_dis = 0
    total_dis = 0
    for i in range(len(expected)):
        actual_result = actual[i]
        expected_result = expected[i]
        score_dis += mean_percentile_rank_single_query(expected_result, actual_result)
        total_dis += len(actual_result) * len(expected_result)
    return 1 - 1.0 * score_dis / total_dis

def mean_percentile_rank_single_query(expected, actual):
    total_dis = 0
    for i in range(len(actual)):
        dis = len(expected)
        actual_URL = actual[i]
        for j in range(len(expected)):
            expected_URL = expected[j]
            if actual_URL.lower() == expected_URL.lower():
                dis = j - i
                break
        total_dis += dis
    return total_dis
