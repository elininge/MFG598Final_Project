#Imports pandas and os
import pandas as pd
import os

# File path of the csv file containing player data
file_path = r"C:\Users\Jason\Documents\MFG598Final\NFL draft Prospects - Sheet1.csv"

# Loads the CSV file using pandas
df = pd.read_csv(file_path)

# Cleans the column names and values
df.columns = df.columns.str.strip()
df['Player Position'] = df['Player Position'].str.strip()

# Sorts the players by position and rank initially
df = df.sort_values(by=["Player Position", "Player Rank"])

# Draft order, in order of who picks from 1-32 in the acutal draft
draft_order = [
    "Tennesse Titans", "Cleveland Browns", "New York Giants", "New England Patriots", "Jacksonville Jaguars", "Las Vegas Raiders", "New York Jets", "Carolina Panthers",
    "New Orleans Saints", "Chicago Bears", "San Francisco 49ers", "Dallas Cowboys", "Miami Dolphins", "Indianapolis Colts", "Atlanta Falcons", "Arizona Cardinals",
    "Cincinnati Bengals", "Seattle Seahawks", "Tampa Bay Buccaneers", "Denver Broncos", "Pittsburgh Steelers", "Los Angeles Chargers", "Green Bay Packers", "Minnesota Vikings",
    "Houston Texans", "Los Angeles Rams", "Baltimore Ravens", "Detroit Lions", "Washington Commanders", "Buffalo Bills", "Kansa City Chiefs", "Philadelphia Eagles"
]

# Team needs, based on which positions are of the upmost need for each team
team_needs = {
    "Tennesse Titans": ["QB", "WR","ED"], "Cleveland Browns": ["ED", "QB","WR"],
    "New York Giants": ["CB", "WR", "OT"], "New England Patriots": ["OT", "ED","WR"],
    "Jacksonville Jaguars": ["DT", "CB","S"], "Las Vegas Raiders": ["WR","RB","CB"],
    "New York Jets": ["OT","ED","TE"], "Carolina Panthers": ["ED","DT","LB"],
    "New Orleans Saints": ["TE","OT","ED"], "Chicago Bears": ["RB","ED","CB"],
    "San Francisco 49ers": ["DT","OT","ED"], "Dallas Cowboys":["RB","WR","OT"], 
    "Miami Dolphins":["OT","OG","S"], "Indianapolis Colts":["TE","S","ED"],
    "Atlanta Falcons": ["ED","DT","OG"], "Arizona Cardinals": ["DT","OG","ED"],
    "Cincinnati Bengals": ["CB","DT","OG"], "Seattle Seahawks": ["OT","OG","ED"],
    "Tampa Bay Buccaneers": ["ED","DB","LB"], "Denver Broncos": ["RB","TE","DT"],
    "Pittsburgh Steelers": ["QB","RB","CB"], "Los Angeles Chargers": ["WR","TE","DT"],
    "Green Bay Packers": ["WR","CB","ED"], "Minnesota Vikings": ["DT","CB","S"],
    "Houston Texans":["WR","OT","OG"], "Los Angeles Rams": ["CB","TE","LB"],
    "Baltimore Ravens": ["OG","ED","CB"], "Detroit Lions": ["ED","OG","DT"],
    "Washington Commanders": ["ED","CB","OG"], "Buffalo Bills": ["ED","CB","WR"],
    "Kansa City Chiefs": ["OT","DT","TE"], "Philadelphia Eagles": ["G","LB","TE"]
}

# Asks for user to imput which picks they want to control 
user_input = input("Enter pick numbers you want to control (e.g. 1-16,18,20): ")
user_picks = set()
for part in user_input.split(','):
    if '-' in part:
        start, end = map(int, part.split('-'))
        user_picks.update(range(start, end + 1))
    else:
        user_picks.add(int(part))

# Empty list to store the draft results
draft_results = []

# Shows the current draft board, the players drafted, and the top remaining players 
def show_draft_board(results, remaining_players):
    print("\n📋 Draft Board")
    print("----------------")
    for pick in results:
        print(f"{pick['Pick']:>2}. {pick['Team']:<25} - {pick['Player']} ({pick['Position']})")
    print("\nTop Remaining Players:")
    top_players = remaining_players.sort_values("Player Rank").head(15)
    print(top_players[["Player Rank", "Name", "Player Position", "School"]].to_string(index=False))

# Assigns a grade to each pick based on player rank and team need
def assign_grade(pick_number, player_rank, position, team_needs):
    value_diff = player_rank - pick_number
    fills_need = position in team_needs
    buffer = int(pick_number * 0.2) + 5 

    if fills_need and value_diff <= 0:
        return "A+"
    elif fills_need and value_diff <= buffer:
        return "A"
    elif fills_need:
        return "B+"
    elif not fills_need and value_diff <= 0:
        return "A"
    elif not fills_need and value_diff <= buffer:
        return "B"
    else:
        return "C"

# Loops through each pick, assigning a pick number to each team 
for pick_number, team in enumerate(draft_order, start=1):
    needs = team_needs.get(team, [])
    player_picked = None

    # User pick function in loop and positional filter input
    if pick_number in user_picks:
        while True:
            show_draft_board(draft_results, df)
            print(f"\n🟦 It's your pick! ({pick_number}) - {team}")
            pos_input = input("Enter position to filter by (e.g. WR, QB), or type 'all' to see top players, or 'done' to select: ").strip().upper()
            # Allows user to get out of positional filter
            if pos_input == "DONE":
                print("You must select a player before continuing.")
                continue
            # Positional Filter to show all top 20 avaliable players based on rank
            if pos_input == "ALL":
                filtered = df.sort_values("Player Rank").head(20)
            else:
                # Filter top 20 players based on position
                filtered = df[df["Player Position"].str.upper() == pos_input].sort_values("Player Rank").head(20)
   
            # Prints a statement if all players at that postion are gone
            if filtered.empty:
                print(f"No available players found for position '{pos_input}'. Try again.")
                continue

            # Prints the filtered list of players
            print("\nAvailable Players:")
            print(filtered[["Player Rank", "Name", "Player Position", "School"]].reset_index(drop=True).to_string(index=True))

            # Tells user input the players index number to pick them 
            try:
                choice = int(input("Enter the index number of the player you want to pick: "))
                if 0 <= choice < len(filtered):
                    # Removes selected player from the pool
                    player_picked = filtered.iloc[choice]
                    df = df.drop(player_picked.name)
                    break
                else:
                    print("Invalid index. Try again.")
            except ValueError:
                print("Please enter a valid number.")

    else:
        # CPU will pick a top player at need or simply best player available
        for need in needs:
            available = df[df["Player Position"] == need]
            if not available.empty:
                player_picked = available.sort_values("Player Rank").iloc[0]
                df = df.drop(player_picked.name)
                break
        # Picks best player available if other criteria is not met
        if player_picked is None and not df.empty:
            player_picked = df.sort_values("Player Rank").iloc[0]
            df = df.drop(player_picked.name)
    
    # Records pick results 
    if player_picked is not None:
        grade = assign_grade(pick_number, player_picked["Player Rank"], player_picked["Player Position"], needs)
        draft_results.append({
            "Pick": pick_number,
            "Team": team,
            "Player": player_picked["Name"],
            "Position": player_picked["Player Position"],
            "Rank": player_picked["Player Rank"],
            "Grade": grade
        })
    else:
        draft_results.append({
            "Pick": pick_number,
            "Team": team,
            "Player": "No suitable player available",
            "Position": "N/A",
            "Rank": "N/A",
            "Grade": "F"
        })

# Final Draft Results
print("\n🏁 Final Draft Results")
for pick in draft_results:
    print(f"{pick['Pick']:>2}. {pick['Team']:<25} - {pick['Player']} ({pick['Position']}) | Rank: {pick['Rank']} | Grade: {pick['Grade']}")
