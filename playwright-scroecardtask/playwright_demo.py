from playwright.sync_api import sync_playwright
import time 
import os

def capture_scorecard():
    with sync_playwright() as p:
        # Launch browser with normal user-like settings
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/119.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1066, "height": 768}
        )
        page = context.new_page()

        # 1️⃣ Open Google normally
        page.goto("https://www.google.com/")
        time.sleep(2)

        # 2️⃣ Accept cookies if prompt appears
        try:
            page.click("text=Accept all", timeout=3000)
        except:
            pass

        # 3️⃣ Type the search term slowly like a human
        page.click("textarea[name='q']")
        for ch in "SA vs India womens final scorecard":
            page.keyboard.insert_text(ch)
            time.sleep(0.05)
        page.keyboard.press("Enter")
        time.sleep(4)

        # 4️⃣ Click on scorecard link (Cricbuzz / ESPN)
        try:
            page.click("text=India Women vs South Africa Women, Final", timeout=10000)
        except:
            page.click("text=Live Cricket Score", timeout=10000)
        time.sleep(5)

        # 5️⃣ Take screenshot
        page.screenshot(path="scorecard.png", full_page=True)
        print("✅ Screenshot saved as scorecard.png")

        browser.close()

capture_scorecard()