# 📸 IG Intel: Advanced Deep Scraper & Recon Dashboard

A professional, modern Streamlit OSINT dashboard designed for deep public data parsing, engagement metrics auditing, connection graph analysis, and hashtag intelligence extraction on public Instagram profiles. 

Built around a secure, direct-to-API transaction workflow that avoids fragile front-end scrapers by utilizing direct internal GraphQL fallback nodes.

---

## ✨ Key Capabilities & Layout Framework

* **🔒 Adaptive Authentication Layer:** Works anonymously for high-level public sweeps; integrates browser session tokens safely via an isolated sidebar panel to bypass deep page-load hurdles.
* **📊 High-Contrast KPI Analytics Row:** Custom structural metric widgets showing **Follower Count**, **Following Count**, and **Total Posts**, fully hardened with `!important` CSS overrides to ensure perfect legibility in both light and dark mode templates.
* **🏷️ Dual-Layer Hashtag Extraction:** * `🧬 Bio Hashtags`: Isolated straight from the target’s static profile presentation string.
  * `📝 Posted Hashtags`: Deep-combed from recent timeline entries and reel captions using standard transaction fallback hashes to guarantee complete visibility.
* **📞 Intel & Contact Data Surface:** Extracts hidden creator profile parameters including **Public Business Emails**, **Mobile Contact Numbers** (with international country dialing prefixes), and the full collection of embedded **Bio URLs** (Linktrees, external platforms).
* **👥 Graph Connection Enumerator Tables:** Extracts large, paginated collections of recent followers and following lists, instantly parsing them into an interactive tabular layout (`st.dataframe`) complete with native string-filtering, multi-column sorting, and **one-click CSV data exports**.

---

## 🛠️ System Configuration & Local Deployment

### 1. Project Directory Installation
Ensure you have Python 3.10+ deployed on your host environment. Pull the file structure down into your working shell:

```bash
mkdir ig-intel-scraper && cd ig-intel-scraper
```

### 2. Dependency Resolution
Create a local python virtual environment and deploy the explicit external dependencies requested by the system framework:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

pip install streamlit requests pandas pillow
```

### 3. File Initialization
Save your complete Streamlit script application down into the working root directory as `main.py`.

### 4. Running the Dashboard
Fire up the local Streamlit application node server engine using your terminal interface:

```bash
streamlit run main.py
```

---

## ⚙️ Operating Procedures & Session Hijacking Safeguards

For maximum extraction rates when compiling large graph relationship lists (Followers/Following data pools), it is highly advised to append an active authenticated browser cookie state.

### How to Safely Extract Your `sessionid` Cookie:
1. Open your desktop browser (Chrome, Edge, Brave, or Firefox) and navigate to [Instagram.com](https://www.instagram.com). Ensure you are logged into a valid placeholder or target profile asset.
2. Open your browser's Developer Tools console interface by pressing `F12` or hitting `Ctrl + Shift + I` (`Cmd + Option + I` on macOS).
3. Walk through the layout navigation path: **Application (or Storage)** ➔ **Cookies** ➔ Select `https://www.instagram.com`.
4. Use the interface query column to find the cookie parameter row named exactly `sessionid`.
5. Select and copy the entire string sequence inside the **Value** column panel. (Example format string: `4829104729%3AABCdef123XYZ...`).
6. Paste the alphanumeric sequence directly into the **SessionID Cookie** text field inside the left configuration panel sidebar.

> **⚠️ Security & Operation Disclaimer:** Do not copy or pass trailing flags, validation parameters, or meta indicators like the secure validation checkbox marker (`✓`). Only copy the alphanumeric string value itself.

---

## 💡 Operational Best Practices to Prevent Rate-Throttling

To protect your browser workspace sessions and circumvent structural endpoint blocking metrics deployed across Meta edge routing servers, always configure the system around these core guidelines:

1. **Throttling Delay Arrays:** The script has native back-off loop engines configured around explicit `time.sleep(2.0)` calls. Do not forcefully optimize or decrease these padding thresholds, as rapid requests will cause Instagram's firewalls to block your host IP.
2. **Proxy Integration:** When running intensive continuous checks, supply an HTTP residential rotation proxy server layout down within the configuration module inputs (`http://user:pass@ip:port`). 
3. **Account Safety:** For high-volume discovery tasks, always run your scraping workflows through alternative placeholder or testing profiles ("burner assets") rather than your personal primary accounts.

---

## 🛠️ Data Scheme Footprint

When mapping connection graph tables, the engine outputs the following relational database layout schema:

| Column Header | Data Blueprint Typology | Scope Target Description |
| :--- | :--- | :--- |
| **User ID** | Alphanumeric Unique String | The explicit internal tracking index assigned by Instagram's servers. |
| **Username** | String Text Token | Unique digital routing handle string (e.g., `@nasa`). |
| **Full Name** | Comprehensive Text | Public display identity text set by the user profile profile owner. |
| **Profile Pic Link** | Secure URL String | Direct high-resolution link routing to the CDN avatar image file. |
| **Verified Status** | Boolean Visual Token | Reflects meta verification badge checkmarks (`✅ Yes` / `No`). |
| **Is Private** | Boolean Shield Pill | Flags private profile visibility locks (`🔒 Yes` / `No`). |

---
*Dashboard Modified and Maintained by **The M0nst3r** Engine Workspace Framework.*
