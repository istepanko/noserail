from nose.plugins import Plugin
import json
import os
import requests
import base64
import time
CASE_ID = 'case_id'
import nose.case


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
        self.items = ['root: INFO: ', 'root: CRITICAL: ', 'DEBUG: ',
                      '-------------------- >> begin captured logging << --------------------',
                      '--------------------- >> end captured logging << ---------------------']
        user = os.environ['TESTRAIL_USERNAME']
        password = os.environ['TESTRAIL_PASSWORD']
        to_encode = '{0}:{1}'.format(user, password).encode('ascii')
        auth = base64.b64encode(to_encode).strip().decode('utf-8')
        self.headers = dict()
        self.headers['Authorization'] = 'Basic {0}'.format(auth)
        self.headers['Content-Type'] = 'application/json'
        if os.environ['TESTRAIL_HOST']:
            self.host = os.environ['TESTRAIL_HOST']
        else:
            self.host = 'ayla.testrail.com'

    def startTest(self, test):
        self.test_name = test.__str__()
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
        self.result['comment'] = self.formatErr(err)

    def send_result(self, result):
        if self.test_case_id:
            run_id = self.get_last_run_id(self.test_case_id)
            if run_id:
                uri = 'https://{0}/index.php?/api/v2/add_result_for_case/{1}/{2}'.format(
                    self.host, run_id, self.test_case_id)
                try:
                    data = json.dumps(result)
                except Exception:
                    result['comment'] = 'Could not send comment.'
                    data = json.dumps(result)
                requests.request(
                        method='POST',
                        url=uri,
                        data=data,
                        headers=self.headers
                    )

    def get_last_run_id(self, case_id):
        r = requests.request(
            method='GET',
            url='https://{0}/index.php?/api/v2/get_case/{1}'.format(self.host, case_id),
            headers=self.headers
        )
        if r.status_code == 200:
            suite_id = r.json()['suite_id']
            r = requests.request(
                method='GET',
                url='https://{0}/index.php?/api/v2/get_suite/{1}'.format(self.host, suite_id),
                headers=self.headers
            )
            if r.status_code == 200:
                project_id = r.json()['project_id']
                r = requests.request(
                    method='GET',
                    url='https://{0}/index.php?/api/v2/get_runs/{1}&suite_id={2}&limit=1'.format(self.host, project_id,
                                                                                                 suite_id),
                    headers=self.headers
                )
                if r.status_code == 200:
                    return r.json()[0]['id']
            else:
                return False

    def formatErr(self, err):
        exctype, value, tb = err
        self.items.append(self.test_name)
        value = str(value)
        for item in self.items:
            value = value.replace(item, '')
        return value

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
