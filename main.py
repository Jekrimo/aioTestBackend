# from aiohttp import web
# import aiohttp_cors
# import json

# async def handle(request):
#     name = request.match_info.get('name', "Anoous")
#     text = "Hello, " + name
#     y = json.dumps(text)
#     return web.json_response(y, headers={
#             "X-Custom-Server-Header": "Custom data",
#         })
# # async def testroute(request):
# #     id = request.match_info.get('id')
# #     print(id)
# #     # confirmhit = 'confirmhit'
# #     return web.Response('confirmhit')
# app = web.Application()
# cors = aiohttp_cors.setup(app)
# resource = cors.add(app.router.add_resource("/test/{name}"))
# route = cors.add(
#     resource.add_route("GET", handle), {
#         "http://localhost:4200": aiohttp_cors.ResourceOptions(
#             allow_credentials=True,
#             expose_headers=("X-Custom-Server-Header",),
#             allow_headers=("X-Requested-With", "Content-Type"),
#             max_age=3600,
#         )
#     })

# # for route in list(app.router.routes()):
# #     cors.add(route)
# app.add_routes([web.get('/', handle),
#                 web.get('/{name}', handle),
#                 web.get('/test/{name}', handle)])

# if __name__ == '__main__': web.run_app(app)

import asyncio
import sqlite3
from pathlib import Path
from typing import Any, AsyncIterator, Awaitable, Callable, Dict
import aiohttp_cors
import json
import aiosqlite
from aiohttp import web


router = web.RouteTableDef()

async def fetch_post(db: aiosqlite.Connection, post_id: int) -> Dict[str, Any]:
    async with db.execute(
        "SELECT owner, editor, title, text FROM posts WHERE id = ?", [post_id]
    ) as cursor:
        row = await cursor.fetchone()
        if row is None:
            raise RuntimeError(f"Post {post_id} doesn't exist")
        return {
            "id": post_id,
            "owner": row["owner"],
            "editor": row["editor"],
            "title": row["title"],
            "text": row["text"],
        }


def handle_json_error(
    func: Callable[[web.Request], Awaitable[web.Response]]
) -> Callable[[web.Request], Awaitable[web.Response]]:
    async def handler(request: web.Request) -> web.Response:
        try:
            return await func(request)
        except asyncio.CancelledError:
            raise
        except Exception as ex:
            return web.json_response(
                {"status": "failed", "reason": str(ex)}, status=400
            )

    return handler


@router.get("/")
async def root(request: web.Request) -> web.Response:
    y = json.dumps('text')
    return web.Response(text="Placeholder")


@router.get("/api")
@handle_json_error
async def api_list_posts(request: web.Request) -> web.Response:
    ret = []
    db = request.config_dict["DB"]
    async with db.execute("SELECT id, owner, editor, title FROM posts") as cursor:
        async for row in cursor:
            ret.append(
                {
                    "id": row["id"],
                    "owner": row["owner"],
                    "editor": row["editor"],
                    "title": row["title"],
                }
            )
    return web.json_response({"status": "ok", "data": ret})


@router.post("/api")
@handle_json_error
async def api_new_post(request: web.Request) -> web.Response:
    post = await request.json()
    title = post["title"]
    text = post["text"]
    owner = post["owner"]
    db = request.config_dict["DB"]
    async with db.execute(
        "INSERT INTO posts (owner, editor, title, text) VALUES(?, ?, ?, ?)",
        [owner, owner, title, text],
    ) as cursor:
        post_id = cursor.lastrowid
    await db.commit()
    return web.json_response(
        {
            "status": "ok",
            "data": {
                "id": post_id,
                "owner": owner,
                "editor": owner,
                "title": title,
                "text": text,
            },
        }
    )


@router.get("/api/{post}")
@handle_json_error
async def api_get_post(request: web.Request) -> web.Response:
    post_id = request.match_info["post"]
    db = request.config_dict["DB"]
    post = await fetch_post(db, post_id)
    return web.json_response(
        {
            "status": "ok",
            "data": {
                "id": post_id,
                "owner": post["owner"],
                "editor": post["editor"],
                "title": post["title"],
                "text": post["text"],
            },
        }
    )


@router.delete("/api/{post}")
@handle_json_error
async def api_del_post(request: web.Request) -> web.Response:
    post_id = request.match_info["post"]
    db = request.config_dict["DB"]
    async with db.execute("DELETE FROM posts WHERE id = ?", [post_id]) as cursor:
        if cursor.rowcount == 0:
            return web.json_response(
                {"status": "fail", "reason": f"post {post_id} doesn't exist"},
                status=404,
            )
    await db.commit()
    return web.json_response({"status": "ok", "id": post_id})


@router.patch("/api/{post}")
@handle_json_error
async def api_update_post(request: web.Request) -> web.Response:
    post_id = request.match_info["post"]
    post = await request.json()
    db = request.config_dict["DB"]
    fields = {}
    if "title" in post:
        fields["title"] = post["title"]
    if "text" in post:
        fields["text"] = post["text"]
    if "editor" in post:
        fields["editor"] = post["editor"]
    if fields:
        field_names = ", ".join(f"{name} = ?" for name in fields)
        field_values = list(fields.values())
        await db.execute(
            f"UPDATE posts SET {field_names} WHERE id = ?", field_values + [post_id]
        )
        await db.commit()
    new_post = await fetch_post(db, post_id)
    return web.json_response(
        {
            "status": "ok",
            "data": {
                "id": new_post["id"],
                "owner": new_post["owner"],
                "editor": new_post["editor"],
                "title": new_post["title"],
                "text": new_post["text"],
            },
        }
    )


def get_db_path() -> Path:
    here = Path.cwd()
    while not (here / ".git").exists():
        if here == here.parent:
            raise RuntimeError("Cannot find root github dir")
        here = here.parent

    return here / "db.sqlite3"


async def init_db(app: web.Application) -> AsyncIterator[None]:
    sqlite_db = get_db_path()
    db = await aiosqlite.connect(sqlite_db)
    db.row_factory = aiosqlite.Row
    app["DB"] = db
    yield
    await db.close()

async def init_app() -> web.Application:
    app = web.Application()
    app.add_routes(router)
    app.cleanup_ctx.append(init_db)
    
#     cors = aiohttp_cors.setup(app)
#     #  cors.add(route)
#     for route in list(router.routes):
#         resource = cors.add(route)
#         cors.setup(app, defaults={
#         "*": aiohttp_cors.ResourceOptions(
#         allow_credentials=True,
#         expose_headers="*",
#         allow_headers="*"
#     )
#   })
#         cors.add(
#         resource.add_route("GET", root), {
#         "http://localhost:4200/home": aiohttp_cors.ResourceOptions(
#             allow_credentials=True,
#             expose_headers=("X-Custom-Server-Header",),
#             allow_headers=("X-Requested-With", "Content-Type"),
#             max_age=3600,
#         )
#     })
    cors = aiohttp_cors.setup(app, defaults={
        "http://localhost:4200": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers=("X-Custom-Server-Header",),
                allow_headers=("X-Requested-With", "Content-Type"),
                max_age=3600,
                )
        })

    for route in list(app.router.routes()):
        cors.add(route)
    
    return app


def try_make_db() -> None:
    sqlite_db = get_db_path()
    if sqlite_db.exists():
        return

    with sqlite3.connect(sqlite_db) as conn:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE posts (
            id INTEGER PRIMARY KEY,
            title TEXT,
            text TEXT,
            owner TEXT,
            editor TEXT,
            image BLOB)
        """
        )
        conn.commit()


try_make_db()
web.run_app(init_app())