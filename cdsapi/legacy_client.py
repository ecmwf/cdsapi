import abc
import logging
import os

import requests


def read_config(path):
    config = {}
    with open(path) as f:
        for line in f.readlines():
            if ":" in line:
                k, v = line.strip().split(":", 1)
                if k in ("url", "key", "verify"):
                    config[k] = v.strip()
    return config


class LegacyClient(abc.ABC):
    logger = logging.getLogger("cdsapi")

    def __init__(
        self,
        url=None,
        key=None,
        quiet=False,
        debug=False,
        verify=None,
        timeout=60,
        progress=True,
        full_stack=False,
        delete=True,
        retry_max=500,
        sleep_max=120,
        wait_until_complete=True,
        info_callback=None,
        warning_callback=None,
        error_callback=None,
        debug_callback=None,
        metadata=None,
        forget=False,
        session=requests.Session(),
    ):
        self.args = [
            url,
            key,
            quiet,
            debug,
            verify,
            timeout,
            progress,
            full_stack,
            delete,
            retry_max,
            sleep_max,
            wait_until_complete,
            info_callback,
            warning_callback,
            error_callback,
            debug_callback,
            metadata,
            forget,
            session,
        ]

        if not quiet:
            if debug:
                level = logging.DEBUG
            else:
                level = logging.INFO

            self.logger.setLevel(level)

            # avoid duplicate handlers when creating more than one Client
            if not self.logger.handlers:
                formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
                handler = logging.StreamHandler()
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)

        if url is None:
            url = os.environ.get("CDSAPI_URL")
        if key is None:
            key = os.environ.get("CDSAPI_KEY")
        dotrc = os.environ.get("CDSAPI_RC", os.path.expanduser("~/.cdsapirc"))

        if url is None or key is None:
            if os.path.exists(dotrc):
                config = read_config(dotrc)

                if key is None:
                    key = config.get("key")

                if url is None:
                    url = config.get("url")

                if verify is None:
                    verify = bool(int(config.get("verify", 1)))

        if url is None or key is None or key is None:
            raise Exception("Missing/incomplete configuration file: %s" % (dotrc))

        # If verify is still None, then we set to default value of True
        if verify is None:
            verify = True

        self.url = url
        self.key = key

        self.quiet = quiet
        self.progress = progress and not quiet

        self.verify = True if verify else False
        self.timeout = timeout
        self.sleep_max = sleep_max
        self.retry_max = retry_max
        self.full_stack = full_stack
        self.delete = delete
        self.last_state = None
        self.wait_until_complete = wait_until_complete

        self.debug_callback = debug_callback
        self.warning_callback = warning_callback
        self.info_callback = info_callback
        self.error_callback = error_callback

        self._initialize_session(session)

        self.metadata = metadata
        self.forget = forget

        self.debug(
            "CDSAPI %s",
            dict(
                url=self.url,
                key=self.key,
                quiet=self.quiet,
                verify=self.verify,
                timeout=self.timeout,
                progress=self.progress,
                sleep_max=self.sleep_max,
                retry_max=self.retry_max,
                full_stack=self.full_stack,
                delete=self.delete,
                metadata=self.metadata,
                forget=self.forget,
            ),
        )

    def _initialize_session(self, session):
        self.session = session

    @abc.abstractmethod
    def retrieve(self, name, request, target=None):
        ...

    @abc.abstractmethod
    def service(self, name, *args, **kwargs):
        ...

    @abc.abstractmethod
    def workflow(self, code, *args, **kwargs):
        ...

    @abc.abstractmethod
    def status(self, context=None):
        ...

    def info(self, *args, **kwargs):
        if self.info_callback:
            self.info_callback(*args, **kwargs)
        else:
            self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        if self.warning_callback:
            self.warning_callback(*args, **kwargs)
        else:
            self.logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        if self.error_callback:
            self.error_callback(*args, **kwargs)
        else:
            self.logger.error(*args, **kwargs)

    def debug(self, *args, **kwargs):
        if self.debug_callback:
            self.debug_callback(*args, **kwargs)
        else:
            self.logger.debug(*args, **kwargs)

    @abc.abstractmethod
    def download(self, results, targets=None):
        ...

    @abc.abstractmethod
    def remote(self, url):
        ...

    @abc.abstractmethod
    def robust(self, call):
        ...
