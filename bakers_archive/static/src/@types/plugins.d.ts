declare module "plugins" {
    import {
        DynamicSnippetArchiveRecipesOptionShared
    } from "custom-addons/bakers_archive/static/src/website_builder/dynamic_snippet_archive_recipes_option_plugin";

    interface SharedMethods {
        dynamicSnippetArchiveRecipesOption: DynamicSnippetArchiveRecipesOptionShared;
    }
}
