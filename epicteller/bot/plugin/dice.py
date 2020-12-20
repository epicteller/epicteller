#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Iterable, Optional

from nonebot.adapters.cqhttp import MessageSegment
from datum import error as datum_error
from datum.base import Result
from lark import LarkError, UnexpectedCharacters, UnexpectedToken
from nonebot import on_message, on_command, permission
from nonebot.adapters.cqhttp import Bot
from nonebot.rule import regex
from nonebot.typing import Event

from epicteller.bot.controller import base
from epicteller.core.config import Config
from epicteller.core.controller import dice as dice_ctl
from epicteller.core.controller import message as message_ctl
from epicteller.core.model.character import Character
from epicteller.core.model.episode import Episode
from epicteller.core.model.message import DiceMessageContent
from epicteller.core.util.enum import DiceType, MessageType


dice = on_message(rule=regex(r'^[#:：]|(\.r)(.*)'))


@dice.handle()
async def _(bot: Bot, event: Event, state: dict):
    await prepare(bot, event, state)
    is_prepared = await base.prepare_context(dice, bot, event, state)
    result, reason = await must_get_dice_result(bot, event, state)
    value = result.value
    reason_clause = f"以「{reason}」的名义" if reason else ''
    msg = f"🎲 {MessageSegment.at(event.user_id)} {reason_clause}掷出了"
    if isinstance(value, Iterable):
        dice_type = DiceType.ARRAY
        msg += f"一串骰子，分别是 {', '.join(map(str, value))} 点。\n"
    elif isinstance(value, bool):
        dice_type = DiceType.CHECK
        # TODO: 现在还没有 CHECK 类型的骰子
        raise NotImplementedError
    else:
        dice_type = DiceType.SCALAR
        msg += f" {value} 点。\n"
    msg += f"展开算式：\n{result}"

    await dice.send(msg)
    if not is_prepared:
        await dice.finish()
    episode: Episode = state.get('episode')
    character: Character = state.get('character')
    is_gm: bool = state.get('is_gm')
    content = DiceMessageContent(
        dice_type=dice_type,
        reason=reason or None,
        expression=state.get('expr'),
        detail=str(result),
        value=value,
    )
    await message_ctl.create_message(episode, character, MessageType.DICE, content, is_gm)


async def prepare(bot: Bot, event: Event, state: dict):
    if 'anonymous' in event.raw_event and event.raw_event['anonymous']:
        await dice.finish((f"化身为「{event.raw_event['anonymous']['name']}」的无名鼠辈啊……"
                           f"若要掷出决定命运之骰的话，不如先光明正大地亮出自己的身份如何？"))
    arg = event.raw_message[len(state['_matched']):].strip().strip()
    if not arg:
        await dice.finish('🤔 奇怪，好像没有见到算式呢？')
    args = arg.split('|', maxsplit=1)
    state['expr'] = args[0]
    if len(args) > 1:
        state['reason'] = args[1]


async def must_get_dice_result(bot: Bot, event: Event, state: dict) -> (Result, Optional[str]):
    result: Optional[Result] = None
    reason: Optional[str] = state.get('reason')
    errmsg: Optional[str] = None
    user_id = event.user_id
    expr: str = state.get('expr')
    while True:
        try:
            result = await dice_ctl.roll_dice(expr)
        except (UnexpectedCharacters, UnexpectedToken) as e:
            if not reason:
                pos = e.column - 1
                expr, reason = expr[:pos], expr[pos:]
                continue
            errmsg = f"🤔 似乎 {MessageSegment.at(user_id)} 的算式写错了，再检查一下如何？"
        except ZeroDivisionError:
            errmsg = f"喂！{MessageSegment.at(user_id)}！为什么要除以零啊……！💢"
        except datum_error.DiceFaceTooSmallError as e:
            errmsg = f"😒 {MessageSegment.at(user_id)} 竟然试图掷出 {e.face} 面的骰子……给我认真一点啊！"
        except datum_error.DiceFaceTooBigError:
            errmsg = f"😒 {MessageSegment.at(user_id)} 哪里有这么多面的骰子啊！……面数要控制在 10000 以下才行。"
        except (datum_error.DiceCountTooSmallError, datum_error.EmptyDiceletError):
            errmsg = f"🤔 {MessageSegment.at(user_id)} 掷出了一串寂寞。\n至少也得投一个骰子才行吧？"
        except datum_error.DiceCountTooBigError:
            errmsg = f"😠 {MessageSegment.at(user_id)}！一次不要掷这么多骰子啊！给我把数量控制在 1000 以下！"
        except datum_error.DiceHighestTooSmallError as e:
            errmsg = f"😒 {MessageSegment.at(user_id)} 竟然试图从中选出 {e.highest} 个骰子……给我认真一点啊！"
        except datum_error.DiceLowestTooSmallError as e:
            errmsg = f"😒 {MessageSegment.at(user_id)} 竟然试图从中选出 {e.lowest} 个骰子……给我认真一点啊！"
        except (datum_error.DiceHighestTooBigError, datum_error.DiceHighestTooBigError):
            errmsg = f"😠 {MessageSegment.at(user_id)}！给我把数量控制在 10000 以下！"
        except datum_error.DiceletOverSizeError:
            errmsg = f"😠 {MessageSegment.at(user_id)}！一次不要掷这么多骰子啊！给我把数量控制在 100 以下！"
        except datum_error.DiceletSizeMismatchError:
            errmsg = f"🤔 {MessageSegment.at(user_id)} 两串骰子的数量一定要一致，再检查一下自己的算式吧？"
        except LarkError:
            errmsg = f"🤔 似乎 {MessageSegment.at(user_id)} 的算式写错了。再检查一下如何？"
        except Exception as e:
            print(e)
            errmsg = (f"💦 啊啊不好意思，在计算过程中发生了奇怪的错误！\n"
                      f"……不、不如 {MessageSegment.at(user_id)} 试着重投一下？")
            # TODO: 上报到 Sentry
        if errmsg:
            await dice.finish(errmsg)
        break
    if reason:
        reason = reason.strip()
    if not reason:
        reason = None
    return result, reason


refresh = on_command('refresh', permission=permission.PRIVATE_FRIEND)


@refresh.handle()
async def _(bot: Bot, event: Event, state: dict):
    seed = event.raw_message.encode('utf8')
    if not seed:
        seed = None
    await dice_ctl.refresh_randomizer(seed)
    await refresh.finish(str(Config.RUNTIME_ID))


predict = on_command('p', permission=permission.PRIVATE_FRIEND)


@predict.handle()
async def _(bot: Bot, event: Event, state: dict):
    await dice_ctl.update_memory_dump()
    await predict.finish(str(Config.RUNTIME_ID))
