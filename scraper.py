import os
import re
import time
from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

leagues = {
    # "data/clubs/uruguay-primera-division": "/uruguay/liga-auf-uruguaya",
    # "data/clubs/argentina-primera-division": "/argentina/torneo-betano",
    # "data/clubs/argentina-copa-argentina": "/argentina/copa-argentina",
    "data/clubs/argentina-copa-de-la-liga": "/argentina/copa-de-la-liga-profesional",
    # "data/clubs/brazil-brasileirao-serie-a": "/brazil/serie-a-betano",
    # "data/clubs/brazil-copa-do-brasil": "/brazil/copa-betano-do-brasil",
    # "data/clubs/chile-primera-division": "/chile/liga-de-primera",
    # "data/clubs/chile-copa-chile": "/chile/copa-chile",
    # "data/clubs/bolivia-primera-division": "/bolivia/division-profesional",
    # "data/clubs/colombia-primera-a": "/colombia/primera-a",
    # "data/clubs/colombia-copa-colombia": "/colombia/copa-colombia",
    # "data/clubs/ecuador-liga-pro": "/ecuador/liga-pro",
    # "data/clubs/paraguay-copa-de-primera": "/paraguay/copa-de-primera",
    # "data/clubs/peru-liga-1": "/peru/liga-1",
    # "data/clubs/venezuela-liga-futve": "/venezuela/liga-futve",
    # "data/clubs/mexico-liga-mx": "/mexico/liga-mx",
    # "data/clubs/south-america-copa-libertadores": "/south-america/copa-libertadores",
    # "data/clubs/south-america-copa-sudamericana": "/south-america/copa-sudamericana",
    # "data/clubs/north-central-america-concacaf-champions-cup": "/north-central-america/concacaf-champions-cup",
    # "data/clubs/north-central-america-concacaf-caribbean-cup": "/north-central-america/concacaf-caribbean-cup",
    # "data/clubs/north-central-america-concacaf-central-american-cup": "/north-central-america/concacaf-central-american-cup",
    # "data/clubs/north-central-america-concacaf-caribbean-shield": "/north-central-america/concacaf-caribbean-shield",
    # "data/clubs/dominican-republic/ldf": "/dominican-republic/ldf",
    # "data/clubs/haiti/championnat-national": "/haiti/championnat-national",
    # "data/clubs/jamaica/premier-league": "/jamaica/premier-league",
    # "data/clubs/trinidad-and-tobago/tt-premier-league": "/trinidad-and-tobago/tt-premier-league",
    # "data/clubs/costa-rica/primera-division": "/costa-rica/primera-division",
    # "data/clubs/el-salvador/primera-division": "/el-salvador/primera-division",
    # "data/clubs/guatemala/liga-nacional": "/guatemala/liga-nacional",
    # "data/clubs/honduras/liga-nacional": "/honduras/liga-nacional",
    # "data/clubs/panama/lpf": "/panama/lpf",
    # "data/clubs/nicaragua/liga-primera": "/nicaragua/liga-primera",
    # "data/clubs/usa-mls": "/usa/mls",
    # "data/clubs/usa-us-open-cup": "/usa/us-open-cup",
    # "data/clubs/canada-canadian-championship": "/canada/championship",
    # "data/clubs/canada-canadian-premier-league": "/canada/canadian-premier-league",
}

TIMEZONE = "Europe/Madrid"
MAIN_URL = "https://www.flashscore.com"


def download_logo(src, team_name):
    if not src or not team_name:
        return
    folder = "logos"
    os.makedirs(folder, exist_ok=True)
    team_name = re.sub(r"\(\w{3}\)", "", team_name).strip()
    team_name = team_name.replace(" ", "_").lower()
    filename = os.path.join(folder, f"{team_name}.png")
    if not os.path.exists(filename):
        response = requests.get(src, verify=False)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)


def get_timestamp(date_str, year):
    match = re.search(r"(\d{2}\.\d{2})\.\s+(\d{2}:\d{2})", date_str)
    if match:
        date = match.group(1)
        time = match.group(2)
        full_date_str = f"{date}.{year} {time}"
        date_format = "%d.%m.%Y %H:%M"
        naive_dt = datetime.strptime(full_date_str, date_format)
        tz = pytz.timezone(TIMEZONE)
        utc_tz = pytz.utc
        dt = tz.localize(naive_dt)
        utc_dt = dt.astimezone(utc_tz)
        return int(utc_dt.timestamp())
    match = re.search(r"(\d{2}\.\d{2})\.", date_str)
    if match:
        date = match.group(1)
        full_date_str = f"{date}.{year}"
        date_format = "%d.%m.%Y"
        utc_dt = datetime.strptime(full_date_str, date_format)
        return int(utc_dt.timestamp())


def get_month(date_str):
    match = re.search(r"\d{2}\.(\d{2})\.", date_str)
    if match:
        month = match.group(0)
        return int(month)
    return None


def get_info(date_str):
    match = re.search(r"([a-zA-Z]+)", date_str)
    if match:
        return match.group(1)
    return ""


def get_year(date_str):
    match = re.search(r"\-(\d{4})\-(\d{4})\/", date_str)
    if match:
        return [int(match.group(1)), int(match.group(2))]
    match = re.search(r"\-(\d{4})\/", date_str)
    if match:
        return int(match.group(1))


def extract_results_from_html(html_content, year):
    soup = BeautifulSoup(html_content, "html.parser")
    results = [
        "timestamp,home_team,away_team,home_score,away_score,info,home_part,away_part"
    ]
    matches = soup.find_all("div", class_=["event__match"])
    last_month = None
    current_year = year if isinstance(year, int) else year[0]
    for match in matches[::-1]:
        date = match.find("div", class_=["event__time"]).get_text(strip=True)
        info = get_info(date)
        if isinstance(year, list):
            month = get_month(date)
            if last_month and month < last_month:
                current_year = year[1]
            else:
                last_month = month
        timestamp = get_timestamp(date, current_year)
        home = match.find("div", class_=["event__homeParticipant"])
        away = match.find("div", class_=["event__awayParticipant"])
        home_score = match.find("span", class_=["event__score--home"]).get_text(
            strip=True
        )
        away_score = match.find("span", class_=["event__score--away"]).get_text(
            strip=True
        )
        home_part = match.find("div", class_=["event__part--home"])
        away_part = match.find("div", class_=["event__part--away"])
        if home_part and away_part:
            home_temp = home_score
            away_temp = away_score
            home_score = home_part.get_text(strip=True)
            away_score = away_part.get_text(strip=True)
            home_part = home_temp
            away_part = away_temp
        else:
            home_part = ""
            away_part = ""
        home_team = (home.find("span") or home.find("strong")).get_text(strip=True)
        away_team = (away.find("span") or away.find("strong")).get_text(strip=True)
        home_img = home.find("img")
        away_img = away.find("img")
        home_logo = home_img["src"] if home_img and home_img.has_attr("src") else None
        away_logo = away_img["src"] if away_img and away_img.has_attr("src") else None
        download_logo(home_logo, home_team)
        download_logo(away_logo, away_team)
        results.append(
            ",".join(
                [
                    str(timestamp),
                    home_team,
                    away_team,
                    home_score,
                    away_score,
                    info,
                    home_part,
                    away_part,
                ]
            )
        )
    return results


def get_archive(url):
    try:
        print("Setting options...")
        # Set up the Chrome browser
        options = Options()
        ua = UserAgent()
        user_agent = ua.random

        options.add_argument(f"user-agent={user_agent}")
        # options.add_argument("--headless")
        options.add_argument("--start-maximized")

        # adding argument to disable the AutomationControlled flag
        options.add_argument("--disable-blink-features=AutomationControlled")

        # exclude the collection of enable-automation switches
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # turn-off userAutomationExtension
        options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(options=options)

        # changing the property of the navigator value for webdriver to undefined
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        print("Opening Flashscore ...")
        # Open the page
        driver.get(f"{MAIN_URL}/football{url}/archive/")
        time.sleep(2)

        source = driver.page_source
        pattern = rf"(\/football{url}\-.*\/)\""
        matches = re.findall(pattern, source)
        return matches

    except TimeoutException:
        print("Not able to parse.")
    except Exception as e:
        print(str(e))
    finally:
        driver.quit()


def extract_results(url, filename):
    try:
        print("Setting options...")
        # Set up the Chrome browser
        options = Options()
        ua = UserAgent()
        user_agent = ua.random

        options.add_argument(f"user-agent={user_agent}")
        # options.add_argument("--headless")
        options.add_argument("--start-maximized")

        # adding argument to disable the AutomationControlled flag
        options.add_argument("--disable-blink-features=AutomationControlled")

        # exclude the collection of enable-automation switches
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        # turn-off userAutomationExtension
        options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(options=options)

        # changing the property of the navigator value for webdriver to undefined
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        print("Opening Flashscore ...")
        # Open the page
        driver.get(url)

        time.sleep(2)

        reject_button = driver.find_element(By.XPATH, "//button[text()='Reject All']")
        reject_button.click()

        time.sleep(5)

        while True:
            show_more_link = driver.find_element(By.LINK_TEXT, "Show more matches")
            show_more_link.click()
            # element = driver.find_element(By.XPATH, "//a[contains(text(),'Show more matches')]")
            # driver.execute_script("arguments[0].click();", element)
            time.sleep(5)

        time.sleep(2)

    except NoSuchElementException:
        time.sleep(5)
        year = get_year(url)
        div_element = driver.find_element(By.ID, "live-table")
        results = extract_results_from_html(
            div_element.get_attribute("innerHTML"), year
        )
        with open(filename, "w") as f:
            f.write("\n".join(results))
    except TimeoutException:
        print("Not able to parse.")
    except Exception as e:
        print(str(e))
    finally:
        driver.quit()


if __name__ == "__main__":
    for folder, league_url in leagues.items():
        archive = get_archive(league_url)
        os.makedirs(folder, exist_ok=True)
        for url in archive:
            pattern = r"-(\d{4}-\d{4}|\d{4})\/"
            matches = re.findall(pattern, url)
            if not matches:
                continue
            year_str = matches[0]
            filename = os.path.join(folder, f"{year_str}.csv")
            if not os.path.exists(filename):
                print(f"Extracting results for {url}...")
                url = f"{MAIN_URL}{url}results/"
                extract_results(url, filename)
                time.sleep(5)
