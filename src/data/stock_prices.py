import pandas
import yfinance as yf


def get_stock_prices(
    ticker_symbol: str, start_datetime: str, end_datetime: str
) -> pandas.DataFrame | None:
    try:
        data = yf.download(
            ticker_symbol, start=start_datetime, end=end_datetime, interval="1d"
        )

        # Drop the last two columns - Adj Close, Volume
        data = data.drop(data.columns[-2:], axis=1)

        return data

    except Exception as e:
        print("An error occurred:", e)
        return None


# Example usage
if __name__ == "__main__":
    ticker_symbol = "AAPL"
    start_datetime = "2024-07-08"
    end_datetime = "2024-07-15"

    data = get_stock_prices(ticker_symbol, start_datetime, end_datetime)
    if data is not None:
        print(data.to_csv())
