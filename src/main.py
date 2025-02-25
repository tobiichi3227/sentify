from app import flask_app
from config.config import TOP_COMPANIES_COUNT
from utils import data

app = flask_app.create_app()


def init():
    data.generate_companies_to_ticker_symbol_json_file(TOP_COMPANIES_COUNT)


if __name__ == "__main__":
    init()
    app.run(debug=True)
