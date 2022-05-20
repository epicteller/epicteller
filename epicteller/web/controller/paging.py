#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, Union

from fastapi import Request
from starlette.datastructures import URL

from epicteller.web.model import PagingInfo


def remove_host(url: URL) -> URL:
    if not url:
        return url
    return url.replace(
        hostname='',
        port=None,
        netloc='',
        scheme='',
    )


async def generate_paging_info(r: Request, *,
                               only_path: Optional[bool] = True,
                               before: Optional[str] = None,
                               after: Optional[str] = None,
                               offset: Optional[int] = None,
                               limit: Optional[int] = 20,
                               total: Optional[int] = None,
                               is_end: Optional[bool] = False) -> PagingInfo:
    url = r.url
    previous_url: Optional[Union[URL, str]] = None
    next_url: Optional[Union[URL, str]] = None
    if before:
        params = {'before': before, 'limit': limit}
        previous_url = url.replace_query_params(**params)
    if after:
        params = {'after': after, 'limit': limit}
        next_url = url.replace_query_params(**params)
    if total is not None and offset is not None:
        is_end = offset >= total
    if only_path:
        previous_url = remove_host(previous_url)
        next_url = remove_host(next_url)
    return PagingInfo(next=str(next_url) if next_url else None,
                      previous=str(previous_url) if previous_url else None,
                      total=total,
                      is_end=is_end)
