# (C) Copyright 2018 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation nor
# does it submit to any jurisdiction.

import requests
import json
import time
import os
import logging


def bytes_to_string(n):
    u = ['', 'K', 'M', 'G', 'T', 'P']
    i = 0
    while n >= 1024:
        n /= 1024.0
        i += 1
    return '%g%s' % (int(n * 10 + 0.5) / 10.0, u[i])


class Client(object):

    logger = logging.getLogger('cdsapi')

    def __init__(self,
                 end_point=os.environ.get('CDSAPI_URL'),
                 api_key=os.environ.get('CDSAPI_KEY'),
                 verbose=False,
                 verify=None,
                 timeout=None,
                 full_stack=False,
                 delete=False,
                 retry_max=500,
                 sleep_max=120
                 ):

        dotrc = os.environ.get('CDSAPI_RC', os.path.expanduser('~/.cdsapirc'))

        if end_point is None or api_key is None:
            if os.path.exists(dotrc):
                config = {}
                with open(dotrc) as f:
                    for l in f.readlines():
                        k, v = l.strip().split(':', 1)
                        config[k] = v.strip()
                url = config.get('url')
                key = config.get('key')

                if api_key is None:
                    api_key = key

                if end_point is None:
                    end_point = url

                if verify is None:
                    verify = int(config.get('verify', 1))

        if end_point is None or api_key is None or api_key is None:
            raise Exception('Missing/incomplete configuration file: %s' % (dotrc))

        self.end_point = end_point
        self.api_key = api_key

        self.verbose = verbose
        self.verify = True if verify else False
        self.timeout = timeout
        self.sleep_max = sleep_max
        self.retry_max = retry_max
        self.full_stack = full_stack
        self.delete = delete

        self.logger.debug("CDSAPI %s", dict(end_point=self.end_point,
                                            api_key=self.api_key,
                                            verbose=self.verbose,
                                            verify=self.verify,
                                            timeout=self.timeout,
                                            sleep_max=self.sleep_max,
                                            retry_max=self.retry_max,
                                            full_stack=self.full_stack,
                                            delete=self.delete
                                            ))

    def retrieve(self, name, request, target=None):
        self._api('%s/resources/%s' % (self.end_point, name), request, target)

    def _download(self, url, size, local_filename=None):

        if local_filename is None:
            local_filename = url.split('/')[-1]

        self.logger.debug("Downloading %s to %s (%s)", url, local_filename, bytes_to_string(size))
        start = time.time()
        r = self.robust(requests.get)(url, stream=True, verify=self.verify)
        total = 0
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    total += len(chunk)

        assert total == size

        elapsed = time.time() - start
        if elapsed:
            self.logger.debug("Download rate %s/s", bytes_to_string(size / elapsed))
        return local_filename

    def _api(self, url, request, target):

        session = requests.Session()
        session.auth = tuple(self.api_key.split(':', 2))

        self.logger.debug("POST %s, %s", url, json.dumps(request))
        result = self.robust(session.post)(url, json=request, verify=self.verify)
        reply = None

        try:
            result.raise_for_status()
            reply = result.json()
        except Exception:

            if reply is None:
                try:
                    reply = result.json()
                except Exception:
                    reply = dict(message=result.text)

            self.logger.debug(json.dumps(reply))

            if 'message' in reply:
                error = reply['message']

                if 'context' in reply and 'required_terms' in reply['context']:
                    e = [error]
                    for t in reply['context']['required_terms']:
                        e.append("To access this resource, you first need to accept the terms"
                                 "of '%s' at %s" % (t['title'], t['url']))
                    error = '. '.join(e)
                raise Exception(error)
            else:
                raise

        sleep = 1
        start = time.time()

        while True:

            self.logger.debug("REPLY %s", reply)

            if reply['state'] == 'completed':

                if target:
                    self._download(reply['location'], int(reply['content_length']), target)
                else:
                    self.logger.debug("HEAD %s", reply['location'])
                    metadata = self.robust(session.head)(reply['location'], verify=self.verify)
                    metadata.raise_for_status()
                    self.logger.debug(metadata.headers)

                if 'request_id' in reply:
                    rid = reply['request_id']

                    if self.delete:
                        task_url = '%s/tasks/%s' % (self.end_point, rid)
                        self.logger.debug("DELETE %s", task_url)
                        delete = session.delete(task_url, verify=self.verify)
                        self.logger.debug("DELETE returns %s %s", delete.status_code, delete.reason)
                        try:
                            delete.raise_for_status()
                        except Exception:
                            self.logger.warning("DELETE %s returns %s %s",
                                                task_url, delete.status_code, delete.reason)

                self.logger.debug("Done")
                return

            if reply['state'] in ('queued', 'running'):
                rid = reply['request_id']

                if self.timeout and (time.time() - start > self.timeout):
                    raise Exception('TIMEOUT')

                self.logger.debug("Request ID is %s, sleep %s", rid, sleep)
                time.sleep(sleep)
                sleep *= 1.5
                if sleep > self.sleep_max:
                    sleep = self.sleep_max

                task_url = '%s/tasks/%s' % (self.end_point, rid)
                self.logger.debug("GET %s", task_url)

                result = self.robust(session.get)(task_url, verify=self.verify)
                result.raise_for_status()
                reply = result.json()
                continue

            if reply['state'] in ('failed',):
                self.logger.error("Message: %s", reply['error'].get('message'))
                self.logger.error("Reason:  %s", reply['error'].get('reason'))
                for n in reply.get('error', {}).get('context', {}).get('traceback', '').split('\n'):
                    if n.strip() == '' and not self.full_stack:
                        break
                    self.logger.error("  %s", n)
                raise Exception(reply['error'].get('reason'))

            raise Exception('Unknown API state [%s]' % (reply['state'],))

    def robust(self, call):

        def retriable(code, reason):

            if code in [requests.codes.internal_server_error,
                        requests.codes.bad_gateway,
                        requests.codes.service_unavailable,
                        requests.codes.gateway_timeout,
                        requests.codes.too_many_requests,
                        requests.codes.request_timeout]:
                return True

            return False

        def wrapped(*args, **kwargs):
            tries = 0
            while tries < self.retry_max:
                r = call(*args, **kwargs)
                if not retriable(r.status_code, r.reason):
                    return r

                tries += 1

                self.logger.warning("Recovering from HTTP error [%s %s], attemps %s of %s",
                                    r.status_code, r.reason, tries, self.retry_max)
                self.logger.warning("Retrying in %s second (", self.sleep_max)
                time.sleep(self.sleep_max)

        return wrapped
