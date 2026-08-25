# Part of The Baker's Archive. See LICENSE file for full copyright and licensing details.

import json

from odoo import http
from odoo.http import request

from ..services.bakers_archive_model_serializer import (
    BakersArchiveModelSerializer,
)


class BakersArchiveAPIController(http.Controller):
    """
    Public API for The Baker's Archive mobile companion.

    Available endpoints:

        GET /archive/api/v1/archives
        GET /archive/api/v1/archive/<archive_id>
        GET /archive/api/v1/recipe/<recipe_id>
    """

    API_VERSION = 'v1'

    @staticmethod
    def _json_response(data, status=200):
        """
        Return a JSON HTTP response.
        """
        response = request.make_response(
            json.dumps(
                data,
                ensure_ascii=False,
                separators=(',', ':'),
                default=str,
            ),
            headers=[
                (
                    'Content-Type',
                    'application/json; charset=utf-8',
                ),
            ],
        )

        response.status_code = status

        return response

    def _not_found(self, message='Resource not found.'):
        """
        Return a 404 response.
        """
        return self._json_response(
            {
                'error': {
                    'code': 'not_found',
                    'message': message,
                },
            },
            status=404,
        )

    def _bad_request(self, code, message):
        """
        Return a 400 response.
        """
        return self._json_response(
            {
                'error': {
                    'code': code,
                    'message': message,
                },
            },
            status=400,
        )

    @staticmethod
    def _base_url():
        """
        Return the base URL for the current request.
        """
        return request.httprequest.host_url.rstrip('/')

    @http.route(
        '/archive/api/v1/archives',
        type='http',
        auth='public',
        methods=['GET'],
        website=True,
        sitemap=False,
        csrf=False,
    )
    def archives(self, **kwargs):
        """
        Discover all archives available to the current website.
        """

        Archives = request.env[
            'bakers_archive.archive'
        ].sudo()

        archives = Archives.search(
            request.website.website_domain(),
            order='sequence, name',
        )

        base_url = self._base_url()
        slug = request.env['ir.http']._slug

        return self._json_response({
            'api_version': self.API_VERSION,
            'archives': [
                {
                    'id': archive.id,
                    'name': archive.name,
                    'subtitle': (
                        archive.subtitle
                        if hasattr(archive, 'subtitle')
                        else None
                    ),
                    'url': '%s/archive/%s' % (
                        base_url,
                        slug(archive),
                    ),
                    'feed_url': '%s/archive/%s/feed' % (
                        base_url,
                        slug(archive),
                    ),
                    'api_url': (
                            '%s/archive/api/%s/archive/%s'
                            % (
                                base_url,
                                self.API_VERSION,
                                archive.id,
                            )
                    ),
                }
                for archive in archives
            ],
        })

    @http.route(
        '/archive/api/v1/archive/<int:archive_id>',
        type='http',
        auth='public',
        methods=['GET'],
        website=True,
        sitemap=False,
        csrf=False,
    )
    def api_archive(
            self,
            archive_id,
            page=None,
            limit=None,
            **kwargs
    ):
        """
        Return the complete generic representation of one archive.
        """

        archive = request.env[
            'bakers_archive.archive'
        ].sudo().browse(archive_id).exists()

        if not archive:
            return self._not_found('Archive not found.')

        # Only expose an archive explicitly belonging to another website when
        # that relationship exists on the model.
        if (
                'website_id' in archive._fields
                and archive.website_id
                and archive.website_id != request.website
        ):
            return self._not_found('Archive not found.')

        pagination = self._parse_pagination(
            page,
            limit,
        )

        if isinstance(pagination[0], str):
            return self._bad_request(
                pagination[0],
                pagination[1],
            )

        page, limit = pagination

        Recipe = request.env[
            'bakers_archive.recipe'
        ].sudo()

        domain = [
            ('archive_id', '=', archive.id),
            ('website_published', '=', True),
        ]

        if 'active' in Recipe._fields:
            domain.append(
                ('active', '=', True)
            )

        if 'website_id' in Recipe._fields:
            domain.append(
                '|',
                ('website_id', '=', False),
                ('website_id', '=', request.website.id),
            )

        total = Recipe.search_count(domain)

        offset = (page - 1) * limit

        recipes = Recipe.search(
            domain,
            offset=offset,
            limit=limit,
            order='id ASC',
        )

        base_url = self._base_url()

        return self._json_response({
            'api_version': self.API_VERSION,
    
            'data': {
                'id': archive.id,
                'model': archive._name,
                'name': archive.name,
                'subtitle': (
                    archive.subtitle
                    if 'subtitle' in archive._fields
                    else None
                ),
            },

            'recipes': {
                'page': page,
                'limit': limit,
                'total': total,
                'page_count': (
                        (total + limit - 1) // limit
                ),

                'items': [
                    {
                        'id': recipe.id,
                        'name': recipe.name,

                        'teaser': (
                            recipe.teaser
                            if 'teaser' in recipe._fields
                               and recipe.teaser
                            else ''
                        ),

                        'published_date': (
                            recipe.published_date
                            if 'published_date'
                               in recipe._fields
                            else None
                        ),

                        'api_url': (
                                '%s/archive/api/%s/recipe/%s'
                                % (
                                    base_url,
                                    self.API_VERSION,
                                    recipe.id,
                                )
                        ),
                    }
                    for recipe in recipes
                ],
            },
        })

    @http.route(
        '/archive/api/v1/recipe/<int:recipe_id>',
        type='http',
        auth='public',
        methods=['GET'],
        website=True,
        sitemap=False,
        csrf=False,
    )
    def recipe(
            self,
            recipe_id,
            depth=None,
            **kwargs
    ):
        """
        Return the complete generic representation of one public recipe.
        """

        recipe = request.env[
            'bakers_archive.recipe'
        ].sudo().search(
            [
                ('id', '=', recipe_id),
                ('website_published', '=', True),
            ],
            limit=1,
        )

        if not recipe:
            return self._not_found('Recipe not found.')

        # Do not expose a recipe explicitly belonging to another website.
        if (
                'website_id' in recipe._fields
                and recipe.website_id
                and recipe.website_id != request.website
        ):
            return self._not_found('Recipe not found.')

        # Don't expose inactive recipes if the model supports ``active``.
        if (
                'active' in recipe._fields
                and not recipe.active
        ):
            return self._not_found('Recipe not found.')

        max_depth = self._parse_depth(depth)

        if isinstance(max_depth, tuple):
            return self._bad_request(
                max_depth[0],
                max_depth[1],
            )

        serializer = BakersArchiveModelSerializer(
            max_depth=max_depth,
        )

        return self._json_response({
            'api_version': self.API_VERSION,
            'data': serializer.serialize(recipe),
        })

    @staticmethod
    def _parse_depth(depth):
        """
        Parse the optional ``depth`` query parameter.

        Returns either:
            int | None

        or an error tuple:
            (error_code, error_message)
        """

        if depth is None:
            return None

        try:
            depth = int(depth)
        except (TypeError, ValueError):
            return (
                'invalid_depth',
                'Depth must be an integer.',
            )

        if depth < 0:
            return (
                'invalid_depth',
                'Depth must be greater than or equal to zero.',
            )

        return depth

    DEFAULT_PAGE = 1
    DEFAULT_LIMIT = 20
    MAX_LIMIT = 50

    def _parse_pagination(self, page, limit):
        """
        Parse and validate pagination parameters.

        Returns:
            (page, limit)

        or an error tuple:
            (error_code, error_message)
        """

        try:
            page = (
                int(page)
                if page is not None
                else self.DEFAULT_PAGE
            )
        except (TypeError, ValueError):
            return (
                'invalid_page',
                'Page must be an integer.',
            )

        try:
            limit = (
                int(limit)
                if limit is not None
                else self.DEFAULT_LIMIT
            )
        except (TypeError, ValueError):
            return (
                'invalid_limit',
                'Limit must be an integer.',
            )

        if page < 1:
            return (
                'invalid_page',
                'Page must be greater than or equal to one.',
            )

        if limit < 1:
            return (
                'invalid_limit',
                'Limit must be greater than or equal to one.',
            )

        if limit > self.MAX_LIMIT:
            limit = self.MAX_LIMIT

        return page, limit
