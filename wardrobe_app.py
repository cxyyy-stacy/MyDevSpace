
import streamlit as st
import json
import os
import random
import base64

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
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_data(clothes):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(clothes, file, ensure_ascii=False, indent=4)


if "clothes" not in st.session_state:
    st.session_state.clothes = load_data()


# ---------- Color Matching ----------

def color_score(color1, color2):
    compatible_colors = {
        "Black": ["White", "Grey", "Beige", "Blue", "Red"],
        "White": ["Black", "Blue", "Grey", "Beige", "Red"],
        "Blue": ["White", "Black", "Beige", "Grey"],
        "Red": ["Black", "White", "Beige"],
        "Grey": ["Black", "White", "Blue", "Red"],
        "Beige": ["Black", "White", "Blue", "Red"],
        "Other": ["Black", "White", "Grey"]
    }

    if color1 == color2:
        return 2

    if color2 in compatible_colors.get(color1, []):
        return 3

    return 1


# ---------- Page Navigation ----------

st.title("👗 Smart Wardrobe")
st.caption("Your Personal Digital Closet & Outfit Assistant")

page = st.sidebar.radio(
    "Navigation",
    [
        "My Wardrobe",
        "Add Clothing",
        "Smart Outfit",
        "Weather Recommendation"
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
        st.info("Your wardrobe is empty. Add your first clothing item!")

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

                new_item = {
                    "name": name.strip(),
                    "type": clothing_type,
                    "color": color,
                    "warmth": warmth,
                    "image": image_data
                }

                st.session_state.clothes.append(new_item)
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

            cols = st.columns(3)

            for col, item, label in zip(
                cols,
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


# ---------- Weather Recommendation ----------

elif page == "Weather Recommendation":

    st.header("🌤️ Weather Outfit Assistant")

    temperature = st.slider(
        "Today's temperature (°C)",
        min_value=-10,
        max_value=40,
        value=22
    )

    weather = st.selectbox(
        "Today's weather",
        ["Sunny", "Cloudy", "Rainy", "Snowy", "Windy"]
    )

    if temperature < 10:
        warmth_needed = "Warm"
        st.info("🥶 Cold weather! Choose warm clothing.")

    elif temperature < 20:
        warmth_needed = "Medium"
        st.info("🧥 Cool weather! A light jacket is recommended.")

    else:
        warmth_needed = "Light"
        st.info("☀️ Warm weather! Choose light and breathable clothing.")

    if weather == "Rainy":
        st.warning("🌧️ Remember to bring an umbrella!")

    elif weather == "Snowy":
        st.warning("❄️ Wear warm layers and suitable shoes!")

    elif weather == "Windy":
        st.warning("💨 Consider wearing a windproof jacket!")

    st.subheader("Your Weather Outfit")

    suitable = [
        item for item in st.session_state.clothes
        if item.get("warmth", "Medium") == warmth_needed
    ]

    if suitable:

        for item in suitable:

            with st.container(border=True):

                if item.get("image"):
                    st.image(
                        base64.b64decode(item["image"]),
                        width=150
                    )

                st.write(f"**{item['name']}**")
                st.write(f"{item['type']} | {item['color']}")

    else:
        st.info(
            "No clothing with the recommended warmth level. "
            "Try adding more clothes to your wardrobe!"
        )

st.sidebar.divider()
st.sidebar.caption("Smart Wardrobe 3.0 | Built with Python")
