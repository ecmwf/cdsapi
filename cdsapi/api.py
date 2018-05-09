import requests
import json
import time
import datetime
import os


def bytes_to_string(n):
    u = ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi']
    i = 0
    while n >= 1024:
        n /= 1024.0
        i += 1
    return "%g%s" % (int(n * 10 + 0.5) / 10.0, u[i])


class Client(object):

    def __init__(self, end_point=None, user_id=None, api_key=None, verbose=False, verify=None, timeout=None, full_stack=False):

        dotrc = os.path.expanduser('~/.cdsapirc')

        if end_point is None or user_id is None or api_key is None:
            if os.path.exists(dotrc):
                config = {}
                with open(dotrc) as f:
                    for l in f.readlines():
                        k, v = l.strip().split(':', 1)
                        config[k] = v
                url = config.get('url')
                key = config.get('key')

                if end_point is None:
                    end_point = url

                if user_id is None and key is not None:
                    user_id = key.split(':')[0]

                if api_key is None and key is not None:
                    api_key = key.split(':')[-1]

                if verify is None:
                    verify = int(config.get('verify', 1))

        if end_point is None or api_key is None or api_key is None:
            raise Exception("Missing/incomplete configuration file: %s" % (dotrc))

        if verify is None:
            verify = True

        self.end_point = end_point
        self.user_id = user_id
        self.api_key = api_key

        self.verbose = verbose
        self.verify = verify
        self.timeout = timeout
        self.sleep_max = 120
        self.full_stack = full_stack

        print("===>", self.end_point, self.user_id, self.api_key, self.verify)

    def get_resource(self, name, request, target=None):
        self._api("%s/resources/%s" % (self.end_point, name), request, target)

    def _download(self, url, local_filename=None):

        if local_filename is None:
            local_filename = url.split('/')[-1]

        r = requests.get(url, stream=True, verify=self.verify)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        return local_filename

    def _api(self, url, request, target):

        session = requests.Session()
        session.auth = (str(self.user_id), str(self.api_key))

        self._trace("POST %s %s" % (url, json.dumps(request)))
        result = session.post(url, json=request, verify=self.verify)
        result.raise_for_status()

        try:
            reply = result.json()
        except Exception:
            raise Exception(result.text)

        try:
            result.raise_for_status()
        except Exception:
            if 'message' in reply:
                error = reply['message']

                if 'context' in reply and 'required_terms' in reply['context']:
                    e = [error]
                    for t in reply['context']['required_terms']:
                        e.append("To access this resource, you first need to accept the terms of '%s' at %s" % (t['title'], t['url']))
                    error = '. '.join(e)
                raise Exception(error)
            else:
                raise

        sleep = 1
        start = time.time()

        while True:

            self._trace(reply)

            if reply['state'] == 'completed':

                if self.target:
                    self._download(reply['location'], int(reply['content_length']), target, verify=self.verify)
                else:
                    metadata = session.head(reply['location'], verify=self.verify)
                    metadata.raise_for_status()
                    print(metadata)

                self._trace("Done")
                return

            if reply['state'] in ('queued', 'running'):
                rid = reply['request_id']

                if self.timeout and (time.time() - start > self.timeout):
                    raise Exception("TIMEOUT")

                time.sleep(sleep)
                self._trace("Request ID is %s, sleep %s" % (rid, sleep))
                sleep *= 1.5
                if sleep > self.sleep_max:
                    sleep = self.sleep_max

                result = session.get("%s/tasks/%s" % (self.end_point, rid), verify=self.verify)
                result.raise_for_status()
                reply = result.json()
                continue

            if reply['state'] in ('failed',):
                print("Message: %s" % (reply['error'].get("message"),))
                print("Reason:  %s" % (reply['error'].get("reason"),))
                for n in reply['error']['context']['traceback'].split('\n'):
                    if n.strip() == '' and not self.full_stack:
                        break
                    print("  %s" % (n,))
                raise Exception(reply['error'].get("reason"),)

            raise Exception("Unknown API state [%s]" % (reply['state'],))

    def _trace(self, what):
        if isinstance(what, (dict, list)):
            what = json.dumps(what, indent=4, sort_keys=True)

        ts = "{:%Y-%m-%d %H:%M:%S}".format(datetime.datetime.now())
        print('CDS-API %s %s' % (ts, what))
