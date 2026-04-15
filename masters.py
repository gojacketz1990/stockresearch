import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_masters_leaderboard():
    # ESPN is often easier to scrape; masters.com is more dynamic
    url = "https://www.espn.com/golf/leaderboard"  # or https://www.masters.com/leaderboard
    headers = {"User-Agent": "Mozilla/5.0"}  # Avoid blocking
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the leaderboard table (inspect the page for exact class names - they change)
    rows = soup.find_all('tr', class_=lambda x: x and 'PlayerRow' in x)  # Example selector
    
    data = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 5:
            pos = cols[0].text.strip()
            player = cols[1].text.strip()
            score = cols[2].text.strip()
            today = cols[3].text.strip()
            thru = cols[4].text.strip()
            r1 = cols[5].text.strip()
            # ... add more rounds
            data.append([pos, player, score, today, thru, r1])  # etc.
    
    df = pd.DataFrame(data, columns=['POS', 'PLAYER', 'SCORE', 'TODAY', 'THRU', 'R1'])
    print(df.to_string(index=False))
    return df

# Run it in a loop for live updates
while True:
    get_masters_leaderboard()
    time.sleep(60)  # Refresh every minute