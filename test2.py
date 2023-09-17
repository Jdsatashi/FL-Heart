import asyncio

async def main():
    print('Hello ...')
    await asyncio.sleep(5)
    print('... World!')

asyncio.run(main())
