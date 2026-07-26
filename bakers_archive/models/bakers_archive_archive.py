from datetime import datetime
import random

from odoo import api, models, fields, _
from odoo.addons.website.tools import text_from_html
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.tools.translate import html_translate
from odoo.tools import html_escape


class BakersArchiveArchive(models.Model):
    _name = 'bakers_archive.archive'
    _description = 'Bakers Archive Archive'
    _inherit = [
        'mail.thread',
        'website.seo.metadata',
        'website.multi.mixin',
        'website.located.mixin',
        'website.cover_properties.mixin',
        'website.searchable.mixin',
    ]
    _order = 'name'

    _CUSTOMER_HEADERS_LIMIT_COUNT = 0 # Should never use X-Msg-To headers

    def _default_sequence(self):
        return (self.search([], order='sequence desc', limit=1).sequence or 0) + 1

    sequence = fields.Integer('Sequence', default=_default_sequence)
    name = fields.Char('Archive Name', required=True, translate=True)
    subtitle = fields.Char('Archive Subtitle', translate=True)
    active = fields.Boolean('Active', default=True)
    content = fields.Html('Content', translate=html_translate, sanitize=False)
    archive_recipe_ids = fields.One2many('bakers_archive.recipe', 'archive_id', 'Archive Recipes')
    archive_recipe_count = fields.Integer('Recipes', compute='_compute_archive_recipe_count')

    def _compute_website_url(self):
        super()._compute_website_url()
        for record in self:
            if record.id:
                record.website_url = '/bakers-archive/%s' % self.env['ir.http']._slug(record)

    @api.depends('archive_recipe_ids')
    def _compute_archive_recipe_count(self):
        for record in self:
            record.archive_recipe_count = len(record.archive_recipe_ids)

    def write(self, vals):
        res = super().write(vals)
        if 'active' in vals:
            # Archiving or unarchiving an entire archive will also do it to the recipes in it.
            recipe_ids = self.env['bakers_archive.recipe'].with_context(active_test=False).search([
                ('archive_id', 'in', self.ids)
            ])
            for archive_recipe in recipe_ids:
                archive_recipe.active = vals['active']
        return res

    def message_post(self, *, parent_id=False, subtype_id=False, **kwargs):
        self.ensure_one()
        if parent_id:
            parent_message = self.env['mail.message'].sudo().browse(parent_id)
            if parent_message.subtype_id and parent_message.subtype_id == self.env.ref('website_archive.mt_archive_archive_published'):
                subtype_id = self.env.ref('mail.mt_note').id
        return super().message_post(parent_id=parent_id, subtype_id=subtype_id, **kwargs)

    def all_tags(self, join=False, min_limit=1):
        BakersArchiveTag = self.env['bakers_archive.tag']
        req = """
            SELECT
                p.archive_id, count(*), r.bakers_archive_tag_id
            FROM
                bakers_archive_recipe_bakers_archive_tag_rel r
                    join bakers_archive_recipe p on r.bakers_archive_recipe_id=p.id
            WHERE
                p.archive_id in %s
            GROUP BY
                p.archive_id,
                r.bakers_archive_tag_id
            ORDER BY
                count(*) DESC
        """
        self.env.cr.execute(req, [tuple(self.ids)])
        tag_by_archive = {i.id: [] for i in self}
        all_tags = set()
        for archive_id, freq, tag_id in self.env.cr.fetchall():
            if freq > min_limit:
                if join:
                    all_tags.add(tag_id)
                else:
                    tag_by_archive[archive_id].append(tag_id)

        if join:
            return BakersArchiveTag.browse(all_tags)

        for archive_id in tag_by_archive:
            tag_by_archive[archive_id] = BakersArchiveTag.browse(tag_by_archive[archive_id])

        return tag_by_archive

    @api.model
    def _search_get_detail(self, website, order, options):
        with_description = options['displayDescription']
        search_fields = ['name']
        fetch_fields = ['id', 'name']
        mapping = {
            'name': {'name': 'name', 'type': 'text', 'match': True},
            'website_url': {'name': 'url', 'type': 'text', 'truncate': False},
        }
        if with_description:
            search_fields.append('subtitle')
            fetch_fields.append('subtitle')
            mapping['description'] = {'name': 'subtitle', 'type': 'text', 'match': True}
        return {
            'model': 'bakers_archive.archive',
            'base_domain': [website.website_domain()],
            'search_fields': search_fields,
            'fetch_fields': fetch_fields,
            'mapping': mapping,
            'icon': 'fa-rss-square',
            'order': 'name desc, id desc' if 'name desc' in order else 'name asc, id desc',
        }

    def _search_render_result(self, fetch_fields, mapping, icon, limit):
        results_data = super()._search_render_result(fetch_fields, mapping, icon, limit)
        for data in results_data:
            data['url'] = '/bakers-archive/%s' % data['id']
        return results_data