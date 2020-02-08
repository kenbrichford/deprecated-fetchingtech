$(function() {
  var query = $(this).find('#id_query');
  var category = $(this).find('#id_category');

  $('#head-search').submit(function () {
    // trim search form text
    $(query).val($(query).val().trim());

    // don't submit category if empty
    if (!category.val()) {
      category.prop('disabled', true);
    }
  });

  // menu dropdown
  $('#head-arrow img').click(function() {
    if (!$(this).hasClass('flip')) {
      $(this).removeClass('unflip');
      $(this).addClass('flip');
      $('#head-links').show(200);
      $('#head-search').show(200);
    } else {
      $(this).removeClass('flip');
      $(this).addClass('unflip');
      $('#head-links').hide(200);
      $('#head-search').hide(200);
    }
  });
});
