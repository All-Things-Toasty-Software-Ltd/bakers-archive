import { scrollTo } from "@html_builder/utils/scrolling";
import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";

import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";
import { verifyHttpsUrl } from "@website/utils/misc";
import { getActiveHotkey } from "@web/core/hotkeys/hotkey_service";

export class BakersArchive extends Interaction {
    static selector = ".bakers_archive";
    dynamicContent = {
        ".o_barchive_next_button": {
            "t-on-click.prevent": this.onNextArchiveClick,
            "t-on-keydown": this.onNextArchiveKeydown,
        },
        "#o_barchive_recipe_content_jump": {
            "t-on-click.prevent.withTarget": this.onContentAnchorClick,
        },
        ".o_twitter, .o_facebook, .o_linkedin, .o_google, .o_twitter_complete, .o_facebook_complete, .o_linkedin_complete, .o_google_complete":
            {
                "t-on-click.prevent.withTarget": this.onShareRecipeClick,
            },
    };
    
    async onNextArchiveClick(ev) {
        const archiveNextContainerEl = ev.currentTarget.closest("#o_barchive_next_container");
        const nextInfo = archiveNextContainerEl.querySelector("#o_barchive_next_recipe_info").dataset;
        const recordCoverContainerEl = archiveNextContainerEl.querySelector(
            ".o_record_cover_container"
        );
        const classes = nextInfo.size.split(" ");
        recordCoverContainerEl.classList.add(...classes, nextInfo.textContent);
        archiveNextContainerEl
            .querySelectorAll(".o_barchive_toggle")
            .forEach((el) => el.classList.toggle("d-none"));
   
        const placeholder = document.createElement("div");
        placeholder.style.minHeight = "100vh";
        this.insert(placeholder, this.el.querySelector("#o_barchive_next_container"), "beforeend");
        const nextUrl = verifyHttpsUrl(nextInfo.url);
        await this.forumScrollAction(
            archiveNextContainerEl,
            300,
            () => (browser.location.href = nextUrl)
        );
    }
  
    onNextArchiveKeydown(ev) {
        const hotkey = getActiveHotkey(ev);
        if (hotkey === "enter" || hotkey === "space") {
            return this.onNextArchiveClick(ev);
        }
    }


    async onContentAnchorClick(ev, currentTargetEl) {
        ev.stopImmediatePropagation();
        const scrollTargetEl = document.querySelector(currentTargetEl.hash);

        await this.forumScrollAction(
            scrollTargetEl,
            500,
            () => (browser.location.hash = "archive_content")
        );
    }
    
    onShareRecipeClick(ev, currentTargetEl) {
        let url = "";
        const archiveRecipeTitle = document.querySelector(".o_barchive_recipe_name").textContent || "";
        const recipeURL = browser.location.href;
        if (currentTargetEl.classList.contains("o_twitter")) {
            const tweetText = _t("Amazing archive recipe: %(title)s! Check it live: %(url)s", {
                title: archiveRecipeTitle,
                url: recipeURL,
            });
            url =
                "https://twitter.com/intent/tweet?tw_p=tweetbutton&text=" +
                encodeURIComponent(tweetText);
        } else if (currentTargetEl.classList.contains("o_facebook")) {
            url = "https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(recipeURL);
        } else if (currentTargetEl.classList.contains("o_linkedin")) {
            url =
                "https://www.linkedin.com/sharing/share-offsite/?url=" +
                encodeURIComponent(recipeURL);
        }
        window.open(url, "", "menubar=no, width=500, height=400");
    }

    async forumScrollAction(el, duration, callback) {
        await this.waitFor(scrollTo(el, { duration }));
        callback();
    }
}

registry.category("public.interactions").add("bakers_archive.bakers_archive", BakersArchive);
