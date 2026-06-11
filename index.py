import re
import time
import requests
from pathlib import Path
import streamlit as st
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="IG Public Data Tool", layout="centered")
st.title("📸 Instagram Public Data Tool")

def extract_username(input_str: str) -> str:
    if not input_str:
        return ""
    input_str = input_str.strip().lower()
    if "instagram.com" in input_str:
        username = re.sub(r'https?://(www\.)?instagram\.com/', '', input_str)
        username = username.split('/')[0].split('?')[0].strip()
        return username
    return input_str

def fetch_public_profile(username: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "X-IG-App-ID": "936619743392459",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://www.instagram.com/{username}/",
        "Origin": "https://www.instagram.com"
    }
    
    try:
        # Best public endpoint
        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
        resp = requests.get(url, headers=headers, timeout=20)
        
        if resp.status_code == 200:
            data = resp.json()
            user = data.get("data", {}).get("user", {})
        else:
            st.warning(f"Status {resp.status_code} - Trying fallback...")
            # Fallback to main page
            resp = requests.get(f"https://www.instagram.com/{username}/", headers=headers, timeout=15)
            if resp.status_code != 200:
                return None
            # Limited parsing
            user = {}
        
        if not user:
            return None
        
        profile_data = {
            "username": user.get("username", username),
            "full_name": user.get("full_name", ""),
            "bio": user.get("biography", ""),
            "profile_pic": user.get("profile_pic_url_hd") or user.get("profile_pic_url", ""),
            "followers": user.get("edge_followed_by", {}).get("count", 0),
            "following": user.get("edge_follow", {}).get("count", 0),
            "is_private": user.get("is_private", False),
            "is_verified": user.get("is_verified", False),
            "external_url": user.get("external_url", ""),
            "hashtags": re.findall(r'#\w+', user.get("biography", "")),
            "email": None,
            "phone": None,
        }
        
        # Extract contacts from bio
        bio = user.get("biography", "")
        if bio:
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', bio)
            if emails:
                profile_data["email"] = emails[0]
            phones = re.findall(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{8,}', bio)
            if phones:
                profile_data["phone"] = phones[0]
        
        return profile_data
    
    except Exception as e:
        st.error(f"Fetch error: {e}")
        return None

# ====================== UI ======================
url_input = st.text_input(
    "Instagram Profile URL or Username",
    placeholder="https://www.instagram.com/ashyrakaelith/ or ashyrakaelith",
    value="https://www.instagram.com/ashyrakaelith/",
    key="fetch_input"
)

if st.button("🔍 Fetch Profile", type="primary"):
    username = extract_username(url_input)
    if not username:
        st.error("Please enter a valid username or URL")
    else:
        with st.spinner(f"Fetching @{username}..."):
            data = fetch_public_profile(username)
            if data:
                col1, col2 = st.columns([1, 2])
                with col1:
                    if data.get("profile_pic"):
                        try:
                            resp = requests.get(data["profile_pic"], timeout=15)
                            if resp.status_code == 200:
                                st.image(Image.open(BytesIO(resp.content)), width=240)
                            else:
                                st.image(data["profile_pic"], width=240)
                        except:
                            st.image(data["profile_pic"], width=240)
                
                with col2:
                    st.subheader(data["full_name"] or username)
                    st.markdown(f"**@{data['username']}**")
                    st.write(f"**Bio:** {data.get('bio') or '—'}")
                    st.write(f"**Followers:** {data.get('followers', 0):,} | **Following:** {data.get('following', 0):,}")
                    st.write(f"**Account:** {'🔒 Private' if data.get('is_private') else '🌍 Public'}")
                    st.write(f"**Verified:** {'✅ Yes' if data.get('is_verified') else 'No'}")
                    
                    if data.get("external_url"):
                        st.write(f"**Link:** {data['external_url']}")
                    if data.get("email"):
                        st.write(f"**Email:** {data['email']}")
                    if data.get("phone"):
                        st.write(f"**Phone:** {data['phone']}")
                    if data.get("hashtags"):
                        st.write("**Hashtags:**", " ".join(data["hashtags"]))
                
                st.success("✅ Profile data fetched!")
                with st.expander("Raw Data"):
                    st.json(data)
            else:
                st.error("❌ Could not fetch profile. The account may be private or Instagram is blocking requests.")

st.caption("Works best for **public accounts**. Private accounts show only basic info.")
st.info("If it still fails, try a VPN or wait a few minutes.")