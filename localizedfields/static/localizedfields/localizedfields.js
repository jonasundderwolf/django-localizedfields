(function ($) {
    var LOCALIZED_FIELDS, ADMIN_URL, $translation_field;

    $.holdReady(true);

    if (window.location.pathname.substr(-7) === 'change/') {
        // When inside Django /change/ url, step back two path increments
        ADMIN_URL = window.location.pathname + '../../localizedfields/';
    } else {
        // When inside Django /add/ url (or others without a pk), step back one path increment
        ADMIN_URL = window.location.pathname + '../localizedfields/';
    }

    $.getJSON(ADMIN_URL, function (data) {
    })
        .done(function (data) {
            LOCALIZED_FIELDS = data;
            $.holdReady(false);
        })
        .fail(function () {
            $.holdReady(false);
            console.error('API endpoint admin/localizedfields not found.');
        });

    $(function () {
        // Shortcut, if there isn't any change form
        if (!LOCALIZED_FIELDS || !$('body').hasClass('change-form')) {
            return;
        }

        $translation_field = $('div.field-translated_languages input');

        if (window.location.search.match(/lang=(\w{2})/)) {
            visible_translations([LOCALIZED_FIELDS.default_language, RegExp.$1]);
        }
        $('fieldset.language').wrapAll('<div id="all_languages"/>');

        // move default language to first position
        $('fieldset.language.' + LOCALIZED_FIELDS.default_language).prependTo($('#all_languages'));

        prepare_language_selector();
        if (prepare_visibility_fields()) {
            prepare_fallback_checkbox();
        }
    });

    function prepare_language_selector() {
        // add checkboxes to turn display of individual languages on and off
        var lang_selectors = '<div id="language-selector" class="inline-group">' +
            '<div class="form-row">' + LOCALIZED_FIELDS.translation_label + ': ',
            translations = visible_translations();

        $.each(LOCALIZED_FIELDS.languages, function () {
            var lang = this[0], name = this[1];

            // primary language can't be toggled
            if (lang == LOCALIZED_FIELDS.default_language) {
                return;
            }
            var show_fields_for_language = $.inArray(lang, translations) > -1;

            lang_selectors += '<input id="id_translation_show_' + lang + '" type="checkbox"  value="' + lang + '" ' +
                (show_fields_for_language ? 'checked="checked"' : '') + ' /> ' + '<label for="id_translation_show_' + lang + '">' +
                name + ' (' + lang + ')</label>&nbsp;&nbsp;';

        });
        lang_selectors += '</div></div>';
        $('.breadcrumbs').after(lang_selectors);

        $('#language-selector').on('click', 'input', function () {
            if ($(this).is(':checked')) {
                visible_translations(this.value);
            } else {
                visible_translations(undefined, this.value);
            }
            show_hide_elements()
        });

        show_hide_elements()
    }

    function prepare_visibility_fields() {
        // add button to make all language versions visible
        $($('div[class*=field-visible][class*=field-box]')[0])  // before the first checkbox
            .before('<div class="field-box"><input id="id_visible_all" type="checkbox"> '
                + '<label for="id_visible_all" class="vCheckboxLabel">Visible (all)</label></div>');
        $('#id_visible_all').change(function () {
            if ($(this).is(':checked')) {
                $('input[name^=visible]').attr('checked', false);
            } else {
                $('input[name^=visible]').attr('checked', true);
            }
        });

        $('input[name^=visible]').change(function () {
            // check or uncheck "all visible" checkbox when applicable
            if ($(this).is(':checked')) {
                if (!$('input[name^=visible]:not(:checked)').length) {
                    $('#id_visible_all').attr('checked', true);
                }
            } else {
                $('#id_visible_all').attr('checked', false);
            }
        }).change();

        return $('div.field-translated_languages').hide().length > 0;
    }

    function prepare_fallback_checkbox() {
        var fallback_toggle_label_color = $('fieldset.language h2').css('color'),
            fallback_title = LOCALIZED_FIELDS.fallback_label.replace(/\{language\}/, LOCALIZED_FIELDS.languages[0][1]),
            active = active_translations();

        $.each(LOCALIZED_FIELDS.languages, function () {
            var lang = this[0], name = this[1],
                fallback_active = false;
            fallback_toggle_id = 'fallback-toggle-' + lang;

            if (lang == LOCALIZED_FIELDS.default_language) {
                return;
            }

            if ($.inArray(lang, active) == -1) {
                fallback_active = true;
            } else {
                $('#language-selector label[for=id_translation_show_' + lang + ']').addClass('translated');
            }

            $fallback_toggle = $(
                '<div class="fallback-toggle">' +
                '<input type="checkbox" id="' + fallback_toggle_id + '" ' + (fallback_active ? 'checked="checked"' : '') + ' value="' + lang +
                '"/> <label style="color: ' + fallback_toggle_label_color + '" for=' + fallback_toggle_id + '>' + fallback_title + '</label>' +
                '</div>'
            );

            $('fieldset.language.' + lang + ' h2').text(name).append($fallback_toggle);

        });

        function align_objects() {
            var field_types = [
                'link',
                'key_fact',
                'document',
                'title',
                'tile',
                'text',
                'name',
                'button',
                'image',
                'cropping',
                'headline',
                'teaser',
                'black_overlay_text'
            ];

            for (i = 0; i < field_types.length; i++) {
                $('div[class*=' + field_types[i] + ']').addClass('field-' + field_types[i]);
            }

            $.each($('fieldset'), function () {
                for (i = 0; i < field_types.length; i++) {
                    $(this).find($('.field-' + field_types[i])).wrapAll("<div class='" + field_types[i] + "-wrapper' />");
                }
            });
        }

        align_objects();

        $('#all_languages').on('click', '.fallback-toggle input', function () {
            var $this = $(this),
                lang = $this.val(),
                $lang_label = $('#language-selector label[for=id_translation_show_' + lang + ']');

            if ($this.is(':checked')) {
                // remove from existing translations
                active_translations(undefined, lang);
                $lang_label.removeClass('translated');
            } else {
                // activate language
                active_translations(lang);
                $lang_label.addClass('translated');
            }

            show_hide_elements();
        });

        // update FeinCMS content blocks
        if (typeof(contentblock_init_handlers) != 'undefined') {
            contentblock_init_handlers.push(function () {
                show_hide_elements();

                var def_lang_fields = $('#main > div fieldset.module:not(.lang-processed) > .form-row').filter(function () {
                    return $(this).attr('class').indexOf('_' + LOCALIZED_FIELDS.default_language) > 0;
                });
                // languages should be next to each in feincms contents
                // clear the left float on the primary language
                def_lang_fields.css('clear', 'left');

                // prevent multiple execution
                def_lang_fields.each(function () {
                    $(this).closest('fieldset').addClass('lang-processed');
                });
            });
        }
    }

    function show_hide_elements() {
        var visible = visible_translations(),
            active = active_translations();

        $('#all_languages, #main').css('width', 460 * (visible.length));

        // loop over fields and show/hide as appropriate
        $.each(LOCALIZED_FIELDS.languages, function () {
            var lang = this[0], name = this[1];
            if (lang == LOCALIZED_FIELDS.default_language) {
                return;
            }

            // hide elements where class name contains "_lang" (e.g. "_de")
            var $elements = $('fieldset.language.' + lang),
                $feincms_elements = $('div.item-content div.form-row')
                    .filter('[class*="_' + lang + ' "], [class$="_' + lang + '"]');

            if ($.inArray(lang, visible) > -1) {
                // show this language's fieldset
                $elements.show();
                $feincms_elements.show();
                if ((active === false) || ($.inArray(lang, active) > -1)) {
                    // no visibility checking or language exists - show all fields
                    $elements.find('.form-row').show();
                    $feincms_elements.css('visibility', 'visible');
                    if ($.show_tinymce !== undefined) {
                        $.show_tinymce();
                    }
                } else {
                    // language doesn't exist yet
                    $elements.find('.form-row').hide();
                    $feincms_elements.css('visibility', 'hidden');
                }
            } else {
                $elements.hide();
                $feincms_elements.hide();
            }
        });
    }

    function visible_translations(add, remove) {
        var translations = (Cookies.get('admin_translations') || LOCALIZED_FIELDS.default_language).split(/,/);
        if (add || remove) {
            if (add && ($.inArray(add, translations) == -1)) {
                translations.push(add);
            }
            if (remove) {
                translations = $.grep(translations, function (v) {
                    return v != remove
                });
            }
            Cookies.set('admin_translations', translations.join(','), {path: '/'});
        }
        return translations;
    }

    function active_translations(add, remove) {
        if (!$translation_field.length) {
            return false;
        }
        var translations = $translation_field.val().replace(/,,/g, ',').replace(/^,/, '').replace(/,$/, '').split(/,/);

        if (add || remove) {
            if (add && ($.inArray(add, translations) == -1)) {
                translations.push(add);
                $('#language-selector label[for=id_translation_show_' + add + ']').addClass('translated');
            }
            if (remove) {
                translations = $.grep(translations, function (v) {
                    return v != remove
                });
                $('#language-selector label[for=id_translation_show_' + remove + ']').removeClass('translated');
            }
            $translation_field.val(translations.join(','));
        }
        return translations;
    }
})(django.jQuery);
