import asyncio
import random

import aiohttp
from proxybroker.resolver import Resolver
from proxybroker.utils import log


class ResolverCustom(Resolver):
    _temp_host = []

    def _pop_random_ip_host(self):

        host = random.choice(self._temp_host)
        self._temp_host.remove(host)
        return host

    async def get_real_ext_ip(self):
        self._temp_host = self._ip_hosts.copy()
        while self._temp_host:
            try:
                timeout = aiohttp.ClientTimeout(total=self._timeout)
                async with aiohttp.ClientSession(
                        timeout=timeout, loop=self._loop
                ) as session, session.get(self._pop_random_ip_host()) as resp:
                    ip = await resp.text()
            except asyncio.TimeoutError:
                pass
            else:
                ip = ip.strip()
                if self.host_is_ip(ip):
                    log.debug('Real external IP: %s', ip)
                    break
        else:
            raise RuntimeError('Could not get the external IP')
        return ip