# Odoo Fields

## Boolean

A true or false field.

- `default`: The default state. Either `True` or `False`.

## Char

A classic short text entry field.

- `string`: The title for the entry box
- `tracking`: Enables automatic change logging that can be set up with the
  chatter, or viewed in `Settings->Technical->Discuss->Messages`
- `required`: A boolean for if the field is required to have data.

## Many2one

A many to one relation field.

- The first data passed should be the model its relating to.
- `string`: The display name for the entry box.
- `ondelete`: defines what happens when removed.

## One2many

A one to many relation field

- The first value should be the model its relating to.
- The second value should be field name for the corresponding Many2one
- `string`: The display name for the entry box.