import asyncio
from playwright.async_api import async_playwright
import os

SCREENSHOTS_DIR = "docs/demo/screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

BASE_URL = "http://localhost:8080"


async def find_button(page, texts):
    for txt in texts:
        btn = page.locator(f"button:has-text('{txt}')").first
        if await btn.count() > 0:
            return btn
    return None


async def dismiss_tutorial(page):
    for _ in range(5):
        await page.wait_for_timeout(300)
        btn = await find_button(page, ["AVANTI", "INIZIA ORA"])
        if btn:
            await btn.click()
            await page.wait_for_timeout(600)
        else:
            break


async def make_choice(page, idx=0):
    try:
        await page.wait_for_selector(".choice-btn", timeout=5000)
    except:
        pass
    choice_btns = page.locator(".choice-btn")
    cc = await choice_btns.count()
    if cc == 0:
        return False
    await choice_btns.nth(idx % cc).click(timeout=3000)
    await page.wait_for_timeout(2000)
    btn = await find_button(page, ["PROSEGUI", "OK", "Continua"])
    if btn:
        await btn.click()
        await page.wait_for_timeout(1500)
    return True


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            device_scale_factor=2,
        )
        page = await context.new_page()

        # ═══════════════════════════════════════════════════
        # 1. START SCREEN
        # ═══════════════════════════════════════════════════
        await page.goto(BASE_URL)
        await page.wait_for_timeout(4000)
        await page.screenshot(path=f"{SCREENSHOTS_DIR}/01_start_screen.png")
        print("✅ 01_start_screen.png")

        # ═══════════════════════════════════════════════════
        # 2. LABORATORY (agenti sciame)
        # ═══════════════════════════════════════════════════
        await page.locator("button", has_text="ENTRA NEL LABORATORIO").click()
        await page.wait_for_timeout(5000)
        await page.screenshot(path=f"{SCREENSHOTS_DIR}/02_laboratory.png")
        print("✅ 02_laboratory.png")

        # ═══════════════════════════════════════════════════
        # 3. POSSESS AGENT → GAME SCREEN
        # ═══════════════════════════════════════════════════
        possess_btn = page.locator("button:has-text('POSSIEDI')").first
        if await possess_btn.count() > 0:
            await possess_btn.click()
            await page.wait_for_timeout(5000)
        else:
            continue_btn = page.locator("button:has-text('CONTINUA')").first
            if await continue_btn.count() > 0:
                await continue_btn.click()
                await page.wait_for_timeout(5000)

        await dismiss_tutorial(page)
        await page.wait_for_timeout(2000)
        await page.screenshot(path=f"{SCREENSHOTS_DIR}/03_game_screen.png")
        print("✅ 03_game_screen.png")

        # ═══════════════════════════════════════════════════
        # 4. PLAY A FEW TURNS
        # ═══════════════════════════════════════════════════
        for turn in range(3):
            result = await make_choice(page, turn % 2)
            if turn == 0:
                await page.wait_for_timeout(1000)
                await page.screenshot(path=f"{SCREENSHOTS_DIR}/04_choice_feedback.png")
                print("✅ 04_choice_feedback.png")

        await page.wait_for_timeout(1000)
        await page.screenshot(path=f"{SCREENSHOTS_DIR}/05_game_progress.png")
        print("✅ 05_game_progress.png")

        # ═══════════════════════════════════════════════════
        # 5. EXIT GAME → GAME OVER
        # ═══════════════════════════════════════════════════
        exit_btn = page.locator(
            'button:has(span.material-icons:has-text("logout"))'
        ).first
        if await exit_btn.count() == 0:
            exit_btn = page.locator(
                'button:has(i.material-icons:has-text("logout"))'
            ).first
        if await exit_btn.count() > 0:
            await exit_btn.click()
            await page.wait_for_timeout(3000)
        else:
            await page.locator(".choice-btn").first.click(timeout=2000)
            await page.wait_for_timeout(2000)
            btn = await find_button(page, ["PROSEGUI", "OK", "Continua"])
            if btn:
                await btn.click()
                await page.wait_for_timeout(2000)

        await page.wait_for_timeout(2000)
        await page.screenshot(path=f"{SCREENSHOTS_DIR}/06_game_over.png")
        print("✅ 06_game_over.png")

        # ═══════════════════════════════════════════════════
        # 6. BACK TO START → ANALYTICS
        # ═══════════════════════════════════════════════════
        again_btn = page.locator("button:has-text('Gioca Ancora')").first
        if await again_btn.count() > 0:
            await again_btn.click()
            await page.wait_for_timeout(3000)
        else:
            menu_btn = page.locator("button:has-text('← MENU')").first
            if await menu_btn.count() > 0:
                await menu_btn.click()
                await page.wait_for_timeout(3000)

        analytics_btn = page.locator("button:has-text('Analytics')").first
        if await analytics_btn.count() > 0:
            await analytics_btn.click()
            await page.wait_for_timeout(4000)
            await page.screenshot(path=f"{SCREENSHOTS_DIR}/07_analytics.png")
            print("✅ 07_analytics.png")
        else:
            await page.screenshot(path=f"{SCREENSHOTS_DIR}/07_fallback.png")
            print("⚠️  Analytics button not found")

        await browser.close()
        print("\n🎉 All done!")


if __name__ == "__main__":
    asyncio.run(main())
