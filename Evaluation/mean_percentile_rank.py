# Takes in two lists in the following form:
# [[URLs for query1], [URLS for query2], ...
# Measure distance normalized distance between our rank and google's rank.
def mean_percentile_rank(expected, actual):
    score_dis = 0
    total_dis = 0
    for i in range(len(expected)):
        actual_result = actual[i]
        expected_result = expected[i]

        remaining = set(actual_result)
        for j in range(actual_result):
            dis = len(expected_result)

            for k in range(expected_result):
                if actual_result[j] == expected_result[k]:
                    remaining.remove(expected_result[k])
                    break
            score_dis += dis

        score_dis += len(expected_result) * len(remaining)
        total_dis += len(expected_result) * len(actual_result)
    return 1.0 * score_dis / total_dis


