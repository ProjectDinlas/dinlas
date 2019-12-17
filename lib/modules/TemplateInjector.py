# coding:utf-8

from urllib import parse

import requests
import random


class TemplateInjector:
    def __init__(self, results, reports, **kwargs):
        self.results = results
        self.reports = reports
        self.args = kwargs
        self.vulnerable = []

    @staticmethod
    def meta():
        return {
            'name': 'Template Injector for all',
            'version': '1.0'
        }

    def exec(self):
        def set_payload():
            randint1 = random.randint(32768, 65536)
            randint2 = random.randint(16384, 32768)

            _sum = randint1 + randint2

            _payload = '{{' + str(randint1) + '+' + str(randint2) + '}}'
            check_str = str(_sum)
            return {'payload': _payload, 'check_str': check_str}

        header = {
            'User_Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.'
                          '2924.87 Safari/537.36'
        }

        raw_url = self.results['url']

        for url in raw_url:
            check = set()
            attack_url = []

            if url[0:4] != 'http':
                url = 'http://' + url
            parse_result = parse.urlparse(url)
            query = parse.parse_qs(parse_result.query)

            split_dir = parse_result.path.split('/')
            _url = parse_result.scheme + '://' + parse_result.netloc

            for i in range(1, len(split_dir)):
                payload = set_payload()
                former = '/'.join(split_dir[0:i])
                latter = '/'.join(split_dir[i+1:])
                check_url = _url + former + latter
                if check_url in check:
                    continue
                check.add(check_url)
                _url += former + '/' + payload['payload']
                if latter != '':
                    _url += '/' + latter
                attack_url.append({'url': _url, 'payload': payload})

            _url += parse_result.path

            for value in query.values():
                for i in value:
                    q = ''
                    payload = set_payload()
                    for _key, _value in query.items():
                        for j in _value:
                            q += '&' + _key + '='
                            if i == j:
                                q += payload['payload']
                            else:
                                q += j
                    q = '?' + q[1:]
                    attack_url.append({'url': _url + q, 'payload': payload})

            for test_url in attack_url:
                req = requests.get(test_url, header=header)
                if req.text.find(test_url['payload']['check_str']) != -1:
                    self.vulnerable.append({
                        'url': test_url['url'],
                        'payload': test_url['payload']['payload']
                    })

            self.reports.append({
                'title': 'Server Side Template Injection Points',
                'overview': 'Found {} SSTI point(s)'.format(len(self.results)),
                'header': ['Path', 'Payload'],
                'entries': list(map(lambda x: [x['url'], x['payload']], self.vulnerable))
            })

        pass
