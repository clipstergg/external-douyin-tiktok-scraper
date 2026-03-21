import asyncio
import logging

from fastapi import APIRouter, Query, Request, HTTPException
from fastapi.responses import Response
from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel

from crawlers.tiktok.app.app_crawler import TikTokAPPCrawler

logger = logging.getLogger("Douyin_TikTok_Download_API_Crawlers")

router = APIRouter()
TikTokAPPCrawler = TikTokAPPCrawler()


@router.get("/fetch_one_video",
            response_model=ResponseModel,
            summary="获取单个作品数据/Get single video data"
            )
async def fetch_one_video(request: Request,
                          aweme_id: str = Query(example="7350810998023949599", description="作品id/Video id")):
    """
    # [中文]
    ### 用途:
    - 获取单个作品数据
    ### 参数:
    - aweme_id: 作品id
    ### 返回:
    - 作品数据

    # [English]
    ### Purpose:
    - Get single video data
    ### Parameters:
    - aweme_id: Video id
    ### Return:
    - Video data

    # [示例/Example]
    aweme_id = "7350810998023949599"
    """
    task = asyncio.create_task(TikTokAPPCrawler.fetch_one_video(aweme_id))

    while not task.done():
        if await request.is_disconnected():
            task.cancel()
            logger.warning("fetch_one_video client disconnected for aweme_id=%s", aweme_id)
            return Response(status_code=499)
        await asyncio.sleep(0.1)

    try:
        data = task.result()
        return ResponseModel(code=200,
                             router=request.url.path,
                             data=data)
    except Exception as e:
        logger.warning("fetch_one_video failed for aweme_id=%s: %s", aweme_id, e)
        status_code = 400
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())
    