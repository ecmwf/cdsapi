import functools

import cads_api_client.legacy_api_client

from . import abstract_legacy_client, api


class Client(abstract_legacy_client.AbstractLegacyClient):
    @functools.cached_property
    def client(self):
        if ":" in self.key:
            return api.Client(*self.args)
        return cads_api_client.legacy_api_client.LegacyApiClient(*self.args)

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
