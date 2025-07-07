import os
import re
import time
from datetime import datetime
from unidecode import unidecode

import pytz
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

leagues = {
    # "data/clubs/uruguay-primera-division": "/uruguay/liga-auf-uruguaya",
    # "data/clubs/uruguay-copa-uruguay": "/uruguay/copa-uruguay",
    # "data/clubs/argentina-primera-division": "/argentina/torneo-betano",
    # "data/clubs/argentina-copa-argentina": "/argentina/copa-argentina",
    # "data/clubs/argentina-copa-de-la-liga": "/argentina/copa-de-la-liga-profesional",
    # "data/clubs/brazil-brasileirao-serie-a": "/brazil/serie-a-betano",
    # "data/clubs/brazil-copa-do-brasil": "/brazil/copa-betano-do-brasil",
    # "data/clubs/chile-primera-division": "/chile/liga-de-primera",
    # "data/clubs/chile-copa-chile": "/chile/copa-chile",
    # "data/clubs/bolivia-primera-division": "/bolivia/division-profesional",
    # "data/clubs/bolivia-copa-pacena": "/bolivia/copa-pacena",
    # "data/clubs/colombia-primera-a": "/colombia/primera-a",
    # "data/clubs/colombia-copa-colombia": "/colombia/copa-colombia",
    # "data/clubs/ecuador-liga-pro": "/ecuador/liga-pro",
    # "data/clubs/ecuador-copa-ecuador": "/ecuador/copa-ecuador",
    # "data/clubs/paraguay-copa-de-primera": "/paraguay/copa-de-primera",
    # "data/clubs/paraguay-copa-paraguay": "/paraguay/copa-paraguay",
    # "data/clubs/peru-liga-1": "/peru/liga-1",
    # "data/clubs/peru-copa-bicentenario": "/peru/copa-bicentenario",
    # "data/clubs/peru-copa-peru": "/peru/copa-peru",
    # "data/clubs/venezuela-liga-futve": "/venezuela/liga-futve",
    # "data/clubs/venezuela-copa-venezuela": "/venezuela/copa-venezuela",
    # "data/clubs/mexico-liga-mx": "/mexico/liga-mx",
    # "data/clubs/mexico-copa-mexico": "/mexico/copa-mexico",
    # "data/clubs/south-america-copa-libertadores": "/south-america/copa-libertadores",
    # "data/clubs/south-america-copa-sudamericana": "/south-america/copa-sudamericana",
    # "data/clubs/north-central-america-concacaf-champions-cup": "/north-central-america/concacaf-champions-cup",
    # "data/clubs/north-central-america-concacaf-caribbean-cup": "/north-central-america/concacaf-caribbean-cup",
    # "data/clubs/north-central-america-concacaf-central-american-cup": "/north-central-america/concacaf-central-american-cup",
    # "data/clubs/north-central-america-concacaf-caribbean-shield": "/north-central-america/concacaf-caribbean-shield",
    # "data/clubs/dominican-republic-ldf": "/dominican-republic/ldf",
    # "data/clubs/dominican-republic-copa-de-la-ldf": "/dominican-republic/copa-de-la-ldf",
    # "data/clubs/haiti-championnat-national": "/haiti/championnat-national",
    # "data/clubs/jamaica-premier-league": "/jamaica/premier-league",
    # "data/clubs/trinidad-and-tobago-tt-premier-league": "/trinidad-and-tobago/tt-premier-league",
    # "data/clubs/costa-rica-primera-division": "/costa-rica/primera-division",
    # "data/clubs/costa-rica-copa-costa-rica": "/costa-rica/copa-costa-rica",
    # "data/clubs/el-salvador-primera-division": "/el-salvador/primera-division",
    # "data/clubs/guatemala-liga-nacional": "/guatemala/liga-nacional",
    # "data/clubs/honduras-liga-nacional": "/honduras/liga-nacional",
    # "data/clubs/panama-lpf": "/panama/lpf",
    # "data/clubs/nicaragua-liga-primera": "/nicaragua/liga-primera",
    # "data/clubs/nicaragua-copa-primera": "/nicaragua/copa-primera",
    # "data/clubs/usa-mls": "/usa/mls",
    # "data/clubs/usa-us-open-cup": "/usa/us-open-cup",
    # "data/clubs/canada-canadian-championship": "/canada/championship",
    # "data/clubs/canada-canadian-premier-league": "/canada/canadian-premier-league",
    # "data/clubs/portugal-liga-portugal": "/portugal/liga-portugal",
    # "data/clubs/portugal-taca-de-portugal": "/portugal/taca-de-portugal",
    # "data/clubs/spain-laliga": "/spain/laliga",
    # "data/clubs/spain-copa-del-rey": "/spain/copa-del-rey",
    # "data/clubs/france-ligue-1": "/france/ligue-1",
    # "data/clubs/france-coupe-de-france": "/france/coupe-de-france",
    # "data/clubs/germany-bundesliga": "/germany/bundesliga",
    # "data/clubs/germany-dfb-pokal": "/germany/dfb-pokal",
    # "data/clubs/italy-serie-a": "/italy/serie-a",
    # "data/clubs/italy-coppa-italia": "/italy/coppa-italia",
    # "data/clubs/england-premier-league": "/england/premier-league",
    # "data/clubs/england-championship": "/england/championship",
    # "data/clubs/netherlands-eredivisie": "/netherlands/eredivisie",
    # "data/clubs/netherlands-knvb-beker": "/netherlands/knvb-beker",
    # "data/clubs/belgium-jupiler-pro-league": "/belgium/jupiler-pro-league",
    # "data/clubs/belgium-belgian-cup": "/belgium/belgian-cup",
    # "data/clubs/scotland-premiership": "/scotland/premiership",
    # "data/clubs/scotland-scottish-cup": "/scotland/scottish-cup",
    # "data/clubs/russia-premier-league": "/russia/premier-league",
    # "data/clubs/russia-russian-cup": "/russia/russian-cup",
    # "data/clubs/ireland-premier-division": "/ireland/premier-division",
    # "data/clubs/ireland-fai-cup": "/ireland/fai-cup",
    # "data/clubs/albania-abissnet-superiore": "/albania/abissnet-superiore",
    # "data/clubs/albania-albanian-cup": "/albania/albanian-cup",
    # "data/clubs/andorra-primera-divisio": "/andorra/primera-divisio",
    # "data/clubs/andorra-andorra-cup": "/andorra/andorra-cup",
    # "data/clubs/armenia-premier-league": "/albania/premier-league",
    # "data/clubs/armenia-armenian-cup": "/armenia/armenian-cup",
    # "data/clubs/austria-bundesliga": "/austria/bundesliga",
    # "data/clubs/austria-ofb-cup": "/austria/ofb-cup",
    # "data/clubs/azerbaijan-premier-league": "/azerbaijan/premier-league",
    # "data/clubs/azerbaijan-azerbaijan-cup": "/azerbaijan/azerbaijan-cup",
    # "data/clubs/belarus-vysshaya-liga": "/belarus/vysshaya-liga",
    # "data/clubs/belarus-belarusian-cup": "/belarus/belarusian-cup",
    # "data/clubs/bosnia-and-herzegovina-abissnet-superiore": "/bosnia-and-herzegovina/wwin-liga-bih",
    # "data/clubs/bosnia-and-herzegovina-bosnia-and-herzegovina-cup": "/bosnia-and-herzegovina/bosnia-and-herzegovina-cup",
    # "data/clubs/bulgaria-parva-liga": "/bulgaria/parva-liga",
    # "data/clubs/bulgaria-bulgarian-cup": "/bulgaria/bulgarian-cup",
    # "data/clubs/croatia-hnl": "/croatia/hnl",
    # "data/clubs/croatia-croatian-cup": "/croatia/croatian-cup",
    # "data/clubs/cyprus-cyprus-league": "/cyprus/cyprus-league",
    # "data/clubs/cyprus-cyprus-cup": "/cyprus/cyprus-cup",
    # "data/clubs/czech-republic-chance-liga": "/czech-republic/chance-liga",
    # "data/clubs/czech-republic-mol-cup": "/czech-republic/mol-cup",
    # "data/clubs/denmark-superliga": "/denmark/superliga",
    # "data/clubs/denmark-landspokal-cup": "/denmark/landspokal-cup",
    # "data/clubs/estonia-meistriliiga": "/estonia/meistriliiga",
    # "data/clubs/estonia-estonian-cup": "/estonia/estonian-cup",
    # "data/clubs/faroe-islands-meistriliiga": "/faroe-islands/premier-league",
    # "data/clubs/faroe-islands-faroe-islands-cup": "/faroe-islands/faroe-islands-cup",
    # "data/clubs/finland-veikkausliiga": "/finland/veikkausliiga",
    # "data/clubs/finland-suomen-cup": "/finland/suomen-cup",
    # "data/clubs/georgia-crystalbet-erovnuli-liga": "/georgia/crystalbet-erovnuli-liga",
    # "data/clubs/georgia-georgian-cup": "/georgia/georgian-cup",
    # "data/clubs/gibraltar-national-league": "/gibraltar/national-league",
    # "data/clubs/gibraltar-gibraltar-cup": "/gibraltar/gibraltar-cup",
    # "data/clubs/greece-super-league": "/greece/super-league",
    # "data/clubs/greece-greek-cup": "/greece/greek-cup",
    # "data/clubs/hungary-nb-i": "/hungary/nb-i",
    # "data/clubs/hungary-hungarian-cup": "/hungary/hungarian-cup",
    # "data/clubs/iceland-besta-deild-karla": "/iceland/besta-deild-karla",
    # "data/clubs/iceland-league-cup": "/iceland/league-cup",
    # "data/clubs/iceland-icelandic-cup": "/iceland/icelandic-cup",
    # "data/clubs/israel-ligat-ha-al": "/israel/ligat-ha-al",
    # "data/clubs/israel-state-cup": "/israel/state-cup",
    # "data/clubs/kazakhstan-premier-league": "/kazakhstan/premier-league",
    # "data/clubs/kazakhstan-kazakhstan-cup": "/kazakhstan/kazakhstan-cup",
    # "data/clubs/kosovo-superliga": "/kosovo/superliga",
    # "data/clubs/kosovo-kosovar-cup": "/kosovo/kosovar-cup",
    # "data/clubs/latvia-virsliga": "/latvia/virsliga",
    # "data/clubs/latvia-latvian-cup": "/latvia/latvian-cup",
    # "data/clubs/liechtenstein-liechtenstein-cup": "/liechtenstein/liechtenstein-cup",
    # "data/clubs/lithuania-a-lyga": "/lithuania/a-lyga",
    # "data/clubs/lithuania-lithuanian-cup": "/lithuania/lithuanian-cup",
    # "data/clubs/luxembourg-bgl-ligue": "/luxembourg/bgl-ligue",
    # "data/clubs/luxembourg-luxembourg-cup": "/luxembourg/luxembourg-cup",
    # "data/clubs/malta-premier-league": "/malta/premier-league",
    # "data/clubs/malta-fa-trophy": "/malta/fa-trophy",
    # "data/clubs/moldova-super-liga": "/moldova/super-liga",
    # "data/clubs/moldova-moldovan-cup": "/moldova/moldovan-cup",
    # "data/clubs/montenegro-prva-crnogorska-liga": "/montenegro/prva-crnogorska-liga",
    # "data/clubs/montenegro-montenegrin-cup": "/montenegro/montenegrin-cup",
    # "data/clubs/north-macedonia-1-mfl": "/north-macedonia/1-mfl",
    # "data/clubs/north-macedonia-macedonian-cup": "/north-macedonia/macedonian-cup",
    # "data/clubs/northern-ireland-nifl-premiership": "/northern-ireland/nifl-premiership",
    # "data/clubs/northern-ireland-irish-cup": "/northern-ireland/irish-cup",
    # "data/clubs/norway-eliteserien": "/norway/eliteserien",
    # "data/clubs/norway-nm-cup": "/norway/nm-cup",
    # "data/clubs/poland-ekstraklasa": "/poland/ekstraklasa",
    # "data/clubs/poland-polish-cup": "/poland/polish-cup",
    # "data/clubs/romania-superliga": "/romania/superliga",
    # "data/clubs/romania-romanian-cup": "/romania/romanian-cup",
    # "data/clubs/san-marino-campionato-sammarinese": "/san-marino/campionato-sammarinese",
    # "data/clubs/san-marino-coppa-titano": "/san-marino/coppa-titano",
    # "data/clubs/serbia-mozzart-bet-super-liga": "/serbia/mozzart-bet-super-liga",
    # "data/clubs/serbia-serbian-cup": "/serbia/serbian-cup",
    # "data/clubs/slovakia-nike-liga": "/slovakia/nike-liga",
    # "data/clubs/slovakia-slovak-cup": "/slovakia/slovak-cup",
    # "data/clubs/slovenia-prva-liga": "/slovenia/prva-liga",
    # "data/clubs/slovenia-slovenian-cup": "/slovenia/slovenian-cup",
    # "data/clubs/sweden-allsvenskan": "/sweden/allsvenskan",
    # "data/clubs/sweden-svenska-cupen": "/sweden/svenska-cupen",
    # "data/clubs/switzerland-super-league": "/switzerland/super-league",
    # "data/clubs/switzerland-swiss-cup": "/switzerland/swiss-cup",
    # "data/clubs/turkey-super-lig": "/turkey/super-lig",
    # "data/clubs/turkey-turkish-cup": "/turkey/turkish-cup",
    # "data/clubs/ukraine-premier-league": "/ukraine/premier-league",
    # "data/clubs/ukraine-ukrainian-cup": "/ukraine/ukrainian-cup",
    # "data/clubs/wales-cymru-premier": "/wales/cymru-premier",
    # "data/clubs/wales-fa-cup": "/wales/fa-cup",
    # "data/clubs/algeria/ligue-1": "/algeria/ligue-1",
    # "data/clubs/algeria-algeria-cup": "/algeria/algeria-cup",
    # "data/clubs/egypt-premier-league": "/egypt/premier-league",
    # "data/clubs/egypt-egypt-cup": "/egypt/egypt-cup",
    # "data/clubs/libya-premier-league": "/libya/premier-league",
    # "data/clubs/morocco-botola-pro": "/morocco/botola-pro",
    # "data/clubs/morocco-coupe-du-trone": "/morocco/coupe-du-trone",
    # "data/clubs/tunisia-ligue-professionnelle-1": "/tunisia/ligue-professionnelle-1",
    # "data/clubs/tunisia-tunisia-cup": "/tunisia/tunisia-cup",
    # "data/clubs/benin-ligue-1": "/benin/ligue-1",
    # "data/clubs/burkina-faso-premier-league": "/burkina-faso/premier-league",
    # "data/clubs/cape-verde-campeonato-nacional": "/cape-verde/campeonato-nacional",
    # "data/clubs/gambia-gfa-league/": "/gambia/gfa-league/",
    # "data/clubs/gambia-ff-cup": "/gambia/ff-cup",
    # "data/clubs/ghana-premier-league": "/ghana/premier-league",
    # "data/clubs/ghana-ghanaian-cup": "/ghana/ghanaian-cup",
    # "data/clubs/guinea-ligue-1": "/guinea/ligue-1",
    # "data/clubs/ivory-coast/ligue-1": "/ivory-coast/ligue-1",
    # "data/clubs/liberia-lfa-first-division": "/liberia/lfa-first-division",
    # "data/clubs/liberia-orange-cup": "/liberia/orange-cup",
    # "data/clubs/mali-premiere-division": "/mali/premiere-division",
    # "data/clubs/mauritania-ligue-1": "/mauritania/ligue-1",
    # "data/clubs/niger-super-ligue": "/niger/super-ligue",
    # "data/clubs/nigeria-npfl": "/nigeria/npfl",
    # "data/clubs/nigeria-federation-cup": "/nigeria/federation-cup",
    # "data/clubs/senegal-ligue-1": "/senegal/ligue-1",
    # "data/clubs/sierra-leone-premier-league": "/sierra-leone/premier-league",
    # "data/clubs/togo-championnat-national": "/togo/championnat-national",
    # "data/clubs/cameroon-elite-one": "/cameroon/elite-one",
    # "data/clubs/chad-premiere-division": "/chad/premiere-division",
    # "data/clubs/dr-congo-ligue-1": "/dr-congo/ligue-1",
    # "data/clubs/gabon-championnat-d1": "/gabon/championnat-d1",
    # "data/clubs/sao-tome-and-principe-campeonato-nacional": "/sao-tome-and-principe/campeonato-nacional",
    # "data/clubs/burundi-primus-league": "/burundi/primus-league",
    # "data/clubs/burundi-coupe-du-president": "/burundi/coupe-du-president",
    # "data/clubs/djibouti-division-1": "/djibouti/division-1",
    # "data/clubs/ethiopia-premier-league": "/ethiopia/premier-league",
    # "data/clubs/kenya-premier-league": "/kenya/premier-league",
    # "data/clubs/rwanda-premier-league": "/rwanda/premier-league",
    # "data/clubs/rwanda-peace-cup": "/rwanda/peace-cup",
    # "data/clubs/somalia-national-league": "/somalia/national-league",
    # "data/clubs/sudan-premier-league": "/sudan/premier-league",
    # "data/clubs/tanzania-ligi-kuu-bara": "/tanzania/ligi-kuu-bara",
    # "data/clubs/tanzania-federation-cup": "/tanzania/federation-cup",
    # "data/clubs/uganda-premier-league": "/uganda/premier-league",
    # "data/clubs/uganda-uganda-cup": "/uganda/uganda-cup",
    # "data/clubs/angola-girabola": "/angola/girabola",
    # "data/clubs/botswana-premier-league": "/botswana/premier-league",
    # "data/clubs/eswatini-swazi-mtn-premier-league": "/eswatini/swazi-mtn-premier-league",
    # "data/clubs/eswatini-ingwenyama-cup": "/eswatini/ingwenyama-cup",
    # "data/clubs/lesotho-premier-league": "/lesotho/premier-league",
    # "data/clubs/malawi-super-league": "/malawi/super-league",
    # "data/clubs/malawi-castel-challenge-cup": "/malawi/castel-challenge-cup",
    # "data/clubs/mauritius-super-league": "/mauritius/super-league",
    # "data/clubs/mozambique-mocambola": "/mozambique/mocambola",
    # "data/clubs/namibia-premiership": "/namibia/premiership",
    # "data/clubs/namibia-maris-cup/": "/namibia/maris-cup",
    # "data/clubs/seychelles-premier-league": "/seychelles/premier-league",
    # "data/clubs/south-africa-betway-premiership": "/south-africa/betway-premiership",
    # "data/clubs/south-africa-nedbank-cup": "/south-africa/nedbank-cup",
    # "data/clubs/zambia-super-league": "/zambia/super-league",
    # "data/clubs/zambia-absa-cup": "/zambia/absa-cup",
    # "data/clubs/zimbabwe-premier-soccer-league": "/zimbabwe/premier-soccer-league",
    # "data/clubs/zimbabwe-castle-challenge-cup": "/zimbabwe/castle-challenge-cup",
    # "data/clubs/reunion-regionale-1": "/reunion/regionale-1",
    # "data/clubs/fiji-premier-league": "/fiji/premier-league",
    # "data/clubs/new-zealand-national-league": "/new-zealand/national-league",
    # "data/clubs/new-zealand-chatham-cup": "/new-zealand/chatham-cup",
    # "data/clubs/australia-a-league": "/australia/a-league",
    # "data/clubs/australia-australia-cup": "/australia/australia-cup",
    # "data/clubs/cambodia-cpl": "/cambodia/cpl",
    # "data/clubs/cambodia-hun-sen-cup": "/cambodia/hun-sen-cup",
    # "data/clubs/indonesia-liga-1": "/indonesia/liga-1",
    # "data/clubs/indonesia-president-cup": "/indonesia/president-cup",
    # "data/clubs/laos-lao-league": "/laos/lao-league",
    # "data/clubs/malaysia-super-league": "/malaysia/super-league",
    # "data/clubs/malaysia-malaysia-cup": "/malaysia/malaysia-cup",
    # "data/clubs/malaysia-fa-cup": "/malaysia/fa-cup",
    # "data/clubs/myanmar-national-league": "/myanmar/national-league",
    # "data/clubs/myanmar-mnl-league-cup": "/myanmar/mnl-league-cup",
    # "data/clubs/philippines-pfl": "/philippines/pfl",
    # "data/clubs/philippines-copa-paulino-alcantara": "/philippines/copa-paulino-alcantara",
    # "data/clubs/singapore-premier-league": "/singapore/premier-league",
    # "data/clubs/singapore-singapore-cup": "/singapore/singapore-cup",
    # "data/clubs/thailand-thai-league-1": "/thailand/thai-league-1",
    # "data/clubs/thailand-thai-fa-cup": "/thailand/thai-fa-cup",
    # "data/clubs/vietnam-v-league-1": "/vietnam/v-league-1",
    # "data/clubs/vietnam-vietnamese-cup": "/vietnam/vietnamese-cup",
    # "data/clubs/iran-persian-gulf-pro-league": "/iran/persian-gulf-pro-league",
    # "data/clubs/iran-hazfi-cup": "/iran/hazfi-cup",
    # "data/clubs/kyrgyzstan-premier-liga": "/kyrgyzstan/premier-liga",
    # "data/clubs/tajikistan-vysshaya-liga": "/tajikistan/vysshaya-liga",
    # "data/clubs/tajikistan-tajikistan-cup": "/tajikistan/tajikistan-cup",
    # "data/clubs/turkmenistan-yokary-liga": "/turkmenistan/yokary-liga",
    # "data/clubs/uzbekistan-super-league": "/uzbekistan/super-league",
    # "data/clubs/uzbekistan-uzbekistan-cup": "/uzbekistan/uzbekistan-cup",
    # "data/clubs/china-super-league": "/china/super-league",
    # "data/clubs/china-fa-cup": "/china/fa-cup",
    # "data/clubs/hong-kong-premier-league": "/hong-kong/premier-league",
    # "data/clubs/hong-kong-fa-cup": "/hong-kong/fa-cup",
    # "data/clubs/japan-j1-league": "/japan/j1-league",
    # "data/clubs/japan-ybc-levain-cup": "/japan/ybc-levain-cup",
    # "data/clubs/japan-emperors-cup": "/japan/emperors-cup",
    # "data/clubs/south-korea-k-league-1": "/south-korea/k-league-1",
    # "data/clubs/south-korea-korean-cup": "/south-korea/korean-cup",
    # "data/clubs/mongolia-premier-league": "/mongolia/premier-league",
    # "data/clubs/bangladesh-premier-league": "/bangladesh/premier-league",
    # "data/clubs/bangladesh-federation-cup": "/bangladesh/federation-cup",
    "data/clubs/bhutan-premier-league": "/bhutan/premier-league",
    "data/clubs/india-isl": "/india/isl",
    "data/clubs/india-durand-cup": "/india/durand-cup",
    "data/clubs/maldives-dhivehi-premier-league": "/maldives/dhivehi-premier-league",
    "data/clubs/pakistan-premier-league": "/pakistan/premier-league",
    "data/clubs/sri-lanka-super-league": "/sri-lanka/super-league",
    "data/clubs/bahrain-premier-league": "/bahrain/premier-league",
    "data/clubs/bahrain-king-s-cup": "/bahrain/king-s-cup",
    "data/clubs/bahrain-bahrain-cup": "/bahrain/bahrain-cup",
    "data/clubs/iraq-stars-league": "/iraq/stars-league",
    "data/clubs/iraq-iraq-cup": "/iraq/iraq-cup",
    "data/clubs/jordan-premier-league": "/jordan/premier-league",
    "data/clubs/jordan-jordan-cup": "/jordan/jordan-cup",
    "data/clubs/kuwait-premier-league": "/kuwait/premier-league",
    "data/clubs/kuwait-crown-prince-cup": "/kuwait/crown-prince-cup",
    "data/clubs/kuwait-emir-cup": "/kuwait/emir-cup",
    "data/clubs/lebanon-premier-league": "/lebanon/premier-league",
    "data/clubs/lebanon-lebanese-cup": "/lebanon/lebanese-cup",
    "data/clubs/oman-professional-league": "/oman/professional-league",
    "data/clubs/oman-sultan-cup": "/oman/sultan-cup",
    "data/clubs/palestine-west-bank-league": "/palestine/west-bank-league",
    "data/clubs/qatar-qsl": "/qatar/qsl",
    "data/clubs/qatar-qfa-cup": "/qatar/qfa-cup",
    "data/clubs/saudi-arabia-saudi-professional-league": "/saudi-arabia/saudi-professional-league",
    "data/clubs/saudi-arabia-king-cup": "/saudi-arabia/king-cup",
    "data/clubs/syria-premier-league": "/syria/premier-league",
    "data/clubs/syria-syria-cup": "/syria/syria-cup",
    "data/clubs/united-arab-emirates-uae-league": "/united-arab-emirates/uae-league",
    "data/clubs/united-arab-emirates-league-cup": "/united-arab-emirates/league-cup",
    "data/clubs/united-arab-emirates-presidents-cup": "/united-arab-emirates/presidents-cup",
    "data/clubs/yemen-division-1": "/yemen/division-1",
    # "data/clubs/oceania-ofc-champions-league": "/australia-oceania/ofc-champions-league",
    # "data/clubs/asia-afc-champions-league": "/asia/afc-champions-league",
    # "data/clubs/africa-caf-champions-league": "/africa/caf-champions-league",
    # "data/clubs/africa-caf-confederation-cup": "/africa/caf-confederation-cup",
    # "data/clubs/europe-champions-league": "/europe/champions-league",
    # "data/clubs/europe-europa-league": "/europe/europa-league",
    # "data/clubs/europe-conference-league": "/europe/conference-league",
    # "data/clubs/world-club-friendly": "/world/club-friendly",
    # "data/clubs/world-fifa-intercontinental-cup": "/world/fifa-intercontinental-cup",
    # "data/clubs/world-fifa-club-world-cup": "/world/fifa-club-world-cup",
    # "data/national/world-world-championship": "/world/world-championship",
    # "data/national/world-friendly-international": "/world/friendly-international",
    # "data/national/world-fifa-confederations-cup": "/world/fifa-confederations-cup",
    # "data/national/south-america-copa-america": "/south-america/copa-america",
    # "data/national/europe-euro": "/europe/euro",
    # "data/national/europe-uefa-nations-league": "/europe/uefa-nations-league",
    # "data/national/north-central-america-concacaf-gold-cup": "/north-central-america/gold-cup",
    # "data/national/north-central-america-concacaf-nations-league": "/north-central-america/concacaf-nations-league",
    # "data/national/africa-african-nations-championship": "/africa/african-nations-championship",
    # "data/national/africa-africa-cup-of-nations": "/africa/africa-cup-of-nations",
    # "data/national/asia-asian-cup": "/asia/asian-cup",
    # "data/national/asia-saff-championship": "/asia/saff-championship",
    # "data/national/asia-asean-championship": "/asia/asean-championship",
    # "data/national/oceania-ofc-nations-cup": "/australia-oceania/ofc-nations-cup",
}

TIMEZONE = "Europe/Madrid"
MAIN_URL = "https://www.flashscore.com"


def download_logo(src, team_name):
    if not src or not team_name:
        return
    folder = "logos"
    os.makedirs(folder, exist_ok=True)
    team_name = re.sub(r"\(\w{3}\)", "", team_name).strip()
    team_name = (
        team_name.replace("'", "")
        .replace("&", "")
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .lower()
    )
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
        if date == "29.02":
            date = "28.02"
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
        if date == "29.02":
            date = "28.02"
        full_date_str = f"{date}.{year}"
        date_format = "%d.%m.%Y"
        utc_dt = datetime.strptime(full_date_str, date_format)
        return int(utc_dt.timestamp())


def get_month(date_str):
    match = re.search(r"\d{2}\.(\d{2})\.", date_str)
    if match:
        month = match.group(1)
        return int(month)
    return None


def get_info(date_str):
    match = re.search(r"([a-zA-Z]+)", date_str)
    if match:
        return match.group(1)
    return ""


def get_year(date_str):
    match = re.search(r"(\d{4})\-(\d{4})", date_str)
    if match:
        return [int(match.group(1)), int(match.group(2))]
    match = re.search(r"(\d{4})", date_str)
    if match:
        return int(match.group(1))


def get_neutral(_id, driver):
    div_id = driver.find_element(By.ID, _id)
    time.sleep(1)
    info_icon = div_id.find_element(
        By.CSS_SELECTOR, '[data-testid="wcl-icon-settings-info-rounded"]'
    )
    # Scroll the info icon into view
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", info_icon)
    time.sleep(0.5)  # Give browser a moment to settle after scroll
    ActionChains(driver).move_to_element(info_icon).perform()
    popup = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".tooltip"))
    )
    if "Neutral location" in popup.text:
        return "1"
    return "0"


def get_url_and_season(html_content):
    link = html_content.find("a", class_=["archive__text"])
    pattern = r"(\d{4}\/\d{4}|\d{4}-\d{4}|\d{4})"
    matches = re.findall(pattern, link.get_text(strip=True))
    season = matches[0].replace("/", "-")
    url = link["href"]
    return (season, url)


def get_archive_urls(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    matches = soup.find_all("div", class_=["archive__row"])
    urls = []
    for index, match in enumerate(matches):
        if index == 0:
            winner = match.find("div", class_=["archive__winner"])
            if not winner:
                continue
            text = winner.get_text(strip=True)
            if text and "No winner" not in text:
                urls.append(get_url_and_season(match))
        else:
            urls.append(get_url_and_season(match))
    return urls


def extract_results_from_html(html_content, year, driver):
    soup = BeautifulSoup(html_content, "html.parser")
    results = [
        "timestamp,home_team,away_team,home_score,away_score,part,home_part,away_part,neutral"
    ]
    matches = soup.find_all("div", class_=["event__match"])
    last_month = None
    current_year = year if isinstance(year, int) else year[0]
    for match in matches[::-1]:
        neutral = "0"
        _id = match.get("id")
        date = match.find("div", class_=["event__time"]).get_text(strip=True)
        info = get_info(date)
        if isinstance(year, list):
            month = get_month(date)
            if last_month and month < last_month:
                current_year = year[1]
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
        icon_match = match.find(attrs={"data-testid": "wcl-icon-settings-info-rounded"})
        if icon_match:
            neutral = get_neutral(_id, driver)
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
                    neutral,
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
        return get_archive_urls(source)

    except TimeoutException:
        print("Not able to parse.")
    except Exception as e:
        print(str(e))
    finally:
        driver.quit()


def extract_results(url, filename, year_str):
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
        year = get_year(year_str)
        div_element = driver.find_element(By.ID, "live-table")
        results = extract_results_from_html(
            # div_element.get_attribute("innerHTML"), year, driver
            unidecode(div_element.get_attribute("innerHTML")), year, driver
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
        for year_str, url in archive[::-1]:
            filename = os.path.join(folder, f"{year_str}.csv")
            if not os.path.exists(filename):
                print(f"Extracting results for {url} for season {year_str}...")
                url = f"{MAIN_URL}{url}results/"
                extract_results(url, filename, year_str)
                time.sleep(5)
