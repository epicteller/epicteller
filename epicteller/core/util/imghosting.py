#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import functools
import hashlib
import imghdr
import io
from typing import Tuple

import httpx
from PIL import Image
from qcloud_cos import CosConfig, CosS3Client

from epicteller.core.config import Config

config = CosConfig(
    Region=Config.COS_REGION,
    SecretId=Config.COS_SECRET_ID,
    SecretKey=Config.COS_SECRET_KEY,
)

cos_client = CosS3Client(config)


async def upload_image_from_url(url: str) -> Tuple[str, int, int]:
    image_data = await download_image(url)
    token, width, height = await upload_image(image_data)
    return token, width, height


async def download_image(url: str) -> bytes:
    async with httpx.AsyncClient() as http_client:
        r = await http_client.get(url)
        r.raise_for_status()
        return r.content


async def get_image_size(*, token: str = None, data: bytes = None) -> Tuple[int, int]:
    if not token and not data:
        raise ValueError
    if token:
        data = await download_image(get_full_url(token, size='r'))
    img = Image.open(io.BytesIO(data))
    return img.size


async def upload_image(image_data: bytes) -> Tuple[str, int, int]:
    image_type = imghdr.what('', h=image_data)
    if image_type not in {'gif', 'jpeg', 'bmp', 'png', 'webp'}:
        raise TypeError
    width, height = await get_image_size(data=image_data)
    mime_type = f"image/{image_type}"
    m = hashlib.md5()
    m.update(image_data)
    image_hexdigest = m.hexdigest()
    image_digest_b64 = base64.b64encode(m.digest()).decode()
    image_token = f"v1-{image_hexdigest}"
    headers = {
        'Host': config.get_host(Config.COS_IMAGE_BUCKET),
        'Content-Type': mime_type,
        'Content-Length': str(len(image_data)),
        'Content-MD5': image_digest_b64,
    }
    target_url = get_presigned_url(image_token, headers)
    async with httpx.AsyncClient() as http_client:
        r = await http_client.put(target_url, content=image_data, headers=headers)
        r.raise_for_status()
    return image_token, width, height


def get_presigned_url(filename: str, headers: dict, bucket: str=None) -> str:
    if not bucket:
        bucket = Config.COS_IMAGE_BUCKET
    return cos_client.get_presigned_url(
        Bucket=bucket,
        Key=filename,
        Method='PUT',
        Headers=headers,
    )


def get_full_url(token: str, size: str='hd', fmt: str='jpg') -> str:
    if not token:
        return ''
    return f"https://img.epicteller.com/{token}_{size}.{fmt}"


get_avatar_url = functools.partial(get_full_url, size='xl')
