import requests
import re
from bs4 import BeautifulSoup
import time

def download_tiktok_video():
    # Hardcoded URL as per "without any input" requirement, using the one from the log.
    url = "https://vt.tiktok.com/ZS5ntSmq8/"

    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*"
    }

    # Step 1: Get main page to extract token
    print("Fetching main page...")
    try:
        response = session.get("https://ssstik.io/en", headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching main page: {e}")
        return

    # Extract s_tt
    match = re.search(r"s_tt\s*=\s*'([^']+)'", response.text)
    if not match:
        print("Could not find s_tt token.")
        return

    s_tt = match.group(1)
    print(f"Token found: {s_tt}")

    # Step 2: POST request
    print("Sending POST request...")
    post_url = "https://ssstik.io/abc?url=dl"

    # HTMX headers are important
    post_headers = headers.copy()
    post_headers.update({
        "hx-current-url": "https://ssstik.io/en",
        "hx-request": "true",
        "hx-target": "target",
        "hx-trigger": "_gcaptcha_pt",
        "Origin": "https://ssstik.io",
        "Referer": "https://ssstik.io/en",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    })

    data = {
        "id": url,
        "locale": "en",
        "tt": s_tt,
    }

    try:
        post_response = session.post(post_url, headers=post_headers, data=data)
        post_response.raise_for_status()
    except Exception as e:
        print(f"Error sending POST request: {e}")
        return

    # Step 3: Parse response
    soup = BeautifulSoup(post_response.text, "html.parser")

    # Look for the download link "Without watermark"
    download_link_tag = soup.find("a", class_="without_watermark")

    if not download_link_tag:
        # Fallback search by text or class part
        download_link_tag = soup.find("a", class_="download_link", string=lambda text: "Without watermark" in text if text else False)

    if not download_link_tag:
        print("Could not find download link in response.")
        return

    download_url = download_link_tag.get("href")
    print(f"Download URL found: {download_url}")

    # Step 4: Download video
    print("Downloading video...")
    try:
        video_response = session.get(download_url, headers=headers, stream=True)
        video_response.raise_for_status()

        filename = "tiktok_video.mp4"
        with open(filename, "wb") as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Video saved as {filename}")
    except Exception as e:
        print(f"Error downloading video: {e}")

if __name__ == "__main__":
    download_tiktok_video()
