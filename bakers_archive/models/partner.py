from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    biography = fields.Text(string='Biography')
    recipe_ids = fields.Many2many('bakers_archive.recipe', 'balers_archive_recipe_author_rel', 'author_id', 'recipe_id', string='Recipes')
