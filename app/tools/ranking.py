def rank_sources(results):
    ranked = []

    for r in results:
        credibility = 0.9 if ".gov" in r["url"] else 0.6
        recency = 0.8 
        relevance = 0.7

        score = (credibility * 0.5) + (recency * 0.3) + (relevance * 0.2)

        r["score"] = score
        ranked.append(r)

    return sorted(ranked, key=lambda x: x["score"], reverse=True)