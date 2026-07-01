import asyncio
from playwright.async_api import async_playwright

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto("http://localhost:8080")
            await page.wait_for_selector('text=ENTRA NEL LABORATORIO')
            await page.click('text=ENTRA NEL LABORATORIO')
            await page.wait_for_selector('text=LABORATORIO ANTROPOLOGICO')

            # Screenshot of the new laboratory layout
            await page.screenshot(path="verification/lab_v3_final.png", full_page=True)
            print("Screenshot saved to verification/lab_v3_final.png")

            # Check for key elements
            await page.wait_for_selector('text=AURA COMPORTAMENTALE')
            await page.wait_for_selector('text=CRONOLOGIA SCELTE')
            await page.wait_for_selector('text=STRESS MEDIO SCIAME')

            print("Frontend elements verified.")
        except Exception as e:
            print(f"Verification failed: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(verify())
