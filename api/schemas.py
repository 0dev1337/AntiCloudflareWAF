from pydantic import BaseModel


class WafSolveRequest(BaseModel):
    domain: str
    headless: bool = True
    proxy: str | None = None
    disable_coop: bool = True
    locale: list[str] = ["en-US"]
    block_webrtc: bool = False
    block_webgl: bool = False
    humanize: bool = True
    geoip: bool = True
    os: str = "macos"
    i_know_what_im_doing: bool = True