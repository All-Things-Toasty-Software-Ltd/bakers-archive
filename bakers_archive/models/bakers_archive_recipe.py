# -*- coding: utf-8 -*-
# Part of The Baker's Archive. See LICENSE file for full copyright and licensing details.

import random
from datetime import datetime
from odoo import api, models, fields, _
from odoo.addons.website.tools import text_from_html
from odoo.tools import html_escape
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.tools.translate import html_translate


class BakersArchiveRecipe(models.Model):
    _name = 'bakers_archive.recipe'
    _description = 'Bakers Archive Recipe'
    _inherit = [
        'mail.thread',
        'website.seo.metadata',
        'website.published.multi.mixin',
        'website.page_visibility_options.mixin',
        'website.cover_properties.mixin',
        'website.searchable.mixin',
    ]
    _order = 'id desc'
    _mail_post_access = 'read'

    def _compute_website_url(self):
        super(BakersArchiveRecipe, self)._compute_website_url()
        for archive_recipe in self:
            if archive_recipe.id:
                archive_recipe.website_url = "/archive/%s/%s" % (self.env['ir.http']._slug(archive_recipe.archive_id),
                                                                 self.env['ir.http']._slug(archive_recipe))

    # Metadata

    def _default_content(self):
        text = html_escape(_("A super cool recipe starts with this..."))
        return """
            <p>%(text)s</p>
        """ % {"text": text}

    name = fields.Char('Title', required=True, translate=True, default='')
    subtitle = fields.Char('Archive Subtitle', translate=True)
    author_id = fields.Many2one('res.partner', 'Author', index='btree_not_null')
    author_avatar = fields.Binary(related='author_id.image_128', string='Avatar', readonly=False)
    author_name = fields.Char(related='author_id.name', string='Author Name', readonly=False, store=True)
    active = fields.Boolean('Active', default=True)
    archive_id = fields.Many2one('bakers_archive.archive', 'Archive', required=True, index=True, ondelete='cascade',
                                 default=lambda self: self.env['bakers_archive.archive'].search([], limit=1))
    tag_ids = fields.Many2many('bakers_archive.tag', string='Tags')
    content = fields.Html('Content', default=_default_content, translate=html_translate,
                          sanitize=False)
    teaser = fields.Text('Teaser', compute='_compute_teaser', inverse='_set_teaser', translate=True)
    teaser_manual = fields.Text('Teaser Content', translate=True)

    source_id = fields.Many2one('bakers_archive.source', 'Source', index='btree_not_null')
    source_name = fields.Char(related='source_id.name', string='Source Name', readonly=False, store=True)
    license = fields.Many2one('bakers_archive.license', string='License')
    country_id = fields.Many2one('res.country', string='Origin Country',
                                 help='The country where this recipe originates from.')
    state_id = fields.Many2one('res.country.state', domain="[('country_id', '=', country_id)]",
                               help='The specific region or state within the origin country.')
    original_language_id = fields.Many2one('res.lang', string='Original Language',
                                            help='The original language of the recipe.')
    ingredient_ids = fields.One2many('bakers_archive.recipe.ingredient', 'recipe_id', string='Ingredients')
    category_ids = fields.One2many('bakers_archive.recipe.instruction.category', 'recipe_id', string='Instruction Categories')
    instruction_ids = fields.One2many('bakers_archive.recipe.instruction', 'recipe_id', string='Instructions')
    notes = fields.Html(string='Notes')
    description = fields.Html(string='Description', help='An intro, or overview of the recipe.')


    media_ids = fields.One2many('bakers_archive.recipe.media', 'recipe_id', string='Media Gallery',
                                help='Images, videos, and other media related to this recipe.')

    main_image = fields.Image(string='Main Image', max_width=1920, max_height=1920)

    website_message_ids = fields.One2many(
        domain=lambda self: [('model', '=', self._name), ('message_type', '=', 'comment')])

    # Creation and Update

    create_date = fields.Datetime('Created on', readonly=True)
    create_uid = fields.Many2one('res.users', 'Created by', readonly=True)
    write_date = fields.Datetime('Last Updated on', readonly=True)
    write_uid = fields.Many2one('res.users', 'Last Contributor', readonly=True)
    visits = fields.Integer('No of Views', copy=False, default=0, readonly=True)
    website_id = fields.Many2one(related='archive_id.website_id', readonly=True, store=True)

    @api.depends('content', 'teaser_manual')
    def _compute_teaser(self):
        for archive_recipe in self:
            if archive_recipe.teaser_manual:
                archive_recipe.teaser = archive_recipe.teaser_manual
            else:
                content = text_from_html(archive_recipe.content, True)
                archive_recipe.teaser = content[:200] + "..."

    def _set_teaser(self):
        for archive_recipe in self:
            if not archive_recipe.with_context(lang='en_GB').teaser_manual:
                archive_recipe.update_field_translations('teaser_manual', {'en_GB': ''})
            archive_recipe.teaser_manual = archive_recipe.teaser

    def _check_for_action_post_published(self):
        """ Will send a notification when a recipe goes live for the first time. """
        self.ensure_one()
        force_publish = self.env.context.get('force_website_published')
        if (force_publish or self.website_published) and self.active and not self.published_date:
            return self.archive_id.message_post_with_source(
                'bakers_archive.archive_recipe_template_new_post',
                subject=self.name,
                render_values={'post': self},
                subtype_xmlid='bakers_archive.mt_archive_recipe_published',
            )
        return self.env['mail.message']

    @api.model_create_multi
    def create(self, vals_list):
        return super(BakersArchiveRecipe, self.with_context(mail_create_nolog=True)).create(vals_list)

    def write(self, vals):
        new_vals = dict(vals)
        if new_vals.get('active') is False:
            new_vals['is_published'] = False
        return super().write(new_vals)

    def copy_data(self, default=None):
        vals_list = super().copy_data(default=default)
        return [dict(vals, name=self.env._("%s (copy)", archive.name)) for archive, vals in zip(self, vals_list)]

    def _get_access_action(self, access_uid=None, force_website=False):
        self.ensure_one()
        user = self.env['res.users'].sudo().browse(access_uid) if access_uid else self.env.user
        if not force_website and user.share and not self.sudo().website_published:
            return super(BakersArchiveRecipe, self)._get_access_action(access_uid=access_uid,
                                                                       force_website=force_website)
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url,
            'target': 'self',
            'target_type': 'public',
            'res_id': self.id,
        }

    def _notify_get_recipients_groups(self, message, model_description, msg_vals=False):
        groups = super()._notify_get_recipients_groups(
            message, model_description, msg_vals=msg_vals
        )
        if not self:
            return groups

        self.ensure_one()
        if self.website_published:
            for _group_name, _group_method, group_data in groups:
                group_data['has_button_access'] = True

        return groups

    def _notify_thread_by_inbox(self, message, recipients_data, msg_vals=False, **kwargs):
        msg_vals = msg_vals or {}
        if msg_vals.get('message_type', message.message_type) == 'comment':
            return
        return super(BakersArchiveRecipe, self)._notify_thread_by_inbox(message, recipients_data, msg_vals=msg_vals,
                                                                        **kwargs)

    def _default_website_meta(self):
        res = super(BakersArchiveRecipe, self)._default_website_meta()
        res['default_opengraph']['og:description'] = self.subtitle
        res['default_opengraph']['og:type'] = 'article'
        res['default_opengraph']['article:published_time'] = self.published_date
        res['default_opengraph']['article:modified_time'] = self.write_date
        res['default_opengraph']['article:tag'] = self.tag_ids.mapped('name')
        res['default_opengraph']['og:image'] = json_scriptsafe.loads(self.cover_properties).get('background-image',
                                                                                                'none')[4:-1].strip(
            "\"'")
        res['default_opengraph']['og:title'] = self.name
        res['default_meta_description'] = self.subtitle
        return res

    @api.model
    def _search_get_detail(self, website, order, options):
        with_description = options['displayDescription']
        with_date = options['displayDetail']
        archive = options.get('archive')
        tags = options.get('tag')
        date_begin = options.get('date_begin')
        date_end = options.get('date_end')
        state = options.get('state')
        domain = [website.website_domain()]
        if archive:
            domain.append([('archive_id', '=', self.env['ir.http']._unslug(archive)[1])])
        if tags:
            active_tag_ids = [self.env['ir.http']._unslug(tag)[1] for tag in tags.split(',')] or []
            if active_tag_ids:
                domain.append([('tag_ids', 'in', active_tag_ids)])
        if date_begin and date_end:
            domain.append([("published_date", ">=", date_begin), ("published_date", "<=", date_end)])
        if self.env.user.has_group('website.group_website_designer'):
            if state == "published":
                domain.append([("website_published", "=", True)])
            elif state == "unpublished":
                domain.append([("website_published", "=", False), ("publish_on", "=", False)])
            elif state == "scheduled":
                domain.append([("publish_on", "!=", False)])
        else:
            domain.append([("website_published", "=", True)])
        search_fields = ['name', 'author_name', 'tag_ids.name']
        fetch_fields = ['name', 'website_url', 'tag_ids']
        mapping = {
            'name': {'name': 'name', 'type': 'text', 'match': True},
            'website_url': {'name': 'website_url', 'type': 'text', 'truncate': False},
            'tags': {'name': 'tag_ids', 'type': 'tags', 'match': True},
        }
        if with_description:
            search_fields.append('content')
            fetch_fields.append('content')
            mapping['description'] = {'name': 'content', 'type': 'text', 'html': True, 'match': True}
        if with_date:
            fetch_fields.append('published_date')
            mapping['detail'] = {'name': 'published_date', 'type': 'date'}
        return {
            'model': 'bakers_archive.recipe',
            'base_domain': domain,
            'search_fields': search_fields,
            'fetch_fields': fetch_fields,
            'mapping': mapping,
            'icon': 'fa-rss',
        }

    def _search_render_results(self, fetch_fields, mapping, icon, limit):
        results_data = super()._search_render_results(fetch_fields, mapping, icon, limit)
        for recipe, data in zip(self, results_data):
            data['tags_ids'] = recipe.tag_ids.read(['name'])
        return results_data

    def action_generate_content(self):
        for recipe in self:
            content_parts = []

            if recipe.ingredient_ids:
                content_parts.append('<h5 class="fw-bold mt-3 mb-2" style="font-size: 1.05rem;">Ingredients</h5>')
                ing_badges = []
                for ing in recipe.ingredient_ids:
                    qty = f"{ing.quantity:g} " if ing.quantity else ""
                    unit = f"{ing.unit} " if ing.unit else ""
                    ing_name = ing.name.name if (hasattr(ing, 'name') and ing.name) else ""

                    full_ing_str = f"{qty}{unit}{ing_name}".strip()
                    if ing.notes:
                        full_ing_str += f" ({ing.notes})"

                    ing_id = ing.name.id if (hasattr(ing, 'name') and ing.name) else ing.id
                    ing_url = f"/archive/ingredient/{ing_id}"

                    ing_badges.append(
                        f'<a href="{ing_url}" class="badge border border-warning text-warning-emphasis fw-normal rounded-pill px-2.5 py-1 text-decoration-none me-1 mb-1" style="font-size: 0.8rem; background-color: rgba(255,193,7,0.08);">'
                        f'{html_escape(full_ing_str)}'
                        f'</a>'
                    )
                content_parts.append(f'<div class="d-flex flex-wrap gap-1 mb-3">{"".join(ing_badges)}</div>')

            if recipe.description:
                content_parts.append(
                    f'<h5 class="fw-bold mt-3 mb-2" style="font-size: 1.05rem;">Description</h5>'
                    f'<div class="bg-transparent border border-1 p-3 rounded-3 mb-3" style="font-size: 0.85rem;">'
                    f'  <p class="mb-0 text-secondary" style="line-height: 1.45;">{html_escape(recipe.description)}</p>'
                    f'</div>'
                )

            if recipe.instruction_ids:
                content_parts.append('<h5 class="fw-bold mt-3 mb-2" style="font-size: 1.05rem;">Recipe</h5>')

                sorted_instructions = recipe.instruction_ids.sorted(
                    key=lambda i: (i.category_id.sequence or 0, i.sequence or 0)
                )

                recipe_inner_html = []
                has_categories = any(i.category_id for i in sorted_instructions)

                if has_categories:
                    from itertools import groupby

                    def cat_sort_key(inst):
                        return (inst.category_id.sequence or 0, inst.category_id.name or "General")

                    instructions_by_cat = sorted(sorted_instructions, key=cat_sort_key)

                    for cat_key, group in groupby(instructions_by_cat, key=lambda i: i.category_id):
                        cat_name = cat_key.name if cat_key else "General"
                        recipe_inner_html.append(
                            f'<h6 class="fw-bold text-dark border-bottom pb-1 mb-2 mt-2" style="font-size: 0.9rem;">{html_escape(cat_name)}</h6>'
                        )

                        for idx, inst in enumerate(group, start=1):
                            inst_text = html_escape(inst.name or "")
                            time_info = (
                                f' <span class="text-muted small ms-1"><i class="fa fa-clock-o"></i> {inst.time:g} min</span>'
                                if inst.time else ""
                            )

                            recipe_inner_html.append(
                                f'<div class="d-flex align-items-start mb-2" style="font-size: 0.85rem;">'
                                f'  <span class="badge border border-secondary text-secondary rounded-circle me-2 flex-shrink-0 d-flex align-items-center justify-content-center" style="width: 20px; height: 20px; font-size: 0.7rem; margin-top: 2px;">{idx}</span>'
                                f'  <div class="text-secondary" style="line-height: 1.45;">{inst_text}{time_info}</div>'
                                f'</div>'
                            )
                else:
                    for idx, inst in enumerate(sorted_instructions, start=1):
                        inst_text = html_escape(inst.name or "")
                        time_info = (
                            f' <span class="text-muted small ms-1"><i class="fa fa-clock-o"></i> {inst.time:g} min</span>'
                            if inst.time else ""
                        )

                        recipe_inner_html.append(
                            f'<div class="d-flex align-items-start mb-2" style="font-size: 0.85rem;">'
                            f'  <span class="badge border border-secondary text-secondary rounded-circle me-2 flex-shrink-0 d-flex align-items-center justify-content-center" style="width: 20px; height: 20px; font-size: 0.7rem; margin-top: 2px;">{idx}</span>'
                            f'  <div class="text-secondary" style="line-height: 1.45;">{inst_text}{time_info}</div>'
                            f'</div>'
                        )

                content_parts.append(
                    f'<div class="bg-transparent border border-1 p-3 rounded-3 mb-3">'
                    f'  {"".join(recipe_inner_html)}'
                    f'</div>'
                )

            if recipe.notes:
                content_parts.append(
                    f'<h5 class="fw-bold mt-3 mb-2" style="font-size: 1.05rem;">Notes</h5>'
                    f'<div class="bg-transparent border border-1 p-3 rounded-3 mb-3" style="font-size: 0.85rem;">'
                    f'  <p class="mb-0 text-secondary" style="line-height: 1.45;">{html_escape(recipe.notes)}</p>'
                    f'</div>'
                )

            recipe.content = "".join(content_parts)
