import os
import re
import io
import time
import requests

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter,
    ImageEnhance
)

from urllib.parse import quote


# ============================================================
# GLOBAL SETTINGS
# ============================================================

WIDTH = 1080
HEIGHT = 1080

POLLINATIONS_URL = (
    "https://image.pollinations.ai/prompt/"
)

POLLINATIONS_TIMEOUT = 180
POLLINATIONS_RETRIES = 3


# ============================================================
# COLORS
# ============================================================

BLACK = (5, 6, 8)
WHITE = (248, 248, 248)
GRAY = (175, 178, 185)

RED = (218, 25, 38)
BRIGHT_RED = (245, 35, 48)
YELLOW = (255, 194, 32)

BLUE = (25, 70, 170)
DARK_BLUE = (8, 25, 65)

GREEN = (25, 145, 80)
DARK_GREEN = (8, 70, 40)

GOLD = (220, 175, 65)

# Barcelona
BARCA_RED = (155, 20, 45)
BARCA_BLUE = (20, 35, 110)
BARCA_GOLD = (210, 180, 55)

# Real Madrid
MADRID_BLUE = (25, 60, 125)
MADRID_GOLD = (210, 170, 65)

# Manchester United
UNITED_RED = (205, 20, 30)
UNITED_BLACK = (10, 10, 12)
UNITED_GOLD = (220, 180, 55)

# Manchester City
CITY_BLUE = (40, 145, 220)
CITY_DARK = (10, 55, 110)

# Arsenal
ARSENAL_RED = (210, 30, 40)
ARSENAL_DARK = (90, 10, 18)

# Chelsea
CHELSEA_BLUE = (20, 65, 150)
CHELSEA_DARK = (8, 25, 75)

# Liverpool
LIVERPOOL_RED = (195, 20, 35)
LIVERPOOL_DARK = (80, 8, 15)

# Bayern
BAYERN_RED = (190, 20, 35)
BAYERN_DARK = (95, 8, 20)

# PSG
PSG_BLUE = (20, 35, 95)
PSG_RED = (210, 25, 50)

# Inter
INTER_BLUE = (20, 55, 130)
INTER_BLACK = (5, 8, 16)

# Milan
MILAN_RED = (190, 20, 30)
MILAN_BLACK = (8, 8, 10)

# Juventus
JUVENTUS_BLACK = (8, 8, 10)

# Dortmund
DORTMUND_YELLOW = (245, 210, 20)
DORTMUND_BLACK = (8, 8, 8)

# Atletico
ATLETICO_RED = (200, 25, 40)
ATLETICO_BLUE = (20, 55, 125)

# Newcastle
NEWCASTLE_BLACK = (7, 8, 10)

# National teams
FRANCE_BLUE = (25, 55, 145)
ARGENTINA_BLUE = (90, 175, 225)
BRAZIL_GREEN = (20, 120, 65)
PORTUGAL_RED = (185, 25, 35)
SPAIN_RED = (200, 30, 40)
GERMANY_BLACK = (10, 10, 10)
ITALY_BLUE = (20, 75, 160)
ENGLAND_BLUE = (25, 55, 135)
NETHERLANDS_ORANGE = (240, 105, 20)


# ============================================================
# FONTS
# ============================================================

LINUX_FONT_BOLD = (
    "/usr/share/fonts/truetype/dejavu/"
    "DejaVuSans-Bold.ttf"
)

LINUX_FONT_REGULAR = (
    "/usr/share/fonts/truetype/dejavu/"
    "DejaVuSans.ttf"
)

WINDOWS_FONT_BOLD = (
    r"C:\Windows\Fonts\arialbd.ttf"
)

WINDOWS_FONT_REGULAR = (
    r"C:\Windows\Fonts\arial.ttf"
)


def get_font(size, bold=True):

    if bold:

        candidates = [
            LINUX_FONT_BOLD,
            WINDOWS_FONT_BOLD
        ]

    else:

        candidates = [
            LINUX_FONT_REGULAR,
            WINDOWS_FONT_REGULAR
        ]

    for path in candidates:

        if os.path.exists(path):

            return ImageFont.truetype(
                path,
                size
            )

    return ImageFont.load_default()


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = str(text)

    replacements = [
        ("[", ""),
        ("]", ""),
        ("(", ""),
        (")", ""),
        ("{", ""),
        ("}", ""),
        ("**", ""),
        ("__", ""),
        ("```", ""),
        ("`", "")
    ]

    for old, new in replacements:

        text = text.replace(
            old,
            new
        )

    text = re.sub(
        r"^(POST|TEXT|CATEGORY|TEAM_A|TEAM_B|"
        r"HEADLINE|VISUAL_TYPE|PRIMARY_TEAM|"
        r"SECONDARY_TEAM)\s*:\s*",
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
# TEAM NORMALIZATION
# ============================================================

def normalize_team_name(team_name):

    if not team_name:

        return ""

    value = clean_text(
        team_name
    ).lower().strip()

    aliases = {
        "barca": "barcelona",
        "barça": "barcelona",
        "fc barcelona": "barcelona",

        "madrid": "real madrid",

        "man utd": "manchester united",
        "man united": "manchester united",
        "manchester utd": "manchester united",

        "man city": "manchester city",

        "spurs": "tottenham",
        "tottenham hotspur": "tottenham",

        "bayern": "bayern munich",
        "fc bayern": "bayern munich",

        "dortmund": "borussia dortmund",

        "psg": "psg",
        "paris saint-germain": "psg",
        "paris saint germain": "psg",

        "inter": "inter milan",
        "internazionale": "inter milan",

        "milan": "ac milan",

        "atletico": "atletico madrid",
        "atlético": "atletico madrid",

        "juve": "juventus",

        "holland": "netherlands",

        "brasil": "brazil",

        "türkiye": "turkey"
    }

    return aliases.get(
        value,
        value
    )


# ============================================================
# TEAM IDENTITIES
# ============================================================

TEAM_IDENTITIES = {

    "barcelona": {
        "keywords": [
            "barcelona",
            "fc barcelona",
            "barca",
            "barça"
        ],
        "primary": BARCA_BLUE,
        "secondary": BARCA_RED,
        "accent": BARCA_GOLD,
        "style": (
            "deep Barcelona blue and burgundy "
            "editorial lighting, refined Catalan football "
            "atmosphere, elegant vertical architectural lines, "
            "premium European football media composition"
        ),
        "pattern": "vertical",
        "energy": 0.65
    },

    "real madrid": {
        "keywords": [
            "real madrid",
            "real madrid cf"
        ],
        "primary": MADRID_BLUE,
        "secondary": WHITE,
        "accent": MADRID_GOLD,
        "style": (
            "royal blue, white and elegant gold editorial "
            "lighting, luxury European football atmosphere, "
            "premium Champions League visual language, "
            "refined geometric structure"
        ),
        "pattern": "luxury",
        "energy": 0.55
    },

    "atletico madrid": {
        "keywords": [
            "atletico madrid",
            "atlético madrid"
        ],
        "primary": ATLETICO_RED,
        "secondary": WHITE,
        "accent": ATLETICO_BLUE,
        "style": (
            "intense red and white editorial lighting with "
            "dark blue shadows and aggressive diagonal geometry"
        ),
        "pattern": "stripes",
        "energy": 0.85
    },

    "manchester united": {
        "keywords": [
            "manchester united",
            "man utd",
            "man united"
        ],
        "primary": UNITED_RED,
        "secondary": UNITED_BLACK,
        "accent": UNITED_GOLD,
        "style": (
            "deep Manchester red, black shadows and subtle "
            "gold highlights, dramatic historic English football "
            "atmosphere with premium broadcast lighting"
        ),
        "pattern": "diagonal",
        "energy": 0.85
    },

    "manchester city": {
        "keywords": [
            "manchester city",
            "man city"
        ],
        "primary": CITY_BLUE,
        "secondary": CITY_DARK,
        "accent": WHITE,
        "style": (
            "modern sky blue and dark blue football media "
            "atmosphere with clean futuristic architectural lines"
        ),
        "pattern": "modern",
        "energy": 0.55
    },

    "liverpool": {
        "keywords": [
            "liverpool",
            "liverpool fc"
        ],
        "primary": LIVERPOOL_RED,
        "secondary": LIVERPOOL_DARK,
        "accent": WHITE,
        "style": (
            "deep Liverpool red, dark atmospheric shadows, "
            "intense English football media atmosphere and "
            "dramatic stadium illumination"
        ),
        "pattern": "diagonal",
        "energy": 0.85
    },

    "arsenal": {
        "keywords": [
            "arsenal",
            "arsenal fc"
        ],
        "primary": ARSENAL_RED,
        "secondary": ARSENAL_DARK,
        "accent": WHITE,
        "style": (
            "strong Arsenal red and white visual identity, "
            "elegant modern London football atmosphere, "
            "clean premium geometry"
        ),
        "pattern": "clean",
        "energy": 0.7
    },

    "chelsea": {
        "keywords": [
            "chelsea",
            "chelsea fc"
        ],
        "primary": CHELSEA_BLUE,
        "secondary": CHELSEA_DARK,
        "accent": WHITE,
        "style": (
            "royal Chelsea blue, deep navy shadows, "
            "modern London football architecture and "
            "premium European media design"
        ),
        "pattern": "radial",
        "energy": 0.65
    },

    "tottenham": {
        "keywords": [
            "tottenham",
            "tottenham hotspur",
            "spurs"
        ],
        "primary": WHITE,
        "secondary": DARK_BLUE,
        "accent": CITY_BLUE,
        "style": (
            "white and dark navy modern football atmosphere, "
            "futuristic stadium geometry and clean premium lighting"
        ),
        "pattern": "modern",
        "energy": 0.5
    },

    "bayern munich": {
        "keywords": [
            "bayern munich",
            "bayern",
            "fc bayern"
        ],
        "primary": BAYERN_RED,
        "secondary": BAYERN_DARK,
        "accent": WHITE,
        "style": (
            "powerful Bayern red and white editorial atmosphere, "
            "elite German football environment, dramatic depth "
            "and strong architectural lighting"
        ),
        "pattern": "radial",
        "energy": 0.8
    },

    "borussia dortmund": {
        "keywords": [
            "borussia dortmund",
            "dortmund"
        ],
        "primary": DORTMUND_YELLOW,
        "secondary": DORTMUND_BLACK,
        "accent": WHITE,
        "style": (
            "electric Dortmund yellow and black visual identity, "
            "energetic German football atmosphere and high-contrast "
            "broadcast lighting"
        ),
        "pattern": "blocks",
        "energy": 0.95
    },

    "juventus": {
        "keywords": [
            "juventus",
            "juventus fc"
        ],
        "primary": JUVENTUS_BLACK,
        "secondary": WHITE,
        "accent": GRAY,
        "style": (
            "minimalist Juventus black and white luxury football "
            "editorial design, clean premium geometry and dramatic shadows"
        ),
        "pattern": "minimal",
        "energy": 0.45
    },

    "inter milan": {
        "keywords": [
            "inter milan",
            "inter",
            "internazionale"
        ],
        "primary": INTER_BLUE,
        "secondary": INTER_BLACK,
        "accent": CITY_BLUE,
        "style": (
            "deep Inter blue and black cinematic football atmosphere, "
            "night stadium mood, modern Milanese football media design"
        ),
        "pattern": "stripes",
        "energy": 0.8
    },

    "ac milan": {
        "keywords": [
            "ac milan",
            "milan"
        ],
        "primary": MILAN_RED,
        "secondary": MILAN_BLACK,
        "accent": WHITE,
        "style": (
            "classic AC Milan red and black editorial lighting, "
            "premium Italian football atmosphere and dramatic contrast"
        ),
        "pattern": "stripes",
        "energy": 0.8
    },

    "psg": {
        "keywords": [
            "psg",
            "paris saint-germain"
        ],
        "primary": PSG_BLUE,
        "secondary": PSG_RED,
        "accent": WHITE,
        "style": (
            "dark Paris blue and vivid red luxury football media "
            "atmosphere, modern night city influence and elegant depth"
        ),
        "pattern": "luxury",
        "energy": 0.7
    },

    "newcastle united": {
        "keywords": [
            "newcastle united",
            "newcastle"
        ],
        "primary": NEWCASTLE_BLACK,
        "secondary": WHITE,
        "accent": GRAY,
        "style": (
            "black and white Newcastle editorial atmosphere, "
            "dark dramatic English football media style"
        ),
        "pattern": "stripes",
        "energy": 0.7
    }
}


# ============================================================
# NATIONAL TEAM IDENTITIES
# ============================================================

NATIONAL_IDENTITIES = {

    "france": {
        "keywords": [
            "france",
            "french national team"
        ],
        "primary": FRANCE_BLUE,
        "secondary": WHITE,
        "accent": RED,
        "style": (
            "French blue, white and red national-team editorial "
            "lighting with elegant European tournament atmosphere"
        ),
        "pattern": "tricolor",
        "energy": 0.65
    },

    "argentina": {
        "keywords": [
            "argentina",
            "argentina national team"
        ],
        "primary": ARGENTINA_BLUE,
        "secondary": WHITE,
        "accent": ARGENTINA_BLUE,
        "style": (
            "sky blue and white Argentina national-team "
            "atmosphere with elegant tournament lighting"
        ),
        "pattern": "horizontal",
        "energy": 0.65
    },

    "brazil": {
        "keywords": [
            "brazil",
            "brazil national team"
        ],
        "primary": BRAZIL_GREEN,
        "secondary": YELLOW,
        "accent": BLUE,
        "style": (
            "Brazilian green and yellow energetic football "
            "atmosphere with vivid tournament lighting"
        ),
        "pattern": "blocks",
        "energy": 0.9
    },

    "portugal": {
        "keywords": [
            "portugal",
            "portugal national team"
        ],
        "primary": PORTUGAL_RED,
        "secondary": GREEN,
        "accent": GOLD,
        "style": (
            "deep Portuguese red and green premium national-team "
            "media atmosphere with subtle gold highlights"
        ),
        "pattern": "diagonal",
        "energy": 0.75
    },

    "spain": {
        "keywords": [
            "spain",
            "spanish national team"
        ],
        "primary": SPAIN_RED,
        "secondary": YELLOW,
        "accent": BLACK,
        "style": (
            "Spain red and gold tournament atmosphere with "
            "clean dramatic editorial lighting"
        ),
        "pattern": "diagonal",
        "energy": 0.75
    },

    "italy": {
        "keywords": [
            "italy",
            "italian national team"
        ],
        "primary": ITALY_BLUE,
        "secondary": WHITE,
        "accent": GREEN,
        "style": (
            "deep Italian blue national-team atmosphere, "
            "premium tournament lighting and elegant depth"
        ),
        "pattern": "clean",
        "energy": 0.55
    },

    "germany": {
        "keywords": [
            "germany",
            "german national team"
        ],
        "primary": GERMANY_BLACK,
        "secondary": WHITE,
        "accent": RED,
        "style": (
            "black and white Germany national-team atmosphere "
            "with subtle red accents and modern tournament lighting"
        ),
        "pattern": "minimal",
        "energy": 0.6
    },

    "england": {
        "keywords": [
            "england",
            "england national team"
        ],
        "primary": ENGLAND_BLUE,
        "secondary": WHITE,
        "accent": RED,
        "style": (
            "royal blue and white English national-team atmosphere "
            "with refined tournament-style lighting"
        ),
        "pattern": "clean",
        "energy": 0.55
    },

    "netherlands": {
        "keywords": [
            "netherlands",
            "holland",
            "dutch national team"
        ],
        "primary": NETHERLANDS_ORANGE,
        "secondary": BLACK,
        "accent": WHITE,
        "style": (
            "vivid Dutch orange and black football atmosphere "
            "with energetic modern tournament lighting"
        ),
        "pattern": "blocks",
        "energy": 0.9
    }
}


# ============================================================
# FIND IDENTITY
# ============================================================

def find_team_identity(
    team_name
):

    normalized = normalize_team_name(
        team_name
    )

    if not normalized:
        return None

    if normalized in {
        "unknown",
        "none",
        "null"
    }:
        return None

    # Clubs first
    if normalized in TEAM_IDENTITIES:

        return TEAM_IDENTITIES[
            normalized
        ]

    # National teams
    if normalized in NATIONAL_IDENTITIES:

        return NATIONAL_IDENTITIES[
            normalized
        ]

    # Fallback keyword search
    for identity in TEAM_IDENTITIES.values():

        for keyword in identity["keywords"]:

            if keyword in normalized:

                return identity

    for identity in NATIONAL_IDENTITIES.values():

        for keyword in identity["keywords"]:

            if keyword in normalized:

                return identity

    return None


# ============================================================
# TEAM NAME DISPLAY
# ============================================================

def clean_display_team(
    team
):

    if not team:
        return ""

    value = clean_text(
        team
    )

    if value.lower() in {
        "unknown",
        "none",
        "null"
    }:
        return ""

    return value


# ============================================================
# TEXT WRAPPING
# ============================================================

def wrap_text(
    draw,
    text,
    font,
    max_width
):

    text = clean_text(
        text
    )

    if not text:
        return []

    words = text.split()

    lines = []

    current = ""

    for word in words:

        test = (
            current + " " + word
        ).strip()

        bbox = draw.textbbox(
            (0, 0),
            test,
            font=font
        )

        width = (
            bbox[2] - bbox[0]
        )

        if width <= max_width:

            current = test

        else:

            if current:

                lines.append(
                    current
                )

            current = word

    if current:
        lines.append(
            current
        )

    return lines


def draw_wrapped_text(
    draw,
    text,
    x,
    y,
    max_width,
    font,
    fill=WHITE,
    spacing=10,
    max_lines=None
):

    lines = wrap_text(
        draw,
        text,
        font,
        max_width
    )

    if max_lines:
        lines = lines[
            :max_lines
        ]

    current_y = y

    for line in lines:

        draw.text(
            (
                x,
                current_y
            ),
            line,
            font=font,
            fill=fill
        )

        bbox = draw.textbbox(
            (
                x,
                current_y
            ),
            line,
            font=font
        )

        current_y += (
            bbox[3] - bbox[1]
        ) + spacing

    return current_y


# ============================================================
# TEXT CENTERING
# ============================================================

def draw_centered_text(
    draw,
    text,
    center_x,
    y,
    font,
    fill=WHITE
):

    text = clean_text(
        text
    )

    if not text:
        return

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    width = (
        bbox[2] - bbox[0]
    )

    draw.text(
        (
            center_x - width // 2,
            y
        ),
        text,
        font=font,
        fill=fill
    )


# ============================================================
# GRADIENT BACKGROUND
# ============================================================

def create_gradient_background(
    identity_a=None,
    identity_b=None
):

    if identity_a:

        color_a = identity_a[
            "primary"
        ]

        color_a2 = identity_a[
            "secondary"
        ]

    else:

        color_a = BLACK
        color_a2 = DARK_BLUE

    if identity_b:

        color_b = identity_b[
            "primary"
        ]

        color_b2 = identity_b[
            "secondary"
        ]

    else:

        color_b = BLACK
        color_b2 = BLACK

    image = Image.new(
        "RGB",
        (
            WIDTH,
            HEIGHT
        )
    )

    pixels = image.load()

    center = WIDTH // 2

    for y in range(
        HEIGHT
    ):

        vertical_ratio = (
            y / HEIGHT
        )

        for x in range(
            WIDTH
        ):

            horizontal_ratio = (
                x / WIDTH
            )

            if x < center:

                blend = (
                    x / center
                )

                c1 = color_a
                c2 = color_a2

            else:

                blend = (
                    (x - center)
                    / center
                )

                c1 = color_b
                c2 = color_b2

            r = int(
                c1[0]
                * (1 - blend)
                + c2[0]
                * blend
            )

            g = int(
                c1[1]
                * (1 - blend)
                + c2[1]
                * blend
            )

            b = int(
                c1[2]
                * (1 - blend)
                + c2[2]
                * blend
            )

            darkness = (
                0.25
                + 0.75
                * vertical_ratio
            )

            pixels[x, y] = (
                int(r * darkness),
                int(g * darkness),
                int(b * darkness)
            )

    return image


# ============================================================
# LOCAL EDITORIAL BACKGROUND
# ============================================================

def create_local_background(
    design_type,
    team_a="UNKNOWN",
    team_b="UNKNOWN"
):

    identity_a = find_team_identity(
        team_a
    )

    identity_b = find_team_identity(
        team_b
    )

    image = create_gradient_background(
        identity_a,
        identity_b
    ).convert(
        "RGBA"
    )

    overlay = Image.new(
        "RGBA",
        (
            WIDTH,
            HEIGHT
        ),
        (
            0,
            0,
            0,
            0
        )
    )

    draw = ImageDraw.Draw(
        overlay
    )

    # --------------------------------------------------------
    # Dark cinematic layer
    # --------------------------------------------------------

    draw.rectangle(
        (
            0,
            0,
            WIDTH,
            HEIGHT
        ),
        fill=(
            0,
            0,
            0,
            90
        )
    )

    # --------------------------------------------------------
    # Design-specific geometry
    # --------------------------------------------------------

    design = str(
        design_type or "general"
    ).lower()

    if design == "match":

        draw.polygon(
            [
                (0, 0),
                (WIDTH // 2 - 40, 0),
                (WIDTH // 2 - 180, HEIGHT),
                (0, HEIGHT)
            ],
            fill=(
                identity_a["primary"]
                + (35,)
                if identity_a
                else (50, 50, 50, 35)
            )
        )

        draw.polygon(
            [
                (WIDTH, 0),
                (WIDTH // 2 + 40, 0),
                (WIDTH // 2 + 180, HEIGHT),
                (WIDTH, HEIGHT)
            ],
            fill=(
                identity_b["primary"]
                + (35,)
                if identity_b
                else (50, 50, 50, 35)
            )
        )

        draw.line(
            (
                WIDTH // 2,
                0,
                WIDTH // 2,
                HEIGHT
            ),
            fill=WHITE + (20,),
            width=3
        )

    elif design == "transfer":

        for i in range(
            6
        ):

            x = (
                100
                + i * 190
            )

            draw.line(
                (
                    x,
                    HEIGHT,
                    x + 260,
                    0
                ),
                fill=(
                    identity_a["accent"]
                    + (28,)
                    if identity_a
                    else YELLOW + (20,)
                ),
                width=8
            )

    elif design == "injury":

        for i in range(
            5
        ):

            margin = (
                100 + i * 185
            )

            draw.arc(
                (
                    margin,
                    120,
                    margin + 260,
                    380
                ),
                start=180,
                end=360,
                fill=(
                    RED + (30,)
                ),
                width=6
            )

    elif design == "trophy":

        draw.ellipse(
            (
                290,
                110,
                790,
                610
            ),
            outline=(
                GOLD + (35,)
            ),
            width=6
        )

        draw.ellipse(
            (
                370,
                190,
                710,
                530
            ),
            outline=(
                GOLD + (20,)
            ),
            width=3
        )

    elif design == "lineup":

        # Pitch-inspired lines, but subtle.
        draw.rounded_rectangle(
            (
                90,
                220,
                990,
                880
            ),
            radius=50,
            outline=(
                WHITE + (25,)
            ),
            width=4
        )

        draw.line(
            (
                WIDTH // 2,
                220,
                WIDTH // 2,
                880
            ),
            fill=(
                WHITE + (18,)
            ),
            width=3
        )

        draw.ellipse(
            (
                465,
                455,
                615,
                605
            ),
            outline=(
                WHITE + (18,)
            ),
            width=3
        )

    elif design == "announcement":

        draw.rectangle(
            (
                75,
                180,
                1005,
                900
            ),
            outline=(
                WHITE + (25,)
            ),
            width=5
        )

        draw.rectangle(
            (
                120,
                225,
                960,
                855
            ),
            outline=(
                (
                    identity_a["accent"]
                    if identity_a
                    else YELLOW
                )
                + (20,)
            ),
            width=2
        )

    elif design == "breaking":

        draw.polygon(
            [
                (0, 220),
                (WIDTH, 0),
                (WIDTH, 130),
                (0, 350)
            ],
            fill=(
                RED + (40,)
            )
        )

        draw.polygon(
            [
                (0, HEIGHT - 250),
                (WIDTH, HEIGHT - 520),
                (WIDTH, HEIGHT - 380),
                (0, HEIGHT - 110)
            ],
            fill=(
                BRIGHT_RED + (25,)
            )
        )

    elif design == "quote":

        draw.line(
            (
                120,
                220,
                960,
                220
            ),
            fill=(
                WHITE + (20,)
            ),
            width=2
        )

        draw.line(
            (
                180,
                850,
                900,
                850
            ),
            fill=(
                WHITE + (15,)
            ),
            width=2
        )

    elif design == "player":

        draw.ellipse(
            (
                240,
                100,
                840,
                700
            ),
            outline=(
                (
                    identity_a["accent"]
                    if identity_a
                    else WHITE
                )
                + (20,)
            ),
            width=5
        )

    else:

        draw.polygon(
            [
                (0, 0),
                (330, 0),
                (0, 360)
            ],
            fill=(
                (
                    identity_a["accent"]
                    if identity_a
                    else RED
                )
                + (35,)
            )
        )

        draw.polygon(
            [
                (WIDTH, HEIGHT),
                (WIDTH - 330, HEIGHT),
                (WIDTH, HEIGHT - 360)
            ],
            fill=(
                (
                    identity_a["secondary"]
                    if identity_a
                    else YELLOW
                )
                + (30,)
            )
        )

    overlay = overlay.filter(
        ImageFilter.GaussianBlur(
            radius=8
        )
    )

    image = Image.alpha_composite(
        image,
        overlay
    )

    # --------------------------------------------------------
    # Vignette
    # --------------------------------------------------------

    vignette = Image.new(
        "RGBA",
        (
            WIDTH,
            HEIGHT
        ),
        (
            0,
            0,
            0,
            0
        )
    )

    vd = ImageDraw.Draw(
        vignette
    )

    steps = 80

    for i in range(
        steps
    ):

        alpha = int(
            2.2 * i
        )

        vd.rectangle(
            (
                i,
                i,
                WIDTH - i,
                HEIGHT - i
            ),
            outline=(
                0,
                0,
                0,
                alpha
            ),
            width=3
        )

    return Image.alpha_composite(
        image,
        vignette
    )


# ============================================================
# BUILD POLLINATIONS PROMPT
# ============================================================

def build_prompt(
    headline,
    design_type,
    team_a="UNKNOWN",
    team_b="UNKNOWN"
):

    identity_a = find_team_identity(
        team_a
    )

    identity_b = find_team_identity(
        team_b
    )

    design_type = (
        str(
            design_type or "general"
        )
        .lower()
        .strip()
    )

    context = clean_text(
        headline
    )

    if len(context) > 260:

        context = context[:260]

    team_a_style = ""

    team_b_style = ""

    if identity_a:

        team_a_style = f"""
Primary team visual identity:

{identity_a["style"]}

Primary colors:
{identity_a["primary"]}

Secondary colors:
{identity_a["secondary"]}

Accent:
{identity_a["accent"]}
"""

    if identity_b:

        team_b_style = f"""
Secondary team visual identity:

{identity_b["style"]}

Secondary colors:
{identity_b["primary"]}

Secondary accent:
{identity_b["accent"]}
"""

    design_prompts = {

        "match": """
Professional football match editorial background.
Strong split composition.
Left side for the first team.
Right side for the second team.
Strong central tension.
Premium European football broadcast aesthetic.
Avoid generic repetitive stadium wallpaper.
""",

        "transfer": """
Premium transfer-news editorial background.
Dynamic directional motion.
Luxury sports journalism aesthetic.
Visual suggestion of movement and negotiation.
Avoid generic football pitch.
""",

        "injury": """
Serious football injury editorial background.
Controlled dramatic lighting.
Dark premium atmosphere.
Subtle sense of tension.
Avoid medical clichés and generic football wallpaper.
""",

        "trophy": """
Luxury football achievement editorial background.
Elegant gold highlights.
Celebration atmosphere.
Premium tournament aesthetic.
Avoid cheesy trophy wallpaper.
""",

        "lineup": """
Professional starting-lineup editorial background.
Tactical visual language.
Clean pitch geometry.
Modern sports broadcast aesthetic.
Avoid clutter.
""",

        "announcement": """
Premium official football announcement background.
Clean formal composition.
Strong centered architecture.
Luxury sports-media appearance.
""",

        "breaking": """
Urgent breaking football-news editorial background.
Strong directional lighting.
Dynamic diagonals.
High-end sports newsroom atmosphere.
""",

        "quote": """
Premium football quote editorial background.
Elegant cinematic atmosphere.
Large clean negative space.
Editorial magazine aesthetic.
""",

        "player": """
Premium football player editorial background.
Strong focal composition.
Dramatic lighting.
Professional football magazine atmosphere.
Do not generate a recognizable real player.
""",

        "general": """
Premium professional football editorial background.
Modern sports journalism.
Sophisticated cinematic depth.
Do not use a generic football pitch wallpaper.
"""
    }

    design_prompt = design_prompts.get(
        design_type,
        design_prompts["general"]
    )

    return f"""
Create an ORIGINAL premium football-media background
for Shingal Sport.

Design type:
{design_type}

{design_prompt}

{team_a_style}

{team_b_style}

Canvas:
1080x1080 square.

News context:
{context}

The news context is only for visual understanding.

Never render the news context as text.

DO NOT generate:
- readable text
- letters
- words
- numbers
- headlines
- fake logos
- fake badges
- fake player faces
- watermarks
- UI panels
- scoreboards
- arrows
- random symbols

Do not copy any specific existing media company.

Create a sophisticated original editorial composition.

Use:
cinematic depth,
controlled color grading,
premium lighting,
subtle architectural football references,
strong negative space,
modern geometric structure,
professional broadcast composition.

The image must look like
a professional football media design background,
not an AI wallpaper.
"""


# ============================================================
# POLLINATIONS GENERATION
# ============================================================

def generate_background(
    headline,
    design_type,
    team_a="UNKNOWN",
    team_b="UNKNOWN"
):

    prompt = build_prompt(
        headline,
        design_type,
        team_a,
        team_b
    )

    encoded_prompt = quote(
        prompt,
        safe=""
    )

    url = (
        POLLINATIONS_URL
        + encoded_prompt
    )

    print()
    print(
        "🎨 Pollinations image generation started..."
    )

    for attempt in range(
        1,
        POLLINATIONS_RETRIES + 1
    ):

        try:

            print(
                f"Attempt {attempt}/"
                f"{POLLINATIONS_RETRIES}"
            )

            response = requests.get(
                url,
                params={
                    "width": WIDTH,
                    "height": HEIGHT,
                    "nologo": "true"
                },
                timeout=POLLINATIONS_TIMEOUT
            )

            print(
                "HTTP status:",
                response.status_code
            )

            response.raise_for_status()

            if not response.content:

                raise ValueError(
                    "Empty Pollinations response."
                )

            image = Image.open(
                io.BytesIO(
                    response.content
                )
            ).convert(
                "RGB"
            )

            image = image.resize(
                (
                    WIDTH,
                    HEIGHT
                ),
                Image.Resampling.LANCZOS
            )

            print(
                "✅ Pollinations background received."
            )

            return image

        except Exception as error:

            print(
                f"⚠️ Pollinations attempt "
                f"{attempt} failed:"
            )

            print(
                error
            )

            if attempt < POLLINATIONS_RETRIES:

                time.sleep(
                    3 * attempt
                )

    print()
    print(
        "⚠️ Pollinations unavailable."
    )

    print(
        "✅ Using local editorial fallback background."
    )

    return create_local_background(
        design_type,
        team_a,
        team_b
    ).convert(
        "RGB"
    )


# ============================================================
# BRANDING
# ============================================================

def add_branding(
    image
):

    draw = ImageDraw.Draw(
        image
    )

    # Small top-left brand
    draw.text(
        (
            55,
            42
        ),
        "Shingal Sport",
        font=get_font(
            29
        ),
        fill=WHITE
    )

    # Small accent line
    draw.rectangle(
        (
            55,
            80,
            155,
            84
        ),
        fill=RED
    )


# ============================================================
# CATEGORY LABEL
# ============================================================

def add_category(
    image,
    category
):

    draw = ImageDraw.Draw(
        image
    )

    labels = {
        "breaking": "BREAKING",
        "transfer": "TRANSFER",
        "match": "MATCH",
        "quote": "QUOTE",
        "injury": "INJURY",
        "trophy": "ACHIEVEMENT",
        "player": "PLAYER",
        "lineup": "STARTING XI",
        "announcement": "OFFICIAL",
        "general": "FOOTBALL"
    }

    label = labels.get(
        str(category).lower(),
        "FOOTBALL"
    )

    font = get_font(
        31
    )

    # Accent bar
    draw.rectangle(
        (
            55,
            105,
            118,
            113
        ),
        fill=YELLOW
    )

    draw.rectangle(
        (
            128,
            105,
            255,
            113
        ),
        fill=RED
    )

    draw.text(
        (
            55,
            132
        ),
        label,
        font=font,
        fill=WHITE
    )


# ============================================================
# TEAM ACCENT
# ============================================================

def add_team_accent(
    image,
    team_a="UNKNOWN",
    team_b="UNKNOWN"
):

    identity_a = find_team_identity(
        team_a
    )

    identity_b = find_team_identity(
        team_b
    )

    draw = ImageDraw.Draw(
        image
    )

    if identity_a and identity_b:

        draw.rectangle(
            (
                0,
                0,
                WIDTH // 2,
                12
            ),
            fill=identity_a[
                "primary"
            ]
        )

        draw.rectangle(
            (
                WIDTH // 2,
                0,
                WIDTH,
                12
            ),
            fill=identity_b[
                "primary"
            ]
        )

    elif identity_a:

        draw.rectangle(
            (
                0,
                0,
                WIDTH,
                12
            ),
            fill=identity_a[
                "primary"
            ]
        )

    elif identity_b:

        draw.rectangle(
            (
                0,
                0,
                WIDTH,
                12
            ),
            fill=identity_b[
                "primary"
            ]
        )


# ============================================================
# BOTTOM BRAND BAR
# ============================================================

def add_bottom_bar(
    image,
    accent=RED
):

    draw = ImageDraw.Draw(
        image
    )

    draw.rectangle(
        (
            55,
            1000,
            1025,
            1007
        ),
        fill=accent
    )

    draw.rectangle(
        (
            55,
            1010,
            280,
            1015
        ),
        fill=YELLOW
    )


# ============================================================
# LOGO PREPARATION
# ============================================================

def prepare_logo(
    logo_path,
    max_width=190,
    max_height=190
):

    if not logo_path:
        return None

    if not os.path.isfile(
        logo_path
    ):

        print(
            "⚠️ Logo not found:",
            logo_path
        )

        return None

    try:

        logo = Image.open(
            logo_path
        ).convert(
            "RGBA"
        )

        logo.thumbnail(
            (
                max_width,
                max_height
            ),
            Image.Resampling.LANCZOS
        )

        return logo

    except Exception as error:

        print(
            "⚠️ Could not prepare logo:",
            error
        )

        return None


# ============================================================
# LOGO GLOW
# ============================================================

def paste_logo_with_glow(
    image,
    logo,
    center_x,
    center_y,
    glow_color,
    glow_radius=28
):

    if logo is None:
        return

    glow = Image.new(
        "RGBA",
        image.size,
        (
            0,
            0,
            0,
            0
        )
    )

    alpha = logo.getchannel(
        "A"
    )

    colored = Image.new(
        "RGBA",
        logo.size,
        glow_color + (0,)
    )

    colored.putalpha(
        alpha
    )

    glow.paste(
        colored,
        (
            center_x
            - logo.width // 2,
            center_y
            - logo.height // 2
        )
    )

    glow = glow.filter(
        ImageFilter.GaussianBlur(
            glow_radius
        )
    )

    image.alpha_composite(
        glow
    )

    image.alpha_composite(
        logo,
        (
            center_x
            - logo.width // 2,
            center_y
            - logo.height // 2
        )
    )


# ============================================================
# DRAW GENERAL EDITORIAL
# ============================================================

def draw_editorial_design(
    image,
    headline,
    category,
    primary_team,
    secondary_team=None,
    primary_logo=None,
    secondary_logo=None
):

    identity_a = find_team_identity(
        primary_team
    )

    identity_b = find_team_identity(
        secondary_team
    )

    draw = ImageDraw.Draw(
        image
    )

    # --------------------------------------------------------
    # Branding
    # --------------------------------------------------------

    add_branding(
        image
    )

    add_category(
        image,
        category
    )

    add_team_accent(
        image,
        primary_team,
        secondary_team or "UNKNOWN"
    )

    # --------------------------------------------------------
    # Top visual subject
    # --------------------------------------------------------

    if identity_a:

        accent = identity_a[
            "accent"
        ]

    else:

        accent = YELLOW

    # Soft ring
    draw.ellipse(
        (
            695,
            140,
            1010,
            455
        ),
        outline=(
            accent + (45,)
        ),
        width=4
    )

    # --------------------------------------------------------
    # Primary logo
    # --------------------------------------------------------

    if primary_logo:

        paste_logo_with_glow(
            image,
            primary_logo,
            850,
            295,
            accent
        )

    # Secondary logo for special designs
    if secondary_logo:

        second_accent = (
            identity_b["accent"]
            if identity_b
            else WHITE
        )

        paste_logo_with_glow(
            image,
            secondary_logo,
            235,
            295,
            second_accent
        )

    # --------------------------------------------------------
    # Headline box
    # --------------------------------------------------------

    # Shadow layer
    shadow = Image.new(
        "RGBA",
        image.size,
        (
            0,
            0,
            0,
            0
        )
    )

    shadow_draw = ImageDraw.Draw(
        shadow
    )

    shadow_draw.rounded_rectangle(
        (
            45,
            570,
            1035,
            935
        ),
        radius=28,
        fill=(
            0,
            0,
            0,
            145
        )
    )

    shadow = shadow.filter(
        ImageFilter.GaussianBlur(
            16
        )
    )

    image.alpha_composite(
        shadow
    )

    draw = ImageDraw.Draw(
        image
    )

    # Accent vertical line
    draw.rectangle(
        (
            65,
            605,
            76,
            855
        ),
        fill=accent
    )

    # Headline
    draw_wrapped_text(
        draw,
        headline,
        105,
        600,
        850,
        get_font(
            54
        ),
        WHITE,
        spacing=12,
        max_lines=5
    )

    add_bottom_bar(
        image,
        accent
    )

    return image


# ============================================================
# DRAW MATCH DESIGN
# ============================================================

def draw_match_design(
    image,
    headline,
    team_a,
    team_b,
    team_a_logo,
    team_b_logo
):

    identity_a = find_team_identity(
        team_a
    )

    identity_b = find_team_identity(
        team_b
    )

    draw = ImageDraw.Draw(
        image
    )

    add_branding(
        image
    )

    add_category(
        image,
        "match"
    )

    add_team_accent(
        image,
        team_a,
        team_b
    )

    left_x = 275
    right_x = 805
    logo_y = 340

    # --------------------------------------------------------
    # Team circles
    # --------------------------------------------------------

    color_a = (
        identity_a["accent"]
        if identity_a
        else YELLOW
    )

    color_b = (
        identity_b["accent"]
        if identity_b
        else WHITE
    )

    draw.ellipse(
        (
            left_x - 150,
            logo_y - 150,
            left_x + 150,
            logo_y + 150
        ),
        outline=color_a,
        width=5
    )

    draw.ellipse(
        (
            right_x - 150,
            logo_y - 150,
            right_x + 150,
            logo_y + 150
        ),
        outline=color_b,
        width=5
    )

    # --------------------------------------------------------
    # Logos
    # --------------------------------------------------------

    logo_a = prepare_logo(
        team_a_logo,
        205,
        205
    )

    logo_b = prepare_logo(
        team_b_logo,
        205,
        205
    )

    if logo_a:

        paste_logo_with_glow(
            image,
            logo_a,
            left_x,
            logo_y,
            color_a
        )

    if logo_b:

        paste_logo_with_glow(
            image,
            logo_b,
            right_x,
            logo_y,
            color_b
        )

    # --------------------------------------------------------
    # VS
    # --------------------------------------------------------

    vs_font = get_font(
        74
    )

    draw_centered_text(
        draw,
        "VS",
        WIDTH // 2,
        310,
        vs_font,
        YELLOW
    )

    # --------------------------------------------------------
    # Team names
    # --------------------------------------------------------

    name_font = get_font(
        32
    )

    display_a = clean_display_team(
        team_a
    )

    display_b = clean_display_team(
        team_b
    )

    draw_centered_text(
        draw,
        display_a,
        left_x,
        515,
        name_font,
        WHITE
    )

    draw_centered_text(
        draw,
        display_b,
        right_x,
        515,
        name_font,
        WHITE
    )

    # --------------------------------------------------------
    # Headline panel
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (
            55,
            620,
            1025,
            925
        ),
        radius=28,
        fill=(
            0,
            0,
            0,
            155
        )
    )

    # Recreate draw after RGBA modifications
    draw = ImageDraw.Draw(
        image
    )

    accent = (
        identity_a["accent"]
        if identity_a
        else YELLOW
    )

    draw.rectangle(
        (
            75,
            650,
            86,
            860
        ),
        fill=accent
    )

    draw_wrapped_text(
        draw,
        headline,
        115,
        645,
        865,
        get_font(
            48
        ),
        WHITE,
        spacing=10,
        max_lines=4
    )

    add_bottom_bar(
        image,
        accent
    )

    return image


# ============================================================
# MAIN IMAGE GENERATOR
# ============================================================

def generate_image(
    headline,
    design_type="general",
    player_image=None,
    output_path="football_post.jpg",
    team_a="UNKNOWN",
    team_b="UNKNOWN",
    team_a_logo=None,
    team_b_logo=None,
    visual_type=None,
    visual_subject=None
):

    design_type = (
        str(
            design_type or "general"
        )
        .lower()
        .strip()
    )

    team_a = (
        team_a
        if team_a
        else "UNKNOWN"
    )

    team_b = (
        team_b
        if team_b
        else "UNKNOWN"
    )

    # --------------------------------------------------------
    # Correct visual design type
    # --------------------------------------------------------

    if visual_type:

        normalized_visual = str(
            visual_type
        ).lower().strip()

        visual_to_category = {
            "club_match": "match",
            "national_match": "match",
            "club": "general",
            "national_team": "general",
            "player": "player",
            "transfer": "transfer",
            "injury": "injury",
            "trophy": "trophy",
            "lineup": "lineup",
            "announcement": "announcement",
            "breaking": "breaking",
            "quote": "quote",
            "match": "match",
            "generic": "general"
        }

        if normalized_visual in visual_to_category:

            design_type = visual_to_category[
                normalized_visual
            ]

    print()
    print(
        "===================================="
    )

    print(
        "🎨 SHINGAL SPORT IMAGE GENERATOR"
    )

    print(
        "===================================="
    )

    print(
        "Design:",
        design_type
    )

    print(
        "Team A:",
        team_a
    )

    print(
        "Team B:",
        team_b
    )

    if visual_type:

        print(
            "Visual type:",
            visual_type
        )

    if visual_subject:

        print(
            "Visual subject:",
            visual_subject
        )

    # --------------------------------------------------------
    # Generate background
    # --------------------------------------------------------

    image = generate_background(
        headline,
        design_type,
        team_a,
        team_b
    )

    image = image.convert(
        "RGBA"
    )

    # --------------------------------------------------------
    # Identity-based enhancement
    # --------------------------------------------------------

    identity_a = find_team_identity(
        team_a
    )

    identity_b = find_team_identity(
        team_b
    )

    if identity_a:

        print(
            "✅ Primary identity detected."
        )

    if identity_b:

        print(
            "✅ Secondary identity detected."
        )

    # --------------------------------------------------------
    # Add final editorial design
    # --------------------------------------------------------

    if design_type == "match":

        image = draw_match_design(
            image,
            headline,
            team_a,
            team_b,
            team_a_logo,
            team_b_logo
        )

    else:

        image = draw_editorial_design(
            image,
            headline,
            design_type,
            team_a,
            team_b,
            team_a_logo,
            team_b_logo
        )

    # --------------------------------------------------------
    # Final enhancement
    # --------------------------------------------------------

    image = ImageEnhance.Contrast(
        image
    ).enhance(
        1.08
    )

    image = ImageEnhance.Color(
        image
    ).enhance(
        1.08
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    directory = os.path.dirname(
        output_path
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    image = image.convert(
        "RGB"
    )

    image.save(
        output_path,
        "JPEG",
        quality=95,
        optimize=True
    )

    # --------------------------------------------------------
    # Verify file
    # --------------------------------------------------------

    if not os.path.isfile(
        output_path
    ):

        raise RuntimeError(
            "Final image was not created."
        )

    file_size = os.path.getsize(
        output_path
    )

    if file_size < 10_000:

        raise RuntimeError(
            f"Final image is too small: "
            f"{file_size} bytes"
        )

    print()
    print(
        "✅ Final image created:"
    )

    print(
        output_path
    )

    print(
        "Image size:",
        file_size,
        "bytes"
    )

    print(
        "===================================="
    )

    return output_path


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    os.makedirs(
        "generated_images",
        exist_ok=True
    )

    test_cases = [

        {
            "name": "real_madrid",
            "headline": (
                "Real Madrid are preparing "
                "for another major European challenge"
            ),
            "design": "general",
            "team_a": "Real Madrid"
        },

        {
            "name": "barcelona_transfer",
            "headline": (
                "Barcelona are monitoring "
                "a new midfielder"
            ),
            "design": "transfer",
            "team_a": "Barcelona"
        },

        {
            "name": "el_clasico",
            "headline": (
                "Real Madrid will face Barcelona "
                "in a huge La Liga clash"
            ),
            "design": "match",
            "team_a": "Real Madrid",
            "team_b": "Barcelona"
        },

        {
            "name": "spain",
            "headline": (
                "Spain will face Germany "
                "in a major international match"
            ),
            "design": "match",
            "team_a": "Spain",
            "team_b": "Germany"
        }
    ]

    for test in test_cases:

        print()
        print(
            "===================================="
        )

        print(
            "TEST:",
            test["name"]
        )

        print(
            "===================================="
        )

        output = os.path.join(
            "generated_images",
            f"test_{test['name']}.jpg"
        )

        try:

            generate_image(
                headline=test["headline"],
                design_type=test["design"],
                team_a=test.get(
                    "team_a",
                    "UNKNOWN"
                ),
                team_b=test.get(
                    "team_b",
                    "UNKNOWN"
                ),
                output_path=output
            )

            print(
                "✅ Test successful."
            )

        except Exception as error:

            print(
                "❌ TEST FAILED:"
            )

            print(
                error
            )

    print()
    print(
        "===================================="
    )

    print(
        "IMAGE GENERATOR TESTS FINISHED"
    )

    print(
        "===================================="
    )