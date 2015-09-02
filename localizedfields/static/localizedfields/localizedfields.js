(function($) {
  $(function() {
    // Shortcut, if there isn't any change form
    if (!$('body').hasClass('change-form')) {return;}

    // trim language suffixes from labels
    $("label").each(function(index){
        var label = $(this),
            newText = label.text().replace(/\s+\(.+?\)/g, '');
            newHTML = label.html().replace(label.text(), newText);
        label.html(newHTML);
    });

    var fallback_toggle_label_color = $('fieldset.language h2').css('color');

    var translation_field = $('div.field-translated_languages')
      .hide()
      .find('input');
    var show_translations = Cookies.get('admin_translations') || LANGUAGE_CODE;
    if (window.location.search.match(/lang=(\w{2})/)) {
      show_translations = LANGUAGE_CODE + ',' + RegExp.$1;
    }

    // add button to make all language versions visible
    $($('div[class*=field-visible][class*=field-box]')[0])  // bevor the first checkbox
      .before('<div class="field-box"><input id="id_visible_all" type="checkbox"> '
        + '<label for="id_visible_all" class="vCheckboxLabel">Visible (all)</label></div>');
    $('#id_visible_all').change(function() {
      if ($(this).is(':checked')) {
        $('input[name^=visible]').attr('checked', true);
      } else {
        $('input[name^=visible]').attr('checked', false);
      }
    });

    $('input[name^=visible]').change(function() {
      // check or uncheck "all visible" checkbox when applicable
      if ($(this).is(':checked')) {
        if (!$('input[name^=visible]:not(:checked)').length) {
          $('#id_visible_all').attr('checked', true);
        }
      } else {
        $('#id_visible_all').attr('checked', false);
      }
    }).change();
    $('fieldset.language').wrapAll('<div id="all_languages"/>')

    // add checkboxes to turn display of individual languages on and off
    var lang_selectors = '<div id="language-selector" class="inline-group">' +
                         '<div class="form-row">Show translation tab for: ';
    var translations = translation_field.val();
    $.each(LANGUAGES, function() {
      var lang = this[0],
          name = this[1];
      // primary language can't be toggled
      if (lang == LANGUAGE_CODE) {return;}
      var translated = '',
          show_fields_for_language = false;
          fallback_active = true;

      if (translations.indexOf(lang) > -1) {
        fallback_active = false;
      }

      if (show_translations.indexOf(lang) > -1) {
        show_fields_for_language = true;
      }

      var fallback_toggle_id = 'language-toggle-' + lang;
      var fallback_title = 'Fallback to ' + LANGUAGE_CODE.toUpperCase();
      var $fallback_toggle = $(
        '<div class="language-toggle">' +
        '<input type="checkbox" id=' + fallback_toggle_id + ' name="activate_language" ' + 
        (fallback_active ? 'checked="checked"' : '') + ' value="' + lang +
        '"/> <label style="color: ' + fallback_toggle_label_color + '" for=' + fallback_toggle_id + '>' + fallback_title + '</label>' +
        '</div>'
      );

      $('fieldset.language.' + lang + ' h2').append($fallback_toggle);

      lang_selectors += '<input id="id_show_' + lang + '" type="checkbox"  name="show_language" value="' + 
        lang + '" ' + (show_fields_for_language ? 'checked="checked"' : '') + ' /> ' + '<label for="id_show_' + lang + '" ' +
        (fallback_active ? 'class="translated"' : '') + '>' + name + ' (' + lang +
        ')</label>&nbsp;&nbsp;';
    });
    lang_selectors += '</div></div>'

    $('.breadcrumbs').append(lang_selectors);

    // move default language to first position
    $('fieldset.language.' + LANGUAGE_CODE).prependTo($('#all_languages'));

    show_hide_elements(show_translations, translation_field.val());

    $('#language-selector input').click(function(e) {
      var show_translations = LANGUAGE_CODE;
      $('#language-selector input:checked').each(function() {
        show_translations += ',' + $(this).val();
      });
      Cookies.set('admin_translations', show_translations, {path: '/'});
      show_hide_elements(show_translations, translation_field.val());
    });

    $('input[name=activate_language]').click(function() {
      var $this = $(this);
      var lang = $this.val();
      $('#language-selector label[for=id_show_' + lang + ']').toggleClass('translated');
      if (!$this.is(':checked')) {
        // activate language
        translation_field.val(translation_field.val() + ',' + lang);
      } else {
        // remove from existing translations
        translation_field.val(translation_field.val().replace(',' + lang, ''));
      }

      show_hide_elements(Cookies.get('admin_translations') || LANGUAGE_CODE,
        translation_field.val());
    });

    // update FeinCMS content blocks
    if (typeof(contentblock_init_handlers) != 'undefined') {
      contentblock_init_handlers.push(function() {
        show_hide_elements(
          Cookies.get('admin_translations') || LANGUAGE_CODE,
          translation_field.val()
        );

        var def_lang_fields = $('#main > div fieldset.module:not(.lang-processed) > .form-row').filter(function () {
          return $(this).attr('class').indexOf('_'+LANGUAGE_CODE) > 0;
        })
        // languages should be next to each in feincms contents
        // clear the left float on the primary language
        def_lang_fields.css('clear', 'left');

        // prevent multiple execution
        def_lang_fields.each(function () {
          $(this).closest('fieldset').addClass('lang-processed');
        });
      });
    }
  });

  function show_hide_elements(show_translations, translations) {
    // loop over fields and show/hide as appropriate
    $.each(LANGUAGES, function() {
      var lang = this[0], name = this[1];
      if (lang == LANGUAGE_CODE) {return;}
      var elements = $('fieldset.language.' + lang);
      var feincms_elements = $('div.item-content div.form-row[class$=_' + lang + ']');

      if (show_translations.indexOf(lang) > -1) {
        // show this language's fieldset
        elements.show();
        feincms_elements.show();
        if (translations.indexOf(lang) > -1) {
          // language exists - show all fields
          elements.find('.form-row').show();
          feincms_elements.css('visibility', 'visible');
          if ($.show_tinymce !== undefined) {$.show_tinymce();}
        } else {
          // language doesn't exist yet
          elements.find('.form-row').hide();
          feincms_elements.css('visibility', 'hidden');
        }
      } else {
        elements.hide();
        feincms_elements.hide();
      }
    });
    $('#all_languages, #main').css('width', 460*(show_translations.split(',').length));
  }
})(django.jQuery);
