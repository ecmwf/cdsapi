import functools

import cads_api_client.legacy_client

from . import api, legacy_client


class Client(legacy_client.LegacyClient):

    @functools.cached_property
    def client(self):
        client = (
            api.Client
            if ":" in self.key
            else cads_api_client.legacy_client.LegacyClient
        )
        return client(*self.args)

    def retrieve(self, name, request, target=None):
        return self.client.retrieve(name, request, target)

    def service(self, name, *args, **kwargs):
        return self.client.service(name, *args, **kwargs)

    def workflow(self, code, *args, **kwargs):
        return self.client.workflow(code, *args, **kwargs)

    def status(self, context=None):
        return self.client.status(context)

    def download(self, results, targets=None):
        return self.client.download(results, targets)

    def remote(self, url):
        return self.client.remote(url)

    def robust(self, call):
        return self.client.robust(call)
