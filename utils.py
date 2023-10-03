import os

cookies = {
    'cck1': os.getenv('CCK1'),
    'lg_pref': os.getenv('LG_PREF'),
    'webtools_session': os.getenv('WEBTOOLS_SEASON'),
    'JSESSIONID': os.getenv('JSESSIONID')
}


def fetch_response(session, url, cookies, params=None):
    response = session.get(url, cookies=cookies, allow_redirects=False, params=params)

    if response.status_code == 200:
        return response
    return None
