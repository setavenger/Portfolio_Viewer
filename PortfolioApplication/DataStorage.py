
import PortfolioApplication.DailyUpdate as DUp


if __name__ == '__main__':
    df1 = DUp.get_prices('NWT.DE')
    print(df1.tail())
