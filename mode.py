import streamlit as st
import pandas as pd
import requests
from PIL import Image, ImageDraw
from io import BytesIO

# Load the dataset (ensure the file is accessible for Streamlit)
file_path = 'rcp_furniture_sales_confidential.csv'
df = pd.read_csv(file_path)

# Filter relevant columns, including USD Retail Price
df_filtered = df[['Room Category', 'Product Category', 'Product Name', 'Public Image URL', 'USD Retail Price']].dropna(subset=['Public Image URL', 'USD Retail Price'])

# Function to fetch and resize images from URLs
def fetch_and_resize_image(url, size=(200, 200)):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img = img.resize(size)
            return img
    except Exception as e:
        st.write(f"Failed to load image from {url}: {e}")
    return None

# Define preferred product categories for each room type
preferred_products = {
    "Living Room": ["Sofa", "Coffee Table", "Floor Lamp", "Rug", "Armchair", "Side Table", "Bookshelf"],
    "Bedroom": ["Bed", "Nightstand", "Dresser", "Wardrobe", "Area Rug", "Table Lamp"],
    "Dining Room": ["Dining Table", "Chairs", "Buffet", "Chandelier", "Rug", "Wall Art"],
    "Office": ["Desk", "Office Chair", "Bookshelf", "Table Lamp", "Filing Cabinet"],
    "Outdoor Patio": ["Outdoor Sofa", "Coffee Table", "Lounge Chair", "Planter", "Outdoor Rug", "Umbrella"]
}

# Function to create a single mood board option with product names and prices
def create_mood_board_option(images_and_names_and_prices):
    grid_size = (3, 2)
    board_width = grid_size[0] * 200
    board_height = grid_size[1] * 220  # Extra height for product names
    mood_board = Image.new("RGB", (board_width, board_height), color="white")
    draw = ImageDraw.Draw(mood_board)

    for idx, (img, name, price) in enumerate(images_and_names_and_prices):
        x = (idx % grid_size[0]) * 200
        y = (idx // grid_size[0]) * 220
        mood_board.paste(img, (x, y + 20))  # Offset for image position
        draw.text((x + 10, y), f"{name[:20]} - ${price:.2f}", fill="black")  # Display up to 20 characters of the product name and price

    return mood_board

# Function to generate and display four mood board options
def display_mood_board_options(df, room_category):
    # Filter items by room category and remove duplicate images
    items = df[df["Room Category"] == room_category].drop_duplicates(subset=['Public Image URL'])
    
    # Get the list of preferred products for the selected room, if available
    preferred_list = preferred_products.get(room_category, [])
    
    # Filter items by preferred product categories first, if any
    if preferred_list:
        items = items[items["Product Category"].isin(preferred_list)]
    
    # Generate four unique mood board options
    options = []
    for _ in range(4):
        selected_images_and_names_and_prices = []
        selected_categories = set()
        
        # Attempt to fetch unique images for each option
        while len(selected_images_and_names_and_prices) < 6 and len(items) > len(selected_categories):
            sample_item = items.sample(n=1).iloc[0]
            product_category = sample_item["Product Category"]
            if product_category not in selected_categories:
                img = fetch_and_resize_image(sample_item["Public Image URL"])
                if img:
                    selected_images_and_names_and_prices.append((img, sample_item["Product Name"], sample_item["USD Retail Price"]))
                    selected_categories.add(product_category)
        
        # Only add option if exactly 6 images were successfully loaded
        if len(selected_images_and_names_and_prices) == 6:
            options.append(create_mood_board_option(selected_images_and_names_and_prices))

    return options

# Streamlit UI
st.title('Furnishr Mood Board')

# Select room category using a drop-down list
room_categories = df_filtered['Room Category'].unique()
selected_category = st.selectbox('Select Room Category', room_categories)

# Button to generate mood board
if st.button('Generate Mood Board'):
    # Display the four mood board options for the selected category
    options = display_mood_board_options(df_filtered, selected_category)
    
    if options:
        # Display all options at once
        st.write("Here are all the mood board options:")
        for i, option in enumerate(options):
            st.image(option, caption=f"Option {i+1}")
    else:
        st.write("No valid mood board options available.")
