import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup

from recommender import apply_filters


laptops = pd.read_csv("cleaned_laptops_updated.csv")


def get_image_and_price(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")
    element = soup.find("div", class_="_2c7YLP")
    image_src = element.find("img", class_="_396cs4").get("src")
    price = element.find("div", class_="_30jeq3").text
    return (image_src, price)


def main():
    # Remove whitespace from the top of the page and sidebar
    st.markdown("""
        <style>
               .block-container {
                    margin-top: -100px;
                    display: flex;
                }
        </style>
        """, unsafe_allow_html=True)
    st.title("Laptop Finder")
    st.sidebar.title("Laptop Specifications")
    intended_use = st.sidebar.multiselect("1. Intended Use", ["Studying", "Programming", "Gaming", "Multimedia"])

    preferred_brands = st.sidebar.multiselect("2. Preferred Brands or Models", laptops["brand"].unique())

    processor_performance = st.sidebar.multiselect("3. Processor Performance", ["Basic tasks (Intel Core i3 or equivalent AMD)", "Moderate multitasking (Intel Core i5 or equivalent AMD Ryzen 5)", "Intensive tasks (Intel Core i7/i9 or equivalent AMD Ryzen 7/9)"])
    budget_range = st.sidebar.multiselect("4. Budget Range", ["Under 40k", "40k - 55k", "55k - 70k", "70k - 85k", "85k above"])
    os_preference = st.sidebar.multiselect("5. Operating System Preference", laptops["os"].unique())
    ram_requirement = st.sidebar.multiselect("6. RAM Requirement", ["4GB - 8GB", "8GB - 16GB", "16GB+"])
    storage_space = st.sidebar.multiselect("7. Desired Storage Space", ["0 GB - 128GB", "128GB - 256GB", "256GB - 512GB", "512GB - 1TB", "1TB+"])
    screen_size = st.sidebar.multiselect("8. Preferred Screen Size", ["11 - 13 inches","13 - 14 inches", "14 - 15 inches", "15+ inches"])
    graphics_tasks = st.sidebar.multiselect("9. Graphics-Intensive Tasks", ["Light gaming and multimedia consumption", "Moderate gaming and video editing", "Heavy gaming or professional video editing/rendering"])
    display_panel = st.sidebar.multiselect("10. Display Panel Type", ["IPS for better color reproduction and viewing angles", "TN for faster response times (often found in gaming laptops)"])
    display_resolution = st.sidebar.multiselect("11. Display Resolution", ["HD (1366 x 768)", "Full HD (1920 x 1080)", "QHD (2560 x 1440) or higher"])
    portability_importance = st.sidebar.multiselect("12. Portability Importance", ["Very important (Looking for lightweight options)", "Moderate (Balanced weight and performance)", "Not a priority"])
    battery_life_priority = st.sidebar.multiselect("13. Battery Life Priority", ["Long battery life is a top priority", "Moderate battery life is sufficient", "Not a significant concern"])
    touchscreen_preference = st.sidebar.multiselect("14. Touchscreen Preference", ["Yes, I prefer a touchscreen", "No, I don't need a touchscreen"])
    ports_connectivity = st.sidebar.multiselect("15. Necessary Ports and Connectivity", ["USB-C", "HDMI", "SD card slot", "Thunderbolt 3/4", "Other specific ports (please specify)"])
    upgradability_importance = st.sidebar.multiselect("16. Importance of Upgradability", ["I prefer a laptop with upgradable components", "Upgradability is not a priority for me"])
    keyboard_type = st.sidebar.multiselect("17. Keyboard Type", ["Standard keyboard", "Backlit keyboard", "Mechanical keyboard"])
    security_features = st.sidebar.multiselect("18. Fingerprint Reader/Security Features", ["Fingerprint reader for security", "No specific need for biometric authentication"])
    warranty_support = st.sidebar.multiselect("19. Warranty and Support", ["Longer warranty and premium support services", "Standard warranty is sufficient"])

    specification = {
        "Intended Use": intended_use,
        "Preferred Brands or Models": preferred_brands,
        "Processor Performance": processor_performance,
        "Budget Range": budget_range,
        "Operating System Preference": os_preference,
        "RAM Requirement": ram_requirement,
        "Desired Storage Space": storage_space,
        "Preferred Screen Size": screen_size,
        "Graphics-Intensive Tasks": graphics_tasks,
        "Display Panel Type": display_panel,
        "Display Resolution": display_resolution,
        "Portability Importance": portability_importance,
        "Battery Life Priority": battery_life_priority,
        "Touchscreen Preference": touchscreen_preference,
        "Necessary Ports and Connectivity": ports_connectivity,
        "Importance of Upgradability": upgradability_importance,
        "Keyboard Type": keyboard_type,
        "Fingerprint Reader/Security Features": security_features,
        "Warranty and Support": warranty_support,
    }
    search = st.sidebar.button("Search")
    col5, col6 = st.columns([0.5, 0.3])
    with col5:
        prices = st.button("Fetch Latest Prices")
    # add a toggle for number of results, selectbox, default 15
    with col6:
        col7, col8 = st.columns([0.5, 0.5])
        with col8:
            results = st.selectbox("Number of Results", [5, 10, 15, 20, 25, 30, 35, 40, 45, 50], index=2)
    if search:
        filtered_laptops = apply_filters(laptops, specification).sort_values(by=["star_rating", "ratings", "reviews"], ascending=False).head(results)
        if len(filtered_laptops) == 0:
            filtered_laptops = laptops.sort_values(by=["star_rating", "ratings", "reviews"], ascending=False).head(results)
    else:
        filtered_laptops = laptops.sort_values(by=["star_rating", "ratings", "reviews"], ascending=False).head(results)

    if prices:
        for i, laptop in filtered_laptops.iterrows():
            try:
                image_src, price = get_image_and_price(laptop["link"])
                filtered_laptops.at[i, "image_url"] = image_src
                filtered_laptops.at[i, "latest_price"] = int(price[1:].replace(',', ''))
            except:
                pass

    # Use multiple columns to display the laptop information
    for i, laptop in filtered_laptops.iterrows():
        # Use two columns: one with 30% width and one with 70% width
        col1, col2 = st.columns([0.3, 0.7])

        with col1:
            # Display the image or a default one if not available
            try:
                st.image(laptop["image_url"], use_column_width=True)
            except:
                # Display a default image OIG.jpeg
                st.image("OIG.jpeg", use_column_width=True)

            if laptop['latest_price'] == 0:
                st.warning("Price not available")
            elif laptop['latest_price'] < laptop['old_price'] and laptop['old_price'] != 0:
                st.write(f" #### Latest Price:")
                st.write(f" ##### ₹{laptop['latest_price']:,}  (~~₹{laptop['old_price']:,}~~)")
                st.success(f"Discount: ₹{laptop['old_price'] - laptop['latest_price']:,} ({round((laptop['old_price'] - laptop['latest_price']) / laptop['old_price'] * 100, 2)}%)")
            elif laptop['latest_price'] > laptop['old_price'] and laptop['old_price'] != 0:
                st.write(f" #### Latest Price:")
                st.write(f" ##### ₹{laptop['latest_price']:,}  (~~₹{laptop['old_price']:,}~~)")
                st.error(f"Discount: ₹{laptop['latest_price'] - laptop['old_price']:,} ({round((laptop['latest_price'] - laptop['old_price']) / laptop['old_price'] * 100, 2)}%)")
            else:
                st.write(f" #### Latest Price:")
                st.write(f" ##### ₹{laptop['latest_price']:,}  (~~₹{laptop['old_price']:,}~~)")

            st.subheader(f"Rating: {laptop['star_rating']}")
            st.write(f"({laptop['ratings']} ratings, {laptop['reviews']} reviews)")
        with col2:
            st.header(laptop["brand"] + " " + laptop["model"])
            st.success("**Specifications:**")
            col3, col4 = st.columns([0.5, 0.5])
            with col3:
                st.write(f"- Processor: {laptop['processor_brand']} {laptop['processor_name']} (Gen {laptop['processor_gnrtn']})")
                st.write(f"- RAM: {laptop['ram_gb']} GB {laptop['ram_type']}")
                st.write(f"- Storage: SSD {laptop['ssd']} GB, HDD {laptop['hdd']} GB")
                st.write(f"- Operating System: {laptop['os']} {laptop['os_bit']}-bit")
                if laptop['graphic_card_gb'] != 0:
                    st.write(f"- Graphics Card: {laptop['graphic_card_gb']} GB")
            with col4:
                st.write(f"- Weight: {laptop['weight']}")
                st.write(f"- Display Size: {laptop['display_size']} inches")
                st.write(f"- Warranty: {laptop['warranty']} years")
                st.write(f"- Touchscreen: {'Yes' if laptop['Touchscreen'] else 'No'}")
                st.write(f"- Microsoft Office: {'Yes' if laptop['msoffice'] else 'No'}")

            if laptop['link'] != "Not Found":
                st.write(f"- Flipkart Link: [Click here]({laptop['link']})")
            col9, col10 = st.columns([0.5, 0.5])
            with col9:
                with st.expander("Usage Categories"):
                    st.write(f"- For Studying: {'Yes' if laptop['Studying'] else 'No'}")
                    st.write(f"- For Programming: {'Yes' if laptop['Programming'] else 'No'}")
                    st.write(f"- For Gaming: {'Yes' if laptop['Gaming'] else 'No'}")
                    st.write(f"- For Multimedia: {'Yes' if laptop['Multimedia'] else 'No'}")
            with col10:
                with st.expander("Processor Performance"):
                    st.write(f"- Basic tasks (Intel Core i3 or equivalent AMD): {'Yes'}")
                    st.write(f"- Moderate multitasking (Intel Core i5 or equivalent AMD Ryzen 5): {'Yes' if laptop['Medium'] else 'No'}")
                    st.write(f"- Intensive tasks (Intel Core i7/i9 or equivalent AMD Ryzen 7/9): {'Yes' if laptop['Advanced'] else 'No'}")
        st.write("---")
        for i in range(2):
            st.write(" ")


if __name__ == "__main__":
    main()
