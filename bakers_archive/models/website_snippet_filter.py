from datetime import timedelta

from odoo import models, fields, api, _

class WebsiteSnippetFilter(models.Model):
    _inherit = 'website.snippet.filter'

    def _get_hardcoded_sample(self, model):
        samples = super()._get_hardcoded_sample(model)
        if model._name == 'bakers_archive.recipe':
            data = []
            merged = []
            for index in range(0, max(len(samples), len(data))):
                merged.append({**samples[index % len(samples)], **data[index % len(data)]})
            samples = merged
        return samples

    @api.model
    def default_get(self, fields):
        defaults = super().default_get(fields)
        if 'field_names' in defaults and self.env.context.get('model') == 'bakers_archive.recipe':
            defaults['field_names'] = 'name,teaser,subtitle'
        return defaults