
import streamlit as st
import json
import os
import random

DATA_FILE = "wardrobe_data.json"

st.set_page_config(
    page_title="Smart Wardrobe",
    page_icon="👗",
    layout="wide"
)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_data(clothes):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(clothes, file, ensure_ascii=False, indent=4)

if "clothes" not in st.session_state:
    st.session_state.clothes = load_data()

st.title("👗 Smart Wardrobe")
st.caption("Your personal digital closet and outfit assistant")

menu = st.sidebar.radio(
    "Navigation",
    ["My Wardrobe", "Add Clothing", "Outfit Recommendation"]
)

if menu == "My Wardrobe":
    st.header("My Wardrobe")

    if not st.session_state.clothes:
        st.info("Your wardrobe is empty. Add some clothes first!")
    else:
        cols = st.columns(3)

        for index, item in enumerate(st.session_state.clothes):
            with cols[index % 3]:
                with st.container(border=True):
                    st.subheader(item["name"])
                    st.write("Type:", item["type"])
                    st.write("Color:", item["color"])

                    if st.button("Delete", key=f"delete_{index}"):
                        st.session_state.clothes.pop(index)
                        save_data(st.session_state.clothes)
                        st.rerun()

elif menu == "Add Clothing":
    st.header("Add New Clothing")

    with st.form("add_clothing_form"):
        name = st.text_input("Clothing name")

        clothing_type = st.selectbox(
            "Clothing type",
            ["Top", "Bottom", "Shoes", "Outerwear", "Accessories"]
        )

        color = st.selectbox(
            "Color",
            ["Black", "White", "Blue", "Red", "Grey", "Beige", "Other"]
        )

        submitted = st.form_submit_button("Add to Wardrobe")

        if submitted:
            if name.strip():
                st.session_state.clothes.append({
                    "name": name.strip(),
                    "type": clothing_type,
                    "color": color
                })

                save_data(st.session_state.clothes)
                st.success("Clothing added successfully!")
            else:
                st.error("Please enter a clothing name.")

elif menu == "Outfit Recommendation":
    st.header("Outfit Recommendation")

    tops = [x for x in st.session_state.clothes if x["type"] == "Top"]
    bottoms = [x for x in st.session_state.clothes if x["type"] == "Bottom"]
    shoes = [x for x in st.session_state.clothes if x["type"] == "Shoes"]

    if st.button("Generate My Outfit"):
        if tops and bottoms and shoes:
            st.subheader("Your Outfit ✨")

            st.write("👕 Top:", random.choice(tops)["name"])
            st.write("👖 Bottom:", random.choice(bottoms)["name"])
            st.write("👟 Shoes:", random.choice(shoes)["name"])
        else:
            st.warning("Please add at least one top, bottom, and shoes.")
