def recall_at_k(
    retrieved_doc_ids: list[str],
    expected_doc_ids: list[str],
    k: int,
) -> float:
    if not expected_doc_ids or k <= 0:
        return 0.0
    seen = set()
    found = 0
    for doc_id in retrieved_doc_ids[:k]:
        if doc_id not in seen:
            seen.add(doc_id)
            if doc_id in expected_doc_ids:
                found += 1
    return found / len(expected_doc_ids)


def hit_at_k(
    retrieved_doc_ids: list[str],
    expected_doc_ids: list[str],
    k: int,
) -> float:
    if not expected_doc_ids or k <= 0:
        return 0.0
    top_k = set()
    for doc_id in retrieved_doc_ids[:k]:
        top_k.add(doc_id)
    for doc_id in expected_doc_ids:
        if doc_id in top_k:
            return 1.0
    return 0.0


def reciprocal_rank(
    retrieved_doc_ids: list[str],
    expected_doc_ids: list[str],
) -> float:
    if not expected_doc_ids:
        return 0.0
    expected_set = set(expected_doc_ids)
    seen = set()
    deduped_rank = 0
    for doc_id in retrieved_doc_ids:
        if doc_id in seen:
            continue
        deduped_rank += 1
        seen.add(doc_id)
        if doc_id in expected_set:
            return 1.0 / deduped_rank
    return 0.0


def mean_reciprocal_rank(reciprocal_ranks: list[float]) -> float:
    if not reciprocal_ranks:
        return 0.0
    return sum(reciprocal_ranks) / len(reciprocal_ranks)


def expected_doc_coverage(
    retrieved_doc_ids: list[str],
    expected_doc_ids: list[str],
    k: int,
) -> float:
    if not expected_doc_ids or k <= 0:
        return 0.0
    found = 0
    seen = set()
    for doc_id in retrieved_doc_ids[:k]:
        if doc_id not in seen:
            seen.add(doc_id)
            if doc_id in expected_doc_ids:
                found += 1
    return found / len(expected_doc_ids)
