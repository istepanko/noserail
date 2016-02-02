from nose.plugins import Plugin
import json
import os
import requests
from datetime import datetime
import base64
import traceback

CASE_ID = 'case_id'


def elapsed_time(seconds):
    suffixes=['y','w','d','h','m','s']
    time = []
    parts = [(suffixes[0], 60 * 60 * 24 * 7 * 52),
          (suffixes[1], 60 * 60 * 24 * 7),
          (suffixes[2], 60 * 60 * 24),
          (suffixes[3], 60 * 60),
          (suffixes[4], 60),
          (suffixes[5], 1)]
    for suffix, length in parts:
        value = seconds / length
        if value > 0:
            seconds = seconds % length
            time.append('%s%s' % (str(value), suffix))
        if seconds < 1:
            break
    return ' '.join(time)


def case_id(id):
    """Decorator that adds test case id to a test"""
    def wrap_ob(ob):
        setattr(ob, CASE_ID, id)
        return ob
    return wrap_ob


class NoseTestRail(Plugin):
    name = 'nose-testrail'

    def options(self, parser, env=os.environ):
        super(NoseTestRail, self).options(parser, env=env)

    def configure(self, options, conf):
        super(NoseTestRail, self).configure(options, conf)
        if not self.enabled:
            return

    def begin(self):
        self.time_before = datetime.now()

    def startTest(self, test):
        self.test_case_id = self.get_test_case_id(test)
        self.result = {}

    def stopTest(self, test):
        time_after = datetime.now()
        delta = time_after - self.time_before
        self.result['elapsed'] = elapsed_time(delta.seconds)
        self.time_before = time_after
        self.send_result(self.result)

    def addSuccess(self, test):
        self.result['status_id'] = 1
        self.result['comment'] = 'test PASS'

    def addFailure(self, test, err):
        self.result['status_id'] = 5
        self.result['comment'] = self.formatErr(err)

    def addError(self, test, err):
        self.result['status_id'] = 5
        self.result['comment'] = self.formatErr(err)

    def send_result(self, result):
        if self.test_case_id:
            headers = dict()
            headers['Content-Type'] = 'application/json'
            user = os.environ['TESTRAIL_USERNAME']
            password = os.environ['TESTRAIL_PASSWORD']
            auth = base64.b64encode('%s:%s' % (user, password)).strip()
            headers['Authorization'] = 'Basic %s' % auth
            host = os.environ['TESTRAIL_HOST']
            run_id = os.environ['TESTRAIL_RUN_ID']
            if host:
                uri = 'https://{0}/index.php?/api/v2/add_result_for_case/{1}/{2}'.format(
                    host, run_id, self.test_case_id)
                requests.Request(
                    method='POST',
                    url=uri,
                    data=json.dumps(result),
                    headers=headers
                )

    def formatErr(self, err):
        """format error"""
        exctype, value, tb = err
        tr = traceback.format_exception(exctype, value, tb)
        return "".join(tr)

    def get_test_case_id(self, test):
        test_name = test.id().split('.')[-1]
        test_method = getattr(test.test, test_name)
        try:
            test_case_id = getattr(test_method, CASE_ID)
        except AttributeError:
            test_case_id = None
        return test_case_id


class APIError(Exception):
    pass
