import os
import time

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def download_logo(src, team_name):
    if not src or not team_name:
        return
    folder = "logos"
    os.makedirs(folder, exist_ok=True)
    team_name = team_name.replace(" ", "_").lower()
    filename = os.path.join(folder, f"{team_name}.png")
    if not os.path.exists(filename):
        response = requests.get(src, verify=False)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)


def extract_results_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    results = ["date,home_team,away_team,home_score,away_score"]
    matches = soup.find_all("div", class_=["event__match"])
    for match in matches:
        date = match.find("div", class_=["event__time"]).get_text(strip=True)
        home = match.find("div", class_=["event__homeParticipant"])
        away = match.find("div", class_=["event__awayParticipant"])
        home_score = match.find("span", class_=["event__score--home"]).get_text(
            strip=True
        )
        away_score = match.find("span", class_=["event__score--away"]).get_text(
            strip=True
        )
        home_team = (home.find("span") or home.find("strong")).get_text(strip=True)
        away_team = (away.find("span") or away.find("strong")).get_text(strip=True)
        home_img = home.find("img")
        away_img = away.find("img")
        home_logo = home_img["src"] if home_img and home_img.has_attr("src") else None
        away_logo = away_img["src"] if away_img and away_img.has_attr("src") else None
        download_logo(home_logo, home_team)
        download_logo(away_logo, away_team)
        results.append(",".join([date, home_team, away_team, home_score, away_score]))
    return results


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
        div_element = driver.find_element(By.ID, "live-table")
        results = extract_results_from_html(div_element.get_attribute("innerHTML"))
        with open(filename, "w") as f:
            f.write("\n".join(results))
    except TimeoutException:
        print("Not able to parse.")
    except Exception as e:
        print(str(e))
    finally:
        driver.quit()


if __name__ == "__main__":
    folder = "data/clubs/uruguay-primera-division"
    os.makedirs(folder, exist_ok=True)
    for year in range(2006, 2016):
        filename = os.path.join(folder, f"{year}-{year+1}.csv")
        if not os.path.exists(filename):
            url = (
                f"https://www.flashscore.com/football/uruguay/liga-auf-uruguaya-{year}-{year+1}/results/"
            )
            
            print(f"Extracting results for {year}-{year+1}...")
            extract_results(url, filename)
            time.sleep(5)
