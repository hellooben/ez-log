from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
import requests, pprint, json, base64, urllib

bp = Blueprint('spotify', __name__)

@bp.route('/spotify-auth')
def spotify_auth():
    authURL = "https://accounts.spotify.com/authorize/?"
    # redirect = 'http://morning-shore-58893.herokuapp.com/spotify'
    redirect_url = 'http://0.0.0.0:5000/spotify'
    id = 'adbede0af98a4e9ca397a4cf4a9214df'
    response_type = 'code'
    # scope = ['streaming', 'user-library-read', 'user-read-recently-played', 'user-modify-playback-state', 'user-read-currently-playing', 'user-read-private']
    scope = 'streaming user-library-read user-read-recently-played user-modify-playback-state user-read-currently-playing user-read-private'
    query = {'client_id': id, 'response_type': response_type, 'redirect_uri': redirect_url, 'scope': scope}
    parsed = urllib.parse.urlencode(query)
    redir = authURL + parsed
    # return requests.get(url=authURL, data=json.dumps(query)).text
    auth = requests.get(url=authURL, params=query)
    print(auth.status_code)
    print('AAAAUUUUUTTTTHHHHH: ', auth)
    # print(auth.text)
    # pprint.pprint(auth)
    print('REDIRECT!!!!!!: ', redir)
    # return urllib.parse.urlencode(auth.url)
    return redirect(redir, code=302)
    # pprint.pprint(json.loads(auth.text))
    # # return render_template('blog/spotify.html', response=auth)
    # # return redirect(auth.text)
    # return redirect(url_for('spotify.music'))
    # return render_template(auth.text)
    # return url_for(auth.text)


@bp.route('/spotify')
def spotify():
    token = request.args['code']
    print('TOKEN: ', token)
    token_url = 'https://accounts.spotify.com/api/token'
    payload = {'grant_type': 'authorization_code', 'code': str(token), 'redirect_uri': 'http://0.0.0.0:5000/spotify'}
    # base64encoded = base64.b64encode(b'adbede0af98a4e9ca397a4cf4a9214df:8e7ec8419b914b13b6a3d1f2f7e87b4c')
    s = 'adbede0af98a4e9ca397a4cf4a9214df:8e7ec8419b914b13b6a3d1f2f7e87b4c'
    base64encoded = base64.b64encode(s.encode('utf-8'))
    print('ENCODED: ', base64encoded)
    headers = {'Authorization': 'Basic {}'.format(base64encoded)}
    params = {'client_id': 'adbede0af98a4e9ca397a4cf4a9214df', 'client_secret': '8e7ec8419b914b13b6a3d1f2f7e87b4c'}
    post_request = requests.post(url=token_url, data=payload, headers=headers)
    print(post_request.status_code)
    print(post_request.reason)
    print(post_request.text)

    response_data = json.loads(post_request.text)
    pprint.pprint(response_data)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    authorization_header = {'Authorization': 'Bearer {}'.format(access_token)}

    api_url = 'https://api.spotify.com/v1'
    user_profile_api_endpoint = "{}/me".format(api_url)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)


    print('made it here at least')
    return render_template('blog/spotify.html')
