from __future__ import annotations

from camoufox.async_api import AsyncCamoufox

from core.logging import get_logger

MULTIPLIER = 1000
logger = get_logger(__name__)


async def get_waf_cookie(domain: str = "https://cfcybernews.eu") -> tuple[str, str] | None:
    cf_clearance_cookie = None
    user_agent = None

    try:
        logger.info("Starting Cloudflare WAF flow for domain: %s", domain)
        async with AsyncCamoufox(
            webgl_config=("Apple", "Apple M1, or similar"),
            disable_coop=True,
            locale=["en-US"],
            block_webrtc=False,
            block_webgl=False,
            humanize=True,
            geoip=True,
            os="macos",
            i_know_what_im_doing=True,
            headless=True,
        ) as browser:
            page = await browser.new_page()
            await page.goto(domain, wait_until="domcontentloaded", timeout=30 * MULTIPLIER)

            if await page.title() == "Just a moment...":
                logger.debug(
                    "(Detected) - Cloudflare - JS/Captcha for domain: %s", domain
                )

                while True:
                    captcha_frame = next(
                        (
                            frame
                            for frame in page.frames
                            if "challenges.cloudflare.com" in frame.url
                        ),
                        None,
                    )

                    if captcha_frame:
                        logger.debug(
                            "Found Captcha Frame for domain %s: %s",
                            domain,
                            captcha_frame.url,
                        )
                        await captcha_frame.wait_for_load_state(
                            "networkidle", timeout=10 * MULTIPLIER
                        )
                        await captcha_frame.wait_for_timeout(3 * MULTIPLIER)

                        try:
                            frame_element = await captcha_frame.frame_element()
                            if not frame_element:
                                logger.warning(
                                    "Frame element not found for domain: %s", domain
                                )
                                return None

                            box = await frame_element.bounding_box()
                            if not box:
                                logger.warning(
                                    "Bounding box not found for domain: %s", domain
                                )
                                return None

                            checkbox_x = box["x"] + box["width"] / 2
                            checkbox_y = box["y"] + box["height"] / 2

                            logger.info(
                                "Clicking on captcha checkbox for domain %s at (%s, %s)",
                                domain,
                                checkbox_x,
                                checkbox_y,
                            )
                            await page.mouse.click(checkbox_x, checkbox_y)

                            await page.wait_for_load_state(
                                "networkidle", timeout=20 * MULTIPLIER
                            )

                            while await page.title() == "Just a moment...":
                                logger.info(
                                    "Waiting for captcha to be solved for domain: %s",
                                    domain,
                                )
                                await page.wait_for_timeout(5 * MULTIPLIER)

                            logger.info(
                                "Captcha solved successfully for domain: %s", domain
                            )

                            break

                        except Exception as exc:
                            logger.error(
                                "Error while handling captcha for domain %s: %s",
                                domain,
                                exc,
                            )
                            return None
                    else:
                        logger.warning("Captcha frame not found for domain: %s", domain)
                        return None

            cookies = await page.context.cookies()
            for cookie in cookies:
                if cookie["name"] == "cf_clearance":
                    cf_clearance_cookie = f"{cookie['name']}={cookie['value']}"
                    break

            user_agent = await page.evaluate("() => navigator.userAgent")
            await page.close()
            if cf_clearance_cookie and user_agent:
                logger.info(
                    "Cloudflare WAF bypassed successfully for domain: %s",
                    domain,
                )
            else:
                logger.warning(
                    "cf_clearance or user-agent not found for domain: %s", domain
                )
                return None

        if cf_clearance_cookie and user_agent:
            return cf_clearance_cookie, user_agent

        logger.warning("cf_clearance or user-agent not found for domain: %s", domain)
        return None

    except Exception as exc:
        logger.error("An error occurred for domain %s: %s", domain, exc)
        return None

