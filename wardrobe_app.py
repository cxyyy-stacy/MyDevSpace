
import streamlit as st
import json
import os
import base64
import requests
from itertools import product

# -------------------- Page setup --------------------
st.set_page_config(
    page_title="WARDROBE | Your Digital Closet",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_FILE = "wardrobe_data.json"

# -------------------- Premium minimalist styling --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #F7F5F0;
    color: #24231F;
}

[data-testid="stSidebar"] {
    background: #EEEAE1;
    border-right: 1px solid #DED9CE;
}

[data-testid="stSidebar"] * {
    color: #292720;
}

.hero {
    background: #E9E3D8;
    padding: 42px 38px;
    border-radius: 18px;
    margin-bottom: 28px;
}

.hero-label {
    font-size: 11px;
    letter-spacing: 4px;
    color: #817866;
    font-weight: 700;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(36px, 5vw, 58px);
    line-height: 1.1;
    margin: 15px 0 12px 0;
    color: #27251F;
}

.hero-subtitle {
    color: #777164;
    font-size: 14px;
}

.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 30px;
    color: #292720;
    margin: 12px 0 5px 0;
}

.muted {
    color: #8A8478;
    font-size: 13px;
}

.stat-card {
    background: #FFFFFF;
    border: 1px solid #E9E5DC;
    border-radius: 14px;
    padding: 20px;
    min-height: 110px;
}

.stat-number {
    font-family: 'Playfair Display', serif;
    font-size: 32px;
    color: #292720;
}

.stat-label {
    color: #898274;
    font-size: 12px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.clothing-card {
    background: #FFFFFF;
    border: 1px solid #E9E5DC;
    border-radius: 14px;
    padding: 13px;
    margin-bottom: 12px;
}

.tag {
    display: inline-block;
    background: #EEEAE1;
    color: #625B4F;
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 11px;
    margin: 3px 3px 3px 0;
}

div.stButton > button {
    background: #292720;
    color: #FFFFFF;
    border: 1px solid #292720;
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: 600;
    transition: 0.2s;
}

div.stButton > button:hover {
    background: #575044;
    color: #FFFFFF;
    border-color: #575044;
}

.stTextInput input, .stSelectbox div[data-baseweb="select"] {
    background: #FFFFFF;
    border-radius: 8px;
}

hr {
    border-color: #E4DFD5;
}

footer {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# -------------------- Data --------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []
    except (json.JSONDecodeError, OSError):
        return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


wardrobe = load_data()

# -------------------- Color matching --------------------
COLOR_GROUPS = {
    "neutral": ["black", "white", "grey", "gray", "beige", "cream",
                "brown", "navy", "ivory", "米色", "白色", "黑色", "灰色",
                "棕色", "藏青", "奶油色"],
    "warm": ["red", "orange", "yellow", "pink", "coral",
             "红色", "橙色", "黄色", "粉色", "珊瑚色"],
    "cool": ["blue", "green", "purple", "teal",
             "蓝色", "绿色", "紫色", "青色"]
}


def get_color_group(color):
    color = str(color).lower().strip()

    for group, colors in COLOR_GROUPS.items():
        if any(item in color for item in colors):
            return group

    return "other"


def color_score(color1, color2):
    group1 = get_color_group(color1)
    group2 = get_color_group(color2)

    if group1 == "neutral" or group2 == "neutral":
        return 95

    if group1 == group2:
        return 82

    if "other" in [group1, group2]:
        return 65

    return 88


# -------------------- Weather --------------------
def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "weather_code",
            "wind_speed_10m"
        ]
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json().get("current")
    except requests.RequestException:
        return None


def get_city_name(latitude, longitude):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": latitude,
        "lon": longitude,
        "format": "json"
    }
    headers = {"User-Agent": "SmartWardrobeApp/5.0"}

    try:
        response = requests.get(
            url, params=params, headers=headers, timeout=10
        )
        response.raise_for_status()
        address = response.json().get("address", {})
        return (
            address.get("city")
            or address.get("town")
            or address.get("county")
            or address.get("state")
            or "Your location"
        )
    except requests.RequestException:
        return "Your location"


def find_city(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get("results", [])

        if results:
            return results[0]

        return None
    except requests.RequestException:
        return None


def weather_description(code):
    descriptions = {
        0: "Clear sky ☀️",
        1: "Mainly clear 🌤️",
        2: "Partly cloudy ⛅",
        3: "Overcast ☁️",
        45: "Foggy 🌫️",
        48: "Foggy 🌫️",
        51: "Light drizzle 🌦️",
        53: "Drizzle 🌦️",
        55: "Heavy drizzle 🌧️",
        61: "Light rain 🌧️",
        63: "Rain 🌧️",
        65: "Heavy rain 🌧️",
        71: "Light snow ❄️",
        73: "Snow ❄️",
        75: "Heavy snow ❄️",
        80: "Rain showers 🌦️",
        81: "Rain showers 🌧️",
        82: "Heavy showers 🌧️",
        95: "Thunderstorm ⛈️",
        96: "Thunderstorm ⛈️",
        99: "Thunderstorm ⛈️"
    }
    return descriptions.get(code, "Weather information available")


def warmth_for_temperature(temp):
    if temp < 10:
        return "Warm"
    elif temp < 20:
        return "Medium"
    return "Light"


# -------------------- Reusable UI --------------------
def page_heading(title, subtitle):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="muted">{subtitle}</div>', unsafe_allow_html=True)
    st.write("")


def show_clothing_image(item, height=220):
    image_data = item.get("image")
    if image_data:
        try:
            image_bytes = base64.b64decode(image_data)
            st.image(image_bytes, use_container_width=True)
        except Exception:
            st.markdown("🧥")
    else:
        st.markdown(
            '<div style="background:#EEEAE1;border-radius:10px;'
            'height:160px;display:flex;align-items:center;'
            'justify-content:center;font-size:48px;">👕</div>',
            unsafe_allow_html=True
        )


# -------------------- Sidebar --------------------
with st.sidebar:
    st.markdown(
        '<div style="font-family:Playfair Display,serif;'
        'font-size:27px;font-weight:600;letter-spacing:1px;">WARDROBE.</div>',
        unsafe_allow_html=True
    )
    st.caption("YOUR PERSONAL STYLE SPACE")
    st.divider()

    page = st.radio(
        "MENU",
        [
            "Overview",
            "My Wardrobe",
            "Add Clothing",
            "Smart Outfit",
            "Weather & Location"
        ],
        label_visibility="visible"
    )

    st.divider()
    st.markdown("**YOUR DIGITAL CLOSET**")
    st.caption(f"{len(wardrobe)} pieces in your collection")
    st.caption("EST. 2026")


# -------------------- Overview --------------------
if page == "Overview":
    st.markdown("""
    <div class="hero">
        <div class="hero-label">YOUR PERSONAL DIGITAL CLOSET</div>
        <div class="hero-title">Dress well.<br>Feel yourself.</div>
        <div class="hero-subtitle">
            A little organization. A little inspiration.<br>
            A better way to discover your personal style.
        </div>
    </div>
    """, unsafe_allow_html=True)

    clothing_count = len(wardrobe)
    categories = set(
        str(item.get("type", "Other")).title()
        for item in wardrobe
    )
    colors = set(
        str(item.get("color", "Unknown")).title()
        for item in wardrobe
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f'<div class="stat-card"><div class="stat-number">{clothing_count}</div>'
            '<div class="stat-label">Total Pieces</div></div>',
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f'<div class="stat-card"><div class="stat-number">{len(categories)}</div>'
            '<div class="stat-label">Categories</div></div>',
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f'<div class="stat-card"><div class="stat-number">{len(colors)}</div>'
            '<div class="stat-label">Colors</div></div>',
            unsafe_allow_html=True
        )

    st.write("")
    st.markdown('<div class="section-title">A wardrobe made yours.</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="muted">Manage your pieces, explore combinations, '
        'and find something lovely to wear.</div>',
        unsafe_allow_html=True
    )

    st.write("")
    a, b = st.columns(2)

    with a:
        st.markdown("#### ✦ Organize your style")
        st.write("Keep all your clothing pieces in one beautiful digital space.")

    with b:
        st.markdown("#### ✦ Discover new outfits")
        st.write("Find color combinations and get weather-aware suggestions.")

    st.write("")
    if wardrobe:
        st.markdown("#### Recently added")
        recent = wardrobe[-3:][::-1]
        cols = st.columns(3)

        for i, item in enumerate(recent):
            with cols[i]:
                show_clothing_image(item)
                st.markdown(f"**{item.get('name', 'Untitled')}**")
                st.caption(
                    f"{item.get('type', 'Other')} · {item.get('color', 'Unknown')}"
                )
    else:
        st.info("Your wardrobe is waiting. Add your first clothing piece!")


# -------------------- My Wardrobe --------------------
elif page == "My Wardrobe":
    page_heading("My Wardrobe", "Every piece has a place. Explore your collection.")

    if not wardrobe:
        st.info("Your wardrobe is empty. Go to Add Clothing to get started.")
    else:
        all_types = sorted(set(
            str(item.get("type", "Other")).title()
            for item in wardrobe
        ))

        selected_type = st.selectbox(
            "Filter by category",
            ["All"] + all_types
        )

        filtered = [
            item for item in wardrobe
            if selected_type == "All"
            or str(item.get("type", "Other")).title() == selected_type
        ]

        st.caption(f"SHOWING {len(filtered)} PIECES")
        cols = st.columns(3)

        for index, item in enumerate(filtered):
            with cols[index % 3]:
                with st.container(border=True):
                    show_clothing_image(item)

                    st.markdown(f"**{item.get('name', 'Untitled')}**")
                    st.caption(
                        f"{item.get('type', 'Other')} · "
                        f"{item.get('color', 'Unknown')}"
                    )

                    warmth = item.get("warmth", "Medium")
                    st.markdown(
                        f'<span class="tag">{warmth}</span>',
                        unsafe_allow_html=True
                    )

                    original_index = wardrobe.index(item)

                    if st.button(
                        "Remove piece",
                        key=f"delete_{original_index}",
                        use_container_width=True
                    ):
                        wardrobe.pop(original_index)
                        save_data(wardrobe)
                        st.rerun()


# -------------------- Add Clothing --------------------
elif page == "Add Clothing":
    page_heading("Add a New Piece", "Give your clothing a place in your digital closet.")

    with st.container(border=True):
        uploaded_file = st.file_uploader(
            "Upload a clothing photo",
            type=["jpg", "jpeg", "png"]
        )

        if uploaded_file:
            st.image(uploaded_file, width=220)

        st.divider()

        name = st.text_input("Clothing name", placeholder="e.g. White cotton shirt")

        col1, col2 = st.columns(2)

        with col1:
            clothing_type = st.selectbox(
                "Category",
                ["Top", "Bottom", "Shoes", "Outerwear", "Dress", "Bag", "Accessory", "Other"]
            )

        with col2:
            color = st.text_input("Main color", placeholder="e.g. Beige")

        warmth = st.selectbox(
            "Warmth level",
            ["Light", "Medium", "Warm"],
            index=1
        )

        st.write("")

        if st.button("＋  Add to My Wardrobe", use_container_width=True):
            if not name.strip() or not color.strip():
                st.warning("Please enter both a clothing name and a color.")
            else:
                image_data = None

                if uploaded_file:
                    image_data = base64.b64encode(
                        uploaded_file.getvalue()
                    ).decode("utf-8")

                new_item = {
                    "name": name.strip(),
                    "type": clothing_type,
                    "color": color.strip(),
                    "warmth": warmth,
                    "image": image_data
                }

                wardrobe.append(new_item)
                save_data(wardrobe)

                st.success(f"{name} has been added to your wardrobe!")
                st.rerun()


# -------------------- Smart Outfit --------------------
elif page == "Smart Outfit":
    page_heading("Smart Outfit", "Let your wardrobe inspire your next look.")

    tops = [x for x in wardrobe if x.get("type", "").lower() == "top"]
    bottoms = [x for x in wardrobe if x.get("type", "").lower() == "bottom"]
    shoes = [x for x in wardrobe if x.get("type", "").lower() == "shoes"]

    if not tops or not bottoms:
        st.info("Add at least one Top and one Bottom to generate outfit ideas.")
    else:
        outfits = []

        for top, bottom in product(tops, bottoms):
            score = color_score(
                top.get("color", ""),
                bottom.get("color", "")
            )

            if shoes:
                for shoe in shoes:
                    shoe_score = color_score(
                        top.get("color", ""),
                        shoe.get("color", "")
                    )
                    total_score = round((score + shoe_score) / 2)
                    outfits.append((total_score, top, bottom, shoe))
            else:
                outfits.append((score, top, bottom, None))

        outfits.sort(key=lambda x: x[0], reverse=True)

        st.markdown("#### Your outfit suggestions")
        st.caption("Based on color harmony in your current wardrobe.")

        for number, (score, top, bottom, shoe) in enumerate(outfits[:5], 1):
            with st.container(border=True):
                st.markdown(f"**LOOK {number:02d}**")
                st.markdown(f"Color harmony score: **{score}/100**")

                pieces = [top, bottom]
                if shoe:
                    pieces.append(shoe)

                cols = st.columns(len(pieces))

                for i, item in enumerate(pieces):
                    with cols[i]:
                        show_clothing_image(item)
                        st.markdown(f"**{item.get('name', 'Untitled')}**")
                        st.caption(
                            f"{item.get('type', '')} · {item.get('color', '')}"
                        )


# -------------------- Weather & Location --------------------
elif page == "Weather & Location":
    page_heading("Weather & Location", "Dress for the day, wherever you are.")

    st.markdown("#### Find your local weather")
    st.caption("Allow location access, or search for a city manually.")

    if "coords" not in st.session_state:
        st.session_state.coords = None

    try:
        from streamlit_geolocation import streamlit_geolocation

        location_data = streamlit_geolocation()

        if location_data and location_data.get("latitude") is not None:
            st.session_state.coords = (
                location_data["latitude"],
                location_data["longitude"]
            )
    except Exception:
        st.warning("Automatic location is unavailable. You can search for a city below.")

    city_input = st.text_input(
        "Search city",
        placeholder="e.g. New York, London, Tokyo"
    )

    if st.button("Search city"):
        if city_input.strip():
            result = find_city(city_input.strip())

            if result:
                st.session_state.coords = (
                    result["latitude"],
                    result["longitude"]
                )
                st.session_state.city_name = result.get("name", city_input.strip())
                st.success(f"Location set to {st.session_state.city_name}")
                st.rerun()
            else:
                st.error("City not found. Please try another spelling.")

    if st.session_state.coords:
        latitude, longitude = st.session_state.coords

        city_name = st.session_state.get(
            "city_name",
            get_city_name(latitude, longitude)
        )

        weather = get_weather(latitude, longitude)

        if weather:
            temperature = weather.get("temperature_2m", 0)
            feels_like = weather.get("apparent_temperature", temperature)
            code = weather.get("weather_code", 0)
            humidity = weather.get("relative_humidity_2m", "--")
            wind = weather.get("wind_speed_10m", "--")

            st.write("")
            st.markdown(f"### {city_name}")
            st.markdown(
                f'<div class="hero">'
                f'<div class="hero-label">CURRENT WEATHER</div>'
                f'<div class="hero-title">{temperature}°C</div>'
                f'<div class="hero-subtitle">{weather_description(code)}</div>'
                f'<div class="hero-subtitle">Feels like {feels_like}°C</div>'
                f'</div>',
                unsafe_allow_html=True
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric("Feels like", f"{feels_like}°C")
            with c2:
                st.metric("Humidity", f"{humidity}%")
            with c3:
                st.metric("Wind", f"{wind} km/h")

            st.divider()
            st.markdown("#### What should you wear?")

            target_warmth = warmth_for_temperature(temperature)

            st.markdown(
                f'<span class="tag">Suggested warmth: {target_warmth}</span>',
                unsafe_allow_html=True
            )

            suitable = [
                item for item in wardrobe
                if item.get("warmth", "Medium") == target_warmth
            ]

            if suitable:
                cols = st.columns(3)

                for i, item in enumerate(suitable):
                    with cols[i % 3]:
                        with st.container(border=True):
                            show_clothing_image(item)
                            st.markdown(f"**{item.get('name', 'Untitled')}**")
                            st.caption(
                                f"{item.get('type', '')} · {item.get('color', '')}"
                            )
            else:
                st.info(
                    f"No {target_warmth.lower()} clothing found yet. "
                    "Try adding some pieces with this warmth level."
                )

            if code in [51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99]:
                st.warning("Rain or storms may occur. Consider bringing an umbrella!")

            if code in [71, 73, 75]:
                st.warning("Snow is possible. Remember to dress warmly!")

        else:
            st.error("Could not load weather data. Please try again later.")

    else:
        st.info("Click the location permission prompt in your browser, or search for a city above.")

    st.caption("Weather data provided by Open-Meteo.")
