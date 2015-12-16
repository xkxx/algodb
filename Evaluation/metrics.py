import math


# All inputs takes in two lists in the following form:
# [[URLs for query1], [URLS for query2], ...
# Try different type of metrics

# Measure distance normalized distance between our rank and google's rank. (Spearman dist)
def normalized_spearman_dist(expected, actual):
    score_dis = 0
    total_dis = 0
    for i in range(len(expected)):
        actual_result = actual[i]
        expected_result = expected[i]
        score_dis += _spearman_single_query(expected_result, actual_result)
        total_dis += len(actual_result) * len(expected_result)
    return 1 - 1.0 * score_dis / total_dis


def _spearman_single_query(expected, actual):
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


# P / R
def precision_recall(expected, actual):
    ttp = 0
    tfp = 0
    tfn = 0
    for i in range(len(expected)):
        e_query = expected[i]
        a_query = actual[i]
        tp, fp, fn = _precision_recall_single(e_query, a_query)
        ttp += tp
        tfp += fp
        tfn += fn
    prec = 1.0 * ttp / (ttp + tfp)
    rec = 1.0 * ttp / (ttp + tfn)
    f1 = 2.0 * (prec * rec) / (prec + rec)
    return prec, rec, f1


def _precision_recall_single(expected, actual):
    tp = 0
    fp = 0
    fn = len(expected)
    for a_query in actual:
        isTP = False
        for e_query in expected:
            if a_query.lower() == e_query.lower():
                fn -= 1
                isTP = True
                break
        if isTP:
            tp += 1
        else:
            fp += 1
    return tp, fp, fn


# Discounted cumulative gain
def ndcg(expected, actual):
    dcg_sum = 0
    for i in range(len(expected)):
        e_query = expected[i]
        a_query = actual[i]
        dcg_sum += _dcg_single_query(e_query, a_query)
    return dcg_sum / len(expected)


def _dcg_single_query(expected, actual):
    dcg = 0
    ideal = []
    for i in range(len(actual)):
        rank = 0
        for j in range(len(expected)):
            if actual[i].lower() == expected[j].lower():
                rank = len(expected) - j
                break
        ideal.append(rank)
        if i == 0:
            dcg += rank
        else:
            dcg += rank / math.log((i+1), 2)

    idcg = 0
    ideal.sort(reverse=True)
    for i in range(len(ideal)):
        if i == 0:
            idcg += ideal[i]
        else:
            idcg += ideal[i] / math.log((i+1), 2)
    if idcg == 0:
        return 0
    else:
        return dcg / idcg