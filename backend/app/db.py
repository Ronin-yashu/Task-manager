import threading
from supabase import create_client
from .config import Config

_local = threading.local()


def get_client():
    client = getattr(_local, "client", None)
    if client is None:
        client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        _local.client = client
    return client


class SupabaseProxy:
    def __getattr__(self, name):
        return getattr(get_client(), name)


supabase = SupabaseProxy()