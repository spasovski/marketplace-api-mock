"""
This is a simple application which mocks out the APIs used by Fireplace.
Pointing your instance of Fireplace using settings.js will allow you to
quickly get up and running without needing your own installation of Zamboni
or without needing to use -dev (offline mode).
"""
import json
import random

from flask import make_response, request

import app

import factory
from factory import feed as feed_factory
from factory import langpack as langpack_factory


DEFAULT_API_VERSION = 'v1'


def app_generator():
    while True:
        yield factory.app()


def langpack_generator():
    while True:
        yield langpack_factory.langpack(url_root=request.url_root)


def review_generator(**kw):
    while True:
        yield factory.review(**kw)


@app.route('/api/<version>/account/login/', methods=['POST'])
def login(version=DEFAULT_API_VERSION):
    """TODO: update for FxA."""
    return {
        'error': None,
        'token': 'some token',
        'settings': {
            'display_name': 'user',
            'email': 'user123@mozilla.com',
            'enable_recommendations': True,
            'region': 'us',
        },
        'permissions': {},
        'apps': factory._user_apps(),
    }


@app.route('/api/<version>/account/logout/', methods=['DELETE'])
def logout(version=DEFAULT_API_VERSION):
    return ''


@app.route('/api/<version>/account/settings/mine/', methods=['GET', 'PATCH'])
def settings(version=DEFAULT_API_VERSION):
    return {
        'display_name': 'Joe User',
        'email': request.args.get('email'),
        'region': 'us',
    }


@app.route('/api/<version>/abuse/app/', methods=['POST'])
def app_abuse(version=DEFAULT_API_VERSION):
    if not request.form.get('text'):
        return {'error': True}
    return {'error': False}


@app.route('/api/<version>/account/feedback/', methods=['POST'])
def feedback(version=DEFAULT_API_VERSION):
    if not request.form.get('feedback'):
        return {'error': True}
    return {'error': False}


@app.route('/api/<version>/apps/app/<slug>/privacy/', methods=['GET'])
def privacy(version=DEFAULT_API_VERSION, slug=''):
    return {
        'privacy_policy': factory.rand_text(),
    }


@app.route('/api/<version>/account/installed/mine/')
def installed(version=DEFAULT_API_VERSION):
    query = request.args.get('q')
    data = app._paginated('objects', app_generator,
                          0 if query == 'empty' else 42)
    return data


@app.route('/api/<version>/fireplace/search/', endpoint='search-fireplace')
@app.route('/api/<version>/apps/search/')
def search(version=DEFAULT_API_VERSION):
    query = request.args.get('q')
    data = app._paginated('objects', app_generator,
                          0 if query == 'empty' else 42)
    return data


@app.route('/api/<version>/fireplace/search/featured/',
           endpoint='featured-fireplace')
@app.route('/api/<version>/apps/recommend/', endpoint='apps-recommended')
def category(version=DEFAULT_API_VERSION):
    return app._paginated('objects', app_generator)


@app.route('/api/v2/langpacks/', endpoint='langpacks')
def langpacks():
    fxos_version = request.args.get('fxos_version')
    return app._paginated('objects',
                          langpack_generator,
                          0 if fxos_version == 'empty' else 42)


@app.route('/api/<version>/apps/rating/', methods=['GET', 'POST'])
def app_ratings(version=DEFAULT_API_VERSION):
    if request.method == 'POST':
        return {'error': False}

    slug = request.form.get('app') or request.args.get('app')

    if slug == 'unrated':
        return {
            'info': {
                'average': 0,
                'slug': slug,
            },
            'meta': {
                'next': None,
                'prev': None,
                'total_count': 0,
            },
            'objects': [],
        }

    data = app._paginated('objects', review_generator, slug=slug)
    data['info'] = {
        'average': random.random() * 4 + 1,
        'slug': slug,
    }
    data.update(factory.review_user_data(slug))

    if slug == 'has_rated':
        data['objects'][0]['has_flagged'] = False
        data['objects'][0]['is_author'] = True

    return data


@app.route('/api/<version>/apps/rating/<id>/',
           methods=['GET', 'PUT', 'DELETE'])
def app_rating(version=DEFAULT_API_VERSION, id=None):
    if request.method in ('PUT', 'DELETE'):
        return {'error': False}

    return factory.review()


@app.route('/api/<version>/apps/rating/<id>/flag/', methods=['POST'])
def app_rating_flag(version=DEFAULT_API_VERSION, id=None):
    return ''


@app.route('/api/<version>/fireplace/app/<slug>/')
def app_(version=DEFAULT_API_VERSION, slug=None):
    return factory.app(slug=slug)


@app.route('/api/<version>/installs/record/', methods=['POST'])
def record_free(version=DEFAULT_API_VERSION):
    return {'error': False}


@app.route('/api/<version>/receipts/install/', methods=['POST'])
def record_paid(version=DEFAULT_API_VERSION):
    return {'error': False}


@app.route('/api/<version>/apps/<id>/statistics/', methods=['GET'])
def app_stats(version=DEFAULT_API_VERSION, id=None):
    return json.loads(open('./fixtures/3serieschart.json', 'r').read())


@app.route('/api/<version>/fireplace/consumer-info/', methods=['GET'])
def consumer_info(version=DEFAULT_API_VERSION):
    return {
        'region': 'us',
        'apps': factory._user_apps(),
        # New users default to recommendations enabled.
        'enable_recommendations': True
    }


@app.route('/api/<version>/feed/get/', methods=['GET', 'POST'])
def feed(version=DEFAULT_API_VERSION):
    return app._paginated('objects', None, 30, feed_factory.feed())


@app.route('/api/<version>/fireplace/feed/brands/<slug>/', methods=['GET'])
def feed_brand(version=DEFAULT_API_VERSION, slug=''):
    return feed_factory.brand(slug=slug)


@app.route('/api/<version>/fireplace/feed/collections/<slug>/',
           methods=['GET'])
def feed_collection(version=DEFAULT_API_VERSION, slug=''):
    return feed_factory.collection(name='slug', slug=slug)


@app.route('/api/<version>/fireplace/feed/shelves/<slug>/', methods=['GET'])
def feed_shelf(version=DEFAULT_API_VERSION, slug=''):
    return feed_factory.shelf(slug=slug)


@app.route('/api/<version>/account/newsletter/', methods=['POST'])
def newsletter(version=DEFAULT_API_VERSION, id=None):
    return make_response('', 204)


@app.route('/api/<version>/services/config/site/')
def site_config(version=DEFAULT_API_VERSION):
    return {'waffle': {}}


if __name__ == '__main__':
    app.run()
