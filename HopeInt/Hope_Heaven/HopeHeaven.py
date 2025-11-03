import streamlit as st
from geopy.distance import geodesic
from utils.data_loader import ORPHANAGES, DONATION_TYPES, AGE_GROUPS
from PIL import Image
import base64
from io import BytesIO
from pathlib import Path
import os
import re
# City to coordinates mapping
CITY_COORDS = {
    "salem": (11.6581, 78.1587),
    "erode": (11.3400, 77.7200),
    "namakkal": (11.2200, 78.1700),
    "coimbatore": (11.0168, 76.9558),
    "chennai": (13.0827, 80.2707),
    "tirupur": (11.1085, 77.3411)
}

# ============================================
# THEME MANAGEMENT SYSTEM
# ============================================
ms = st.session_state
if "themes" not in ms:
    ms.themes = {
        "current_theme": "light",
        "refreshed": True,
        "light": {
            "theme.base": "dark",
            "theme.backgroundColor": "#F8F5FF",
            "theme.primaryColor": "#6A4C93",
            "theme.secondaryBackgroundColor": "#E8E0F7",
            "theme.textColor": "#1A0933",
            "button_face": "🌙"
        },
        "dark": {
            "theme.base": "light",
            "theme.backgroundColor": "#1A0933",
            "theme.primaryColor": "#8C6ED3",
            "theme.secondaryBackgroundColor": "#2E1B5B",
            "theme.textColor": "#F8F5FF",
            "button_face": "☀️"
        }
    }

def change_theme():
    previous_theme = ms.themes["current_theme"]
    tdict = ms.themes["light"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]
    for vkey, vval in tdict.items():
        if vkey.startswith("theme"): st._config.set_option(vkey, vval)
    
    ms.themes["refreshed"] = False
    ms.themes["current_theme"] = "dark" if previous_theme == "light" else "light"

# Add theme toggle button to sidebar
btn_face = ms.themes["light"]["button_face"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]["button_face"]
st.sidebar.button(btn_face, on_click=change_theme)

if ms.themes["refreshed"] == False:
    ms.themes["refreshed"] = True
    st.rerun()

# ============================================
# CUSTOM CSS STYLING (UPDATED)
# ============================================
st.markdown("""
<style>
    .center-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        gap: 1rem;
    }
    .logo-container {
        width: 250px;
        height: 250px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px auto;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .title-container {
        text-align: center;
        margin: 0;
        padding: 0;
        line-height: 1;
    }
    .title-text {
        display: inline;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0.5rem 0;
        background: linear-gradient(90deg, #6A4C93 0%, #8C6ED3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        white-space: nowrap;
    }
    .subtitle-text {
        color: var(--text-color);
        font-size: 1.25rem;
        opacity: 0.9;
        margin-bottom: 2rem;
        max-width: 600px;
        text-align: center;
        margin-left: auto;
        margin-right: auto;
    }
    .primary-button {
        padding: 0.75rem 2rem !important;
        font-size: 1.1rem !important;
        border-radius: 50px !important;
        margin: 1.5rem auto !important;
        transition: all 0.3s ease !important;
        width: fit-content !important;
        display: block !important;
    }
    .user-message {
        background-color: #edcdff !important;
        color: #000 !important;
        padding: 12px !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
        max-width: 60% !important;
        text-align: right !important;
        float: right !important;
        clear: both !important;
        border: 1px solid #dda4ff !important;
    }
    .bot-message {
        background-color: #f8f1ff !important;
        color: #000 !important;
        padding: 12px !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
        max-width: 60% !important;
        text-align: left !important;
        float: left !important;
        clear: both !important;
        border: 1px solid #e6bbff !important;
    }
    .logo-img {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }
</style>
""", unsafe_allow_html=True)

# Constants
MAX_RESULTS = 5

# ⛔ Stop the app if data failed to load
if not ORPHANAGES or isinstance(ORPHANAGES, str):
    st.error(f"❌ Failed to load orphanage data: {ORPHANAGES if isinstance(ORPHANAGES, str) else 'Unknown error'}")
    st.stop()

# Initialize session state
if 'page' not in st.session_state:
    st.session_state['page'] = 'welcome'
if 'form_submitted' not in st.session_state:
    st.session_state['form_submitted'] = False
if 'donation_info' not in st.session_state:
    st.session_state['donation_info'] = {}
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

def calculate_distance(coord1, coord2):
    """Calculate distance between two coordinates in kilometers"""
    try:
        return geodesic(coord1, coord2).km
    except Exception as e:
        st.error(f"Error calculating distance: {str(e)}")
        return float('inf')

def find_matching_orphanages(location_coords, donation_type, quantity):
    """Find orphanages matching donation criteria"""
    matches = []

    for orphanage in ORPHANAGES:
        try:
            # ⛔️ Skip if orphanage is not in the selected city
            if orphanage['address']['city'].lower() != st.session_state['donation_info']['location'].lower():
                continue

            coordinates = orphanage.get('address', {}).get('coordinates')
            if not coordinates or len(coordinates) != 2:
                continue

            distance = calculate_distance(location_coords, coordinates)
            capacity = orphanage.get('capacity', 0)

            for need in orphanage.get('current_needs', []):
                if need['type'] == 'food_per_person':
                    if donation_type.lower() in ['food', 'food_per_person']:
                        if capacity >= quantity:
                            matches.append({
                                'orphanage': orphanage,
                                'distance': distance,
                                'matched_need': need,
                                'match_score': min(quantity / capacity, 1)
                            })
                elif (need['type'].lower() == donation_type.lower() and 
                      need['quantity_needed'] >= quantity):
                    matches.append({
                        'orphanage': orphanage,
                        'distance': distance,
                        'matched_need': need,
                        'match_score': 1
                    })

        except Exception as e:
            st.warning(f"Skipping orphanage {orphanage.get('id')} due to error: {str(e)}")
            continue

    return sorted(matches, key=lambda x: (-x['match_score'], x['distance']))[:5]

def format_orphanage_info(orphanage, distance, matched_need):
    """Format orphanage information for display"""
    try:
        phone = orphanage['contact']['phone'].strip().replace(' ', '')
        whatsapp_link = f"https://wa.me/91{phone}"
        
        if matched_need['type'] == 'food_per_person':
            return f"""
**{orphanage['name']}**  
📍 {orphanage['address']['street']}, {orphanage['address']['city']}  
📏 {distance:.1f} km away  
👥 Can feed: {orphanage['capacity']} people  
📞 [Contact via WhatsApp]({whatsapp_link})  
🕒 Hours: {orphanage.get('operating_hours', 'Not specified')}  
"""
        else:
            return f"""
**{orphanage['name']}**  
📍 {orphanage['address']['street']}, {orphanage['address']['city']}  
📏 {distance:.1f} km away  
🍽 Can use: {matched_need['quantity_needed']} {matched_need['type'].replace('_', ' ')}  
📞 [Contact via WhatsApp]({whatsapp_link})  
🕒 Hours: {orphanage.get('operating_hours', 'Not specified')}  
"""
    except KeyError as e:
        st.error(f"Missing data in orphanage record: {str(e)}")
        return f"**{orphanage.get('name', 'Unnamed orphanage')}** - Incomplete data"

def welcome_page():
    """Render welcome page with logo and introduction"""
    st.markdown("""
    <style>
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        gap: 1rem;
    }
    .logo-container {
        width: 250px;
        height: 250px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .title-text {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0.5rem 0;
        background: linear-gradient(90deg, #6A4C93 0%, #8C6ED3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        white-space: nowrap;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main container
    st.markdown("""
    <div class="welcome-container">
        <h1 class="title-text">Welcome to HopeHaven</h1>
    """, unsafe_allow_html=True)

    try:
        # Try multiple possible image locations
        possible_paths = [
            Path("IMAGES/Hopee.png"),               # IMAGES folder
            Path("D:/Hope_Heaven/IMAGES/Hopee.png"), # Absolute path
            Path("Hopee.png")                
        ]
        
        img_found = False
        for img_path in possible_paths:
            if img_path.exists():
                img = Image.open(img_path)
                img.thumbnail((250, 250))  # Maintain aspect ratio
                
                # Convert to base64
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Display image
                st.markdown(f"""
                <div class="logo-container">
                    <img src="data:image/png;base64,{img_str}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain;">
                </div>
                """, unsafe_allow_html=True)
                img_found = True
                break
        
        if not img_found:
            st.error(f"Logo not found. Checked paths:\n{chr(10).join(str(p) for p in possible_paths)}")

    except Exception as e:
        st.error(f"Error loading logo: {str(e)}")

    # Close container and add remaining content
    st.markdown("""
        <p class="subtitle-text"><center>
           Every meal you share brings hope to a child's heart. <br>
           Join us in building a bridge between kindness and need.
           </center>
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Start Donation Process", use_container_width=True, type="primary"):
        st.session_state['page'] = 'donation_form'
        st.rerun()

# [Rest of your existing functions (donation_form_page, chatbot_page) remain exactly the same]
# ... (keep all your existing donation_form_page and chatbot_page code unchanged)
def donation_form_page():
    """Render donation form page"""
    st.title("Donation Information")

    with st.form(key='donation_form'):
        st.subheader("Tell us about your donation")
        
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input(
                "Your Location (Address or Landmark)",
                help="Example: Near Gandhi Park, Salem",
                placeholder="Enter your location"
            )
            donation_type = st.selectbox(
                "Type of Donation",
                [t.replace('_', ' ').title() for t in DONATION_TYPES],
                index=0
            )
        
        with col2:
            quantity = st.number_input("Quantity", min_value=1, value=10)
            other_info = st.text_area(
                "Additional Information (Optional)",
                placeholder="Any special notes about your donation"
            )

        submitted = st.form_submit_button("Find Matching Orphanages")

        if submitted:
            if not location:
                st.error("Please enter your location")
            else:
                st.session_state['donation_info'] = {
                    'location': location,
                    'donation_type': donation_type.lower().replace(' ', '_'),
                    'quantity': quantity,
                    'other_info': other_info,
                    'coordinates': (11.6581, 78.1587)  # Default Salem coordinates
                }
                st.session_state['form_submitted'] = True
                st.session_state['page'] = 'chatbot'
                st.rerun()

def chatbot_page():
    """Render chatbot interface"""
    st.title("HopeHeaven Donation Assistant")

    # Process form submission if needed
    if st.session_state.get('form_submitted', False):
        donation = st.session_state['donation_info']
        matches = find_matching_orphanages(
            donation['coordinates'],
            donation['donation_type'],
            donation['quantity']
        )

        if matches:
            response = "Here are nearby orphanages that could use your donation:\n\n"
            for match in matches:
                response += format_orphanage_info(
                    match['orphanage'],
                    match['distance'],
                    match['matched_need']
                ) + "\n"
            response += "**Please contact them to arrange your donation.**"
        else:
            response = """I couldn't find orphanages nearby that match your donation. 
\n\nPlease try:\n- A different donation type\n- A smaller quantity\n- Or check back later"""

        st.session_state['chat_history'].append((
            "USER", 
            f"I have {donation['quantity']} {donation['donation_type'].replace('_', ' ')} to donate in {donation['location']}"
        ))
        st.session_state['chat_history'].append(("HOPELINK", response))
        st.session_state['form_submitted'] = False

    # Display chat history
    for role, message in st.session_state['chat_history']:
        if role == "USER":
            st.markdown(f'<div class="user-message">{message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{message}</div>', unsafe_allow_html=True)

    # Handle user input
    user_input = st.text_input(
        "Ask a question about donating...", 
        key="chat_input",
        placeholder="Type your question here..."
    )

    if user_input:
        st.session_state['chat_history'].append(("USER", user_input))

        user_input_lower = user_input.lower()

        # Detect city and donation type from input
        found_city = next((city for city in CITY_COORDS if city in user_input_lower), None)
        found_type = next((dtype for dtype in DONATION_TYPES if dtype.replace('_', ' ') in user_input_lower), None)

        if found_city and found_type:
            st.session_state['donation_info'] = {
                'location': found_city,
                'donation_type': found_type,
                'quantity': 10,  # default or extract with regex if needed
                'other_info': '',
                'coordinates': CITY_COORDS[found_city]
            }
            st.session_state['form_submitted'] = True
            response = f"Great! Looking for **{found_type.replace('_', ' ')}** needs in **{found_city.title()}** orphanages..."
        elif any(word in user_input_lower for word in ["thank", "thanks"]):
            response = "You're welcome! Thank you for helping those in need. 💜"
        elif any(word in user_input_lower for word in ["how", "work", "process"]):
            response = """**How HopeLink works:**
            \n1. You tell us what you'd like to donate
            \n2. We match you with nearby orphanages that need those items
            \n3. You contact the orphanage directly to arrange delivery
            \n4. You make a difference in children's lives!"""
        elif any(word in user_input_lower for word in ["hi", "hello", "hey"]):
            response = "Hello! How can I help you with your donation today?"
        else:
            response = """I'm here to help you connect your donations with orphanages in need. 
            \nYou can ask me about:\n- How the process works\n- What items are needed\n- Or tell me what you'd like to donate"""

        st.session_state['chat_history'].append(("HOPELINK", response))
        st.rerun()

    # Navigation button
    if st.button("Start New Donation", type="primary"):
        st.session_state['page'] = 'donation_form'
        st.rerun()

def should_respond(user_input):
    if user_input and user_input != st.session_state['last_user_input']:
        st.session_state['last_user_input'] = user_input
        return True
    return False

# Main app routing
if st.session_state['page'] == 'welcome':
    welcome_page()
elif st.session_state['page'] == 'donation_form':
    donation_form_page()
elif st.session_state['page'] == 'chatbot':
    chatbot_page()