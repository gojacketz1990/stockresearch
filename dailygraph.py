import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_trading_chart(csv_filepath):
    """
    Reads a CSV file containing DATE, DAILY, and TOTAL columns
    and generates a line graph of the cumulative total.
    """
    try:
        # 1. Load the data from your local file
        # We use parse_dates to ensure the 'DATE' column is a proper datetime object
        df = pd.read_csv(csv_filepath)
        
        # Ensure column names are stripped of any accidental whitespace
        df.columns = df.columns.str.strip()
        
        # Convert Date to datetime objects (handles M/D/YYYY format)
        df['DATE'] = pd.to_datetime(df['DATE'])
        
        # Sort by date just in case the CSV is out of order
        df = df.sort_values('DATE')

        # 2. Setup the Visuals
        plt.style.use('seaborn-v0_8-muted') # Uses a clean, modern style
        fig, ax = plt.subplots(figsize=(12, 7))

        # 3. Plot the 'TOTAL' column
        ax.plot(df['DATE'], df['TOTAL'], 
                color='#1f77b4',       # Classic professional blue
                linewidth=2.5, 
                marker='o',             # Adds dots at each data point
                markersize=5, 
                label='Cumulative Total')

        # 4. Formatting the X-Axis (Dates)
        # This prevents the dates from overlapping and makes them readable
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d, %Y'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2)) # Label every 2 days
        plt.xticks(rotation=45)

        # 5. Adding Labels and Grid
        ax.set_title('Trading Performance: Cumulative Total', fontsize=16, pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Total Profit/Loss ($)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add a horizontal line at 0 for easy "break-even" reference
        ax.axhline(0, color='red', linewidth=1, linestyle='-', alpha=0.5)

        # Fill the area under the curve for better visual impact
        ax.fill_between(df['DATE'], df['TOTAL'], 0, where=(df['TOTAL'] >= 0), 
                        interpolate=True, color='green', alpha=0.1)
        ax.fill_between(df['DATE'], df['TOTAL'], 0, where=(df['TOTAL'] < 0), 
                        interpolate=True, color='red', alpha=0.1)

        # 6. Final Layout and Display
        plt.tight_layout()
        plt.show()

        # Print summary statistics to the console
        print("-" * 30)
        print(f"Analysis for: {csv_filepath}")
        print(f"Total Days Tracked: {len(df)}")
        print(f"Final Total: ${df['TOTAL'].iloc[-1]:.2f}")
        print(f"Max Drawdown Point: ${df['TOTAL'].min():.2f}")
        print("-" * 30)

    except FileNotFoundError:
        print(f"Error: The file '{csv_filepath}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Change 'your_data.csv' to the actual name of your file
    generate_trading_chart('daily.csv')