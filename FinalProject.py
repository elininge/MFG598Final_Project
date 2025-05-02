# Imports Pandas and Streamlit
import pandas as pd
import streamlit as st

# Loads in the draft csv cleans the data and sorts the data
file_path = r"C:\Users\Jason\Documents\MFG598Final\NFL draft Prospects - Sheet1.csv"
df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()
df['Player Position'] = df['Player Position'].str.strip()
df = df.sort_values(by="Player Rank").reset_index(drop=True)

# Draft order, in order of who picks from 1-32 in the acutal draft
draft_order = [
    "Tennessee Titans", "Cleveland Browns", "New York Giants", "New England Patriots", "Jacksonville Jaguars",
    "Las Vegas Raiders", "New York Jets", "Carolina Panthers", "New Orleans Saints", "Chicago Bears",
    "San Francisco 49ers", "Dallas Cowboys", "Miami Dolphins", "Indianapolis Colts", "Atlanta Falcons",
    "Arizona Cardinals", "Cincinnati Bengals", "Seattle Seahawks", "Tampa Bay Buccaneers", "Denver Broncos",
    "Pittsburgh Steelers", "Los Angeles Chargers", "Green Bay Packers", "Minnesota Vikings", "Houston Texans",
    "Los Angeles Rams", "Baltimore Ravens", "Detroit Lions", "Washington Commanders", "Buffalo Bills",
    "Kansas City Chiefs", "Philadelphia Eagles"
]

# Team needs, based on which positions are of the upmost need for each team
team_needs = {
    "Tennessee Titans": ["QB", "WR", "ED"], "Cleveland Browns": ["ED", "QB", "WR"],
    "New York Giants": ["CB", "WR", "OT"], "New England Patriots": ["OT", "ED", "WR"],
    "Jacksonville Jaguars": ["DT", "CB", "S"], "Las Vegas Raiders": ["WR", "RB", "CB"],
    "New York Jets": ["OT", "ED", "TE"], "Carolina Panthers": ["ED", "DT", "LB"],
    "New Orleans Saints": ["TE", "OT", "ED"], "Chicago Bears": ["RB", "ED", "CB"],
    "San Francisco 49ers": ["DT", "OT", "ED"], "Dallas Cowboys": ["RB", "WR", "OT"], 
    "Miami Dolphins": ["OT", "OG", "S"], "Indianapolis Colts": ["TE", "S", "ED"],
    "Atlanta Falcons": ["ED", "DT", "OG"], "Arizona Cardinals": ["DT", "OG", "ED"],
    "Cincinnati Bengals": ["CB", "DT", "OG"], "Seattle Seahawks": ["OT", "OG", "ED"],
    "Tampa Bay Buccaneers": ["ED", "DB", "LB"], "Denver Broncos": ["RB", "TE", "DT"],
    "Pittsburgh Steelers": ["QB", "RB", "CB"], "Los Angeles Chargers": ["WR", "TE", "DT"],
    "Green Bay Packers": ["WR", "CB", "ED"], "Minnesota Vikings": ["DT", "CB", "S"],
    "Houston Texans": ["WR", "OT", "OG"], "Los Angeles Rams": ["CB", "TE", "LB"],
    "Baltimore Ravens": ["OG", "ED", "CB"], "Detroit Lions": ["ED", "OG", "DT"],
    "Washington Commanders": ["ED", "CB", "OG"], "Buffalo Bills": ["ED", "CB", "WR"],
    "Kansas City Chiefs": ["OT", "DT", "TE"], "Philadelphia Eagles": ["G", "LB", "TE"]
}

# Initializes session state
if "current_pick" not in st.session_state:
    st.session_state.current_pick = 1
if "available_players" not in st.session_state:
    st.session_state.available_players = df.copy()
if "draft_results" not in st.session_state:
    st.session_state.draft_results = []
if "user_teams" not in st.session_state:
    st.session_state.user_teams = []

# Grading function used to grade the picks based on player rank and team needs
def grade_pick(rank, team, position):
    needs = team_needs.get(team, [])
    grade = ""
    if rank <= 5:
        grade = "A" if position in needs else "B+"
    elif rank <= 15:
        grade = "A-" if position in needs else "B"
    elif rank <= 25:
        grade = "B" if position in needs else "C+"
    elif rank <= 50:
        grade = "C" if position in needs else "C-"
    else:
        grade = "D+" if position in needs else "D"
    return grade

# Auto pick simulation for non-user teams
def advance_draft():
    while st.session_state.current_pick <= 32:
        pick_num = st.session_state.current_pick
        if pick_num in st.session_state.user_teams:
            break
        team = draft_order[pick_num - 1]
        needs = team_needs.get(team, [])
        best_match = None
        for need in needs:
            match = st.session_state.available_players[st.session_state.available_players['Player Position'] == need]
            if not match.empty:
                best_match = match.iloc[0]
                break
        if best_match is None:
            best_match = st.session_state.available_players.iloc[0]
        st.session_state.draft_results.append({
            "Pick": pick_num,
            "Team": team,
            "Player": best_match["Name"],
            "Position": best_match["Player Position"],
            "Rank": best_match["Player Rank"],
            "Grade": grade_pick(best_match["Player Rank"], team, best_match["Player Position"])
        })
        st.session_state.available_players = st.session_state.available_players[
            st.session_state.available_players["Name"] != best_match["Name"]
        ].reset_index(drop=True)
        st.session_state.current_pick += 1

# Title of the streamlit app
st.title("🏈 NFL Draft Simulator (First Round)")

# User team setup (allows for user to select which teams they want to pick for)
if not st.session_state.user_teams:
    user_input = st.text_input("Enter pick numbers you want to control (e.g., 1-32, 11,13,16)", "1-32")
    if st.button("Set My Picks"):
        if '-' in user_input:
            start, end = map(int, user_input.split('-'))
            st.session_state.user_teams = list(range(start, end + 1))
        else:
            st.session_state.user_teams = list(map(int, user_input.split(',')))

if not st.session_state.user_teams:
    st.warning("Please set your picks to begin the draft.")
    st.stop()

st.info(f"You are picking for: {st.session_state.user_teams}")

# Allows for the draft to advance automatically to the users picks
advance_draft()

# Organizes the layout of the streamlit app: draft order + current pick
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Draft Order")
    for i, team in enumerate(draft_order, start=1):
        pick_made = next((p for p in st.session_state.draft_results if p["Pick"] == i), None)
        if pick_made:
            st.write(f"{i}. {team} - {pick_made['Player']} ({pick_made['Position']}) [{pick_made['Grade']}]")
        else:
            st.write(f"{i}. {team}")

with col2:
    if st.session_state.current_pick <= 32:
        pick_num = st.session_state.current_pick
        team = draft_order[pick_num - 1]
        st.subheader(f"🟢 On the Clock: {team}")

        if pick_num in st.session_state.user_teams:
            available = st.session_state.available_players.copy()
            available["Label"] = available.apply(
                lambda x: f"{x['Name']} ({x['Player Position']}, {x['School']}) - Rank {x['Player Rank']}", axis=1
            )
            selected_label = st.selectbox("Select a player to draft", available["Label"].tolist(), key=pick_num)
            if st.button("Draft Player", key=f"draft_{pick_num}"):
                player_row = available[available["Label"] == selected_label].iloc[0]
                st.session_state.draft_results.append({
                    "Pick": pick_num,
                    "Team": team,
                    "Player": player_row["Name"],
                    "Position": player_row["Player Position"],
                    "Rank": player_row["Player Rank"],
                    "Grade": grade_pick(player_row["Player Rank"], team, player_row["Player Position"])
                })
                st.session_state.available_players = available[available["Label"] != selected_label].drop(columns=["Label"]).reset_index(drop=True)
                st.session_state.current_pick += 1
                advance_draft()

#Final results
if st.session_state.current_pick > 32:
    st.success("✅ First round complete!")
    results_df = pd.DataFrame(st.session_state.draft_results)
    st.subheader("📊 First Round Results")
    st.dataframe(results_df)

