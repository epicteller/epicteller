#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional

from fastapi import Request
from starlette.datastructures import URL

from epicteller.web.model import PagingInfo


async def generate_paging_info(r: Request, *,
                               before: Optional[str] = None,
                               after: Optional[str] = None,
                               offset: Optional[int] = None,
                               limit: Optional[int] = 20,
                               total: Optional[int] = None,
                               is_end: Optional[bool] = False) -> PagingInfo:
    url = r.url
    previous_url: Optional[URL] = None
    next_url: Optional[URL] = None
    if before:
        params = {'before': before, 'limit': limit}
        previous_url = url.replace_query_params(**params)
    if after:
        params = {'after': after, 'limit': limit}
        next_url = url.replace_query_params(**params)
    if total is not None and offset is not None:
        is_end = offset >= total
    return PagingInfo(next=str(next_url) if next_url else None,
                      previous=str(previous_url) if previous_url else None,
                      total=total,
                      is_end=is_end)
