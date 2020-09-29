#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
from signal import signal, SIGINT

from epicteller.web.app import create_app


def main():
    app = create_app()
    server = app.create_server('0.0.0.0', 5000, debug=True, return_asyncio_server=True)
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(server)
    signal(SIGINT, lambda s, f: loop.stop())
    server = loop.run_until_complete(task)
    server.after_start()
    try:
        loop.run_forever()
    except KeyboardInterrupt as e:
        loop.stop()
    finally:
        server.before_stop()

        # Wait for server to close
        close_task = server.close()
        loop.run_until_complete(close_task)

        # Complete all tasks on the loop
        for connection in server.connections:
            connection.close_if_idle()
        server.after_stop()


if __name__ == '__main__':
    main()
