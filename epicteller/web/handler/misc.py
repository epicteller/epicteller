#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64

from fastapi import APIRouter
from pydantic import BaseModel

from epicteller.core.util import imghosting
from epicteller.web.error.misc import BadRequestError
from epicteller.web.model import BasicResponse

router = APIRouter()


class UploadForm(BaseModel):
    data: str


class UploadResponse(BasicResponse):
    token: str
    url: str
    width: int
    height: int


@router.post('/image-upload', response_model=UploadResponse)
async def image_upload(form: UploadForm):
    data: bytes
    try:
        data = base64.b64decode(form.data)
    except:
        raise BadRequestError()
    token, width, height = await imghosting.upload_image(data)
    return UploadResponse(token=token, url=imghosting.get_full_url(token),
                          width=width, height=height)
