
import streamlit as st
import json
import os
import random
import base64
import requests

from streamlit_geolocation import streamlit_geolocation

DATA_FILE = "wardrobe_data.json"

st.set_page_config(
    page_title="Smart Wardrobe",
    page_icon="👗",
    layout="wide"
)

# ---------- Data Management ----------

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_data(clothes):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(clothes, f, ensure_ascii=False, indent=4)


if "clothes" not in st.session_state:
    st.session_state.clothes = load_data()

if "weather_coords" not in st.session_state:
    st.session_state.weather_coords = None


# ---------- Color Matching ----------

def color_score(c1, c2):
    compatible = {
        "Black": ["White", "Grey", "Beige", "Blue", "Red"],
        "White": ["Black", "Blue", "Grey", "Beige", "Red"],
        "Blue": ["White", "Black", "Beige", "Grey"],
        "Red": ["Black", "White", "Beige"],
        "Grey": ["Black", "White", "Blue", "Red"],
        "Beige": ["Black", "White", "Blue", "Red"],
        "Other": ["Black", "White", "Grey"]
    }

    if c1 == c2:
        return 2

    if c2 in compatible.get(c1, []):
        return 3

    return 1


# ---------- Weather Functions ----------

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,apparent_temperature,"
            "relative_humidity_2m,weather_code,"
            "precipitation,wind_speed_10m"
        ),
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    return response.json()["current"]


def get_city_name(latitude, longitude):
    url = "https://nominatim.openstreetmap.org/reverse"

    headers = {
        "User-Agent": "SmartWardrobeStudentProject/1.0"
    }

    params = {
        "lat": latitude,
        "lon": longitude,
        "format": "jsonv2",
        "zoom": 10
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=15
    )

    response.raise_for_status()

    address = response.json().get("address", {})

    return (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("county")
        or "Your current area"
    )


def find_city(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    results = response.json().get("results", [])

    if not results:
        return None

    place = results[0]

    return {
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "name": place["name"]
    }


def weather_description(code):
    if code == 0:
        return "Clear sky ☀️"
    elif code in [1, 2, 3]:
        return "Partly cloudy ⛅"
    elif code in [45, 48]:
        return "Foggy 🌫️"
    elif code in [51, 53, 55, 56, 57]:
        return "Drizzle 🌦️"
    elif code in [61, 63, 65, 66, 67, 80, 81, 82]:
        return "Rainy 🌧️"
    elif code in [71, 73, 75, 77, 85, 86]:
        return "Snowy ❄️"
    elif code in [95, 96, 99]:
        return "Thunderstorm ⛈️"

    return "Unknown weather"


def show_weather(latitude, longitude, city):
    try:
        weather = get_weather(latitude, longitude)

        temperature = weather["temperature_2m"]
        feels_like = weather["apparent_temperature"]
        description = weather_description(weather["weather_code"])

        st.subheader("📍 Current Location")
        st.write(city)

        col1, col2, col3 = st.columns(3)

        col1.metric("Temperature", f"{temperature} °C")
        col2.metric("Feels Like", f"{feels_like} °C")
        col3.metric("Wind Speed", f"{weather['wind_speed_10m']} km/h")

        st.info(f"Current weather: {description}")

        return temperature, weather["weather_code"]

    except requests.RequestException:
        st.error("Unable to get weather. Please try again.")
        return None, None


# ---------- Navigation ----------

st.title("👗 Smart Wardrobe")
st.caption("Your Personal Digital Closet & Outfit Assistant")

page = st.sidebar.radio(
    "Navigation",
    [
        "My Wardrobe",
        "Add Clothing",
        "Smart Outfit",
        "Weather & Location"
    ]
)

st.sidebar.metric(
    "Total Clothing Items",
    len(st.session_state.clothes)
)


# ---------- My Wardrobe ----------

if page == "My Wardrobe":

    st.header("✨ My Wardrobe")

    if not st.session_state.clothes:
        st.info("Your wardrobe is empty. Add your first item!")

    else:
        cols = st.columns(3)

        for index, item in enumerate(st.session_state.clothes):

            with cols[index % 3]:
                with st.container(border=True):

                    if item.get("image"):
                        st.image(
                            base64.b64decode(item["image"]),
                            use_container_width=True
                        )
                    else:
                        st.write("👕 No photo uploaded")

                    st.subheader(item["name"])
                    st.write("Type:", item["type"])
                    st.write("Color:", item["color"])
                    st.write("Warmth:", item.get("warmth", "Medium"))

                    if st.button("Delete", key=f"delete_{index}"):
                        st.session_state.clothes.pop(index)
                        save_data(st.session_state.clothes)
                        st.rerun()


# ---------- Add Clothing ----------

elif page == "Add Clothing":

    st.header("➕ Add New Clothing")

    with st.form("add_clothing_form"):

        name = st.text_input("Clothing name")

        clothing_type = st.selectbox(
            "Clothing type",
            ["Top", "Bottom", "Shoes", "Outerwear", "Accessories"]
        )

        color = st.selectbox(
            "Clothing color",
            ["Black", "White", "Blue", "Red", "Grey", "Beige", "Other"]
        )

        warmth = st.selectbox(
            "Warmth level",
            ["Light", "Medium", "Warm"]
        )

        uploaded_file = st.file_uploader(
            "Upload clothing photo",
            type=["jpg", "jpeg", "png"]
        )

        submitted = st.form_submit_button("Add to Wardrobe")

        if submitted:

            if not name.strip():
                st.error("Please enter a clothing name.")

            else:

                image_data = None

                if uploaded_file:
                    image_data = base64.b64encode(
                        uploaded_file.getvalue()
                    ).decode("utf-8")

                st.session_state.clothes.append({
                    "name": name.strip(),
                    "type": clothing_type,
                    "color": color,
                    "warmth": warmth,
                    "image": image_data
                })

                save_data(st.session_state.clothes)

                st.success("Clothing added successfully!")
                st.rerun()


# ---------- Smart Outfit ----------

elif page == "Smart Outfit":

    st.header("✨ Smart Outfit Recommendation")

    tops = [
        x for x in st.session_state.clothes
        if x["type"] == "Top"
    ]

    bottoms = [
        x for x in st.session_state.clothes
        if x["type"] == "Bottom"
    ]

    shoes = [
        x for x in st.session_state.clothes
        if x["type"] == "Shoes"
    ]

    if st.button("Generate My Outfit"):

        if tops and bottoms and shoes:

            combinations = []

            for top in tops:
                for bottom in bottoms:
                    for shoe in shoes:

                        score = (
                            color_score(top["color"], bottom["color"])
                            + color_score(bottom["color"], shoe["color"])
                            + color_score(top["color"], shoe["color"])
                        )

                        combinations.append(
                            (score, top, bottom, shoe)
                        )

            best_score = max(x[0] for x in combinations)

            best = [
                x for x in combinations
                if x[0] == best_score
            ]

            _, top, bottom, shoe = random.choice(best)

            st.success("Your outfit is ready!")

            for col, item, label in zip(
                st.columns(3),
                [top, bottom, shoe],
                ["👕 Top", "👖 Bottom", "👟 Shoes"]
            ):

                with col:
                    with st.container(border=True):

                        st.subheader(label)

                        if item.get("image"):
                            st.image(
                                base64.b64decode(item["image"]),
                                use_container_width=True
                            )

                        st.write(item["name"])
                        st.caption(item["color"])

            st.caption(f"Color coordination score: {best_score}/9")

        else:
            st.warning(
                "Please add at least one top, bottom, and pair of shoes."
            )


# ---------- Weather & Location ----------

elif page == "Weather & Location":

    st.header("🌍 Weather & Location Assistant")

    st.write(
        "Allow location access to get weather near you automatically."
    )

    location = streamlit_geolocation()

    if isinstance(location, dict):

        latitude = location.get("latitude")
        longitude = location.get("longitude")

        if latitude is not None and longitude is not None:

            st.session_state.weather_coords = {
                "latitude": latitude,
                "longitude": longitude
            }

    coords = st.session_state.weather_coords

    if coords:

        try:
            city = get_city_name(
                coords["latitude"],
                coords["longitude"]
            )

            temperature, code = show_weather(
                coords["latitude"],
                coords["longitude"],
                city
            )

        except requests.RequestException:
            st.warning(
                "Could not identify your area. "
                "You can search for a city below."
            )
            temperature = None
            code = None

    else:
        st.info(
            "Location not available yet. "
            "Please allow location permission or search manually."
        )
        temperature = None
        code = None

    st.divider()

    st.subheader("🔎 Search Another City")

    with st.form("city_search"):

        city_input = st.text_input(
            "Enter city name",
            placeholder="For example: New York"
        )

        search = st.form_submit_button("Get City Weather")

        if search:

            if city_input.strip():

                try:
                    place = find_city(city_input.strip())

                    if place:
                        st.session_state.weather_coords = {
                            "latitude": place["latitude"],
                            "longitude": place["longitude"]
                        }

                        st.rerun()

                    else:
                        st.error("City not found. Try another name.")

                except requests.RequestException:
                    st.error("Unable to search for this city.")

    # Weather outfit suggestions

    if coords and temperature is not None:

        st.divider()
        st.subheader("👗 Weather Outfit Suggestions")

        if temperature < 10:
            warmth_needed = "Warm"
            st.info("Cold weather: Choose warm clothes and a coat.")

        elif temperature < 20:
            warmth_needed = "Medium"
            st.info("Cool weather: Choose medium-weight clothing.")

        else:
            warmth_needed = "Light"
            st.info("Warm weather: Choose light and breathable clothing.")

        if code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            st.warning("🌧️ Rain is possible. Remember an umbrella!")

        elif code in [71, 73, 75, 77, 85, 86]:
            st.warning("❄️ Snowy weather. Wear warm layers!")

        suitable = [
            item for item in st.session_state.clothes
            if item.get("warmth", "Medium") == warmth_needed
        ]

        if suitable:

            for item in suitable:

                with st.container(border=True):

                    st.write(f"**{item['name']}**")
                    st.write(
                        f"{item['type']} | {item['color']} | "
                        f"{item.get('warmth', 'Medium')}"
                    )

                    if item.get("image"):
                        st.image(
                            base64.b64decode(item["image"]),
                            width=140
                        )

        else:
            st.info(
                "No matching clothes found. "
                "Add more clothes with this warmth level."
            )

st.sidebar.divider()
st.sidebar.caption("Smart Wardrobe 4.0")
