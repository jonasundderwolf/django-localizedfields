(function($) {
  $(function() {
    // Shortcut, if there isn't any change form
    if (!$('body').hasClass('change-form')) {return;}

    var translation_field = $('div.field-translated_languages')
      .hide()
      .find('input');
    var show_translations = $.cookie('admin_translations') || LANGUAGE_CODE;
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

    // ---- add checkboxes to turn display of individual languages on and off
    var html = '<div id="language-selector" class="inline-group"><div class="form-row">';
    var translations = translation_field.val();
    $.each(LANGUAGES, function() {
      var lang = this[0], name = this[1];
      if (lang == LANGUAGE_CODE) {return;}
      var translated = '', visible = '';
      if (show_translations.indexOf(lang) > -1) {
        visible = 'checked="checked""'
      }
      if (translations.indexOf(lang) > -1) {
        translated = 'class="translated"';

        // show button to deactivate language
        $('fieldset.language.' + lang + ' h2')
          .append(' <input type="checkbox" name="activate_language" checked="checked" value="' + lang + '"/> Translated');
      } else {
        // show button to activate language
        $('fieldset.language.' + lang + ' h2')
          .append(' <input type="checkbox" name="activate_language" value="' + lang + '"/> Translated');
      }
      html += '<input id="id_show_' + lang + '" type="checkbox"  name="show_language" value="' + lang + '" ' + visible + '" /> '
        + '<label for="id_show_' + lang + '" ' + translated + '>' + name + ' (' + lang + ')</label>&nbsp;&nbsp;';
    });
    html += '</div></div>'

    $('#content').prepend(html);
    // move default language to first position
    $('fieldset.language.' + LANGUAGE_CODE).prependTo($('#all_languages'));

    show_hide_elements(show_translations, translation_field.val());

    $('#language-selector input').click(function(e) {
      var show_translations = LANGUAGE_CODE;
      $('#language-selector input:checked').each(function() {
        show_translations += ',' + $(this).val();
      });
      $.cookie('admin_translations', show_translations, {path: '/'});
      show_hide_elements(show_translations, translation_field.val());
    });

    $('input[name=activate_language]').click(function() {
      var $this = $(this);
      var lang = $this.val();
      $('#language-selector label[for=id_show_' + lang + ']').toggleClass('translated');
      if ($this.is(':checked')) {
        // activate language
        translation_field.val(translation_field.val() + ',' + lang);
      } else {
        // remove from existing translations
        translation_field.val(translation_field.val().replace(',' + lang, ''));
      }

      show_hide_elements($.cookie('admin_translations') || LANGUAGE_CODE,
          translation_field.val());
    });

    // update FeinCMS content blocks
    if (typeof(contentblock_init_handlers) != 'undefined') {
      contentblock_init_handlers.push(function() {
        show_hide_elements(
          $.cookie('admin_translations') || LANGUAGE_CODE,
          translation_field.val()
        );
        // languages should be next to each in feincms contents
        // clear the left float on the primary language
        $('#main > div .form-row').filter(function () {
          return $(this).attr('class').indexOf('_'+LANGUAGE_CODE) > 0;
        }).css('clear', 'left');
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
