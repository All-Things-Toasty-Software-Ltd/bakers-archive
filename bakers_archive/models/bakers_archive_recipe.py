from datetime import datetime
import random

from odoo import api, models, fields, _
from odoo.addons.website.tools import text_from_html
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.tools.translate import html_translate
from odoo.tools import html_escape


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
                archive_recipe.website_url = "/bakers-archive/%s/%s" % (self.env['ir.http']._slug(archive_recipe.archive_id), self.env['ir.http']._slug(archive_recipe))

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
    author_name = fields.Char(related='author_id.display_name', string='Author Name', readonly=False, store=True)
    active = fields.Boolean('Active', default=True)
    archive_id = fields.Many2one('bakers_archive.archive', 'Archive', required=True, index=True, ondelete='cascade', default=lambda self: self.env['bakers_archive.archive'].search([], limit=1))
    tag_ids = fields.Many2many('bakers_archive.tag', string='Tags')
    content = fields.Html('Content', default=_default_content, translate=html_translate, sanitize=False) # Content will initially be generated based on the given model data, but then can also be HTML edited where needed.
    teaser = fields.Text('Teaser', compute='_compute_teaser', inverse='_set_teaser', translate=True)
    teaser_manual = fields.Text('Teaser Content', translate=True)

    """ I'm not too sure how I'll handle the content generation from this, likely an external script to format it."""
    sources = fields.Many2many('bakers_archive.source', string='Sources')
    license = fields.Many2one('bakers_archive.license', string='License')
    languages = fields.Many2many('bakers_archive.language', string='Languages')
    origins = fields.Many2many('bakers_archive.origin', string='Origins')
    ingredients = fields.One2many('bakers_archive.recipe.ingredient', 'recipe_id', string='Ingredients')
    instructions = fields.One2many('bakers_archive.recipe.instruction', 'recipe_id', string='Instructions')
    notes = fields.Text(string='Notes')

    # Media

    image = fields.Image(string='Image')

    website_message_ids = fields.One2many(domain=lambda self: [('model', '=', self._name), ('message_type', '=', 'comment')])

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
            return super(BakersArchiveRecipe, self)._get_access_action(access_uid=access_uid, force_website=force_website)
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
        return super(BakersArchiveRecipe, self)._notify_thread_by_inbox(message, recipients_data, msg_vals=msg_vals, **kwargs)

    def _default_website_meta(self):
        res = super(BakersArchiveRecipe, self)._default_website_meta()
        res['default_opengraph']['og:description'] = self.subtitle
        res['default_opengraph']['og:type'] = 'article'
        res['default_opengraph']['article:published_time'] = self.published_date
        res['default_opengraph']['article:modified_time'] = self.write_date
        res['default_opengraph']['article:tag'] = self.tag_ids.mapped('name')
        res['default_opengraph']['og:image'] = json_scriptsafe.loads(self.cover_properties).get('background-image','none')[4:-1].strip("\"'")
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
            active_tag_ids = [self.env['ir.http'].unslug(tag)[1] for tag in tags.split(',')] or []
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

            if recipe.subtitle:
                content_parts.append(f'<p class="lead text-muted">{html_escape(recipe.subtitle)}</p>')

            overview_items = []
            if recipe.author_name:
                overview_items.append(f'<strong>Author:</strong> {html_escape(recipe.author_name)}')
            if recipe.origins:
                origins_str = ', '.join(recipe.origins.mapped('name'))
                overview_items.append(f'<strong>Origin:</strong> {html_escape(origins_str)}')
            if recipe.languages:
                langs_str = ', '.join(recipe.languages.mapped('name'))
                overview_items.append(f'<strong>Language:</strong> {html_escape(langs_str)}')
            if recipe.license:
                license_title = recipe.license.short_name or recipe.license.name
                if recipe.license.url:
                    overview_items.append(f'<strong>License:</strong> <a href="{html_escape(recipe.license.url)}" target="_blank">{html_escape(license_title)}</a>')
                else:
                    overview_items.append(f'<strong>License:</strong> {html_escape(license_title)}')

            if overview_items:
                items_html = ''.join([f'<li class="list-inline-item mr-3 pr-3 border-right">{item}</li>' for item in overview_items])
                content_parts.append(f'<ul class="list-inline bg-light p-3 rounded mb-4">{items_html}</ul>')

            if recipe.ingredients:
                content_parts.append('<h3 class="mt-4 mb-3"><i class="fa fa-shopping-basket mr-2"></i>Ingredients</h3>')
                ing_items = []
                for ing in recipe.ingredients:
                    qty = f"{ing.quantity:g} " if ing.quantity else ""  # :g cleans up trailing zeros (1.0 -> 1)
                    unit = f"{ing.unit} " if ing.unit else ""
                    ing_name = ing.name.name if ing.name else ""

                    ing_line = f'<strong>{html_escape(qty)}{html_escape(unit)}</strong>{html_escape(ing_name)}'
                    if ing.notes:
                        ing_line += f' <span class="text-muted small">({html_escape(ing.notes)})</span>'

                    ing_items.append(f'<li class="list-group-item">{ing_line}</li>')
                content_parts.append(f'<ul class="list-group mb-4">{"".join(ing_items)}</ul>')

            if recipe.instructions:
                content_parts.append('<h3 class="mt-4 mb-3"><i class="fa fa-list-ol mr-2"></i>Instructions</h3>')
                inst_items = []
                sorted_instructions = recipe.instructions.sorted(key=lambda i: i.sequence or 0)

                for idx, inst in enumerate(sorted_instructions, start=1):
                    time_badge = ""
                    if inst.time:
                        time_badge = f' <span class="badge badge-info ml-2"><i class="fa fa-clock-o"></i> {inst.time:g} min</span>'

                    inst_text = inst.name or ""
                    inst_items.append(
                        f'<li class="media mb-3 p-3 border rounded">'
                        f'  <span class="badge badge-primary badge-pill mr-3 font-weight-bold" style="font-size: 1.1rem; width: 32px; height: 32px; line-height: 24px;">{idx}</span>'
                        f'  <div class="media-body">'
                        f'    <p class="mb-0">{html_escape(inst_text)}{time_badge}</p>'
                        f'  </div>'
                        f'</li>'
                    )
                content_parts.append(f'<ul class="list-unstyled mb-4">{"".join(inst_items)}</ul>')

            if recipe.notes:
                content_parts.append(
                    f'<div class="alert alert-info mt-4" role="alert">'
                    f'  <h4 class="alert-heading"><i class="fa fa-sticky-note mr-2"></i>Notes</h4>'
                    f'  <p class="mb-0">{html_escape(recipe.notes)}</p>'
                    f'</div>'
                )

            if recipe.sources:
                content_parts.append('<h5 class="mt-4 text-muted"><i class="fa fa-book mr-2"></i>Sources</h5>')
                src_items = []
                for src in recipe.sources:
                    src_title = src.name or "Source"
                    if src.type:
                        src_title = f"{src_title} ({src.type})"

                    if src.url:
                        line = f'<a href="{html_escape(src.url)}" target="_blank">{html_escape(src_title)}</a>'
                    else:
                        line = html_escape(src_title)

                    if src.notes:
                        line += f' — <span class="text-muted">{html_escape(src.notes)}</span>'

                    src_items.append(f'<li>{line}</li>')
                content_parts.append(f'<ul class="small">{"".join(src_items)}</ul>')

            recipe.content = "".join(content_parts)