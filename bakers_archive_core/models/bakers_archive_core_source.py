from odoo import fields, models


class BakersArchiveCoreSource(models.Model):
    _name = 'bakers_archive.core.source'
    _description = 'Bakers Archive Core Source'

    recipe_id = fields.Many2many('bakers_archive.core.recipe', String="Recipes")

    name = fields.Char(string='Name')
    type = fields.Char(string='Type')
    url = fields.Char(string='URL')
    notes = fields.Text(string='Notes')
