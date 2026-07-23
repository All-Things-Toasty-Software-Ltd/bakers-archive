# Model Structure

## Recipe

The base model that handles an actual recipe.

### Metadata

- `active`: A boolean way to easily show/hide recipes.
- `name`: Char to represent the name of the recipe.
- `author` Char to represent the author of the recipe.
- `license:` Char to represent what license the recipe is under.
- `language`: Char to represent what language the recipe is in.
- `origin`: Char to represent where the recipe is from.
- `tags`: Currently chars to indicate what tags are on the recipe.

### Recipe Data

- `description`: Text to represent a short description of the recipe.
- `ingredients`: A One2many relation with the `Recipe Ingredient` model linked
  with the `recipe_id` field.
- `instructions`: A One2many relation with the `Recipe Instruction` model
  linked with the `recipe_id` field.
- `notes`: A Text to represent notes for the recipe.

## Recipe Ingredient

- `recipe_id`: Many2one field to link to the `Recipe` model.
- `quantity`: Float to represent the quantity of the ingredient.
- `unit`: Char to represent the unit of measure for the ingredient.
- `ingredient`: A Many2one relation with the `Ingredient` model.
- `notes`: A Text to represent notes for the ingredient.

## Ingredient

- `name`: Char to represent the name of the ingredient.
- `description`: Text to represent a description of the ingredient.
- `recipe_ingredient_ids`: A One2many relation with the `Recipe Ingredient` model
  through the `recipe` field.

## Instructions

- `recipe_id`: Many2one field to link to the `Recipe` model.
- `sequence`: Integer to represent the order of the step.
- `description`: Text to represent the description of the step.
- `time`: Float to represent time taken or needed for the step.