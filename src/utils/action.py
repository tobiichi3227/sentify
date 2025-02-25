from config.constants import NEGATIVE, NEUTRAL, POSITIVE


def normalize(action: str, score: float) -> float:
    if action == POSITIVE:
        return score / 2 + 0.5
    return (1 - score) / 2


def get_recommended_action(
    sentiment_scores_of_news: list[dict],
) -> tuple[str, float]:
    news_count = 0
    action = ""
    action_column_score, correspond_column_score = 0.0, 0.0
    positive_count, negative_count = 0, 0
    for item in sentiment_scores_of_news:
        sentiment_label, _, _ = item.values()
        if sentiment_label == NEUTRAL:
            continue

        news_count += 1
        if sentiment_label == POSITIVE:
            positive_count += 1
        elif sentiment_label == NEGATIVE:
            negative_count += 1

    if positive_count >= negative_count:
        action = POSITIVE
    else:
        action = NEGATIVE

    for item in sentiment_scores_of_news:
        (
            sentiment_label,
            highest_sentiment_score,
            corresponding_sentiment_score,
        ) = item.values()
        if sentiment_label == NEUTRAL:
            continue

        if sentiment_label == POSITIVE:
            if action == POSITIVE:
                action_column_score += highest_sentiment_score
                correspond_column_score -= corresponding_sentiment_score
            else:
                action_column_score -= highest_sentiment_score
                correspond_column_score += corresponding_sentiment_score
        if sentiment_label == NEGATIVE:
            if action == NEGATIVE:
                action_column_score += highest_sentiment_score
                correspond_column_score -= corresponding_sentiment_score
            else:
                action_column_score -= highest_sentiment_score
                correspond_column_score += corresponding_sentiment_score

    if action == POSITIVE:
        correspond_column_score = -correspond_column_score
    else:
        action_column_score = -action_column_score

    if news_count:
        action_column_score /= news_count
        correspond_column_score /= news_count

    # Signs not clear enough
    if 0 <= action_column_score - correspond_column_score <= 0.2:
        return "Hold", 0.0

    if action_column_score > correspond_column_score:
        return "Buy", normalize(action, action_column_score)
    else:
        return "Sell", normalize(action, correspond_column_score)
