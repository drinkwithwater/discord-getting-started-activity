
import asyncio
import aiohttp
import os
from aiohttp import web

async def fetch_token(request):
    # 从环境变量中获取信息
    client_id = os.getenv('VITE_DISCORD_CLIENT_ID')
    client_secret = os.getenv('DISCORD_CLIENT_SECRET')

    # 从请求体中获取 code
    code = request.POST.get('code')

    # 构建请求数据
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'code': code
    }

    # 发送 POST 请求
    async with aiohttp.ClientSession() as session:
        async with session.post('https://discord.com/api/oauth2/token', data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'}) as response:
            if response.status == 200:
                json_response = await response.json()
                access_token = json_response.get('access_token')
                return web.Response(text=json.dumps({'access_token': access_token}), content_type='application/json')
            else:
                return web.Response(status=response.status, text='Failed to fetch token')

async def main():
    app = web.Application()
    app.router.add_post('/api/token', fetch_token)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 3001)
    await site.start()

if __name__ == '__main__':
    asyncio.run(main())
