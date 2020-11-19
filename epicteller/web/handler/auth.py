#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from epicteller.core.controller import member as member_ctl

router = APIRouter()


class Token(BaseModel):
    access_token: str
    refresh_token: str


@app.route('/register')
class RegisterHandler(HTTPMethodView):
    async def post(self, request: Request):
        data = request.json
        email = data['email'].lower()
        name = data['name']
        password = data['password']
        member = await member_ctl.register_member(name, email, password)
        auth.login_user(request, member)
        return response.json(member)


@app.route('/login')
class LoginHandler(HTTPMethodView):
    @staticmethod
    @auth.login_required
    async def get(request: Request):
        return response.json(auth.current_user(request))

    async def post(self, request: Request):
        data = request.json
        email = data['email'].lower()
        password = data['password']
        matched = await member_ctl.check_member_email_password(email, password)
        if not matched:
            return response.json({'error': 'Email or password incorrect.'}, status=403)
        member = await member_ctl.get_member(email=email)
        return response.json(member)


@router.post('/login')
async def login(email: str = Body(...), password: str = Body(...)):
    matched = await member_ctl.check_member_email_password(email, password)
    if not matched:
        return HTTPException(404, detail='邮箱或密码不正确')
    member = await


@app.route('/logout')
class LogoutHandler(HTTPMethodView):
    @staticmethod
    @auth.login_required
    async def post(request: Request):
        auth.logout_user(request)
        return response.text('', status=204)
