from dotenv import load_dotenv
load_dotenv()
import os
import re
import json

from groq import Groq


# ============================================================
# GROQ
# ============================================================

API_KEY = os.environ.get("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY is not configured.")

client = Groq(api_key=API_KEY)

GROQ_MODEL = "openai/gpt-oss-20b"


# ============================================================
# CATEGORIES
# ============================================================

ALLOWED_CATEGORIES = {
    "BREAKING",
    "TRANSFER",
    "MATCH",
    "QUOTE",
    "GENERAL",
    "TROPHY",
    "INJURY",
    "PLAYER",
    "LINEUP",
    "ANNOUNCEMENT"
}


# ============================================================
# NON-FOOTBALL SPORTS
# ============================================================

NON_FOOTBALL_SPORTS = {
    "tennis",
    "cricket",
    "golf",
    "rugby",
    "basketball",
    "baseball",
    "nfl",
    "american football",
    "formula 1",
    "formula one",
    "f1",
    "motorsport",
    "motogp",
    "boxing",
    "mma",
    "ufc",
    "cycling",
    "athletics",
    "horse racing",
    "horse-racing",
    "horse race",
    "racing",
    "snooker",
    "darts",
    "swimming",
    "volleyball",
    "handball",
    "hockey",
    "ice hockey",
    "fencing",
    "wrestling",
    "badminton",
    "table tennis",
    "water polo",
    "skiing",
    "ski",
    "surfing",
    "rowing",
    "gymnastics",
    "marathon",
    "nascar",
    "indycar"
}


# ============================================================
# MAJOR CLUBS
# ============================================================

MAJOR_CLUBS = {

    "Real Madrid": {
        "priority": 100,
        "keywords": [
            "real madrid",
            "real madrid cf",
            "los blancos",
            "madrid"
        ]
    },

    "Barcelona": {
        "priority": 100,
        "keywords": [
            "barcelona",
            "fc barcelona",
            "barça",
            "barca",
            "blaugrana"
        ]
    },

    "Manchester United": {
        "priority": 95,
        "keywords": [
            "manchester united",
            "man united",
            "man utd"
        ]
    },

    "Manchester City": {
        "priority": 95,
        "keywords": [
            "manchester city",
            "man city"
        ]
    },

    "Liverpool": {
        "priority": 95,
        "keywords": [
            "liverpool",
            "liverpool fc"
        ]
    },

    "Arsenal": {
        "priority": 95,
        "keywords": [
            "arsenal",
            "arsenal fc"
        ]
    },

    "Chelsea": {
        "priority": 95,
        "keywords": [
            "chelsea",
            "chelsea fc"
        ]
    },

    "Bayern Munich": {
        "priority": 95,
        "keywords": [
            "bayern munich",
            "bayern",
            "fc bayern"
        ]
    },

    "Paris Saint-Germain": {
        "priority": 95,
        "keywords": [
            "psg",
            "paris saint-germain",
            "paris saint germain"
        ]
    },

    "Juventus": {
        "priority": 90,
        "keywords": [
            "juventus",
            "juventus fc"
        ]
    },

    "Inter Milan": {
        "priority": 90,
        "keywords": [
            "inter milan",
            "internazionale",
            "inter"
        ]
    },

    "AC Milan": {
        "priority": 90,
        "keywords": [
            "ac milan",
            "milan"
        ]
    },

    "Atlético Madrid": {
        "priority": 90,
        "keywords": [
            "atletico madrid",
            "atlético madrid",
            "atletico de madrid"
        ]
    },

    "Borussia Dortmund": {
        "priority": 88,
        "keywords": [
            "borussia dortmund",
            "dortmund"
        ]
    },

    "Bayer Leverkusen": {
        "priority": 88,
        "keywords": [
            "bayer leverkusen",
            "leverkusen"
        ]
    },

    "Tottenham": {
        "priority": 85,
        "keywords": [
            "tottenham",
            "tottenham hotspur",
            "spurs"
        ]
    },

    "Newcastle United": {
        "priority": 82,
        "keywords": [
            "newcastle united",
            "newcastle"
        ]
    },

    "Napoli": {
        "priority": 82,
        "keywords": [
            "napoli"
        ]
    },

    "Roma": {
        "priority": 80,
        "keywords": [
            "roma",
            "as roma"
        ]
    },

    "Lazio": {
        "priority": 80,
        "keywords": [
            "lazio"
        ]
    },

    "Ajax": {
        "priority": 78,
        "keywords": [
            "ajax",
            "ajax amsterdam"
        ]
    },

    "Benfica": {
        "priority": 78,
        "keywords": [
            "benfica"
        ]
    },

    "Porto": {
        "priority": 78,
        "keywords": [
            "porto",
            "fc porto"
        ]
    },

    "Sporting CP": {
        "priority": 78,
        "keywords": [
            "sporting cp",
            "sporting lisbon"
        ]
    },

    "Marseille": {
        "priority": 75,
        "keywords": [
            "marseille",
            "olympique de marseille"
        ]
    },

    "Monaco": {
        "priority": 75,
        "keywords": [
            "monaco",
            "as monaco"
        ]
    },

    "Sevilla": {
        "priority": 75,
        "keywords": [
            "sevilla",
            "sevilla fc"
        ]
    },

    "Valencia": {
        "priority": 72,
        "keywords": [
            "valencia",
            "valencia cf"
        ]
    },

    "Villarreal": {
        "priority": 72,
        "keywords": [
            "villarreal"
        ]
    }
}


# ============================================================
# MAJOR NATIONAL TEAMS
# ============================================================

MAJOR_NATIONAL_TEAMS = {

    "Spain": {
        "priority": 95,
        "keywords": [
            "spain",
            "spanish national team",
            "la roja"
        ]
    },

    "Argentina": {
        "priority": 95,
        "keywords": [
            "argentina",
            "argentina national team"
        ]
    },

    "Brazil": {
        "priority": 95,
        "keywords": [
            "brazil",
            "brazil national team"
        ]
    },

    "France": {
        "priority": 95,
        "keywords": [
            "france",
            "france national team",
            "french national team"
        ]
    },

    "England": {
        "priority": 95,
        "keywords": [
            "england",
            "england national team"
        ]
    },

    "Germany": {
        "priority": 95,
        "keywords": [
            "germany",
            "germany national team"
        ]
    },

    "Portugal": {
        "priority": 95,
        "keywords": [
            "portugal",
            "portugal national team"
        ]
    },

    "Netherlands": {
        "priority": 92,
        "keywords": [
            "netherlands",
            "holland",
            "netherlands national team",
            "dutch national team"
        ]
    },

    "Italy": {
        "priority": 92,
        "keywords": [
            "italy",
            "italy national team",
            "italian national team"
        ]
    },

    "Belgium": {
        "priority": 88,
        "keywords": [
            "belgium",
            "belgium national team"
        ]
    },

    "Croatia": {
        "priority": 85,
        "keywords": [
            "croatia",
            "croatia national team"
        ]
    },

    "Uruguay": {
        "priority": 85,
        "keywords": [
            "uruguay",
            "uruguay national team"
        ]
    },

    "Colombia": {
        "priority": 85,
        "keywords": [
            "colombia",
            "colombia national team"
        ]
    },

    "Morocco": {
        "priority": 85,
        "keywords": [
            "morocco",
            "morocco national team",
            "morocco nt"
        ]
    },

    "Japan": {
        "priority": 82,
        "keywords": [
            "japan",
            "japan national team"
        ]
    },

    "South Korea": {
        "priority": 82,
        "keywords": [
            "south korea",
            "korea republic",
            "south korea national team"
        ]
    },

    "Mexico": {
        "priority": 80,
        "keywords": [
            "mexico",
            "mexico national team"
        ]
    },

    "Turkey": {
        "priority": 80,
        "keywords": [
            "turkey",
            "turkey national team",
            "türkiye"
        ]
    },

    "Scotland": {
        "priority": 75,
        "keywords": [
            "scotland",
            "scotland national team"
        ]
    },

    "Wales": {
        "priority": 75,
        "keywords": [
            "wales",
            "wales national team"
        ]
    }
}


# ============================================================
# FOOTBALL KEYWORDS
# ============================================================

FOOTBALL_KEYWORDS = {

    "football",
    "soccer",
    "footballer",
    "footballers",
    "football club",
    "football team",

    # Competitions
    "premier league",
    "la liga",
    "champions league",
    "europa league",
    "conference league",
    "serie a",
    "serie b",
    "bundesliga",
    "ligue 1",
    "copa del rey",
    "fa cup",
    "carabao cup",
    "community shield",
    "world cup",
    "world cup qualifier",
    "euro",
    "euros",
    "uefa",
    "fifa",
    "club world cup",
    "afcon",
    "wafcon",
    "african cup of nations",
    "women's africa cup of nations",
    "afc asian cup",
    "copa america",
    "concacaf",
    "gold cup",
    "nations league",
    "women's world cup",
    "women's champions league",

    # Women's football
    "women's football",
    "women's soccer",
    "womens football",
    "womens soccer",

    # Major leagues
    "mls",
    "nwsl",
    "liga mx",
    "saudi pro league",
    "eredivisie",
    "primeira liga",
    "scottish premiership",
    "j1 league",
    "k league",

    # Transfers
    "transfer",
    "transfers",
    "signing",
    "signed",
    "signs",
    "agreement",
    "deal",
    "contract",
    "medical",
    "bid",
    "interest",
    "joins",
    "joined",

    # Match actions
    "goal",
    "goals",
    "scored",
    "scores",
    "assist",
    "assists",
    "assisted",
    "match",
    "fixture",
    "fixtures",
    "starting xi",
    "lineup",
    "line-up",
    "win",
    "wins",
    "won",
    "defeat",
    "defeats",
    "beat",
    "beats",
    "lost",
    "draw",
    "draws",
    "promoted",
    "relegated",

    # Positions
    "manager",
    "coach",
    "head coach",
    "striker",
    "midfielder",
    "defender",
    "goalkeeper",
    "captain",
    "substitute",
    "bench",

    # Match events
    "red card",
    "yellow card",
    "penalty",
    "offside",

    # Trophies
    "trophy",
    "champion",
    "champions",

    # Stadium
    "stadium",
    "kick-off",
    "kickoff"
}


# ============================================================
# IMPORTANT FOOTBALL TOPICS
# ============================================================

IMPORTANT_TOPICS = {

    "transfer",
    "signed",
    "signing",
    "agreement",
    "deal",
    "medical",
    "contract",
    "joins",
    "bid",
    "interest",

    "injury",
    "injured",

    "match",
    "fixture",
    "lineup",
    "starting xi",

    "goal",
    "goals",

    "trophy",
    "champion",
    "champions",

    "official",
    "announced",
    "announcement",

    "manager",
    "coach",

    "win",
    "wins",
    "won",
    "defeat",
    "defeats",
    "beat",
    "beats",
    "final"
}


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_post(text):

    if not text:
        return ""

    text = str(text)

    text = text.replace("[", "")
    text = text.replace("]", "")
    text = text.replace("(", "")
    text = text.replace(")", "")
    text = text.replace("{", "")
    text = text.replace("}", "")

    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("```", "")
    text = text.replace("`", "")

    text = re.sub(
        r"^(POST|TEXT|CATEGORY|TEAM_A|TEAM_B|IMPORTANT|SPORT)\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# CLEAN TEAM
# ============================================================

def clean_team_name(team):

    if not team:
        return "UNKNOWN"

    team = str(team).strip()

    team = team.replace("[", "")
    team = team.replace("]", "")
    team = team.replace("(", "")
    team = team.replace(")", "")
    team = team.replace('"', "")
    team = team.replace("'", "")

    team = re.sub(
        r"\s+",
        " ",
        team
    )

    if not team:
        return "UNKNOWN"

    if team.lower() in {
        "unknown",
        "none",
        "null",
        "n/a",
        "na",
        "not available",
        "not identified",
        "not specified"
    }:
        return "UNKNOWN"

    return team


# ============================================================
# DEFAULT RESULT
# ============================================================

def empty_result():

    return {
        "is_football": False,
        "is_important": False,
        "priority": "low",
        "category": "general",
        "post": "",
        "subject_type": "football",
        "club": "UNKNOWN",
        "national_team": "UNKNOWN",
        "player": "UNKNOWN",
        "team_a": "UNKNOWN",
        "team_b": "UNKNOWN",
        "visual_subject": "",
        "visual_type": "generic",
        "primary_team": "UNKNOWN",
        "secondary_team": "UNKNOWN"
    }


# ============================================================
# NORMALIZE BOOLEAN
# ============================================================

def normalize_boolean(value):

    if isinstance(value, bool):
        return value

    if value is None:
        return False

    value = str(
        value
    ).strip().lower()

    return value in {
        "true",
        "yes",
        "1",
        "important"
    }


# ============================================================
# NORMALIZE PRIORITY
# ============================================================

def normalize_priority(value):

    value = str(
        value or "normal"
    ).strip().lower()

    if value not in {
        "very_high",
        "high",
        "normal",
        "low"
    }:
        return "normal"

    return value


# ============================================================
# NORMALIZE SUBJECT TYPE
# ============================================================

def normalize_subject_type(value):

    value = str(
        value or "football"
    ).strip().lower()

    if value not in {
        "club",
        "national_team",
        "football",
        "player"
    }:
        return "football"

    return value


# ============================================================
# NORMALIZE VISUAL TYPE
# ============================================================

def normalize_visual_type(value):

    value = str(
        value or "generic"
    ).strip().lower()

    allowed = {
        "club",
        "club_match",
        "national_team",
        "national_match",
        "player",
        "transfer",
        "injury",
        "trophy",
        "lineup",
        "announcement",
        "breaking",
        "quote",
        "match",
        "generic"
    }

    if value not in allowed:
        return "generic"

    return value


# ============================================================
# NON-FOOTBALL FILTER
# ============================================================

def contains_non_football_sport(text):

    if not text:
        return False

    text_lower = str(
        text
    ).lower()

    for sport in NON_FOOTBALL_SPORTS:

        pattern = (
            r"\b"
            + re.escape(sport)
            + r"\b"
        )

        if re.search(
            pattern,
            text_lower
        ):
            return True

    return False


# ============================================================
# CLUB DETECTION
# ============================================================

def detect_major_clubs(text):

    if not text:
        return []

    text_lower = str(
        text
    ).lower()

    found = []

    for club_name, data in MAJOR_CLUBS.items():

        for keyword in data["keywords"]:

            if keyword.lower() in text_lower:

                found.append(
                    (
                        club_name,
                        data["priority"]
                    )
                )

                break

    return found


# ============================================================
# NATIONAL TEAM DETECTION
# ============================================================

def detect_national_teams(text):

    if not text:
        return []

    text_lower = str(
        text
    ).lower()

    found = []

    for team_name, data in MAJOR_NATIONAL_TEAMS.items():

        for keyword in data["keywords"]:

            if keyword.lower() in text_lower:

                found.append(
                    (
                        team_name,
                        data["priority"]
                    )
                )

                break

    return found


# ============================================================
# FOOTBALL SIGNAL
# ============================================================

def contains_football_signal(text):

    if not text:
        return False

    text_lower = str(
        text
    ).lower()

    if contains_non_football_sport(
        text
    ):
        return False

    if detect_major_clubs(
        text
    ):
        return True

    if detect_national_teams(
        text
    ):
        return True

    for keyword in FOOTBALL_KEYWORDS:

        if keyword.lower() in text_lower:

            return True

    return False


# ============================================================
# FOOTBALL IMPORTANCE SIGNAL
# ============================================================

def has_important_football_topic(text):

    if not text:
        return False

    text_lower = str(
        text
    ).lower()

    for keyword in IMPORTANT_TOPICS:

        if keyword in text_lower:

            return True

    return False


# ============================================================
# ENGLISH CHECK
# ============================================================

def is_reasonably_english(text):

    if not text:
        return False

    text = str(
        text
    ).strip()

    if not text:
        return False

    non_latin_script = re.search(
        r"[\u0600-\u06FF"
        r"\u0400-\u04FF"
        r"\u4E00-\u9FFF"
        r"\u3040-\u30FF"
        r"\uAC00-\uD7AF]",
        text
    )

    if non_latin_script:
        return False

    latin_letters = re.findall(
        r"[A-Za-zÀ-ÖØ-öø-ÿ]",
        text
    )

    if len(latin_letters) < 5:
        return False

    return True


# ============================================================
# HASHTAG HELPERS
# ============================================================

def hashtagify(text):

    if not text:
        return ""

    text = str(text).strip()

    text = re.sub(
        r"[#]",
        "",
        text
    )

    text = re.sub(
        r"[^A-Za-z0-9À-ÖØ-öø-ÿ]+",
        " ",
        text
    )

    words = text.split()

    if not words:
        return ""

    return "#" + "".join(
        word.capitalize()
        for word in words
    )


def clean_hashtag(tag):

    if not tag:
        return ""

    tag = str(tag).strip()

    tag = tag.replace(
        "#",
        ""
    )

    tag = re.sub(
        r"[^A-Za-z0-9À-ÖØ-öø-ÿ]",
        "",
        tag
    )

    if not tag:
        return ""

    return "#" + tag


def extract_hashtags(text):

    if not text:
        return []

    matches = re.findall(
        r"#[A-Za-z0-9À-ÖØ-öø-ÿ]+",
        str(text)
    )

    result = []

    for tag in matches:

        tag = clean_hashtag(
            tag
        )

        if not tag:
            continue

        if tag.lower() not in {
            existing.lower()
            for existing in result
        }:

            result.append(
                tag
            )

    return result


def remove_hashtags(text):

    if not text:
        return ""

    text = re.sub(
        r"#[A-Za-z0-9À-ÖØ-öø-ÿ]+",
        "",
        str(text)
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# BUILD HASHTAGS
# ============================================================

def build_hashtags(
    category,
    club,
    national_team,
    player,
    team_a,
    team_b,
    news=""
):

    hashtags = []

    def add(tag):

        if not tag:
            return

        tag = clean_hashtag(
            tag
        )

        if not tag:
            return

        if tag.lower() in {
            existing.lower()
            for existing in hashtags
        }:
            return

        hashtags.append(
            tag
        )

    category = str(
        category or ""
    ).lower()

    club = clean_team_name(
        club
    )

    national_team = clean_team_name(
        national_team
    )

    player = clean_team_name(
        player
    )

    team_a = clean_team_name(
        team_a
    )

    team_b = clean_team_name(
        team_b
    )

    # ========================================================
    # MATCH
    # ========================================================

    if category == "match":

        if team_a != "UNKNOWN":
            add(
                hashtagify(
                    team_a
                )
            )

        if team_b != "UNKNOWN":
            add(
                hashtagify(
                    team_b
                )
            )

        if national_team != "UNKNOWN":
            add(
                hashtagify(
                    national_team
                )
            )

        if len(hashtags) < 3:
            add("#Football")

    # ========================================================
    # NATIONAL TEAM
    # ========================================================

    elif national_team != "UNKNOWN":

        add(
            hashtagify(
                national_team
            )
        )

        if player != "UNKNOWN":
            add(
                hashtagify(
                    player
                )
            )

        add(
            "#Football"
        )

    # ========================================================
    # CLUB STORY
    # ========================================================

    else:

        if club != "UNKNOWN":

            add(
                hashtagify(
                    club
                )
            )

        elif team_a != "UNKNOWN":

            add(
                hashtagify(
                    team_a
                )
            )

        if player != "UNKNOWN":

            add(
                hashtagify(
                    player
                )
            )

        if team_b != "UNKNOWN":

            add(
                hashtagify(
                    team_b
                )
            )

        if category == "transfer":

            add("#Transfer")

        elif category == "injury":

            add("#Football")

        elif category == "lineup":

            add("#Football")

        elif category == "trophy":

            add("#Football")

        elif category == "announcement":

            add("#Football")

        elif category == "breaking":

            add("#Breaking")

        elif category == "quote":

            add("#Football")

        elif category == "player":

            add("#Football")

        else:

            add("#Football")

    # ========================================================
    # UNIVERSAL FALLBACKS
    # ========================================================

    add("#Football")
    add("#FootballNews")
    add("#Soccer")

    # ========================================================
    # EXACTLY 3
    # ========================================================

    return hashtags[:3]


# ============================================================
# APPEND HASHTAGS
# ============================================================

def append_hashtags(
    post,
    category,
    club,
    national_team,
    player,
    team_a,
    team_b,
    news=""
):

    post = remove_hashtags(
        post
    )

    if not post:
        return ""

    hashtags = build_hashtags(
        category=category,
        club=club,
        national_team=national_team,
        player=player,
        team_a=team_a,
        team_b=team_b,
        news=news
    )

    # ========================================================
    # ALWAYS EXACTLY 3
    # ========================================================

    fallback_hashtags = [
        "#Football",
        "#FootballNews",
        "#Soccer"
    ]

    for fallback in fallback_hashtags:

        if len(hashtags) >= 3:
            break

        if fallback.lower() not in {
            tag.lower()
            for tag in hashtags
        }:

            hashtags.append(
                fallback
            )

    return (
        post.rstrip()
        + "\n\n"
        + " ".join(
            hashtags[:3]
        )
    )


# ============================================================
# AI PROMPT
# ============================================================

def rewrite_news(news):

    prompt = f"""
You are the chief editor of Shingal Sport,
a serious professional football news media page.

Analyze ONE news headline.

Your job is to determine:

1. Is this association football / soccer?
2. Is it important enough to publish?
3. What category does it belong to?
4. Which club, national team or player is involved?
5. Which teams are involved if it is a match?
6. What should the visual design focus on?

============================================================
ABSOLUTE SPORT FILTER
============================================================

ONLY association football / soccer is allowed.

Reject completely if the article is mainly about:

Tennis
Cricket
Golf
Rugby
Basketball
Baseball
NFL
American football
Formula 1
Motorsport
MotoGP
Boxing
MMA
UFC
Cycling
Horse racing
Athletics
Snooker
Darts
Swimming
Volleyball
Handball
Hockey
Ice hockey
Skiing
Gymnastics
Badminton
Table tennis
Other sports

Also reject:

Fantasy football
FPL analysis
Betting
Gambling
Casino
Odds
Predictions based on betting
Commercial promotions

IMPORTANT:

Do NOT classify something as football simply because
the article appears in a sports RSS feed.

The actual headline must concern association football.

============================================================
EDITORIAL PRIORITY
============================================================

The page should strongly prioritize major clubs.

HIGHEST PRIORITY:

1. Real Madrid
2. Barcelona

VERY HIGH PRIORITY:

Manchester United
Manchester City
Liverpool
Arsenal
Chelsea
Bayern Munich
PSG
Juventus
Inter Milan
AC Milan
Atlético Madrid

HIGH PRIORITY:

Borussia Dortmund
Bayer Leverkusen
Tottenham
Newcastle United
Napoli
Roma
Lazio
Ajax
Benfica
Porto
Sporting CP
Marseille
Monaco
Sevilla
Valencia
Villarreal

Major national teams should also receive strong priority.

============================================================
NATIONAL TEAMS
============================================================

Prioritize:

Spain
Argentina
Brazil
France
England
Germany
Portugal
Netherlands
Italy
Belgium
Croatia
Uruguay
Colombia
Morocco
Japan
South Korea
Mexico
Turkey
Scotland
Wales

National-team football is allowed and important.

============================================================
IMPORTANT NEWS
============================================================

VERY HIGH:

- Real Madrid major news
- Barcelona major news
- Major transfer
- Official signing
- Major contract
- Major manager appointment
- Major injury to a famous player
- Major match
- El Clasico
- Champions League major event
- Major final
- Major trophy
- Major national-team event
- Major breaking football news

HIGH:

- Important transfer
- Important injury
- Important fixture
- Important lineup
- Important official announcement
- Important player development
- Major club decision

NORMAL:

- Genuine football news with moderate importance

LOW:

- Minor football story
- Generic opinion
- Generic analysis
- Fantasy football
- Betting
- Promotional content

============================================================
DO NOT INVENT
============================================================

Use ONLY information contained in the headline.

Do NOT invent:

players
clubs
scores
transfers
dates
competitions
quotes
fees
contracts
results

If a team is not clearly identified,
return UNKNOWN.

============================================================
TEAM IDENTIFICATION
============================================================

If the main subject is a club:

subject_type = "club"

If the main subject is a national team:

subject_type = "national_team"

If the main subject is mainly one football player:

subject_type = "player"

Otherwise:

subject_type = "football"

For a match:

team_a = first team
team_b = second team

For a club story:

club = main club

For a national-team story:

national_team = main national team

============================================================
VISUAL DESIGN
============================================================

Choose ONE:

club
club_match
national_team
national_match
player
transfer
injury
trophy
lineup
announcement
breaking
quote
match
generic

If a major club is clearly involved,
the visual must focus on that club.

============================================================
POST
============================================================

The post must:

- Be English.
- Be concise.
- Sound natural.
- Sound like professional football media.
- Be suitable for Facebook and Instagram.
- Use normal capitalization.
- Use 1 to 3 football emojis when useful.
- Never use ALL CAPS.
- Never use markdown.
- Never use square brackets.
- Never mention the source.
- Never invent information.
- Never add information not contained in the headline.
- Never use "Here we go".
- Never imitate Fabrizio Romano.
- DO NOT add hashtags.
- The system will add exactly 3 hashtags automatically.

============================================================
JSON OUTPUT
============================================================

If the news is football and important,
return:

{{
    "is_football": true,
    "is_important": true,
    "priority": "normal",
    "category": "GENERAL",
    "post": "English football post",
    "subject_type": "football",
    "club": "UNKNOWN",
    "national_team": "UNKNOWN",
    "player": "UNKNOWN",
    "team_a": "UNKNOWN",
    "team_b": "UNKNOWN",
    "visual_subject": "",
    "visual_type": "generic",
    "primary_team": "UNKNOWN",
    "secondary_team": "UNKNOWN"
}}

If NOT football or NOT important,
return:

{{
    "is_football": false,
    "is_important": false,
    "priority": "low",
    "category": "GENERAL",
    "post": "",
    "subject_type": "football",
    "club": "UNKNOWN",
    "national_team": "UNKNOWN",
    "player": "UNKNOWN",
    "team_a": "UNKNOWN",
    "team_b": "UNKNOWN",
    "visual_subject": "",
    "visual_type": "generic",
    "primary_team": "UNKNOWN",
    "secondary_team": "UNKNOWN"
}}

============================================================
JSON ONLY
============================================================

Return ONLY valid JSON.

NEWS HEADLINE:

{news}
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.10
    )

    return (
        response
        .choices[0]
        .message
        .content
        .strip()
    )


# ============================================================
# PARSE RESULT
# ============================================================

def parse_ai_result(
    result,
    original_news=""
):

    if not result:
        return empty_result()

    result = result.strip()

    result = re.sub(
        r"^```json\s*",
        "",
        result,
        flags=re.IGNORECASE
    )

    result = re.sub(
        r"\s*```$",
        "",
        result
    )

    # ========================================================
    # JSON PARSE
    # ========================================================

    try:

        data = json.loads(
            result
        )

    except json.JSONDecodeError:

        match = re.search(
            r"\{.*\}",
            result,
            flags=re.DOTALL
        )

        if not match:

            print(
                "⚠️ AI returned invalid JSON."
            )

            return empty_result()

        try:

            data = json.loads(
                match.group(0)
            )

        except Exception:

            print(
                "❌ Could not parse AI result."
            )

            return empty_result()

    # ========================================================
    # VALUES
    # ========================================================

    is_football = normalize_boolean(
        data.get(
            "is_football",
            False
        )
    )

    is_important = normalize_boolean(
        data.get(
            "is_important",
            False
        )
    )

    priority = normalize_priority(
        data.get(
            "priority",
            "normal"
        )
    )

    category = str(
        data.get(
            "category",
            "GENERAL"
        )
    ).strip().upper()

    if category not in ALLOWED_CATEGORIES:

        category = "GENERAL"

    post = clean_post(
        data.get(
            "post",
            ""
        )
    )

    subject_type = normalize_subject_type(
        data.get(
            "subject_type",
            "football"
        )
    )

    club = clean_team_name(
        data.get(
            "club",
            "UNKNOWN"
        )
    )

    national_team = clean_team_name(
        data.get(
            "national_team",
            "UNKNOWN"
        )
    )

    player = clean_team_name(
        data.get(
            "player",
            "UNKNOWN"
        )
    )

    team_a = clean_team_name(
        data.get(
            "team_a",
            "UNKNOWN"
        )
    )

    team_b = clean_team_name(
        data.get(
            "team_b",
            "UNKNOWN"
        )
    )

    visual_subject = clean_post(
        data.get(
            "visual_subject",
            ""
        )
    )

    visual_type = normalize_visual_type(
        data.get(
            "visual_type",
            "generic"
        )
    )

    primary_team = clean_team_name(
        data.get(
            "primary_team",
            "UNKNOWN"
        )
    )

    secondary_team = clean_team_name(
        data.get(
            "secondary_team",
            "UNKNOWN"
        )
    )

    # ========================================================
    # HARD NON-FOOTBALL FILTER
    # ========================================================

    combined_text = " ".join(
        [
            post,
            visual_subject,
            club,
            national_team,
            player,
            team_a,
            team_b
        ]
    )

    if contains_non_football_sport(
        combined_text
    ):

        print(
            "🚫 AI result rejected because it contains a non-football sport."
        )

        return empty_result()

    # ========================================================
    # ENGLISH VALIDATION
    # ========================================================

    post = remove_hashtags(
        post
    )

    if post and not is_reasonably_english(
        post
    ):

        print(
            "⚠️ AI post rejected because it is not English."
        )

        post = ""

        is_important = False

    # ========================================================
    # FOOTBALL VALIDATION
    # ========================================================

    if not is_football:

        return empty_result()

    # ========================================================
    # IMPORTANT VALIDATION
    # ========================================================

    if not is_important:

        post = ""

    # ========================================================
    # IF IMPORTANT BUT NO POST
    # ========================================================

    if is_important and not post:

        is_important = False
        priority = "low"

    # ========================================================
    # MATCH VALIDATION
    # ========================================================

    if category == "MATCH":

        if (
            team_a == "UNKNOWN"
            or team_b == "UNKNOWN"
        ):

            print(
                "⚠️ Match category detected but teams are missing."
            )

            visual_type = "generic"

            primary_team = "UNKNOWN"
            secondary_team = "UNKNOWN"

    # ========================================================
    # AUTOMATIC VISUAL TYPE CORRECTION
    # ========================================================

    if (
        team_a != "UNKNOWN"
        and team_b != "UNKNOWN"
        and category == "MATCH"
    ):

        if (
            detect_major_clubs(
                team_a
            )
            or detect_major_clubs(
                team_b
            )
        ):

            if (
                detect_national_teams(
                    team_a
                )
                or detect_national_teams(
                    team_b
                )
            ):

                visual_type = "national_match"

            else:

                visual_type = "club_match"

    elif (
        club != "UNKNOWN"
        and category == "TRANSFER"
    ):

        visual_type = "transfer"

    elif (
        club != "UNKNOWN"
        and category == "INJURY"
    ):

        visual_type = "injury"

    elif (
        club != "UNKNOWN"
        and category == "TROPHY"
    ):

        visual_type = "trophy"

    elif (
        club != "UNKNOWN"
        and category == "LINEUP"
    ):

        visual_type = "lineup"

    elif (
        club != "UNKNOWN"
        and category == "ANNOUNCEMENT"
    ):

        visual_type = "announcement"

    elif (
        club != "UNKNOWN"
        and category == "BREAKING"
    ):

        visual_type = "breaking"

    elif (
        club != "UNKNOWN"
        and category == "QUOTE"
    ):

        visual_type = "quote"

    elif (
        national_team != "UNKNOWN"
        and category == "MATCH"
    ):

        visual_type = "national_match"

    # ========================================================
    # PRIMARY TEAM FALLBACK
    # ========================================================

    if primary_team == "UNKNOWN":

        if club != "UNKNOWN":

            primary_team = club

        elif national_team != "UNKNOWN":

            primary_team = national_team

        elif team_a != "UNKNOWN":

            primary_team = team_a

    # ========================================================
    # SECONDARY TEAM FALLBACK
    # ========================================================

    if secondary_team == "UNKNOWN":

        if team_b != "UNKNOWN":

            secondary_team = team_b

    # ========================================================
    # ADD EXACTLY 3 HASHTAGS
    # ========================================================

    if is_important and post:

        post = append_hashtags(
            post=post,
            category=category,
            club=club,
            national_team=national_team,
            player=player,
            team_a=team_a,
            team_b=team_b,
            news=original_news
        )

    # ========================================================
    # RESULT
    # ========================================================

    return {
        "is_football": True,
        "is_important": is_important,
        "priority": priority,
        "category": category.lower(),
        "post": post,
        "subject_type": subject_type,
        "club": club,
        "national_team": national_team,
        "player": player,
        "team_a": team_a,
        "team_b": team_b,
        "visual_subject": visual_subject,
        "visual_type": visual_type,
        "primary_team": primary_team,
        "secondary_team": secondary_team
    }


# ============================================================
# ANALYZE NEWS
# ============================================================

def analyze_news(news):

    news = str(
        news or ""
    ).strip()

    if not news:

        return empty_result()

    print(
        "🤖 Analyzing football news..."
    )

    # ========================================================
    # HARD NON-FOOTBALL CHECK
    # ========================================================

    if contains_non_football_sport(
        news
    ):

        print(
            "🚫 Quick filter rejected non-football sport."
        )

        return empty_result()

    # ========================================================
    # FOOTBALL SIGNAL
    # ========================================================

    football_signal = contains_football_signal(
        news
    )

    if not football_signal:

        print(
            "🚫 No clear football signal."
        )

        return empty_result()

    # ========================================================
    # AI CLASSIFICATION
    # ========================================================

    print(
        "🤖 Asking AI to classify football news..."
    )

    try:

        result = rewrite_news(
            news
        )

    except Exception as error:

        print(
            "❌ Groq classification error:"
        )

        print(
            error
        )

        return empty_result()

    parsed = parse_ai_result(
        result,
        original_news=news
    )

    # ========================================================
    # DEBUG
    # ========================================================

    print()
    print(
        "🤖 AI RESULT"
    )

    print(
        "Football:",
        parsed["is_football"]
    )

    print(
        "Important:",
        parsed["is_important"]
    )

    print(
        "Priority:",
        parsed["priority"]
    )

    print(
        "Category:",
        parsed["category"]
    )

    print(
        "Club:",
        parsed["club"]
    )

    print(
        "National team:",
        parsed["national_team"]
    )

    print(
        "Player:",
        parsed["player"]
    )

    print(
        "Team A:",
        parsed["team_a"]
    )

    print(
        "Team B:",
        parsed["team_b"]
    )

    print(
        "Visual type:",
        parsed["visual_type"]
    )

    print(
        "Primary team:",
        parsed["primary_team"]
    )

    print(
        "Secondary team:",
        parsed["secondary_team"]
    )

    print(
        "Post:",
        parsed["post"]
    )

    return parsed


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    tests = [

        "Real Madrid are preparing a major transfer move.",

        "Barcelona are monitoring a new midfielder.",

        "Real Madrid will face Barcelona in a huge La Liga clash.",

        "Spain will face Germany in a major international match.",

        "Liverpool reach agreement with a midfielder.",

        "Barcelona star ruled out with an injury.",

        "Swiatek beats Rybakina to win the title in Toronto.",

        "Max Verstappen wins the Formula 1 race.",

        "England cricket team announce their squad.",

        "NBA star scores 40 points in a huge game.",

        "Nigeria crush Malawi, win first WAFCON title.",

        "Sullivan assists on 2 in Union rally over NYCFC.",

        "Arsenal complete major transfer agreement.",

        "Real Madrid win the Spanish Super Cup.",

        "France beat Spain in the final."
    ]

    for test_news in tests:

        print()
        print(
            "===================================="
        )

        print(
            "TEST:",
            test_news
        )

        print(
            "===================================="
        )

        result = analyze_news(
            test_news
        )

        print(
            json.dumps(
                result,
                indent=4,
                ensure_ascii=False
            )
        )