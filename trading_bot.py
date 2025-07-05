"""
Crypto Trading Signal Bot for CoinEx

This bot connects to the CoinEx exchange, fetches historical candlestick data,
calculates technical indicators, generates trading signals, logs them,
and schedules the analysis to run periodically.
"""

import ccxt
import pandas as pd
import ta
import schedule
import time
import os
from datetime import datetime

# --- Configuration ---
# Trading pairs and timeframes to monitor
# Example: [('BTC/USDT', '1h'), ('ETH/USDT', '4h')]
TRADING_PAIRS_TIMEFRAMES = [
    ('BTC/USDT', '1h'),
    ('ETH/USDT', '1h'),
    ('LTC/USDT', '1h'),
]

# OHLCV data limit
DATA_LIMIT = 250  # Number of candles to fetch for indicator calculation

# CSV Log file
LOG_FILE = 'trading_signals.csv'

# --- Exchange Connection ---
def connect_to_exchange():
    """
    Initializes and returns the CoinEx exchange object.
    Uses public API access only.
    """
    # Note: API key and secret are not strictly required for public endpoints
    # like fetch_ohlcv. If you encounter rate limiting or need access to
    # private endpoints in the future, you would set them here.
    # For this bot, we will proceed without them as per the requirement
    # of "public API only".
    try:
        exchange = ccxt.coinex({
            'rateLimit': 2000,  # milliseconds, adjust as needed
            'enableRateLimit': True,
        })
        # Test connection (optional, as fetch_ohlcv will also test it)
        # exchange.load_markets()
        print("Successfully initialized CoinEx exchange interface.")
        return exchange
    except ccxt.NetworkError as e:
        print(f"Connection to CoinEx failed due to a network error: {e}")
        return None
    except ccxt.ExchangeError as e:
        print(f"Connection to CoinEx failed due to an exchange error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during exchange connection: {e}")
        return None

# --- Data Fetching ---
def fetch_ohlcv_data(exchange, pair, timeframe, limit):
    """
    Fetches historical OHLCV data for a given trading pair and timeframe.
    Converts the data into a pandas DataFrame.
    """
    try:
        print(f"Fetching OHLCV data for {pair} ({timeframe})...")
        # Fetch OHLCV data
        # ccxt fetch_ohlcv returns a list of lists:
        # [timestamp, open, high, low, close, volume]
        ohlcv = exchange.fetch_ohlcv(pair, timeframe, limit=limit)

        if not ohlcv:
            print(f"No data returned for {pair} ({timeframe}).")
            return None

        # Convert to pandas DataFrame
        df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

        # Convert timestamp to datetime objects (assuming timestamp is in milliseconds)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')

        # Set Timestamp as index (optional, but common for time series analysis)
        # df.set_index('Timestamp', inplace=True)

        # Ensure numeric types for OHLCV columns
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col])

        print(f"Successfully fetched {len(df)} candles for {pair} ({timeframe}).")
        return df

    except ccxt.NetworkError as e:
        print(f"Network error while fetching OHLCV for {pair}: {e}")
        return None
    except ccxt.ExchangeError as e:
        print(f"Exchange error while fetching OHLCV for {pair}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching OHLCV for {pair}: {e}")
        return None

# --- Technical Indicator Calculation ---
def calculate_technical_indicators(df):
    """
    Calculates technical indicators (RSI, MACD, EMAs, Bollinger Bands)
    and adds them to the DataFrame.
    """
    if df is None or df.empty:
        print("Cannot calculate indicators: DataFrame is empty or None.")
        return None

    try:
        print("Calculating technical indicators...")

        # RSI (14)
        df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()

        # MACD (12, 26, 9)
        macd = ta.trend.MACD(close=df['Close'], window_slow=26, window_fast=12, window_sign=9)
        df['MACD_line'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        df['MACD_hist'] = macd.macd_diff() # Histogram

        # EMA 50
        df['EMA50'] = ta.trend.EMAIndicator(close=df['Close'], window=50).ema_indicator()

        # EMA 200
        df['EMA200'] = ta.trend.EMAIndicator(close=df['Close'], window=200).ema_indicator()

        # Bollinger Bands (20, 2)
        bollinger = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['BB_high'] = bollinger.bollinger_hband()
        df['BB_low'] = bollinger.bollinger_lband()
        df['BB_mid'] = bollinger.bollinger_mavg() # Middle band (SMA20)

        print("Technical indicators calculated successfully.")
        return df

    except Exception as e:
        print(f"Error calculating technical indicators: {e}")
        return None

# --- Signal Generation ---
def check_signals(df):
    """
    Checks for trading signals based on the calculated indicators.
    Returns the signal ("BUY", "SELL", "NO_SIGNAL") and current price.
    """
    if df is None or df.empty or len(df) < 2: # Need at least 2 rows for crossover checks
        print("Not enough data to check signals.")
        return "NO_SIGNAL", None, None, None, None, None # Added None for indicators

    try:
        # Get the latest and second latest data points
        latest = df.iloc[-1]
        previous = df.iloc[-2]

        current_price = latest['Close']
        rsi = latest['RSI']
        macd_line = latest['MACD_line']
        macd_signal_line = latest['MACD_signal']
        ema50 = latest['EMA50']
        ema200 = latest['EMA200']

        # Check for missing indicator values (e.g., due to insufficient data for calculation period)
        if pd.isna(rsi) or pd.isna(macd_line) or pd.isna(macd_signal_line) or pd.isna(ema50) or pd.isna(ema200) or \
           pd.isna(previous['MACD_line']) or pd.isna(previous['MACD_signal']) or \
           pd.isna(previous['EMA50']) or pd.isna(previous['EMA200']):
            print("Indicators have NaN values. Not enough data for signal generation.")
            return "NO_SIGNAL", current_price, rsi, macd_line, macd_signal_line, ema50, ema200


        # Signal Logic
        # BUY signal: RSI < 30 and MACD bullish crossover and EMA50 crosses above EMA200
        # MACD bullish crossover: current MACD_line > current MACD_signal AND previous MACD_line <= previous MACD_signal
        macd_bullish_crossover = macd_line > macd_signal_line and \
                                 previous['MACD_line'] <= previous['MACD_signal']

        # EMA bullish crossover: current EMA50 > current EMA200 AND previous EMA50 <= previous EMA200
        ema_bullish_crossover = ema50 > ema200 and \
                                previous['EMA50'] <= previous['EMA200']

        if rsi < 30 and macd_bullish_crossover and ema_bullish_crossover:
            return "BUY", current_price, rsi, macd_line, macd_signal_line, ema50, ema200

        # SELL signal: RSI > 70 and MACD bearish crossover and EMA50 crosses below EMA200
        # MACD bearish crossover: current MACD_line < current MACD_signal AND previous MACD_line >= previous MACD_signal
        macd_bearish_crossover = macd_line < macd_signal_line and \
                                 previous['MACD_line'] >= previous['MACD_signal']

        # EMA bearish crossover: current EMA50 < current EMA200 AND previous EMA50 >= previous EMA200
        ema_bearish_crossover = ema50 < ema200 and \
                                previous['EMA50'] >= previous['EMA200']

        if rsi > 70 and macd_bearish_crossover and ema_bearish_crossover:
            return "SELL", current_price, rsi, macd_line, macd_signal_line, ema50, ema200

        return "NO_SIGNAL", current_price, rsi, macd_line, macd_signal_line, ema50, ema200

    except Exception as e:
        print(f"Error checking signals: {e}")
        # Return indicators as None if an error occurs during signal checking itself
        if 'latest' in locals() and not df.empty: # Check if latest was defined
             return "NO_SIGNAL", latest.get('Close'), latest.get('RSI'), latest.get('MACD_line'), \
                    latest.get('MACD_signal'), latest.get('EMA50'), latest.get('EMA200')
        return "NO_SIGNAL", None, None, None, None, None, None


# --- Logging ---
def log_to_csv(timestamp, pair, price, rsi, macd_line, macd_signal, ema50, ema200, signal_type):
    """
    Logs the trading signal and relevant data to a CSV file.
    """
    file_exists = os.path.isfile(LOG_FILE)

    # Use the provided timestamp if it's a datetime object (from candle data)
    # Otherwise, use current time (for errors where candle time might not be available)
    if isinstance(timestamp, datetime):
        log_timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    else: # Assuming it might be already a string or needs current time
        log_timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    # Prepare data for CSV
    data_row = {
        'Timestamp': log_timestamp_str,
        'Pair': pair,
        'Price': f"{price:.8f}" if price is not None else 'N/A', # Format price
        'RSI': f"{rsi:.2f}" if rsi is not None else 'N/A',
        'MACD_Line': f"{macd_line:.5f}" if macd_line is not None else 'N/A',
        'MACD_Signal': f"{macd_signal:.5f}" if macd_signal is not None else 'N/A',
        'EMA50': f"{ema50:.8f}" if ema50 is not None else 'N/A',
        'EMA200': f"{ema200:.8f}" if ema200 is not None else 'N/A',
        'Signal': signal_type
    }

    try:
        with open(LOG_FILE, 'a', newline='') as csvfile:
            fieldnames = ['Timestamp', 'Pair', 'Price', 'RSI', 'MACD_Line', 'MACD_Signal', 'EMA50', 'EMA200', 'Signal']
            writer = pd.DataFrame([data_row]) # Create a DataFrame for easy CSV writing

            if not file_exists:
                writer.to_csv(csvfile, header=True, index=False)
            else:
                writer.to_csv(csvfile, header=False, index=False)
        # print(f"Successfully logged signal to {LOG_FILE}") # Optional: for verbose logging
    except Exception as e:
        print(f"Error logging to CSV: {e}")

# --- Core Analysis Function ---
def run_analysis(exchange, pair, timeframe):
    """
    Runs the full analysis for a single trading pair:
    fetches data, calculates indicators, checks signals, and logs.
    """
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running analysis for {pair} ({timeframe})...")

    # 1. Fetch OHLCV data
    ohlcv_df = fetch_ohlcv_data(exchange, pair, timeframe, DATA_LIMIT)
    if ohlcv_df is None or ohlcv_df.empty:
        print(f"Could not fetch data for {pair}. Skipping analysis.")
        # Log an empty row or specific error status if desired
        log_to_csv(datetime.now(), pair, None, None, None, None, None, None, "DATA_FETCH_ERROR")
        return

    # 2. Calculate technical indicators
    df_with_indicators = calculate_technical_indicators(ohlcv_df.copy()) # Use .copy() to avoid SettingWithCopyWarning
    if df_with_indicators is None or df_with_indicators.empty:
        print(f"Could not calculate indicators for {pair}. Skipping analysis.")
        log_to_csv(datetime.now(), pair, None, None, None, None, None, None, "INDICATOR_CALC_ERROR")
        return

    # 3. Check for signals
    signal, current_price, rsi, macd_line, macd_signal_val, ema50, ema200 = check_signals(df_with_indicators)

    # Prepare data for logging, even if NO_SIGNAL, to have a record of last check if needed
    # However, the requirement is to log only BUY/SELL signals.
    # We will call log_to_csv based on the signal type.

    # 4. Print signal message
    timestamp_str = df_with_indicators['Timestamp'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S') if not df_with_indicators.empty and 'Timestamp' in df_with_indicators.columns and pd.notna(df_with_indicators['Timestamp'].iloc[-1]) else "N/A"

    price_str = f"{current_price:.8f}" if current_price is not None else "N/A"
    rsi_str = f"{rsi:.2f}" if rsi is not None else "N/A"
    macd_str = f"L:{macd_line:.5f} S:{macd_signal_val:.5f}" if macd_line is not None and macd_signal_val is not None else "N/A"
    ema_str = f"E50:{ema50:.8f} E200:{ema200:.8f}" if ema50 is not None and ema200 is not None else "N/A"

    signal_message = (
        f"[{timestamp_str}] Pair: {pair} | Price: {price_str} | "
        f"RSI(14): {rsi_str} | MACD(12,26,9): {macd_str} | "
        f"EMAs: {ema_str} | Signal: {signal}"
    )
    print(signal_message)

    # 5. Log results if BUY or SELL signal
    if signal in ["BUY", "SELL"]:
        log_to_csv(
            df_with_indicators['Timestamp'].iloc[-1], # Use actual candle timestamp for log
            pair,
            current_price,
            rsi,
            macd_line,
            macd_signal_val,
            ema50,
            ema200,
            signal
        )
        print(f"Signal {signal} for {pair} logged.")
    elif signal == "NO_SIGNAL":
        # Optionally, log NO_SIGNAL events if needed for audit, but requirement is only BUY/SELL
        # log_to_csv(datetime.now(), pair, current_price, rsi, macd_line, macd_signal_val, ema50, ema200, signal)
        pass
    else: # Handles error states from check_signals if any custom ones are returned
        log_to_csv(datetime.now(), pair, current_price, rsi, macd_line, macd_signal_val, ema50, ema200, f"UNKNOWN_STATE: {signal}")


# --- Scheduler ---
def main():
    """
    Main function to initialize the bot and schedule the analysis.
    """
    print("Initializing the crypto trading signal bot...")
    exchange = connect_to_exchange()

    if not exchange:
        print("Failed to connect to the exchange. Exiting.")
        return

    # Ensure CSV file has headers if it's new or empty
    if not os.path.isfile(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        try:
            with open(LOG_FILE, 'w', newline='') as csvfile:
                header_writer = pd.DataFrame(columns=['Timestamp', 'Pair', 'Price', 'RSI', 'MACD_Line', 'MACD_Signal', 'EMA50', 'EMA200', 'Signal'])
                header_writer.to_csv(csvfile, index=False)
            print(f"Initialized log file: {LOG_FILE}")
        except Exception as e:
            print(f"Error initializing log file: {e}")


    print("\n--- Bot Configuration ---")
    print(f"Monitored Pairs & Timeframes: {TRADING_PAIRS_TIMEFRAMES}")
    print(f"Data Limit per Fetch: {DATA_LIMIT} candles")
    print(f"Logging to: {LOG_FILE}")
    print("--- Starting Initial Analysis ---")

    # Run analysis once for all pairs at startup
    for pair, timeframe in TRADING_PAIRS_TIMEFRAMES:
        run_analysis(exchange, pair, timeframe) # Pass exchange object

    print("\n--- Scheduling Regular Analysis ---")
    # Schedule the job for each pair and timeframe
    for pair, timeframe in TRADING_PAIRS_TIMEFRAMES:
        # Schedule the job to run every hour, at the start of the hour (e.g., 10:00, 11:00)
        # Using .at(":01") to run it one minute past the hour to ensure candle data is complete.
        schedule.every().hour.at(":01").do(run_analysis, exchange=exchange, pair=pair, timeframe=timeframe)
        print(f"Scheduled hourly analysis for {pair} ({timeframe}) at XX:01.")

    print("\nScheduler started. Bot is now running.")
    print("Press Ctrl+C to stop the bot.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1) # Check every second
    except KeyboardInterrupt:
        print("\nBot stopped by user. Exiting.")
    except Exception as e:
        print(f"An unexpected error occurred in the main loop: {e}")
    finally:
        print("Bot shutdown complete.")


if __name__ == "__main__":
    main()
