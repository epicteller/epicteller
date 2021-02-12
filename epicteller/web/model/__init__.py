#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Generic, TypeVar, List, Optional

from pydantic import BaseModel
from pydantic.generics import GenericModel


class BasicResponse(BaseModel):
    success: bool = True


T = TypeVar('T')


class PagingInfo(BaseModel):
    is_end: bool
    next: str
    previous: Optional[str]


class PagingResponse(GenericModel, Generic[T]):
    data: List[T]
    paging: Optional[PagingInfo]
