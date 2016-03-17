from nose.plugins import Plugin
import json
import os
import requests
import base64
import traceback
import time
CASE_ID = 'case_id'


def case_id(id):
    """Decorator that adds test case id to a test"""
    def wrap_ob(ob):
        setattr(ob, CASE_ID, id)
        return ob
    return wrap_ob


class NoseTestRail(Plugin):
    name = 'noserail'

    def options(self, parser, env=os.environ):
        super(NoseTestRail, self).options(parser, env=env)

    def configure(self, options, conf):
        super(NoseTestRail, self).configure(options, conf)
        if not self.enabled:
            return

    def begin(self):
        pass

    def startTest(self, test):
        self.time_before = time.time()
        self.test_case_id = self.get_test_case_id(test)
        self.result = {}

    def stopTest(self, test):
        self.time_after = time.time()
        difference = self.time_after - self.time_before
        k = str(difference).split('.')
        if int(k[0]) > 50:
            k = 1
        else:
            k = 0
        difference = '{0:.0f}'.format(difference)
        difference = int(difference)
        difference += k
        self.result['elapsed'] = str(difference) + 's'
        self.send_result(self.result)

    def addSuccess(self, test):
        self.result['status_id'] = 1
        self.result['comment'] = 'test PASS'

    def addFailure(self, test, err):
        self.result['status_id'] = 5
        self.result['comment'] = self.formatErr(err)

    def addError(self, test, err):
        self.result['status_id'] = 5
        self.result['comment'] = err

    def send_result(self, result):
        if self.test_case_id:
            headers = dict()
            headers['Content-Type'] = 'application/json'
            user = os.environ['TESTRAIL_USERNAME']
            password = os.environ['TESTRAIL_PASSWORD']
            to_encode = '%s:%s' % (user, password)
            to_encode = to_encode.encode('ascii')
            auth = base64.b64encode(to_encode).strip().decode('utf-8')
            headers['Authorization'] = 'Basic %s' % auth
            host = os.environ['TESTRAIL_HOST']
            run_id = os.environ['TESTRAIL_RUN_ID']
            if host:
                uri = 'https://{0}/index.php?/api/v2/add_result_for_case/{1}/{2}'.format(
                    host, run_id, self.test_case_id)
                r = requests.request(
                    method='POST',
                    url=uri,
                    data=json.dumps(result),
                    headers=headers
                )

    def formatErr(self, err):
        """format error"""
        exctype, value, tb = err
        tr = traceback.format_exception(exctype, value, tb)
        return ''.join(tr)

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
