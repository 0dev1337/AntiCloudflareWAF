from fastapi import APIRouter
from fastapi.responses import JSONResponse

from api.schemas import WafSolveRequest
from services.cloudflare_solver import get_waf_cookie

router = APIRouter()


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/waf")
async def solve_waf(payload: WafSolveRequest):
    # print(payload)
    result = await get_waf_cookie(payload)
    if not result:
        return JSONResponse(
            status_code=502,
            content={
                "ok": False,
                "message": "Unable to get cf_clearance cookie",
                "domain": payload.domain,
            },
        )

    cookie, user_agent = result
    return {
        "ok": True,
        "domain": payload.domain,
        "cf_clearance": cookie,
        "user_agent": user_agent,
        "proxy": payload.proxy if payload.proxy is not None else None,
    }

