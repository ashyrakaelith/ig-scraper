import re
import time
import json
import requests
import pandas as pd
import streamlit as st
from PIL import Image
from io import BytesIO

# ==========================================
# PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="IG Intel | Advanced Deep Scraper", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
        .metric-card {
            background-color: #f8f9fa !important;
            border: 1px solid #e9ecef !important;
            border-radius: 12px !important;
            padding: 1.25rem !important;
            text-align: center !important;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05) !important;
        }
        html[data-theme="dark"] .metric-card { background-color: #f8f9fa !important; border: 1px solid #e9ecef !important; }
        .metric-label { color: #6c757d !important; font-weight: 600 !important; font-size: 0.9rem !important; text-transform: uppercase !important; display: block !important; }
        .metric-value { margin: 0 !important; color: #1a1d20 !important; font-weight: 700 !important; font-size: 1.8rem !important; }
        .status-badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 50px; font-size: 0.85rem; font-weight: 600; margin-right: 0.5rem; margin-bottom: 0.5rem; }
        .badge-verified { background-color: #e3f2fd; color: #0d47a1; }
        .badge-public { background-color: #e8f5e9; color: #1b5e20; }
        .badge-private { background-color: #ffebee; color: #b71c1c; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# ADVANCED EXTRACTION ENGINE
# ==========================================
def extract_username(input_str: str) -> str:
    if not input_str:
        return ""
    input_str = input_str.strip().lower()
    if "instagram.com" in input_str:
        username = re.sub(r'https?://(www\.)?instagram\.com/', '', input_str)
        username = username.split('/')[0].split('?')[0].strip()
        return username
    return input_str

def fetch_recent_posts_and_hashtags(user_id: str, sessionid: str = None, proxy: str = None):
    TIMELINE_QUERY_HASH = "8845758582119845" 
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "X-IG-App-ID": "936619743392459"
    }
    if sessionid:
        headers["Cookie"] = f"sessionid={sessionid.strip()};"
        
    proxies = {"http": proxy, "https": proxy} if proxy else None
    variables = {"id": user_id, "first": 15}
    encoded_vars = requests.utils.quote(json.dumps(variables))
    
    url = f"https://www.instagram.com/graphql/query/?query_hash={TIMELINE_QUERY_HASH}&variables={encoded_vars}"
    tags = []
    
    try:
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            edges = data.get("data", {}).get("user", {}).get("edge_owner_to_timeline_media", {}).get("edges", [])
            for edge in edges:
                node = edge.get("node", {})
                caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
                if caption_edges:
                    text = caption_edges[0].get("node", {}).get("text", "")
                    if text:
                        tags.extend(re.findall(r'#\w+', text))
    except Exception:
        pass
    return sorted(list(set([t.lower() for t in tags])))

def fetch_profile_base(username: str, sessionid: str = None, proxy: str = None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "X-IG-App-ID": "936619743392459",
        "Referer": f"https://www.instagram.com/{username}/"
    }
    if sessionid:
        headers["Cookie"] = f"sessionid={sessionid.strip()};"
        
    proxies = {"http": proxy, "https": proxy} if proxy else None
    
    try:
        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=20)
        
        if resp.status_code == 200:
            user = resp.json().get("data", {}).get("user", {})
            if user:
                bio_text = user.get("biography", "")
                post_hashtags = []
                
                # Check initial web response node
                timeline_media = user.get("edge_owner_to_timeline_media", {})
                posts_nodes = timeline_media.get("edges", [])
                
                for edge in posts_nodes:
                    node = edge.get("node", {})
                    caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
                    if caption_edges:
                        caption_text = caption_edges[0].get("node", {}).get("text", "")
                        if caption_text:
                            post_hashtags.extend(re.findall(r'#\w+', caption_text))
                
                unique_post_tags = sorted(list(set([tag.lower() for tag in post_hashtags])))
                bio_tags = sorted(list(set([tag.lower() for tag in re.findall(r'#\w+', bio_text)])))
                
                if not unique_post_tags and user.get("id"):
                    unique_post_tags = fetch_recent_posts_and_hashtags(user.get("id"), sessionid, proxy)

                # Extract explicit business email setups
                emails_found = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', bio_text)
                detected_email = emails_found[0] if emails_found else (user.get("business_email") or "None Disclosed")

                # ADDED: Extract public external web links
                links_extracted = []
                bio_links_nodes = user.get("bio_links", [])
                for link in bio_links_nodes:
                    url_val = link.get("url")
                    if url_val:
                        links_extracted.append(url_val)
                if user.get("external_url"):
                    links_extracted.append(user.get("external_url"))
                unique_links = list(set(links_extracted))

                # ADDED: Safe phone number metadata extraction extraction
                phone_country = user.get("public_phone_country_code", "")
                phone_num = user.get("public_phone_number", "") or user.get("contact_phone_number", "")
                full_mobile = f"+{phone_country} {phone_num}".strip() if phone_num else "None Publicly Disclosed"

                return {
                    "id": user.get("id"),
                    "username": user.get("username"),
                    "full_name": user.get("full_name"),
                    "bio": bio_text,
                    "profile_pic": user.get("profile_pic_url_hd") or user.get("profile_pic_url"),
                    "followers": user.get("edge_followed_by", {}).get("count", 0),
                    "following": user.get("edge_follow", {}).get("count", 0),
                    "total_posts": timeline_media.get("count", 0),
                    "is_private": user.get("is_private", False),
                    "is_verified": user.get("is_verified", False),
                    "email": detected_email,
                    "mobile": full_mobile,
                    "public_links": unique_links,
                    "bio_hashtags": bio_tags,
                    "posted_hashtags": unique_post_tags
                }
    except Exception as e:
        st.error(f"Base lookup run fault: {e}")
    return None

def fetch_relation_list(user_id: str, list_type: str, max_records: int, sessionid: str, proxy: str = None):
    endpoint_part = "followers" if list_type == "followers" else "following"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "X-IG-App-ID": "936619743392459",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": f"sessionid={sessionid.strip()};"
    }
    proxies = {"http": proxy, "https": proxy} if proxy else None
    results = []
    has_next = True
    next_max_id = ""
    
    if not sessionid:
        st.warning(f"⚠️ SessionID required to generate list elements for {list_type}.")
        return []

    while has_next and len(results) < max_records:
        url = f"https://i.instagram.com/api/v1/friendships/{user_id}/{endpoint_part}/"
        params = {"count": 50}
        if next_max_id:
            params["max_id"] = next_max_id
            
        try:
            resp = requests.get(url, headers=headers, params=params, proxies=proxies, timeout=15)
            if resp.status_code != 200:
                break
            data = resp.json()
            users = data.get("users", [])
            if not users:
                break
                
            for user in users:
                results.append({
                    "User ID": user.get("pk_id") or user.get("pk"),
                    "Username": user.get("username"),
                    "Full Name": user.get("full_name"),
                    "Profile Pic Link": user.get("profile_pic_url"),
                    "Verified Status": "✅ Yes" if user.get("is_verified") else "No",
                    "Is Private": "🔒 Yes" if user.get("is_private") else "No"
                })
                if len(results) >= max_records:
                    break
                    
            next_max_id = data.get("next_max_id", "")
            has_next = bool(next_max_id)
            time.sleep(2.0)
        except Exception:
            break
            
    return results

# ==========================================
# SIDEBAR CONFIGURATION MODAL
# ==========================================
with st.sidebar:
    st.header("⚙️ Data Options")
    sessionid = st.text_input("SessionID Cookie (Mandatory for lists)", placeholder="Paste sessionid...", type="password")
    proxy = st.text_input("Proxy Server Connection", placeholder="http://ip:port")
    
    st.write("---")
    st.subheader("List Limits")
    record_limit = st.slider("Max deep entries to fetch", min_value=10, max_value=200, value=50, step=10)

# ==========================================
# MAIN RUNTIME INTERFACE
# ==========================================
st.title("📸 IG Intel: Advanced Deep Scraper")

col_input, col_btn = st.columns([4, 1], vertical_alignment="bottom")
with col_input:
    url_input = st.text_input("Target Profile Username or Complete URL", placeholder="e.g., nasa")
with col_btn:
    trigger_fetch = st.button("🔍 Fetch Profile & Connections", type="primary", width="stretch")

st.write("---")

if trigger_fetch:
    username = extract_username(url_input)
    if not username:
        st.toast("⚠️ Input missing.", icon="❌")
    else:
        with st.status(f"Querying Instagram Pipelines for @{username}...", expanded=True) as status_box:
            data = fetch_profile_base(username, sessionid.strip() if sessionid else None, proxy.strip() if proxy else None)
            
            if data:
                layout_left, layout_right = st.columns([1, 2.5], gap="large")
                with layout_left:
                    if data.get("profile_pic"):
                        try:
                            r = requests.get(data["profile_pic"], timeout=15)
                            st.image(Image.open(BytesIO(r.content)), width="stretch")
                        except:
                            st.image(data["profile_pic"], width="stretch")
                
                with layout_right:
                    st.subheader(data["full_name"] or data["username"])
                    badge_html = f"<span class='status-badge badge-public'>@{data['username']}</span>"
                    if data.get("is_verified"): badge_html += "<span class='status-badge badge-verified'>✓ Verified</span>"
                    badge_html += f"<span class='status-badge badge-private'>🔒 Private</span>" if data.get("is_private") else f"<span class='status-badge badge-public'>🌍 Public</span>"
                    st.markdown(badge_html, unsafe_allow_html=True)
                    
                    m_col1, m_col2, m_col3 = st.columns(3)
                    with m_col1:
                        st.markdown(f'<div class="metric-card"><span class="metric-label">Followers</span><h3 class="metric-value">{data.get("followers", 0):,}</h3></div>', unsafe_allow_html=True)
                    with m_col2:
                        st.markdown(f'<div class="metric-card"><span class="metric-label">Following</span><h3 class="metric-value">{data.get("following", 0):,}</h3></div>', unsafe_allow_html=True)
                    with m_col3:
                        st.markdown(f'<div class="metric-card"><span class="metric-label">Total Posts</span><h3 class="metric-value">{data.get("total_posts", 0):,}</h3></div>', unsafe_allow_html=True)
                        
                    st.write("") 
                    st.markdown(f"✉️ **Public Contact Email:** `{data.get('email')}`")
                    st.markdown(f"📞 **Public Mobile Number:** `{data.get('mobile')}`")
                    
                    # ADDED: Dynamic presentation section for extracted links
                    if data.get("public_links"):
                        st.markdown("**🔗 Public Profile Links:**")
                        for url_link in data["public_links"]:
                            st.markdown(f"- [{url_link}]({url_link})")
                    else:
                        st.markdown("🔗 **Public Profile Links:** _No external links assigned._")
                        
                    st.write("---")
                    st.markdown(f"**Bio Details:** \n{data.get('bio') or '_No biography text set._'}")
                    
                    if data.get("bio_hashtags"):
                        b_tags = " ".join([f"`{t}`" for t in data["bio_hashtags"]])
                        st.markdown(f"🧬 **Bio Hashtags:** {b_tags}")
                    
                    if data.get("posted_hashtags"):
                        p_tags = " ".join([f"`{t}`" for t in data["posted_hashtags"]])
                        st.markdown(f"📝 **Hashtags From Recent Posts:** {p_tags}")
                    else:
                        st.markdown("📝 **Hashtags From Recent Posts:** _None parsed from latest public feed._")

                if not data["is_private"] or sessionid:
                    st.write("---")
                    st.subheader("📋 Relationship Deep-Data Extracted Data")
                    
                    tab1, tab2 = st.tabs(["👥 Followers List", "👤 Following List"])
                    
                    with tab1:
                        st.write(f"Pulling recent followers (capped to {record_limit} records)...")
                        followers_list = fetch_relation_list(data["id"], "followers", record_limit, sessionid, proxy)
                        if followers_list:
                            df_followers = pd.DataFrame(followers_list)
                            st.dataframe(df_followers, width="stretch")
                            st.download_button("📥 Export Followers CSV", data=df_followers.to_csv(index=False), file_name=f"{username}_followers.csv", mime="text/csv")
                        else:
                            st.info("No interactive follower logs extracted. Ensure your SessionID input is validated.")
                            
                    with tab2:
                        st.write(f"Pulling recent following list (capped to {record_limit} records)...")
                        following_list = fetch_relation_list(data["id"], "following", record_limit, sessionid, proxy)
                        if following_list:
                            df_following = pd.DataFrame(following_list)
                            st.dataframe(df_following, width="stretch")
                            st.download_button("📥 Export Following CSV", data=df_following.to_csv(index=False), file_name=f"{username}_following.csv", mime="text/csv")
                        else:
                            st.info("No following connection arrays extracted.")
                else:
                    st.error("🔒 Cannot extract connection arrays on Private accounts without authorization credentials.")
                
                status_box.update(label="Complete compilation run succeeded!", state="complete", expanded=False)
            else:
                st.error("Failed to construct profile layout nodes.")
