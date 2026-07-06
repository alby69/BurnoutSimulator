import asyncio
from playwright.async_api import async_playwright
import os

SCREENSHOTS_DIR = "docs/demo/screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

BASE_URL = "http://localhost:8080"
NUM_GAMES = 4
TURNS_PER_GAME = 15


async def find_button(page, texts):
    for txt in texts:
        btn = page.locator(f"button:has-text('{txt}')").first
        if await btn.count() > 0:
            return btn
    return None


async def dismiss_tutorial(page):
    for _ in range(5):
        await page.wait_for_timeout(200)
        btn = await find_button(page, ["AVANTI", "INIZIA ORA"])
        if btn:
            await btn.click()
            await page.wait_for_timeout(400)
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
    await page.wait_for_timeout(800)
    btn = await find_button(page, ["PROSEGUI", "OK", "Continua"])
    if btn:
        await btn.click()
        await page.wait_for_timeout(600)
    return True


async def click_exit(page):
    exit_btn = page.locator('button:has(span.material-icons:has-text("logout"))').first
    if await exit_btn.count() == 0:
        exit_btn = page.locator('button:has(i.material-icons:has-text("logout"))').first
    if await exit_btn.count() > 0:
        await exit_btn.click()
        await page.wait_for_timeout(3000)
        return True
    return False


async def possess_agent(page):
    possess_btn = page.locator("button:has-text('POSSIEDI')").first
    if await possess_btn.count() > 0:
        await possess_btn.click()
        await page.wait_for_timeout(5000)
        return True
    continue_btn = page.locator("button:has-text('CONTINUA')").first
    if await continue_btn.count() > 0:
        await continue_btn.click()
        await page.wait_for_timeout(5000)
        return True
    return False


async def play_turns(page, count, screenshot_callback=None):
    for turn in range(count):
        result = await make_choice(page, turn % 3)
        if screenshot_callback:
            await screenshot_callback(turn, result)
    await page.wait_for_timeout(500)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            device_scale_factor=2,
        )
        page = await context.new_page()

        # ════════════════════════════════════════════════════════════
        # 1. START SCREEN
        # ════════════════════════════════════════════════════════════
        await page.goto(BASE_URL)
        await page.wait_for_timeout(4000)
        await page.screenshot(path=f"{SCREENSHOTS_DIR}/01_start_screen.png")
        print("✅ 01_start_screen.png")

        # ════════════════════════════════════════════════════════════
        # 2. LABORATORY
        # ════════════════════════════════════════════════════════════
        await page.locator("button", has_text="ENTRA NEL LABORATORIO").click()
        await page.wait_for_timeout(5000)
        await page.screenshot(path=f"{SCREENSHOTS_DIR}/02_laboratory.png")
        print("✅ 02_laboratory.png")

        # ════════════════════════════════════════════════════════════
        # MULTI-GAME SIMULATION
        # ════════════════════════════════════════════════════════════
        for game_idx in range(NUM_GAMES):
            is_first_game = game_idx == 0
            print(f"\n🎮 Game {game_idx + 1}/{NUM_GAMES}")

            # Possess agent
            if is_first_game or game_idx > 0:
                if not is_first_game:
                    await page.locator(
                        "button", has_text="ENTRA NEL LABORATORIO"
                    ).click()
                    await page.wait_for_timeout(4000)

                await possess_agent(page)
                await dismiss_tutorial(page)
                await page.wait_for_timeout(1500)

            if is_first_game:
                await page.screenshot(path=f"{SCREENSHOTS_DIR}/03_game_screen.png")
                print("✅ 03_game_screen.png")

            # Play 15 turns
            async def first_game_screenshot(turn, result):
                if turn == 1:
                    await page.wait_for_timeout(500)
                    await page.screenshot(
                        path=f"{SCREENSHOTS_DIR}/04_choice_feedback.png"
                    )
                    print("✅ 04_choice_feedback.png")
                elif turn == 7:
                    await page.wait_for_timeout(500)
                    await page.screenshot(
                        path=f"{SCREENSHOTS_DIR}/05_game_progress.png"
                    )
                    print("✅ 05_game_progress.png")

            await play_turns(
                page,
                TURNS_PER_GAME,
                screenshot_callback=first_game_screenshot if is_first_game else None,
            )

            # Exit → game over
            if is_first_game:
                await page.wait_for_timeout(1000)
                await page.screenshot(path=f"{SCREENSHOTS_DIR}/05_game_progress.png")
                print("✅ 05_game_progress.png")

            await click_exit(page)
            await page.wait_for_timeout(2000)

            if is_first_game:
                await page.screenshot(path=f"{SCREENSHOTS_DIR}/06_game_over.png")
                print("✅ 06_game_over.png")

            # Back to start for next game or analytics
            again_btn = page.locator("button:has-text('Gioca Ancora')").first
            if await again_btn.count() > 0:
                await again_btn.click()
                await page.wait_for_timeout(3000)
            else:
                await page.screenshot(path=f"{SCREENSHOTS_DIR}/06_game_over.png")
                print("✅ 06_game_over.png (fallback)")

        # ════════════════════════════════════════════════════════════
        # FINAL: ANALYTICS DASHBOARD
        # ════════════════════════════════════════════════════════════
        analytics_btn = page.locator("button:has-text('Analytics')").first
        if await analytics_btn.count() > 0:
            await analytics_btn.click()
            await page.wait_for_timeout(5000)
            await page.screenshot(path=f"{SCREENSHOTS_DIR}/07_analytics.png")
            print("✅ 07_analytics.png")
        else:
            await page.screenshot(path=f"{SCREENSHOTS_DIR}/07_fallback.png")
            print("⚠️ Analytics fallback")

        await browser.close()
        print("\n🎉 All done!")


if __name__ == "__main__":
    asyncio.run(main())
