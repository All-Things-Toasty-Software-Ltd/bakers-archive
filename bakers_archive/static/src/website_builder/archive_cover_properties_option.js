import {patch} from "@web/core/utils/patch";
import {useDomState} from "@html_builder/core/utils";
import {CoverPropertiesOption} from "@website/builder/plugins/options/cover_properties_option";
import {_t} from "@web/core/l10n/translation";

patch(CoverPropertiesOption.prototype, {
    setup() {
        super.setup();
        this.archiveState = useDomState((editingElement) => ({
            isRegularCover: editingElement.classList.contains("o_barchive_recipe_page_cover_regular"),
        }));
    },

    coverSizeLabel(className) {
        return this.archiveState.isRegularCover
            ? archiveCoverSizeClassLabels[className]
            : super.coverSizeLabel(className);
    },
});

const archiveCoverSizeClassLabels = {
    o_full_screen_height: _t("Large"),
    o_half_screen_height: _t("Medium"),
    cover_auto: _t("Tiny"),
};
