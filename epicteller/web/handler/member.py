#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends

from epicteller.core.model.member import Member
from epicteller.web.controller.auth import get_current_member

router = APIRouter()


@router.get('/me')
async def me(member: Member = Depends(get_current_member)):
    return member
