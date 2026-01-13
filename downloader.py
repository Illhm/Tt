import requests
import re
from bs4 import BeautifulSoup
import time
import os

def get_filename_from_response(response, default_name):
    """
    Extracts filename from Content-Disposition header.
    Falls back to default_name if not found.
    """
    content_disposition = response.headers.get("Content-Disposition")
    if content_disposition:
        match = re.search(r'filename="?([^";]+)"?', content_disposition)
        if match:
            return match.group(1)
    return default_name

def download_tiktok_video():
    # Hardcoded URL as per requirements
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

    # Try to find HD link first
    hd_link_tag = soup.find("a", class_="without_watermark_hd")
    if not hd_link_tag:
        hd_link_tag = soup.find(id="hd_download")

    hd_download_success = False

    if hd_link_tag:
        print("Detected Type: VIDEO (HD Available)")
        direct_url = hd_link_tag.get("data-directurl") or hd_link_tag.get("href")

        # If it's just a placeholder href "#", ignore it
        if direct_url == "#":
            direct_url = hd_link_tag.get("data-directurl")

        if direct_url and direct_url != "#":
            print(f"Attempting to fetch HD content from {direct_url} ...")
            try:
                if direct_url.startswith("/"):
                    hd_post_url = "https://ssstik.io" + direct_url
                else:
                    hd_post_url = direct_url

                hd_headers = post_headers.copy()
                hd_headers["hx-target"] = "#target"
                hd_headers.pop("hx-trigger", None)

                # Include tt token as per hx-include in the JS
                hd_data = {
                    "tt": s_tt
                }

                hd_response = session.post(hd_post_url, headers=hd_headers, data=hd_data)
                hd_response.raise_for_status()

                content_type = hd_response.headers.get("Content-Type", "")
                if "video" in content_type or "application/octet-stream" in content_type:
                    filename = get_filename_from_response(hd_response, "tiktok_video_hd.mp4")
                    print(f"Downloading HD video to {filename}...")
                    with open(filename, "wb") as f:
                        for chunk in hd_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print("HD Video saved successfully.")
                    hd_download_success = True
                else:
                    # Parse HTML for the link
                    hd_soup = BeautifulSoup(hd_response.text, "html.parser")
                    final_link_tag = hd_soup.find("a")

                    if final_link_tag:
                        final_link = final_link_tag.get("href")

                        if final_link and final_link != "/":
                             if final_link.startswith("/"):
                                 final_link = "https://ssstik.io" + final_link

                             print(f"HD Download Link found: {final_link}")
                             video_response = session.get(final_link, headers=headers, stream=True)
                             video_response.raise_for_status()
                             filename = get_filename_from_response(video_response, "tiktok_video_hd.mp4")
                             with open(filename, "wb") as f:
                                  for chunk in video_response.iter_content(chunk_size=8192):
                                      f.write(chunk)
                             print(f"HD Video saved as {filename}")
                             hd_download_success = True
                        else:
                             print("HD Link returned invalid path (/).")
                    else:
                        print("No anchor tag found in HD response.")
                        # Check for error message in response
                        if "Uh-oh... Something suspicious!" in hd_response.text:
                             print("Server rejected HD request (Anti-bot/Suspicious activity detected).")

            except Exception as e:
                print(f"Error downloading HD video: {e}. Falling back to standard quality.")
        else:
            print("No valid direct URL for HD found. Falling back.")

    if hd_download_success:
        return

    print("Falling back to Standard Quality...")

    # Check for Standard Video Download Link (Fallback)
    download_link_tag = soup.find("a", class_="without_watermark")

    if download_link_tag:
        print("Detected Type: VIDEO (Standard)")
        download_url = download_link_tag.get("href")
        print(f"Download URL: {download_url}")

        print("Downloading video...")
        try:
            video_response = session.get(download_url, headers=headers, stream=True)
            video_response.raise_for_status()

            filename = get_filename_from_response(video_response, "tiktok_video.mp4")

            with open(filename, "wb") as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Video saved as {filename}")
        except Exception as e:
            print(f"Error downloading video: {e}")

    else:
        # Check for Slideshow
        print("Video download link not found. Checking for Slideshow/Photos...")

        image_links = []

        dl_links = soup.find_all("a", class_="download_link")
        if dl_links:
            for link in dl_links:
                href = link.get("href")
                if href and (href.endswith(".jpg") or href.endswith(".jpeg") or href.endswith(".webp") or "tikcdn.io" in href):
                    if href not in image_links:
                        image_links.append(href)

        if not image_links:
            slides_container = soup.find("ul", class_="splide__list")
            if slides_container:
                imgs = slides_container.find_all("img")
                for img in imgs:
                    src = img.get("src") or img.get("data-splide-lazy")
                    if src and src not in image_links:
                        image_links.append(src)
            else:
                 main_result = soup.find(id="mainpicture")
                 if main_result:
                     imgs = main_result.find_all("img")
                     for img in imgs:
                         if "result_author" not in img.get("class", []):
                             src = img.get("src")
                             if src and src not in image_links:
                                 image_links.append(src)

        if image_links:
            print(f"Detected Type: SLIDESHOW/PHOTOS ({len(image_links)} images found)")
            for i, img_url in enumerate(image_links):
                try:
                    print(f"Downloading image {i+1}/{len(image_links)}...")
                    img_response = session.get(img_url, headers=headers, stream=True)
                    img_response.raise_for_status()

                    filename = get_filename_from_response(img_response, f"tiktok_photo_{i+1}.jpg")
                    if os.path.exists(filename) and "tiktok_photo_" not in filename:
                        root, ext = os.path.splitext(filename)
                        filename = f"{root}_{i+1}{ext}"

                    with open(filename, "wb") as f:
                        for chunk in img_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Saved {filename}")
                except Exception as e:
                    print(f"Error downloading image {i+1}: {e}")
        else:
            print("Could not detect video or photos.")

if __name__ == "__main__":
    download_tiktok_video()
