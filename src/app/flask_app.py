from datetime import datetime, timedelta

from config.config import NEWS_LOOKBACK_DAYS, TIMESTAMP_FORMAT
from flask import Flask, render_template, request
from scrapers import yahoo_news_scraper
from utils import action, data, sentiment_analyzer, time


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/", methods=["POST"])
    def search():
        input_company = request.form["company"]

        company_exists, [company_name, ticker_symbol] = (
            data.check_company_exists(input_company)
        )
        if company_exists:
            current_timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
            start_timestamp = (
                datetime.now() - timedelta(days=NEWS_LOOKBACK_DAYS)
            ).strftime(TIMESTAMP_FORMAT)
            news = yahoo_news_scraper.get_news_URLs(
                ticker_symbol,
                start_timestamp=start_timestamp,
                end_timestamp=current_timestamp,
                title_flag=True,
            )

            sentiment_scores_of_news = []  # Including the label, the highest sentiment score, and the corresponding label's score
            for index, news_item in enumerate(news):
                paragraphs_with_sentiment_scores = []
                paragraphs = yahoo_news_scraper.get_news_paragraphs(
                    news_item["news_URL"]
                )
                for paragraph in paragraphs:
                    negative_score, neutral_score, positive_score = (
                        sentiment_analyzer.get_sentiment_score(paragraph)
                    )
                    paragraphs_with_sentiment_scores.append(
                        {
                            "content": paragraph,
                            "positive_score": f"{positive_score: .3f}",
                            "neutral_score": f"{neutral_score: .3f}",
                            "negative_score": f"{negative_score: .3f}",
                        }
                    )

                news[index]["paragraphs"] = paragraphs_with_sentiment_scores

                # How long ago
                current_time_seconds = time.convert_timestamp_to_seconds(
                    TIMESTAMP_FORMAT, current_timestamp
                )
                publish_time_seconds = time.convert_timestamp_to_seconds(
                    TIMESTAMP_FORMAT, news_item["publish_date"]
                )
                if current_time_seconds and publish_time_seconds:
                    how_long_ago = time.format_time_difference(
                        current_time_seconds - publish_time_seconds
                    )
                    news[index]["how_long_ago"] = how_long_ago

                # News overall sentiment score
                (
                    sentiment_label,
                    highest_sentiment_score,
                    corresponding_sentiment_score,
                ) = sentiment_analyzer.get_overall_sentiment_score(
                    paragraphs_with_sentiment_scores
                )
                news[index]["overall_sentiment_score"] = {
                    "label": sentiment_label,
                    "score": f"{highest_sentiment_score: .3f}",
                }
                sentiment_scores_of_news.append(
                    {
                        "label": sentiment_label,
                        "highest_score": highest_sentiment_score,
                        "corresponding_score": corresponding_sentiment_score,
                    }
                )

            # Recommended action
            recommended_action, confidence_index = (
                action.get_recommended_action(sentiment_scores_of_news)
            )

            return render_template(
                "index.html",
                company_exists=company_exists,
                company_name=company_name,
                ticker_symbol=ticker_symbol,
                news=news,
                recommended_action=recommended_action,
                confidence_index=f"{confidence_index: .3f}",
            )
        else:
            return render_template(
                "index.html",
                company_exists=company_exists,
                message="No such company exists",
            )

    return app
