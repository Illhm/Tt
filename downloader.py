import requests
import re
from bs4 import BeautifulSoup
import sys

def download_tiktok_video(url=None):
    """
    Downloads a TikTok video (HD preferred) from the given URL.
    Uses ssstik.io as the backend service.
    """

    # 1. Determine URL source
    if not url:
        print("Error: No URL provided.")
        return

    print(f"Processing URL: {url}")

    session = requests.Session()
    # Emulate a real browser to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*"
    }

    # Step 1: Fetch Main Page
    # Purpose: The site generates a dynamic token ('s_tt') on the main page which is required for the API request.
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

    # Step 2: Send POST Request (HTMX)
    # Purpose: Send the video URL and the token to the backend to generate download links.
    # The site uses HTMX, so we must replicate specific HTMX headers.
    print("Sending POST request...")
    post_url = "https://ssstik.io/abc?url=dl"

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

    # Step 3: Parse Response
    # Purpose: The response contains HTML with download buttons. We parse this to find the best quality link.
    soup = BeautifulSoup(post_response.text, "html.parser")

    # Strategy: Try to find HD download link first
    hd_link_tag = soup.find("a", class_="without_watermark_hd")
    download_url = None
    filename = "tiktok_video.mp4"

    if hd_link_tag:
        print("Found HD link tag. Attempting HD extraction...")
        # The HD button works differently: it's an HTMX trigger itself.
        # It has a 'data-directurl' pointing to a validation endpoint.
        data_directurl = hd_link_tag.get("data-directurl")

        # We also need a new 'tt' token which is usually hidden in the response form
        tt_input = soup.find("input", {"name": "tt"})
        if tt_input:
            token2 = tt_input.get("value")

            # Construct the verification request
            hd_post_url = "https://ssstik.io" + data_directurl
            print(f"Requesting HD link verification...")

            hd_data = {
                "tt": token2
            }

            try:
                hd_response = session.post(hd_post_url, headers=post_headers, data=hd_data)
                hd_response.raise_for_status()

                # Success Logic: The server responds with an 'hx-redirect' header pointing to the actual video file.
                if "hx-redirect" in hd_response.headers:
                    download_url = hd_response.headers["hx-redirect"]
                    print(f"HD Download URL found via hx-redirect: {download_url}")
                    filename = "tiktok_video_hd.mp4"
                else:
                    print("No hx-redirect header found in HD response.")
            except Exception as e:
                print(f"Error requesting HD link: {e}")

    # Fallback Strategy: Standard quality
    # If HD failed or wasn't found, look for the standard 'without_watermark' link.
    if not download_url:
        print("Falling back to standard quality.")
        download_link_tag = soup.find("a", class_="without_watermark")

        if not download_link_tag:
            # Fallback search by text or class part
            download_link_tag = soup.find("a", class_="download_link", string=lambda text: "Without watermark" in text if text else False)

        if not download_link_tag:
            print("Could not find download link in response.")
            return

        download_url = download_link_tag.get("href")
        print(f"Download URL found: {download_url}")

    # Step 4: Download Video
    # Purpose: Stream the video content to a file.
    print(f"Downloading video to {filename}...")
    try:
        video_response = session.get(download_url, headers=headers, stream=True)
        video_response.raise_for_status()

        with open(filename, "wb") as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Video saved successfully as {filename}")
    except Exception as e:
        print(f"Error downloading video: {e}")

if __name__ == "__main__":
    # Automatic Mode: Check args, else prompt user
    print("--- TikTok Downloader Automation ---")

    target_url = None
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        try:
            target_url = input("Enter TikTok URL: ").strip()
        except KeyboardInterrupt:
            print("\nExiting.")
            sys.exit(0)

    if target_url:
        download_tiktok_video(target_url)
    else:
        print("No URL provided. Exiting.")
