#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import functools
import inspect
import typing
from typing import Optional

from pydantic import BaseModel
from starlette.authentication import AuthenticationBackend, AuthCredentials, BaseUser
from starlette.requests import HTTPConnection, Request
from starlette.responses import Response, RedirectResponse
from starlette.websockets import WebSocket

from epicteller.core.controller import credential as credential_ctl
from epicteller.web.error.auth import UnauthorizedError


class User(BaseUser, BaseModel):
    id: int
    access_token: Optional[str]

    @property
    def is_authenticated(self) -> bool:
        return self.id != 0

    @property
    def display_name(self) -> str:
        return ''

    @property
    def identity(self) -> int:
        return self.id


class AuthBackend(AuthenticationBackend):
    async def authenticate(self, r: HTTPConnection):
        session_id: Optional[str] = r.cookies.get('q_c0')
        if not session_id:
            return AuthCredentials(), User(id=0)
        credential = await credential_ctl.get_access_credential(session_id)
        if not credential or credential.is_expired:
            return AuthCredentials(), User(id=0)
        if credential.is_stale:
            await credential_ctl.refresh_access_credential(credential)
        return AuthCredentials(['login']), User(id=credential.member_id, access_token=session_id)


def has_required_scope(conn: HTTPConnection, scopes: typing.Sequence[str]) -> bool:
    for scope in scopes:
        if scope not in conn.auth.scopes:
            return False
    return True


def requires(
    scopes: typing.Union[str, typing.Sequence[str]],
    redirect: str = None,
) -> typing.Callable:
    scopes_list = [scopes] if isinstance(scopes, str) else list(scopes)

    def decorator(func: typing.Callable) -> typing.Callable:
        type = None
        name = None
        sig = inspect.signature(func)
        for idx, parameter in enumerate(sig.parameters.values()):
            if issubclass(parameter.annotation, Request):
                type = 'request'
                name = parameter.name
                break
            elif issubclass(parameter.annotation, WebSocket):
                type = 'websocket'
                name = parameter.name
                break
        else:
            raise Exception(
                f'No "request" or "websocket" argument on function "{func}"'
            )

        if type == "websocket":
            # Handle websocket functions. (Always async)
            @functools.wraps(func)
            async def websocket_wrapper(
                *args: typing.Any, **kwargs: typing.Any
            ) -> None:
                websocket = kwargs.get(name, args[idx] if args else None)
                assert isinstance(websocket, WebSocket)

                if not has_required_scope(websocket, scopes_list):
                    await websocket.close()
                else:
                    await func(*args, **kwargs)

            return websocket_wrapper

        elif asyncio.iscoroutinefunction(func):
            # Handle async request/response functions.
            @functools.wraps(func)
            async def async_wrapper(
                *args: typing.Any, **kwargs: typing.Any
            ) -> Response:
                request = kwargs.get(name, args[idx] if args else None)
                assert isinstance(request, Request)

                if not has_required_scope(request, scopes_list):
                    if redirect is not None:
                        return RedirectResponse(
                            url=request.url_for(redirect), status_code=303
                        )
                    raise UnauthorizedError()
                return await func(*args, **kwargs)

            return async_wrapper

        else:
            # Handle sync request/response functions.
            @functools.wraps(func)
            def sync_wrapper(*args: typing.Any, **kwargs: typing.Any) -> Response:
                request = kwargs.get(name, args[idx] if args else None)
                assert isinstance(request, Request)

                if not has_required_scope(request, scopes_list):
                    if redirect is not None:
                        return RedirectResponse(
                            url=request.url_for(redirect), status_code=303
                        )
                    raise UnauthorizedError()
                return func(*args, **kwargs)

            return sync_wrapper

    return decorator
