import requests
import re
from bs4 import BeautifulSoup
import time
import os

def download_tiktok_video():
    # Hardcoded URL as per "without any input" requirement.
    # This URL is used for testing and automatic execution.
    url = "https://vt.tiktok.com/ZS5ntSmq8/"

    session = requests.Session()
    # Standard user agent to avoid bot detection
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*"
    }

    print(f"Target URL: {url}")

    # Step 1: Get main page to extract the s_tt token
    # ssstik.io requires this token for the subsequent POST request.
    print("Fetching main page...")
    try:
        response = session.get("https://ssstik.io/en", headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching main page: {e}")
        return

    # Extract s_tt token using regex
    match = re.search(r"s_tt\s*=\s*'([^']+)'", response.text)
    if not match:
        print("Could not find s_tt token.")
        return

    s_tt = match.group(1)
    print(f"Token found: {s_tt}")

    # Step 2: POST request to process the TikTok URL
    print("Sending POST request to process URL...")
    post_url = "https://ssstik.io/abc?url=dl"

    # HTMX headers are critical for ssstik.io to respond correctly
    post_headers = headers.copy()
    post_headers.update({
        "hx-current-url": "https://ssstik.io/en",
        "hx-request": "true",
        "hx-target": "target",
        "hx-trigger": "_gcaptcha_pt", # Trigger for the initial form submission
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

    # Step 3: Parse the response to find download links
    soup = BeautifulSoup(post_response.text, "html.parser")

    # Try to find HD download link first
    # The HD link usually has class "without_watermark_hd"
    hd_link_tag = soup.find("a", class_="without_watermark_hd")
    download_url = None
    filename = "tiktok_video.mp4"

    if hd_link_tag:
        print("Found HD link tag.")
        data_directurl = hd_link_tag.get("data-directurl")

        # We also need the new 'tt' token from the response which is inside a hidden input
        tt_input = soup.find("input", {"name": "tt"})
        if tt_input:
            token2 = tt_input.get("value")

            # Now make the request for the HD link
            # The HD download is triggered by a POST request to the data-directurl
            hd_post_url = "https://ssstik.io" + data_directurl
            print(f"Requesting HD link...")

            hd_data = {
                "tt": token2
            }

            # Update headers for HD request
            # hx-trigger should be 'hd_download' (the ID of the HD button) or 'click'
            # to mimic the browser behavior more closely.
            hd_headers = post_headers.copy()
            hd_headers["hx-trigger"] = "hd_download"
            hd_headers["hx-target"] = "target" # Keep target as target, or remove if not strictly needed

            try:
                hd_response = session.post(hd_post_url, headers=hd_headers, data=hd_data)
                hd_response.raise_for_status()

                # The actual download URL is often in the 'hx-redirect' header
                if "hx-redirect" in hd_response.headers:
                    download_url = hd_response.headers["hx-redirect"]
                    print(f"HD Download URL found via hx-redirect: {download_url}")
                    filename = "tiktok_video_hd.mp4"
                else:
                    print("No hx-redirect header found in HD response. Checking body...")
                    # Sometimes it might return a direct link in body (rare for this site but possible)
                    pass
            except Exception as e:
                print(f"Error requesting HD link: {e}")

    # Fallback to standard quality if HD failed or wasn't found
    if not download_url:
        print("Falling back to standard quality.")
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
    print(f"Downloading video to {filename}...")
    try:
        video_response = session.get(download_url, headers=headers, stream=True)
        video_response.raise_for_status()

        total_size = 0
        with open(filename, "wb") as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    total_size += len(chunk)

        print(f"Video saved as {filename}")
        print(f"File size: {total_size / (1024*1024):.2f} MB")

        if total_size < 10000: # Less than 10KB is likely an error page
            print("Warning: File size is very small. Download might have failed.")

    except Exception as e:
        print(f"Error downloading video: {e}")

if __name__ == "__main__":
    download_tiktok_video()
