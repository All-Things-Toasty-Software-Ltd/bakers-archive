from collections import defaultdict
from zoneinfo import ZoneInfo

import babel.dates
import werkzeug

from odoo import http, tools, models
from odoo.addons.website.controllers.main import QueryURL
from odoo.fields import Domain
from odoo.http import request
from odoo.http.session import touch
from odoo.tools import html2plaintext
from odoo.tools.misc import get_lang
from odoo.tools import sql
from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate(__name__)

class BakersArchiveController(http.Controller):
    _archive_recipe_per_page = 12
    _recipe_comment_per_page = 10

    def tags_list(self, tag_ids, current_tag):
        tag_ids = list(tag_ids) # It's important to avoid using the same list.
        if current_tag in tag_ids:
            tag_ids.remove(current_tag)
        else:
            tag_ids.append(current_tag)
        tag_ids = request.env['bakers_archive.tag'].browse(tag_ids)
        return ','.join(request.env['ir.http']._slug(tag) for tag in tag_ids)

    def nav_list(self, archive=None):
        dom = archive and [('archive_id', '=', archive.id)] or []
        dom += [('website_published', '=', True)]
        groups = request.env['bakers_archive.recipe']._read_group(
            dom, groupby=['published_date:month'])

        locale = get_lang(request.env).code
        tzinfo = ZoneInfo(request.env.context.get('tz') or 'UTC')
        fmt = tools.DEFAULT_SERVER_DATETIME_FORMAT

        res = defaultdict(list)
        for [start] in groups:
            year = babel.dates.format_datetime(start, format='yyyy', tzinfo=tzinfo, locale=locale)
            res[year].append({
                'date_begin': start.strftime(fmt),
                'date_end': (start + models.READ_GROUP_TIME_GRANULARITY['month']).strftime(fmt),
                'month': babel.dates.format_datetime(start, format='MMMM', tzinfo=tzinfo, locale=locale),
                'year': year,
            })
        return res

    def _get_archive_recipe_search_options(self, archive=None, active_tags=None, date_begin=None, date_end=None, state=None, **recipe):
        return {
            'displayDescription': True,
            'displayDetail': False,
            'displayExtraDetail': False,
            'displayExtraLink': False,
            'displayImage': False,
            'allowFuzzy': not recipe.get('noFuzzy'),
            'archive': str(archive.id) if archive else None,
            'tag': ','.join([str(id) for id in active_tags.ids]),
            'date_begin': date_begin,
            'date_end': date_end,
            'state': state,
        }

    def _prepare_archive_values(self, archives, archive=False, date_begin=False, date_end=False, tags=False, state=False, page=False, search=None, **recipe):
        BakersArchiveRecipe = request.env['bakers_archive.recipe']
        BakersArchiveTag = request.env['bakers_archive.tag']

        domain = request.website.website_domain()

        if archive:
            domain &= Domain('archive_id', '=', archive.id)

        if date_begin and date_end:
            domain &= Domain('published_date', '>=', date_begin) & Domain('published_date', '<=', date_end)
        active_tag_ids = tags and [tag_id for tag_id in [request.env['ir.http']._unslug(tag)[1] for tag in tags.split(',')] if tag_id] or []
        active_tags = BakersArchiveTag
        if active_tag_ids:
            active_tags = BakersArchiveTag.browse(active_tag_ids).exists()
            fixed_tag_slug = ','.join(request.env['ir.http']._slug(t) for t in active_tags)
            if fixed_tag_slug != tags:
                path = request.httprequest.full_path
                new_url = path.replace('/tag/%s' % tags, fixed_tag_slug and '/tag/%s' % fixed_tag_slug or '', 1)
                if new_url != path:
                    return request.redirect(new_url, 301)
            domain &= Domain('tag_ids', 'in', active_tags.ids)

        published_count = 0
        unpublished_count = 0
        scheduled_count = 0
        if request.env.user.has_group('website.group_website_designer'):
            count_domain = domain & Domain('website_published', '=', True)
            scheduled_domain = domain & Domain('publish_on', '!=', False)
            published_count = BakersArchiveRecipe.search_count(count_domain)
            scheduled_count = BakersArchiveRecipe.search_count(scheduled_domain)
            unpublished_count = BakersArchiveRecipe.search_count(domain) - published_count - scheduled_count

            if state == 'published':
                domain &= Domain('website_published', '=', True)
            elif state == 'unpublished':
                domain &= Domain('website_published', '=', False) & Domain('publish_on', '=', False)
            elif state == 'scheduled':
                domain &= Domain('publish_on', '!=', False)
        else:
            domain &= Domain('website_published', '=', True)

        offset = (page - 1) * self._archive_recipe_per_page

        options = self._get_archive_recipe_search_options(
            archive=archive,
            active_tags=active_tags,
            date_begin=date_begin,
            date_end=date_end,
            state=state,
            **recipe
        )
        total, details, fuzzy_search_term = request.website._search_with_fuzzy('archive_recipes_only', search,
            limit=page * self._archive_recipe_per_page, order='is_published desc, published_date desc, id asc', options=options)
        recipes = details[0].get('results', BakersArchiveRecipe)
        recipes = recipes[offset:offset + self._archive_recipe_per_page]

        url_args = dict()
        if search:
            url_args['search'] = search

        if date_begin and date_end:
            url_args['date_begin'] = date_begin
            url_args['date_end'] = date_end

        pager = tools.lazy(lambda: request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            total=total,
            page=page,
            step=self._archive_recipe_per_page,
            url_args=url_args,
        ))

        if not archives:
            all_tags = request.env['bakers_archive.tag']
        else:
            all_tags = tools.lazy(lambda: archives.all_tags(join=True) if not archive else archives.all_tags().get(archive.id, request.env['bakers_archive.tag']))
        tag_category = tools.lazy(lambda: sorted(all_tags.mapped('category_id'), key=lambda category: category.name.upper()))
        other_tags = tools.lazy(lambda: sorted(all_tags.filtered(lambda x: not x.category_id), key=lambda tag: tag.name.upper()))
        nav_list = tools.lazy(lambda: self.nav_list(archive))
        recipes.archive_id

        return {
            'date_begin': date_begin,
            'date_end': date_end,
            'other_tags': other_tags,
            'tag_category': tag_category,
            'nav_list': nav_list,
            'tags_list': self.tags_list,
            'pager': pager,
            'recipes': recipes.with_prefetch(),
            'tag': tags,
            'active_tag_ids': active_tags.ids,
            'domain': domain,
            'state_info': state and {'state': state, 'published': published_count, 'unpublished': unpublished_count, 'scheduled': scheduled_count},
            'archives': archives,
            'archive': archive,
            'search': fuzzy_search_term or search,
            'search_count': total,
            'original_search': fuzzy_search_term and search,
        }

    def sitemap_archive(env, rule, qs):
        BakersArchiveArchive = env['bakers_archive.archive']
        website = env['website'].get_current_website()
        domain = website.website_domain()
        archives = tools.lazy(lambda: BakersArchiveArchive.search(domain, order='sequence'))
        slug = env['ir.http']._slug

        def match(loc):
            return not qs or qs.lower() in loc.lower()

        if len(archives) > 1:
            if match('/archive'):
                yield {'loc': '/archive'}

        for archive in archives:
            loc = f'/archive/{slug(archive)}'
            if match(loc):
                yield {'loc': loc}

    @http.route([
        '/archive',
        '/archive/page/<int:page>',
        '/archive/tag/<string:tag>',
        '/archive/tag/<string:tag>/page/<int:page>',
        '''/archive/<model("bakers_archive.archive"):archive>''',
        '''/archive/<model("bakers_archive.archive"):archive>/page/<int:page>''',
        '''/archive/<model("bakers_archive.archive"):archive>/tag/<string:tag>''',
        '''/archive/<model("bakers_archive.archive"):archive>/tag/<string:tag>/page/<int:page>''',
    ], type='http', auth='public', website=True, sitemap=sitemap_archive, list_as_website_content=_lt('Archives'))
    def archive(self, archive=None, tag=None, page=1, search=None, **opt):
        BakersArchiveArchive = request.env['bakers_archive.archive']
        archives = tools.lazy(lambda: BakersArchiveArchive.search(request.website.website_domain(), order='sequence'))

        if not archive and len(archives) == 1:
            url = QueryURL('/archive/%s' % request.env['ir.http']._slug(archives[0]), search=search, **opt)()
            return request.redirect(url, code=302)

        date_begin, date_end = opt.get('date_begin'), opt.get('date_end')

        if tag and request.httprequest.method == 'GET':
            tags = tag.split(',')
            if len(tags) > 1:
                url = QueryURL('' if archive else '/archive', ['archive', 'tag'], archive=archive, tag=tags[0], date_begin=date_begin, date_end=date_end, search=search)()
                return request.redirect(url, code=302)

        values = self._prepare_archive_values(archives=archives, archive=archive, tags=tag, page=page, search=search, **opt)

        if isinstance(values, werkzeug.wrappers.Response):
            return values

        if archive:
            values['main_object'] = archive
        values['archive_url'] = QueryURL('/archive', ['archive', 'tag'], archive=archive, tag=tag, date_begin=date_begin, date_end=date_end, search=search)

        return request.render('bakers_archive.archive_recipe_short', values)

    @http.route(['''/archive/<model("bakers_archive.archive"):archive>/feed'''], type='http', auth='public', website=True, sitemap=True)
    def archive_feed(self, archive, limit='15', **kwargs):
        v = {}
        v['archive'] = archive
        v['base_url'] = archive.get_base_url()
        v['recipes'] = request.env['bakers_archive.recipe'].search([
            ('archive_id', '=', archive.id),
            ('website_published', '=', True),
        ], limit=min(int(limit), 50), order='published_date DESC')
        v['html2plaintext'] = html2plaintext
        r = request.render('bakers_archive.archive_feed', v, headers=[('Content-Type', 'application/atom+xml')])
        return r

    @http.route([
        '''/archive/<model("bakers_archive.archive"):archive>/recipe/<model("bakers_archive.recipe"):archive_recipe>''',
    ], type='http', auth='public', website=True, sitemap=False)
    def old_archive_recipe(self, archive, archive_recipe, **recipe):
        return request.redirect('/archive/%s/%s' % (request.env['ir.http']._slug(archive), request.env['ir.http']._slug(archive_recipe)), code=301)

    def sitemap_archive_recipe(env, rule, qs):
        BakersArchiveRecipe = env['bakers_archive.recipe']
        IrHttp = env['ir.http']
        recipes = BakersArchiveRecipe.search([('website_published', '=', True)])

        for recipe in recipes:
            archive = recipe.archive_id
            canonical_url = f'/archive/{IrHttp._slug(archive)}/{IrHttp._slug(recipe)}'

            if not qs or qs.lower() in canonical_url.lower():
                yield {
                    'loc': canonical_url,
                    'lastmod': (recipe.write_date or recipe.create_date).date(),
                }

    @http.route([
        '''/archive/<model("bakers_archive.archive"):archive>/<model("bakers_archive.recipe", "[('archive_id','=', archive.id)]"):archive_recipe>''',
    ], type='http', auth='public', website=True, sitemap=sitemap_archive_recipe)
    def archive_recipe(self, archive, archive_recipe, tag_id=None, page=1, enable_editor=None, **recipe):
        BakersArchiveRecipe = request.env['bakers_archive.recipe']
        date_begin, date_end = recipe.get('date_begin'), recipe.get('date_end')

        domain = request.website.website_domain()
        archives = archive.search(domain, order='sequence')

        tag = None
        if tag_id:
            tag = request.env['bakers_archive.tag'].browse(int(tag_id))
        archive_url = QueryURL('', ['archive', 'tag'], archive=archive_recipe.archive_id, tag=tag, date_begin=date_begin, date_end=date_end)

        if not archive_recipe.archive_id.id == archive.id:
            return request.redirect('/archive/%s/%s' % (request.env['ir.http']._slug(archive_recipe.archive_id), request.env['ir.http']._slug(archive_recipe)), code=301)

        tags = request.env['bakers_archive.tag'].search([])

        archive_recipe_domain = [('archive_id', '=', archive.id)]
        if not request.env.user.has_group('bakers_archive.group_bakers_archive_manager'):
            archive_recipe_domain += [('website_published', '=', True)]

        all_recipe = BakersArchiveRecipe.search(archive_recipe_domain)

        if archive_recipe not in all_recipe:
            return request.redirect('/archive/%s' % (request.env['ir.http']._slug(archive_recipe.archive_id)))

        all_recipe_ids = all_recipe.ids
        current_archive_recipe_index = all_recipe_ids.index(archive_recipe.id)
        nb_recipes = len(all_recipe_ids)
        next_recipe_id = all_recipe_ids[(current_archive_recipe_index + 1) % nb_recipes] if nb_recipes > 1 else None
        next_recipe = next_recipe_id and BakersArchiveRecipe.browse(next_recipe_id) or False

        values = {
            'tags': tags,
            'tag': tag,
            'archive': archive,
            'archive_recipe': archive_recipe,
            'archives': archives,
            'main_object': archive_recipe,
            'nav_list': self.nav_list(archive),
            'enable_editor': enable_editor,
            'next_recipe': next_recipe,
            'date': date_begin,
            'archive_url': archive_url,
        }
        response = request.render('bakers_archive.archive_recipe_complete', values)

        if archive_recipe.id not in request.session.get('recipes_viewed', []):
            if sql.increment_fields_skiplock(archive_recipe, 'visits'):
                if not request.session.get('recipes_viewed'):
                    request.session['recipes_viewed'] = []
                request.session['recipes_viewed'].append(archive_recipe.id)
                touch(request.session)
        return response