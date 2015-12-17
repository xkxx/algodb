import math

# All inputs takes in two lists in the following form:
# [[URLs for query1], [URLS for query2], ...
# Insert one of the metrics into the EVAL_FUNC field in run_final_eval


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


# Discounted cumulative gain. Rather than having a binary relevant or not, assign a score
# based off how relevant the document is, which is determined by the document's rank in
# the ground truth.
# https://en.wikipedia.org/wiki/Discounted_cumulative_gain
def ndcg(expected, actual):
    dcg_sum = 0
    for i in range(len(expected)):
        e_query = expected[i]
        a_query = actual[i]
        dcg_sum += _dcg_single_query(e_query, a_query)
    return dcg_sum / len(expected)


# Precision recall, each actual document gets rated relevant or non relevant if the document appears in the
# expected document list.
# prec = relevant / (relevant + actual docs that weren't relevant)
# rec = relevant / (relevant + expected docs that were not in actual docs)
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


# Mean average precision
# AverageP = sum from i=1 to k of P(k) * rel(k)
def mean_average_precision(expected, actual):
    MAP = 0
    for i in range(len(expected)):
        expected_result = expected[i]
        actual_result = actual[i]
        k = len(expected_result)

        prec = 0
        for j in range(k):
            k_expected = expected_result[:(j+1)]
            k_actual = actual_result[:min(j+1, len(actual_result))]
            tp, fp, _ = _precision_recall_single(k_expected, k_actual)
            if tp + fp != 0:
                prec += 1.0 * tp / (tp + fp)
        MAP += prec / k
    return MAP / len(expected)


# Assume first URL in each expected query is the correct answer.
# Calculate the reciprocal rank of the correct answer  in the actual results. Give
# a reciprocal rank of 0 if it does not appear.
# https://en.wikipedia.org/wiki/Mean_reciprocal_rank
def mean_reciprocal_rank(expected, actual):
    mrr = 0
    for i in range(len(actual)):
        rank = 0
        correct = expected[i][0]

        for j in range(len(actual[i])):
            if actual[i][j].lower() == correct.lower():
                rank = (j+1)
                break

        if rank != 0:
            mrr += 1.0 / rank
    return mrr / len(expected)


# -------------------------------------------------- END METRICS ----------------------------------------------------- #
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
        return 1.0 * dcg / idcg