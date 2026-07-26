import { Plugin } from "@html_editor/plugin";
import { registry } from "@web/core/registry";
import { ArchiveRecipeTagsOption } from "./archive_recipe_tags_option";

class ArchiveRecipeTagsOptionPlugin extends Plugin {
    static id = "archiveRecipeTagsOption";
    /** @type {import("plugins").WebsiteResources} */
    resources = {
        builder_options: [ArchiveRecipeTagsOption],
    };
}

registry.category("website-plugins").add(ArchiveRecipeTagsOptionPlugin.id, ArchiveRecipeTagsOptionPlugin);
