#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from fastapi import APIRouter

from epicteller.core.controller import dice as dice_ctl
from epicteller.web.model import PagingResponse, BasicResponse

router = APIRouter()


@router.get('/predict/{token}', response_model=PagingResponse[int], response_model_exclude_none=True)
async def get_predict(token: str, face: int, start: Optional[int] = 0, end: Optional[int] = 20):
    results = await dice_ctl.predict(token, face, start, end)
    return PagingResponse(data=results)


@router.post('/predict/{token}', response_model=BasicResponse)
async def rollup_predict(token: str, face: int, times: int):
    await dice_ctl.rollup(token, face, times)
    return BasicResponse()
