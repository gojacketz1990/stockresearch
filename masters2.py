import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

def get_masters_leaderboard():
    url = "https://www.espn.com/golf/leaderboard?tournamentId=401811941"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = soup.find('table', class_=lambda x: x and ('Table' in x or 'leaderboard' in x.lower()))
    if not table:
        table = soup.find('table')
    
    rows = table.find_all('tr') if table else []
    
    data = []
    for row in rows:
        cols = row.find_all(['td', 'th'])
        if len(cols) >= 10:          # Need enough columns for R4
            pos = cols[1].get_text(strip=True)      # Usually the POS column
            dummy = ""                               # ← Dummy column (empty)
            player = cols[3].get_text(strip=True).replace('\n', ' ').strip()   # Player name
            score = cols[4].get_text(strip=True)
            today = cols[5].get_text(strip=True)
            thru = cols[6].get_text(strip=True)
            r1 = cols[7].get_text(strip=True) if len(cols) > 7 else ""
            r2 = cols[8].get_text(strip=True) if len(cols) > 8 else ""
            r3 = cols[9].get_text(strip=True) if len(cols) > 9 else ""
            r4 = cols[10].get_text(strip=True) if len(cols) > 10 else ""
            
            data.append([pos, dummy, player, score, today, thru, r1, r2, r3, r4])
    
    df = pd.DataFrame(data, columns=['POS', 'DUMMY', 'PLAYER', 'SCORE', 'TODAY', 'THRU', 'R1', 'R2', 'R3', 'R4'])
    
    # Clean up empty or header rows
    df = df[df['PLAYER'] != ""]
    df = df[~df['PLAYER'].str.contains("PLAYER|NAME", case=False, na=False)]
    
    timestamp = datetime.now().strftime('%I:%M %p EDT')
    print(f"\n=== 2026 Masters Leaderboard - {timestamp} ===\n")
    print(df.to_string(index=False))
    
    # Save CSV (recommended)
    filename = "masters_leaderboard.csv"
    df.to_csv(filename, index=False)
    print(f"\n✅ Saved to {filename} — Ready for Google Sheets!")
    
    # Tab-separated for direct paste
    print("\n" + "="*85)
    print("COPY BELOW THIS LINE and paste into Google Sheets A1 (then Split text to columns → Tab):")
    print("="*85)
    print(df.to_csv(sep='\t', index=False))
    
    return df


# ================== LIVE UPDATES ==================
if __name__ == "__main__":
    print("Masters Leaderboard Scraper Running...\n")
    while True:
        try:
            get_masters_leaderboard()
        except Exception as e:
            print(f"Error: {e}")
        
        print("\nRefreshing in 60 seconds...")
        time.sleep(60)