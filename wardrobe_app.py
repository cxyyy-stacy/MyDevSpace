
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


# ---------- Page Design ----------

st.title("👗 Smart Wardrobe")
st.caption("Your personal digital closet and outfit assistant")

st.sidebar.title("My Closet")

page = st.sidebar.radio(
    "Navigation",
    [
        "My Wardrobe",
        "Add Clothing",
        "Smart Outfit",
    ]
)

st.sidebar.metric(
    "Total Clothing Items",
    len(st.session_state.clothes)
)


# ---------- My Wardrobe ----------

if page == "My Wardrobe":

    st.header("✨ My Wardrobe")
    st.write("Your clothes, organized in one place.")

    if not st.session_state.clothes:
        st.info("Your wardrobe is empty. Add your first clothing item!")

    else:
        cols = st.columns(3)

        for index, item in enumerate(st.session_state.clothes):

            with cols[index % 3]:

                with st.container(border=True):

                    image_data = item.get("image")

                    if image_data:
                        image_bytes = base64.b64decode(image_data)
                        st.image(image_bytes, use_container_width=True)
                    else:
                        st.write("👕 No photo uploaded")

                    st.subheader(item["name"])
                    st.write(f"Type: {item['type']}")
                    st.write(f"Color: {item['color']}")

                    if st.button("Delete", key=f"delete_{index}"):
                        st.session_state.clothes.pop(index)
                        save_data(st.session_state.clothes)
                        st.rerun()


# ---------- Add Clothing ----------

elif page == "Add Clothing":

    st.header("➕ Add New Clothing")
    st.write("Build your digital wardrobe.")

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

                if uploaded_file is not None:
                    image_data = base64.b64encode(
                        uploaded_file.getvalue()
                    ).decode("utf-8")

                new_item = {
                    "name": name.strip(),
                    "type": clothing_type,
                    "color": color,
                    "image": image_data
                }

                st.session_state.clothes.append(new_item)

                save_data(st.session_state.clothes)

                st.success("Clothing added successfully!")
                st.rerun()


# ---------- Smart Outfit ----------

elif page == "Smart Outfit":

    st.header("✨ Smart Outfit Recommendation")
    st.write("Find a coordinated outfit from your wardrobe.")

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

            best_combinations = [
                x for x in combinations
                if x[0] == best_score
            ]

            _, top, bottom, shoe = random.choice(best_combinations)

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

            st.caption(
                f"Color coordination score: {best_score}/9"
            )

        else:

            st.warning(
                "Please add at least one top, bottom, and pair of shoes."
            )
