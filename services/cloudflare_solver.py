from __future__ import annotations

from camoufox.async_api import AsyncCamoufox

from core.logging import get_logger

from api.schemas import WafSolveRequest
MULTIPLIER = 1000
logger = get_logger(__name__)


async def get_waf_cookie(request: WafSolveRequest) -> tuple[str, str] | None:
    cf_clearance_cookie = None
    user_agent = None

    try:
        logger.info("Starting Cloudflare WAF flow for domain: %s", request.domain)
        camoufox_options = {
            "webgl_config": ("Apple", "Apple M1, or similar"),
            "disable_coop": request.disable_coop,
            "locale": request.locale,
            "block_webrtc": request.block_webrtc,
            "block_webgl": request.block_webgl,
            "humanize": request.humanize,
            "geoip": request.geoip,
            "os": request.os,
            "i_know_what_im_doing": request.i_know_what_im_doing,
            "headless": request.headless,
        }
        # proxy format: http://username:password@host:port
        if request.proxy is not None:
            camoufox_options["proxy"] = {
                "server": f"http://{request.proxy.split('@')[1]}", 
                "username": request.proxy.split("://")[1].split(":")[0],
                "password": request.proxy.split("://")[1].split(":")[1].split("@")[0],
            }

        async with AsyncCamoufox(**camoufox_options) as browser:
            page = await browser.new_page()
            await page.goto(request.domain, wait_until="networkidle", timeout=30 * MULTIPLIER)

            if await page.title() == "Just a moment...":
                logger.warning(
                    "(Detected) - Cloudflare - JS/Captcha for domain: %s", request.domain
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
                            request.domain,
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
                                    "Frame element not found for domain: %s", request.domain
                                )
                                return None

                            box = await frame_element.bounding_box()
                            if not box:
                                logger.warning(
                                    "Bounding box not found for domain: %s", request.domain
                                )
                                return None

                            checkbox_x = box["x"] + box["width"] / 2
                            checkbox_y = box["y"] + box["height"] / 2

                            logger.info(
                                "Clicking on captcha checkbox for domain %s at (%s, %s)",
                                request.domain,
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
                                    request.domain,
                                )
                                await page.wait_for_timeout(5 * MULTIPLIER)

                            logger.info(
                                "Captcha solved successfully for domain: %s", request.domain
                            )

                            break

                        except Exception as exc:
                            logger.error(
                                "Error while handling captcha for domain %s: %s",
                                request.domain,
                                exc,
                            )
                            return None
                    else:
                        logger.warning("Captcha frame not found for domain: %s", request.domain)
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
                    request.domain,
                )
            else:
                logger.warning(
                    "cf_clearance or user-agent not found for domain: %s", request.domain
                )
                return None

        if cf_clearance_cookie and user_agent:
            return cf_clearance_cookie, user_agent

        logger.warning("cf_clearance or user-agent not found for domain: %s", request.domain)
        return None

    except Exception as exc:
        logger.error("An error occurred for domain %s: %s", request.domain, exc)
        return None

