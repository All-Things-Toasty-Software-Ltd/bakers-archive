from odoo import fields, models


class BakersArchiveCoreRecipe(models.Model):
    _name = 'bakers_archive.core.recipe'
    _description = 'Bakers Archive Core Recipe'

    # string: The default title of the entry box.
    # tracking: enables automatic change logging that can be set up with the
    #   chatter, or viewed in 'Settings->Technical->Discuss->Messages'.
    # default: The default state of a Boolean.

    active = fields.Boolean(default=True)

    # Metadata

    name = fields.Char(string='Recipe Name', tracking=True)
    author = fields.Char(string='Author')
    license = fields.Char(string='License')
    language = fields.Char(string='Language')
    origin = fields.Char(string='Origin')
    tags = fields.Char(string='Tags')

    # Recipe

    description = fields.Char(string='Description')
    ingredients = fields.Char(string='Ingredients')
    instructions = fields.Char(string='Instructions')
    notes = fields.Char(string='Notes')

