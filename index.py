import re
import requests
import streamlit as st
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="IG Public Data Tool", layout="centered")
st.title("📸 Instagram Public Data Tool")

st.warning("**Your IP seems blocked.** Use proxy / VPN / mobile hotspot below.")

def extract_username(input_str: str) -> str:
    if not input_str:
        return ""
    input_str = input_str.strip().lower()
    if "instagram.com" in input_str:
        username = re.sub(r'https?://(www\.)?instagram\.com/', '', input_str)
        username = username.split('/')[0].split('?')[0].strip()
        return username
    return input_str

def fetch_profile(username: str, sessionid: str = None, proxy: str = None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "X-IG-App-ID": "936619743392459",
        "Referer": f"https://www.instagram.com/{username}/"
    }
    
    if sessionid:
        headers["Cookie"] = f"sessionid={sessionid};"
    
    proxies = {"http": proxy, "https": proxy} if proxy else None
    
    try:
        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=20)
        
        if resp.status_code == 200:
            data = resp.json()
            user = data.get("data", {}).get("user", {})
            if user:
                return {
                    "username": user.get("username"),
                    "full_name": user.get("full_name"),
                    "bio": user.get("biography"),
                    "profile_pic": user.get("profile_pic_url_hd") or user.get("profile_pic_url"),
                    "followers": user.get("edge_followed_by", {}).get("count", 0),
                    "following": user.get("edge_follow", {}).get("count", 0),
                    "is_private": user.get("is_private", False),
                    "is_verified": user.get("is_verified", False),
                    "external_url": user.get("external_url"),
                    "hashtags": re.findall(r'#\w+', user.get("biography", "")),
                }
        else:
            st.error(f"Status Code: {resp.status_code}")
    except Exception as e:
        st.error(f"Request failed: {e}")
    return None

# ====================== UI ======================
url_input = st.text_input(
    "Instagram Profile URL or Username",
    placeholder="https://www.instagram.com/ashyrakaelith/",
    value="https://www.instagram.com/ashyrakaelith/"
)

sessionid = st.text_input(
    "sessionid Cookie (Optional but Recommended)",
    placeholder="Paste sessionid from browser",
    type="password"
)

proxy = st.text_input(
    "Proxy (Optional) - Format: http://ip:port or http://user:pass@ip:port",
    placeholder="http://123.45.67.89:8080",
    help="Use residential/mobile proxies for best results"
)

if st.button("🔍 Fetch Profile", type="primary"):
    username = extract_username(url_input)
    if not username:
        st.error("Enter username or URL")
    else:
        with st.spinner(f"Fetching @{username}..."):
            data = fetch_profile(username, sessionid.strip() if sessionid else None, proxy.strip() if proxy else None)
            
            if data:
                col1, col2 = st.columns([1, 2])
                with col1:
                    if data.get("profile_pic"):
                        try:
                            r = requests.get(data["profile_pic"], timeout=15)
                            st.image(Image.open(BytesIO(r.content)), width=240)
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
                    if data.get("hashtags"):
                        st.write("**Hashtags:**", " ".join(data["hashtags"]))
                
                st.success("✅ Success!")
                with st.expander("Raw Data"):
                    st.json(data)
            else:
                st.error("Failed. Try different proxy / VPN / sessionid.")

st.divider()
st.subheader("How to get sessionid?")
st.markdown("1. Login to Instagram in Chrome → F12 → Application → Cookies → instagram.com → Copy `sessionid` value")

st.caption("**Best combination**: Mobile Hotspot + sessionid + residential proxy")
