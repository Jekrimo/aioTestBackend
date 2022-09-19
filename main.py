from aiohttp import web
import aiohttp_cors

async def handle(request):
    name = request.match_info.get('name', "Anoous")
    text = "Hello, " + name
    
    return web.Response(text=text, headers={
            "X-Custom-Server-Header": "Custom data",
        })
# async def testroute(request):
#     id = request.match_info.get('id')
#     print(id)
#     # confirmhit = 'confirmhit'
#     return web.Response('confirmhit')
app = web.Application()
cors = aiohttp_cors.setup(app)
resource = cors.add(app.router.add_resource("/test/{name}"))
route = cors.add(
    resource.add_route("GET", handle), {
        "http://localhost:4200": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers=("X-Custom-Server-Header",),
            allow_headers=("X-Requested-With", "Content-Type"),
            max_age=3600,
        )
    })

# for route in list(app.router.routes()):
#     cors.add(route)
app.add_routes([web.get('/', handle),
                web.get('/{name}', handle),
                web.get('/test/{name}', handle)])

if __name__ == '__main__': web.run_app(app)