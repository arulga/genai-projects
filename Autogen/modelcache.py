import asyncio
import os

from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.cache import ChatCompletionCache, CHAT_CACHE_VALUE_TYPE
from autogen_ext.cache_store.diskcache import DiskCacheStore
from diskcache import Cache
import os
from dotenv import load_dotenv

load_dotenv()

CACHE_DIR = "./autogen_cache"  # persistent folder


async def main():
    os.makedirs(CACHE_DIR, exist_ok=True)

    openai_model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    cache = Cache(CACHE_DIR)
    cache_store = DiskCacheStore[CHAT_CACHE_VALUE_TYPE](cache)
    cache_client = ChatCompletionCache(openai_model_client, cache_store)

    response1 = await cache_client.create(
        [UserMessage(content="Hello, how are you?", source="user")]
    )
    print("First call:", response1)

    response2 = await cache_client.create(
        [UserMessage(content="Hello, how are you?", source="user")]
    )
    print("Second call (cached):", response2)

    await openai_model_client.close()
    cache.close()   # IMPORTANT on Windows


asyncio.run(main())
