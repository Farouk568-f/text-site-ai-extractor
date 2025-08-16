# --- المكتبات الأساسية ---
import sys
import io
import re
import urllib.parse
from urllib.parse import urljoin, quote_plus
import requests
from bs4 import BeautifulSoup
import json
import subprocess
import difflib
import asyncio
import base64

# --- مكتبات الـ API والبروكسي ---
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
try:
    from pyngrok import ngrok
except ImportError:
    sys.stderr.write("WARN: pyngrok not installed. API will be local only. Run: pip install pyngrok\n")
    ngrok = None

# --- مكتبات التشغيل الآلي للمتصفح (لـ VeloraTV) ---
try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    sys.stderr.write("WARN: Playwright not installed. The 'veloratv' provider will not work. Run: pip install playwright && playwright install\n")
    class PlaywrightTimeoutError(Exception): pass
    async_playwright = None

# --- مكتبة الذكاء الاصطناعي (لـ Akwam) ---
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    
# --- مكتبات إضافية للمزود الجديد ---
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# --- [تهيئة قوية للترميز] ---
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
except (TypeError, AttributeError):
    pass

# ----- الإعدادات العامة -----
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}
GEMINI_API_KEY = "" # ضع مفتاح API الخاص بك هنا
if GEMINI_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        sys.stderr.write("INFO: Gemini AI configured successfully for 'akwam' provider.\n")
    except Exception as e:
        sys.stderr.write(f"WARN: Failed to configure Gemini AI. It will be disabled. Error: {e}\n")
        GEMINI_AVAILABLE = False
else:
    GEMINI_AVAILABLE = False

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==============================================================================
# ========================   (جميع أكواد المزودين كما هي)   ========================
# ==============================================================================
# PROVIDER 1: AKWAM
def akwam_make_request(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        sys.stderr.write(f"[!] AKWAM-LOG: Request error for URL: {url}\n{e}\n")
        return None

def select_best_match_with_gemini(user_query, media_type, target_season, all_results):
    if not GEMINI_AVAILABLE:
        sys.stderr.write("INFO: AKWAM-LOG: Gemini AI not available. Selecting the first search result as a fallback.\n")
        return all_results[0] if all_results else None
    model = genai.GenerativeModel('gemini-1.5-flash')
    formatted_results = "\n".join([f"id:{i}, title:\"{res['title']}\", url:\"{res['url']}\"" for i, res in enumerate(all_results)])
    prompt = f"""You are an intelligent search result selector. Find the single best match from a list of search results.
USER'S REQUEST:
- Title: "{user_query}"
- Type: "{media_type}"
- Requested Season: {target_season or 'N/A (This is a movie)'}
SEARCH RESULTS:
{formatted_results}
INSTRUCTIONS:
1. For 'series': Your PRIMARY goal is to match the 'Requested Season'.
2. For 'movie': Find the result that most closely matches the movie title.
3. Output: MUST be a single JSON object with the ID. Example: {{"best_choice_id": <id_number>}}
"""
    try:
        response = model.generate_content(prompt)
        json_text = re.search(r'\{.*\}', response.text, re.DOTALL).group(0)
        decision = json.loads(json_text)
        best_id = int(decision.get('best_choice_id'))
        if 0 <= best_id < len(all_results):
            chosen = all_results[best_id]
            sys.stderr.write(f"INFO: AKWAM-LOG: Gemini AI chose: ID {best_id}, Title \"{chosen['title']}\"\n")
            return chosen
        else: raise ValueError(f"Gemini returned an invalid ID: {best_id}")
    except Exception as e:
        sys.stderr.write(f"ERROR: AKWAM-LOG: Gemini analysis failed: {e}. Falling back to the first result.\n")
        return all_results[0] if all_results else None

def akwam_get_video_links_from_player(content_page_url):
    soup = akwam_make_request(content_page_url)
    if not soup: return []
    final_video_links = set()
    watch_page_urls = []
    quality_tabs = soup.find_all('div', class_='tab-content quality')
    AKWAM_BASE_URL = "https://ak.sv"
    for tab in quality_tabs:
        watch_link_tag = tab.find('a', class_='link-show')
        if watch_link_tag and 'href' in watch_link_tag.attrs:
            watch_id = watch_link_tag['href'].split('/')[-1]
            try:
                url_parts = content_page_url.split('/')
                content_id, content_slug = url_parts[-2], url_parts[-1]
                final_watch_url = f"{AKWAM_BASE_URL}/watch/{watch_id}/{content_id}/{content_slug}"
                watch_page_urls.append(final_watch_url)
            except IndexError: continue
    if not watch_page_urls: return []
    for url in set(watch_page_urls):
        player_soup = akwam_make_request(url)
        if not player_soup: continue
        video_tag = player_soup.find('video', id='player')
        if video_tag:
            for source in video_tag.find_all('source'):
                if source.get('src'):
                    final_video_links.add((source.get('size', 'N/A'), source['src']))
    return [{"quality": quality, "url": link, "needs_proxy": False} for quality, link in sorted(list(final_video_links), key=lambda x: int(x[0]) if x[0].isdigit() else 0, reverse=True)]

def akwam_find_episode_on_season_page(season_url, episode_number):
    season_soup = akwam_make_request(season_url)
    if not season_soup: return None
    episodes_map = {}
    episode_containers = season_soup.find_all('div', class_='bg-primary2')
    episode_pattern = re.compile(r'(?:الحلقة|حلقة)\s*(\d{1,3})', re.IGNORECASE)
    for container in episode_containers:
        h2_tag = container.find('h2')
        if not h2_tag: continue
        title_tag = h2_tag.find('a')
        if title_tag and title_tag.get('href'):
            full_title = ' '.join(title_tag.text.strip().split())
            match = episode_pattern.search(full_title)
            if match:
                ep_num = int(match.group(1))
                episodes_map[ep_num] = {'url': title_tag['href'], 'title': full_title}
    found_episode = episodes_map.get(episode_number)
    return found_episode['url'] if found_episode else None

def scrape_akwam(query, media_type, season_num, episode_num):
    sys.stderr.write(f"[*] AKWAM-LOG: Starting scrape for '{query}'...\n")
    AKWAM_BASE_URL = "https://ak.sv"
    search_query_encoded = urllib.parse.quote_plus(query)
    all_search_results = []
    current_page = 1
    while True:
        search_url = f"{AKWAM_BASE_URL}/search?q={search_query_encoded}&page={current_page}"
        search_soup = akwam_make_request(search_url)
        if not search_soup: break
        results_on_page = [
            {'title': tag.text.strip(), 'url': tag['href']}
            for entry in search_soup.select('div.widget-body div.entry-box-1')
            if (tag := entry.find('h3', class_='entry-title').find('a')) and tag.get('href')
        ]
        if not results_on_page: break
        all_search_results.extend(results_on_page)
        pagination_nav = search_soup.find('nav', attrs={'aria-label': 'Page navigation'})
        if pagination_nav and pagination_nav.find('a', class_='page-link', string=re.compile(r'التالي')):
            current_page += 1
        else: break
    if not all_search_results:
        return {"status": "error", "message": f"No search results found for '{query}' on Akwam."}
    selected_content = select_best_match_with_gemini(query, media_type, season_num, all_search_results)
    if not selected_content:
         return {"status": "error", "message": "AI could not determine the best match from search results on Akwam."}
    content_url = selected_content['url']
    if media_type == 'movie':
        links = akwam_get_video_links_from_player(content_url)
        return {"status": "success", "links": links} if links else {"status": "error", "message": "No direct video links found for this movie on Akwam."}
    elif media_type == 'series':
        episode_url = akwam_find_episode_on_season_page(content_url, episode_num)
        if not episode_url:
            return {"status": "error", "message": f"Could not find episode {episode_num} in the selected season on Akwam."}
        links = akwam_get_video_links_from_player(episode_url)
        return {"status": "success", "links": links} if links else {"status": "error", "message": f"No direct video links found for episode {episode_num} on Akwam."}
    return {"status": "error", "message": "Unknown content type for Akwam."}

# PROVIDER 2: VELORATV
async def velora_extract_links_from_url(url: str, context):
    VELORA_M3U8_PATTERN = re.compile(r"https://[^\s\"']+\.m3u8[^\s\"']*")
    VELORA_SUBTITLE_PATTERN = re.compile(r"https://[^\s\"']+format=srt[^\s\"']*")
    m3u8_links, subtitle_links = set(), set()
    page = await context.new_page()
    def handle_request(req):
        if VELORA_M3U8_PATTERN.search(req.url): m3u8_links.add(req.url)
        if VELORA_SUBTITLE_PATTERN.search(req.url): subtitle_links.add(req.url)
    page.on("request", handle_request)
    sys.stderr.write(f"[*] VELORA-LOG: Navigating to page {url}\n")
    try:
        await page.goto(url, timeout=60000, wait_until='domcontentloaded')
        await page.wait_for_selector("div.player-servers, iframe", timeout=15000)
        servers_to_try = ["Alpha", "Bravo", "Charlie"]
        for server in servers_to_try:
            try:
                sys.stderr.write(f"[*] VELORA-LOG: Trying server '{server}'...\n")
                await page.get_by_text(server, exact=True).click(timeout=5000)
                await page.wait_for_timeout(3000)
                if m3u8_links:
                    sys.stderr.write(f"[*] VELORA-LOG: Success! Found m3u8 link(s) from server '{server}'.\n")
                    break
            except Exception as e:
                sys.stderr.write(f"[!] VELORA-LOG: Error with server '{server}': {e}\n")
    except Exception as e:
         sys.stderr.write(f"[!] VELORA-LOG: Failed during page navigation: {e}\n")
    finally:
        await page.close()
    return m3u8_links, subtitle_links

async def velora_async_main(watch_url):
    if not async_playwright: return set(), set()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=HEADERS['User-Agent'])
        return await velora_extract_links_from_url(watch_url, context)

def scrape_veloratv(media_type, season, episode, tmdb_id):
    watch_url = f"https://veloratv.ru/watch/{'movie' if media_type == 'movie' else f'tv/{tmdb_id}/{season}/{episode}'}/{tmdb_id}"
    try:
        m3u8_links, subtitle_links = asyncio.run(velora_async_main(watch_url))
        if not m3u8_links:
            return {"status": "error", "message": "No m3u8 links found on VeloraTV."}
        response = {"status": "success", "links": [{"quality": "proxied_m3u8", "url": link, "needs_proxy": True} for link in m3u8_links]}
        if subtitle_links:
            response["subtitles"] = [{"lang": "ar", "url": sub} for sub in subtitle_links]
        return response
    except Exception as e:
        return {"status": "error", "message": f"VeloraTV provider error: {e}"}

# PROVIDER 3: AFLAM
def aflam_get_best_match(query, results):
    titles = list(results.keys())
    best_matches = difflib.get_close_matches(query, titles, n=1, cutoff=0.5)
    if best_matches:
        best_title = best_matches[0]
        sys.stderr.write(f"[*] AFLAM-LOG: Best match for '{query}' is '{best_title}'\n")
        return {'title': best_title, 'url': results[best_title]}
    return None

def aflam_get_video_servers(content_url, session):
    links = []
    try:
        sys.stderr.write(f"[*] AFLAM-LOG: Getting servers from {content_url}\n")
        post_headers = HEADERS.copy()
        post_headers['Referer'] = content_url
        response = session.post(content_url, headers=post_headers, data={'watch': '1'}, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        servers_list = soup.find('ul', id='watch-servers-list')
        if not servers_list: return []
        for server_item in servers_list.find_all('li'):
            encoded_url = server_item.get('data-encoded')
            if not encoded_url: continue
            try:
                iframe_src = base64.b64decode(encoded_url).decode('utf-8')
                sys.stderr.write(f"[*] AFLAM-LOG: Processing server iframe: {iframe_src}\n")
                command = ['yt-dlp', '-g', '--no-warnings', iframe_src]
                result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', timeout=45)
                direct_link = result.stdout.strip().split('\n')[0]
                if direct_link.startswith('http'):
                    links.append({"quality": "Direct MP4", "url": direct_link, "needs_proxy": False})
            except Exception as e:
                sys.stderr.write(f"[!] AFLAM-LOG: Failed to process a server: {e}\n")
    except requests.exceptions.RequestException as e:
        sys.stderr.write(f"[!] AFLAM-LOG: Network error getting servers: {e}\n")
    return links

def aflam_handle_series(page_soup, episode_num, session):
    sys.stderr.write(f"[*] AFLAM-LOG: Looking for episode number {episode_num}\n")
    episode_links = page_soup.select('div.EpisodesArea div.bg-primary2 h2 a')
    episode_pattern = re.compile(r'(?:الحلقة|حلقة)\s*(\d+)')
    for link_tag in episode_links:
        title = link_tag.get_text(strip=True)
        match = episode_pattern.search(title)
        if match and int(match.group(1)) == episode_num:
            sys.stderr.write(f"[*] AFLAM-LOG: Found match: '{title}' -> {link_tag['href']}\n")
            return aflam_get_video_servers(link_tag['href'], session)
    sys.stderr.write(f"[!] AFLAM-LOG: Episode {episode_num} not found in the list.\n")
    return []

def scrape_aflam(query, media_type, episode_num):
    sys.stderr.write(f"[*] AFLAM-LOG: Starting scrape for '{query}'...\n")
    AFLAM_BASE_URL = "https://afllam.onl"
    session = requests.Session()
    session.headers.update(HEADERS)
    search_url = f"{AFLAM_BASE_URL}/?s={urllib.parse.quote(query)}"
    try:
        response = session.get(search_url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        entries = soup.select('div.widget-body .entry-box-1')
        if not entries: return {"status": "error", "message": "No search results on Aflam.onl."}
        results_map = {}
        for entry in entries:
            link_tag = entry.select_one('h3.entry-title a')
            if link_tag and link_tag.has_attr('href'):
                 results_map[link_tag.text.strip()] = link_tag['href']
        if not results_map: return {"status": "error", "message": "Could not parse search results on Aflam.onl."}
        best_match = aflam_get_best_match(query, results_map)
        if not best_match: return {"status": "error", "message": "No close match found in search results on Aflam.onl."}
        page_url = best_match['url']
        response = session.get(page_url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        if soup.find('div', class_='EpisodesArea'):
            links = aflam_handle_series(soup, episode_num, session)
        else:
            links = aflam_get_video_servers(page_url, session)
        if links:
            return {"status": "success", "links": links}
        else:
            return {"status": "error", "message": "Could not extract final video links from Aflam.onl."}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred with Aflam.onl provider: {e}"}

# PROVIDER 4: RISTOANIME
def risto_extract_stream_link(embed_url, referer_url):
    if not embed_url or not referer_url: return None
    command = ['yt-dlp', '-g', '--referer', referer_url, embed_url]
    try:
        sys.stderr.write(f"[*] RISTO-LOG: Running yt-dlp on {embed_url}\n")
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', timeout=60)
        stream_links = result.stdout.strip().split('\n')
        for link in reversed(stream_links):
            if "m3u8" in link or "mp4" in link: return link
    except Exception as e:
        sys.stderr.write(f"[!] RISTO-LOG: yt-dlp failed: {e}\n")
    return None

def scrape_ristoanime(query, season_num, episode_num):
    sys.stderr.write(f"[*] RISTO-LOG: Starting scrape for '{query}' S{season_num}E{episode_num}\n")
    RISTO_BASE_URL = "https://ristoanime.org"
    RISTO_AJAX_URL = f"{RISTO_BASE_URL}/wp-content/themes/TopAnime/Ajaxt/Single/Episodes.php"
    session = requests.Session()
    session.headers.update(HEADERS)
    try:
        search_url = f"{RISTO_BASE_URL}/?s={urllib.parse.quote_plus(query)}"
        res = session.get(search_url, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        search_results = soup.select('div.MovieItem a')
        if not search_results: return {"status": "error", "message": "Anime not found on Ristoanime."}
        series_url = search_results[0]['href']
        sys.stderr.write(f"[*] RISTO-LOG: Found anime page: {series_url}\n")
        res = session.get(series_url, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        season_tabs = soup.select('div.SeasonsList ul li a')
        episodes_html = ""
        target_season_name_pattern = re.compile(f'(الموسم|موسم)\\s*{season_num}')
        season_found = False
        if season_tabs:
            for tab in season_tabs:
                if target_season_name_pattern.search(tab.get_text(strip=True)):
                    sys.stderr.write(f"[*] RISTO-LOG: Found season {season_num}, fetching episodes via AJAX.\n")
                    payload = {'season': tab['data-season']}
                    ajax_res = session.post(RISTO_AJAX_URL, data=payload, timeout=15)
                    ajax_res.raise_for_status()
                    episodes_html = ajax_res.text
                    season_found = True
                    break
        if not season_found:
             episode_list_element = soup.select_one('div.EpisodesList')
             if episode_list_element:
                 episodes_html = str(episode_list_element)
                 sys.stderr.write(f"[*] RISTO-LOG: Using main episode list for season {season_num}.\n")
        if not episodes_html: return {"status": "error", "message": f"Could not find season {season_num}."}
        episodes_soup = BeautifulSoup(episodes_html, 'html.parser')
        episode_links = episodes_soup.select('a')
        episode_pattern = re.compile(r'(?:الحلقة|حلقة)\s*(\d+)')
        episode_url = None
        for link in episode_links:
            match = episode_pattern.search(link.get_text(strip=True))
            if match and int(match.group(1)) == episode_num:
                episode_url = link['href']
                sys.stderr.write(f"[*] RISTO-LOG: Found episode {episode_num} link: {episode_url}\n")
                break
        if not episode_url: return {"status": "error", "message": f"Could not find episode {episode_num} in season {season_num}."}
        watch_page_url = episode_url.strip('/') + '/watch/'
        res = session.get(watch_page_url, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        server = soup.select_one('ul#watch li[data-watch*="sendvid.com"], ul#watch li[data-watch*="vidmoly.net"], ul#watch li[data-watch]')
        if not server: return {"status": "error", "message": "No watch servers found on the page."}
        embed_url = server['data-watch']
        final_link = risto_extract_stream_link(embed_url, watch_page_url)
        if final_link:
            return {"status": "success", "links": [{"quality": "proxied_m3u8", "url": final_link, "needs_proxy": True}]}
        else:
            return {"status": "error", "message": "Failed to extract final stream link using yt-dlp."}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred with Ristoanime provider: {e}"}

# ==============================================================================
# ===================   PROVIDER 5: ARABIC-TOONS (نسخة مطورة)   =================
# ==============================================================================
ATOONS_BASE_URL = "https://www.arabic-toons.com/"
ATOONS_WORKER_URL = "https://snowy-term-f692.itsyassine16.workers.dev/"
atoons_ua = UserAgent()

def atoons_create_robust_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        'User-Agent': atoons_ua.random,
        'Referer': ATOONS_BASE_URL
    })
    return session

def atoons_fetch_via_worker(session, url_to_fetch):
    sys.stderr.write(f"[*] ATOONS-LOG: Fetching via Worker: {url_to_fetch[:70]}...\n")
    try:
        response = session.get(ATOONS_WORKER_URL, params={"url": url_to_fetch}, timeout=20)
        response.raise_for_status()
        response.encoding = 'utf-8' # فرض ترميز UTF-8
        return response.text
    except requests.exceptions.RequestException as e:
        sys.stderr.write(f"[!] ATOONS-LOG: Worker fetch failed: {e}\n")
        return None

def atoons_get_m3u8_direct(session, episode_path):
    episode_url = ATOONS_BASE_URL + episode_path
    sys.stderr.write(f"[*] ATOONS-LOG: Fetching direct: {episode_url[:70]}...\n")
    try:
        resp = session.get(episode_url, timeout=20)
        resp.raise_for_status()
        html = resp.text
        direct_match = re.search(r'yB0hQ\s*=\s*`([^`]+\.m3u8[^`]*)`', html)
        if direct_match: return direct_match.group(1)
        parts_match = re.search(r'x9zFqV3\s*=\s*\{([^}]+)\}', html)
        if parts_match:
            parts_text = parts_match.group(1)
            parts = dict(re.findall(r'(\w+):\s*"([^"]+)"', parts_text))
            if all(k in parts for k in ("jC1kO", "hF3nV", "iA5pX", "tN4qY")):
                return f"{parts['jC1kO']}://{parts['hF3nV']}/{parts['iA5pX']}?{parts['tN4qY']}"
        return None
    except requests.exceptions.RequestException as e:
        sys.stderr.write(f"[!] ATOONS-LOG: Direct fetch failed: {e}\n")
        return None

def atoons_select_best_season_match(query, season_num, search_results):
    """
    يختار أفضل نتيجة بحث بناءً على تشابه الاسم وتطابق رقم الموسم.
    """
    best_match = {'path': None, 'score': -1, 'title': ''}
    season_pattern = re.compile(r'(?:الموسم|الجزء|موسم|جزء)\s*(\d+)')

    for item in search_results:
        title = item.get_text(strip=True).replace(item.find('span').get_text(strip=True), '').strip()
        path = item['href']
        
        similarity_score = difflib.SequenceMatcher(None, query, title).ratio()
        
        match = season_pattern.search(title)
        
        if match:
            found_season = int(match.group(1))
            if found_season == season_num:
                similarity_score += 1.0
        elif season_num == 1:
            similarity_score += 0.8

        sys.stderr.write(f"[*] ATOONS-LOG: Evaluating '{title}' -> Score: {similarity_score:.2f}\n")

        if similarity_score > best_match['score']:
            best_match['score'] = similarity_score
            best_match['path'] = path
            best_match['title'] = title
    
    return best_match

def scrape_arabic_toons(query, season_num, episode_num):
    sys.stderr.write(f"[*] ATOONS-LOG: Starting scrape for '{query}' S{season_num}E{episode_num}\n")
    session = atoons_create_robust_session()

    search_url = f"{ATOONS_BASE_URL}livesearch.php?q={urllib.parse.quote(query)}"
    search_html = atoons_fetch_via_worker(session, search_url)
    if not search_html:
        return {"status": "error", "message": "Failed to get search results from Arabic-Toons."}

    search_soup = BeautifulSoup(search_html, 'html.parser')
    search_results = search_soup.find_all('a', class_='list-group-item')
    if not search_results:
        return {"status": "error", "message": f"No search results found for '{query}' on Arabic-Toons."}
    
    best_match = atoons_select_best_season_match(query, season_num, search_results)
    if not best_match['path']:
        return {"status": "error", "message": f"Could not find a matching result for Season {season_num}."}

    selected_anime_path = best_match['path']
    sys.stderr.write(f"[*] ATOONS-LOG: Auto-selected best match: '{best_match['title']}' (Score: {best_match['score']:.2f})\n")

    anime_url = ATOONS_BASE_URL + selected_anime_path
    episodes_html = atoons_fetch_via_worker(session, anime_url)
    if not episodes_html:
        return {"status": "error", "message": "Failed to get episodes page from Arabic-Toons."}
    
    episodes_soup = BeautifulSoup(episodes_html, 'html.parser')
    movies_container = episodes_soup.find('div', class_='moviesBlocks')
    if not movies_container:
        return {"status": "error", "message": "Could not find episodes container on the page."}

    selected_episode_path = None
    episode_pattern = re.compile(r'(\d+)')
    for episode_div in movies_container.find_all('div', class_='movie'):
        link_tag = episode_div.find('a')
        if not link_tag: continue
        
        name_tag = link_tag.find('div', class_='badge-overd')
        name_text = name_tag.get_text(strip=True) if name_tag else ''
        
        match = episode_pattern.search(name_text)
        if match and int(match.group(1)) == episode_num:
            selected_episode_path = link_tag['href']
            sys.stderr.write(f"[*] ATOONS-LOG: Found episode {episode_num} link.\n")
            break

    if not selected_episode_path:
        return {"status": "error", "message": f"Could not find episode number {episode_num} for this series."}

    m3u8_link = atoons_get_m3u8_direct(session, selected_episode_path)

    if m3u8_link:
        return {"status": "success", "links": [{"quality": "Direct M3U8", "url": m3u8_link, "needs_proxy": False}]}
    else:
        return {"status": "error", "message": "Failed to extract final m3u8 link from the episode page."}

# ==============================================================================
# ======================== PROVIDER 6: SUBTITLES (Wyzie) =======================
# ==============================================================================
# تم تغيير اسم المتغير لتجنب التعارض مع المتغير العام HEADERS
SUBTITLES_HEADERS = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.7",
    "origin": "https://111movies.com",
    "priority": "u=1, i",
    "referer": "https://111movies.com/",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Brave";v="139", "Chromium";v="139"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
}

def get_subtitles_from_wyzie(content_type, tmdb_id, season=None, episode=None):
    sys.stderr.write(f"[*] SUBTITLES-LOG: Starting subtitle search for TMDB ID {tmdb_id}\n")
    # بناء الرابط
    if content_type == "movie":
        url = f"https://sub.wyzie.ru/search?id={tmdb_id}&format=srt"
    elif content_type == "tv":
        if not season or not episode:
            return {"status": "error", "message": "يجب إدخال season و episode للمسلسل"}
        url = f"https://sub.wyzie.ru/search?id={tmdb_id}&season={season}&episode={episode}&format=srt"
    else:
        return {"status": "error", "message": "type يجب أن يكون movie أو tv"}

    try:
        # إرسال الطلب
        resp = requests.get(url, headers=SUBTITLES_HEADERS, timeout=15)
        resp.raise_for_status()

        try:
            # محاولة قراءة الاستجابة كـ JSON
            data = resp.json()
        except requests.exceptions.JSONDecodeError:
            # إذا فشل، اقرأها كنص عادي
            data = resp.text
        
        sys.stderr.write(f"[*] SUBTITLES-LOG: Successfully fetched subtitles. Status: {resp.status_code}\n")
        return {"status": "success", "requested_url": url, "response_data": data}
    except requests.exceptions.RequestException as e:
        sys.stderr.write(f"[!] SUBTITLES-LOG: Request failed: {e}\n")
        return {"status": "error", "message": f"Failed to fetch subtitles: {e}"}

# ==============================================================================
# ==========================   FLASK API & PROXY   ===============================
# ==============================================================================

# PROVIDER 7: TMDB (CinePro Backend Integration)
def scrape_tmdb(media_type, tmdb_id, season=None, episode=None):
    """
    مزود TMDB جديد يستخرج من CinePro Backend
    """
    sys.stderr.write(f"[*] TMDB-LOG: Starting scrape for TMDB ID {tmdb_id}...\n")
    
    # تحديد نوع المحتوى
    if media_type == 'movie':
        endpoint = f"http://localhost:3000/movie/{tmdb_id}"
    elif media_type == 'series':
        if not season or not episode:
            return {"status": "error", "message": "Season and episode are required for series"}
        endpoint = f"http://localhost:3000/tv/{tmdb_id}?s={season}&e={episode}"
    else:
        return {"status": "error", "message": "Invalid media type. Use 'movie' or 'series'"}
    
    try:
        # إنشاء جلسة مع إعدادات محسنة
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Connection': 'keep-alive'
        })
        
        # إعداد timeout أطول وإعادة المحاولة
        session.mount('http://', HTTPAdapter(max_retries=3))
        session.mount('https://', HTTPAdapter(max_retries=3))
        
        sys.stderr.write(f"[*] TMDB-LOG: Connecting to {endpoint}...\n")
        
        # إرسال طلب إلى CinePro Backend مع timeout أطول
        response = session.get(endpoint, timeout=60, verify=False)
        response.raise_for_status()
        
        sys.stderr.write(f"[*] TMDB-LOG: Response received, status: {response.status_code}\n")
        
        data = response.json()
        
        if 'files' not in data or not data['files']:
            return {"status": "error", "message": "No media files found from TMDB provider"}
        
        # تحويل البيانات إلى التنسيق المطلوب
        links = []
        for file_info in data['files']:
            link_type = "Direct MP4" if file_info['type'] == 'mp4' else "HLS Stream"
            links.append({
                "quality": link_type,
                "url": file_info['file'],
                "needs_proxy": False,  # TMDB لا يحتاج بروكسي
                "language": file_info.get('lang', 'en')
            })
        
        # إضافة الترجمة إذا وجدت
        result = {"status": "success", "links": links}
        if 'subtitles' in data and data['subtitles']:
            result["subtitles"] = []
            for sub in data['subtitles']:
                result["subtitles"].append({
                    "lang": sub.get('lang', 'en'),
                    "url": sub['url'],
                    "type": sub.get('type', 'srt')
                })
        
        sys.stderr.write(f"[*] TMDB-LOG: Successfully extracted {len(links)} links\n")
        return result
        
    except requests.exceptions.ConnectTimeout:
        sys.stderr.write(f"[!] TMDB-LOG: Connection timeout to localhost:3000\n")
        return {"status": "error", "message": "Connection timeout: CinePro Backend is not responding on port 3000. Please ensure it's running."}
    except requests.exceptions.ReadTimeout:
        sys.stderr.write(f"[!] TMDB-LOG: Read timeout from localhost:3000\n")
        return {"status": "error", "message": "Read timeout: CinePro Backend is responding slowly. Please check if it's working properly."}
    except requests.exceptions.ConnectionError:
        sys.stderr.write(f"[!] TMDB-LOG: Connection refused to localhost:3000\n")
        return {"status": "error", "message": "Connection refused: CinePro Backend is not running on port 3000. Please start it first."}
    except requests.exceptions.RequestException as e:
        sys.stderr.write(f"[!] TMDB-LOG: Network error: {e}\n")
        return {"status": "error", "message": f"Network error connecting to TMDB provider: {e}"}
    except json.JSONDecodeError as e:
        sys.stderr.write(f"[!] TMDB-LOG: JSON parsing error: {e}\n")
        return {"status": "error", "message": f"Invalid response from TMDB provider: {e}"}
    except Exception as e:
        sys.stderr.write(f"[!] TMDB-LOG: Unexpected error: {e}\n")
        return {"status": "error", "message": f"TMDB provider error: {e}"}

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "Missing 'url' parameter", 400

    proxy_headers = {}
    for header in ['User-Agent', 'Accept', 'Accept-Language', 'Accept-Encoding', 'Origin', 'Referer']:
        if header in request.headers:
            proxy_headers[header] = request.headers[header]
    proxy_headers['ngrok-skip-browser-warning'] = 'true'

    if 'tgtria1dbw.xyz' in target_url:
        proxy_headers['Referer'] = 'https://veloratv.ru/'
        sys.stderr.write("[*] PROXY-LOG: Applying VeloraTV specific headers.\n")
    elif 'vidmoly.net' in target_url or 'sendvid.com' in target_url:
        proxy_headers['Referer'] = 'https://ristoanime.org/'
        sys.stderr.write("[*] PROXY-LOG: Applying Ristoanime specific headers.\n")
    elif 'Origin' in request.headers:
        proxy_headers['Referer'] = request.headers['Origin']
    
    try:
        r = requests.get(target_url, headers=proxy_headers, stream=True, timeout=20, verify=False)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        sys.stderr.write(f"[!] PROXY-ERROR: Failed to fetch {target_url} -> {e}\n")
        return f"Error fetching proxied URL: {e}", 502

    response_headers = {'Access-Control-Allow-Origin': '*'}
    for key, value in r.headers.items():
        if key.lower() not in ['content-encoding', 'content-length', 'transfer-encoding', 'connection', 'access-control-allow-origin']:
            response_headers[key] = value

    if 'mpegurl' in r.headers.get('content-type', ''):
        proxy_base_url = f"{request.host_url.rstrip('/')}/proxy?url="
        
        def generate_rewritten_playlist():
            for line_bytes in r.iter_lines():
                line = line_bytes.decode('utf-8', errors='ignore')
                if line and not line.startswith('#'):
                    segment_url = urljoin(target_url, line.strip())
                    yield f"{proxy_base_url}{quote_plus(segment_url)}\n"
                elif line:
                    yield f"{line}\n"
        return Response(generate_rewritten_playlist(), headers=response_headers)
    else:
        return Response(r.iter_content(chunk_size=8192), headers=response_headers, status=r.status_code)

# --- نقطة النهاية الجديدة للترجمة ---
@app.route("/subs", methods=["GET"])
def subtitles_endpoint():
    content_type = request.args.get("type")  # movie أو tv
    tmdb_id = request.args.get("id")
    season = request.args.get("season")
    episode = request.args.get("episode")

    if not content_type or not tmdb_id:
        return jsonify({"status": "error", "message": "يجب إدخال type و id"}), 400

    result = get_subtitles_from_wyzie(content_type, tmdb_id, season, episode)
    status_code = 200 if result.get('status') == 'success' else 404
    return jsonify(result), status_code

@app.route('/health/tmdb', methods=['GET'])
def check_tmdb_health():
    """فحص حالة اتصال CinePro Backend"""
    try:
        response = requests.get("http://localhost:3000/", timeout=10)
        if response.status_code == 200:
            return jsonify({
                "status": "success",
                "message": "CinePro Backend is running and accessible",
                "response_time": response.elapsed.total_seconds()
            })
        else:
            return jsonify({
                "status": "warning",
                "message": f"CinePro Backend responded with status {response.status_code}"
            })
    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "error",
            "message": f"CinePro Backend is not accessible: {str(e)}"
        }), 503

@app.route('/scrape', methods=['GET'])
def scrape_endpoint():
    provider = request.args.get('provider', '').lower()
    title = request.args.get('title')
    media_type = request.args.get('type')
    
    if not provider: return jsonify({"status": "error", "message": "Missing 'provider'"}), 400
    if not media_type or media_type not in ['movie', 'series']: return jsonify({"status": "error", "message": "Invalid 'type'"}), 400
    
    try:
        season = int(request.args.get('season')) if request.args.get('season') else None
        episode = int(request.args.get('episode')) if request.args.get('episode') else None
    except (ValueError, TypeError): return jsonify({"status": "error", "message": "'season'/'episode' must be integers"}), 400

    result = {}
    
    if provider == 'akwam':
        if not title: return jsonify({"status": "error", "message": "'title' is required for akwam"}), 400
        if media_type == 'series' and (not season or not episode): return jsonify({"status": "error", "message": "'season' and 'episode' required for series"}), 400
        result = scrape_akwam(title, media_type, season, episode)
    elif provider == 'veloratv':
        tmdb_id = request.args.get('tmdb_id')
        if not tmdb_id: return jsonify({"status": "error", "message": "'tmdb_id' is required for veloratv"}), 400
        result_season = season or 1
        result_episode = episode or 1
        if media_type == 'series' and (not season or not episode): return jsonify({"status": "error", "message": "'season' and 'episode' required"}), 400
        result = scrape_veloratv(media_type, result_season, result_episode, tmdb_id)
    elif provider == 'aflam':
        if not title: return jsonify({"status": "error", "message": "'title' is required for aflam"}), 400
        if media_type == 'series' and not episode: return jsonify({"status": "error", "message": "'episode' is required for series"}), 400
        result = scrape_aflam(title, media_type, episode)
    elif provider == 'ristoanime':
        if not title: return jsonify({"status": "error", "message": "'title' is required for ristoanime"}), 400
        if media_type != 'series': return jsonify({"status": "error", "message": "ristoanime only supports 'series'"}), 400
        if not season or not episode: return jsonify({"status": "error", "message": "'season' and 'episode' are required for ristoanime"}), 400
        result = scrape_ristoanime(title, season, episode)
    elif provider == 'arabic-toons':
        if not title: return jsonify({"status": "error", "message": "'title' is required for arabic-toons"}), 400
        if media_type != 'series': return jsonify({"status": "error", "message": "arabic-toons only supports 'series' type"}), 400
        if not season or not episode: return jsonify({"status": "error", "message": "'season' and 'episode' are required for arabic-toons"}), 400
        result = scrape_arabic_toons(title, season, episode)
    elif provider == 'tmdb':
        tmdb_id = request.args.get('tmdb_id')
        if not tmdb_id: return jsonify({"status": "error", "message": "'tmdb_id' is required for tmdb"}), 400
        if media_type == 'series' and (not season or not episode): return jsonify({"status": "error", "message": "'season' and 'episode' are required for series"}), 400
        result = scrape_tmdb(media_type, tmdb_id, season, episode)
    else:
        return jsonify({"status": "error", "message": f"Invalid provider '{provider}'"}), 400

    if result.get('status') == 'success' and result.get('links'):
        api_base_url = request.host_url.rstrip('/')
        for link_item in result['links']:
            if link_item.get("needs_proxy"):
                original_url = link_item.get('url')
                if original_url:
                    encoded_url = quote_plus(original_url)
                    link_item['url'] = f"{api_base_url}/proxy?url={encoded_url}"
                    del link_item["needs_proxy"]
    
    status_code = 200 if result.get('status') == 'success' else 404
    return jsonify(result), status_code

# ----- مشغل البرنامج الرئيسي -----
if __name__ == "__main__":
    try:
        subprocess.run(['yt-dlp', '--version'], check=True, capture_output=True, text=True)
        sys.stderr.write("INFO: yt-dlp check successful.\n")
    except (subprocess.CalledProcessError, FileNotFoundError):
        sys.stderr.write("\nFATAL: 'yt-dlp' is not found. 'aflam' and 'ristoanime' providers will fail.\n"
                         "Please install it from: https://github.com/yt-dlp/yt-dlp\n")
        sys.exit(1)
    
    public_url = None
    port = 5000
    if ngrok:
        try:
            ngrok.kill()
            public_url = ngrok.connect(port)
        except Exception as e:
             sys.stderr.write(f"\nWARN: Could not start ngrok. The API will be local only. Error: {e}\n")
    
    print("\n" + "="*70)
    print("🚀 Unified Media Scraper & Smart Proxy is Ready! 🚀")
    print("="*70)
    if public_url:
        print(f"🌍 Public HTTPS URL (Ngrok): {public_url.public_url}")
    print(f"🏠 Local URL: http://127.0.0.1:{port}")
    print("\n--- [ USAGE EXAMPLES ] ---")
    base_url = public_url.public_url if public_url else f"http://127.0.0.1:{port}"
    print(f"🎬 Movie (VeloraTV): {base_url}/scrape?provider=veloratv&type=movie&tmdb_id=872585")
    print(f"📺 Series (Ristoanime): {base_url}/scrape?provider=ristoanime&title=attack on titan&type=series&season=4&episode=1")
    print(f"🎬 Movie (Akwam): {base_url}/scrape?provider=akwam&title=Oppenheimer&type=movie")
    print(f"🎬 Movie (Aflam): {base_url}/scrape?provider=aflam&title=Oppenheimer&type=movie")
    print(f"📺 Series (Arabic-Toons): {base_url}/scrape?provider=arabic-toons&title=gumball&type=series&season=5&episode=1")
    print(f"🎬 Movie (TMDB): {base_url}/scrape?provider=tmdb&type=movie&tmdb_id=872585")
    print(f"📺 Series (TMDB): {base_url}/scrape?provider=tmdb&type=series&tmdb_id=1399&season=1&episode=1")
    print(f"📜 Subtitles (Wyzie): {base_url}/subs?type=movie&id=872585")
    print(f"🔍 Check TMDB Health: {base_url}/health/tmdb")
    print("="*70)
    print("\n💡 To use, copy an example URL and paste it in your browser.")
    print("   The JSON response will contain the final, playable HTTPS URL(s).")
    print("   Copy a final URL and paste it into VLC or any HLS player.")
    print("="*70)
    
    sys.stdout.flush()
    app.run(port=port, host='0.0.0.0', debug=False, use_reloader=False)