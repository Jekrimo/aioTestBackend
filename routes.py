# from aiohttp import web
# from typing import Any, AsyncIterator, Awaitable, Callable, Dict
# import asyncio
# import aiohttp_cors

# router = web.RouteTableDef()

# def handle_json_error(
#     func: Callable[[web.Request], Awaitable[web.Response]]
# ) -> Callable[[web.Request], Awaitable[web.Response]]:
#     async def handler(request: web.Request) -> web.Response:
#         try:
#             return await func(request)
#         except asyncio.CancelledError:
#             raise
#         except Exception as ex:
#             return web.json_response(
#                 {"status": "failed", "reason": str(ex)}, status=400
#             )

#     return handler

    
# @router.get("/users")
# @handle_json_error
# async def api_list_users(request: web.Request) -> web.Response:
#     ret = []
#     db = request.config_dict["DB"]
#     async with db.execute("SELECT id, email, name, password, is_active, last_login FROM users") as cursor:
#         async for row in cursor:
#             ret.append({
#                 "data": {
#                     "id": row["id"],
#                     "name": row["name"],
#                     "password": row["password"],
#                     "email": row["email"],
#                     "is_active": row["is_active"],
#                     "last_login": row["last_login"],
#                 }}
#             )
#     return web.json_response(ret)    

# @router.post("/users")
# @handle_json_error
# async def api_new_user(request: web.Request) -> web.Response:
#     user = await request.json()
#     name = user["name"]
#     email = user["email"]
#     password = user["password"]
#     db = request.config_dict["DB"]
#     async with db.execute(
#         "INSERT INTO users (email, password, name) VALUES(?, ?, ?)",
#         [email, password, name],
#     ) as cursor:
#         user_id = cursor.lastrowid
#     await db.commit()
#     return web.json_response(
#         {
#             "status": "ok",
#             "user": {
#                 "id": user_id,
#                 "name": name,
#                 "email": email,
#                 "password": password,
#                 "is_active": True,
#             },
#         }
#     )
# def __initAuth__():
#     app = web.Application()
#     app.add_routes(router)
#     cors = aiohttp_cors.setup(app, defaults={
#         "http://localhost:4200": aiohttp_cors.ResourceOptions(
#                 allow_credentials=True,
#                 expose_headers=("X-Custom-Server-Header",),
#                 allow_methods=["POST", "PUT", "GET", "OPTIONS"],
#                 allow_headers=("X-Requested-With", "Content-Type"),
#                 max_age=3600,
#                 )
#         })
#     for route in list(app.router.routes()):
#         cors.add(route)