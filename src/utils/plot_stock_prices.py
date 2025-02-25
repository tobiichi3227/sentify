import matplotlib.pyplot as plt
import yfinance as yf


def plot_minutely_detail(ticker: str, start_datetime: str, end_datetime: str):
    try:
        data = yf.download(
            ticker, start=start_datetime, end=end_datetime, interval="5m"
        )

        # data = data.between_time('09:30', '16:00')
        # data = data.reset_index()

        grouped_data = data.groupby(data.index.date)

        plt.figure(figsize=(10, 6))

        for date, group in grouped_data:
            plt.plot(group.index, group["Close"], label=f"{date}")

        # plt.plot(data.index, data['Close'], label='Close Price', color='blue')
        plt.title(
            f"{ticker} Stock Prices from ({start_datetime} to {end_datetime}) at an interval of 5 minutes"
        )
        plt.xlabel("Datetime")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.grid(True)
        plt.savefig(
            f"./src/app/static/images/{ticker}_{start_datetime}_to_{end_datetime}.png"
        )
    except Exception as e:
        print("An error occurred:", e)


# Example usage
if __name__ == "__main__":
    ticker_symbol = "AAPL"
    start_datetime = "2024-07-08"
    end_datetime = "2024-07-15"

    plot_minutely_detail(ticker_symbol, start_datetime, end_datetime)
