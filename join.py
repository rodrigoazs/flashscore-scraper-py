import os

import pandas as pd


def get_place(path):
    place = path.split("-")[0]
    if place == "north":
        if path.split("-")[1] == "central":
            return "north and central america"
        if path.split("-")[1] == "macedonia":
            return "north macedonia"
    if place == "south":
        return "south america"
    if place == "dominican":
        return "dominican republic"
    if place == "trinidad":
        return "trinidad and tobago"
    if place == "costa":
        return "costa rica"
    if place == "el":
        return "el salvador"
    if place == "bosnia":
        return "bosnia and herzegovina"
    if place == "czech":
        return "czech republic"
    if place == "faroe":
        return "faroe islands"
    if place == "northern":
        return "northern ireland"
    if place == "san":
        return "san marino"
    if place == "usa":
        return "united states"
    return place


if __name__ == "__main__":
    folder_path = "data"
    all_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            all_files.append(full_path)

    df = pd.DataFrame(
        {},
        columns=[
            "timestamp",
            "home_team",
            "away_team",
            "home_score",
            "away_score",
            "part",
            "home_part",
            "away_part",
            "neutral",
            "place",
            "season",
            "tournament",
        ],
    )
    for file in all_files:
        print(f"Loading {file}")
        place = get_place(file.split("/")[2])
        season = file.split("/")[3].split(".")[0]
        tournament = file.split("/")[2]
        load_df = pd.read_csv(file)
        load_df["place"] = place
        load_df["season"] = season
        load_df["tournament"] = tournament
        df = pd.concat([df, load_df], ignore_index=True)

    df["away_part"] = df["away_part"].astype("Int64")
    df["home_part"] = df["home_part"].astype("Int64")
    df.to_csv("matches.csv", index=False)
