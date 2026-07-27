import {onWillStart, useState} from "@odoo/owl";
import {BaseOptionComponent, useDomState} from "@html_builder/core/utils";
import {useDynamicSnippetOption} from "@website/builder/plugins/options/dynamic_snippet_hook";

export class DynamicSnippetArchiveRecipesOption extends BaseOptionComponent {
    static template = "bakers_archive.DynamicSnippetArchiveRecipesOption";
    static dependencies = ["dynamicSnippetArchiveRecipesOption"];
    static selector = ".s_dynamic_snippet_archive_recipes";

    setup() {
        super.setup();
        const {fetchArchives, getModelNameFilter} = this.dependencies.dynamicSnippetArchiveRecipesOption;
        this.modelNameFilter = getModelNameFilter();
        this.dynamicOptionParams = useDynamicSnippetOption(this.modelNameFilter);
        this.archiveState = useState({
            archives: [],
        });
        onWillStart(async () => {
            this.archiveState.archives.push(...(await fetchArchives()));
        });
        this.templateKeyState = useDomState((el) => ({
            templateKey: el.dataset.templateKey,
        }));
    }

    showPictureSizeOption() {
        return [
            "bakers_archive.dynamic_filter_template_archive_recipe_big_picture",
            "bakers_archive.dynamic_filter_template_archive_recipe_horizontal",
            "bakers_archive.dynamic_filter_template_archive_recipe_card",
        ].includes(this.templateKeyState.templateKey);
    }

    showTeaserOption() {
        return [
            "bakers_archive.dynamic_filter_template_archive_recipe_list",
            "bakers_archive.dynamic_filter_template_archive_recipe_card",
        ].includes(this.templateKeyState.templateKey);
    }

    showDateOption() {
        return [
            "bakers_archive.dynamic_filter_template_archive_recipe_list",
            "bakers_archive.dynamic_filter_template_archive_recipe_horizontal",
            "bakers_archive.dynamic_filter_template_archive_recipe_card",
            "bakers_archive.dynamic_filter_template_archive_recipe_single_full",
            "bakers_archive.dynamic_filter_template_archive_recipe_single_aside",
            "bakers_archive.dynamic_filter_template_archive_recipe_single_circle",
        ].includes(this.templateKeyState.templateKey);
    }

    showCategoryOption() {
        return [
            "bakers_archive.dynamic_filter_template_archive_recipe_list",
            "bakers_archive.dynamic_filter_template_archive_recipe_horizontal",
            "bakers_archive.dynamic_filter_template_archive_recipe_card",
            "bakers_archive.dynamic_filter_template_archive_recipe_single_full",
            "bakers_archive.dynamic_filter_template_archive_recipe_single_aside",
            "bakers_archive.dynamic_filter_template_archive_recipe_single_circle",
            "bakers_archive.dynamic_filter_template_archive_recipe_single_badge",
        ].includes(this.templateKeyState.templateKey);
    }

    showNewTagOption() {
        return (
            this.templateKeyState.templateKey ===
            "bakers_archive.dynamic_filter_template_archive_recipe_single_badge"
        );
    }

    showHoverEffectOption() {
        return (
            this.templateKeyState.templateKey ===
            "bakers_archive.dynamic_filter_template_archive_recipe_big_picture"
        );
    }

    showCoverImageOption() {
        return [
            "bakers_archive.dynamic_filter_template_archive_recipe_single_aside",
            "bakers_archive.dynamic_filter_template_archive_recipe_single_circle",
        ].includes(this.templateKeyState.templateKey);
    }
}
