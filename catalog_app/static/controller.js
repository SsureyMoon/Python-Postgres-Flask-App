/**
 * Created by ssureymoon on 6/13/15.
 */
$(function() {
    $('#add-item-form').submit(function(event) {
      event.preventDefault();
      token = $.cookie('token');
        console.log("add item");
      $.ajax({
          type: 'POST',
          url: add_item_url,
          data: $(this).serialize(),
          beforeSend: function (xhr) {
              xhr.setRequestHeader('Authorization', token);
          },
          success: function (result) {
              if (result) {
                  var successFlash = '<div class="alert alert-success" role="alert">' +
                      '<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span>' +
                      result.message + '</div>';
                  $('.flash-holder').html(successFlash);
                  $('form').html("");
                  window.setTimeout(function(){window.location.href = result.redirect;}, 1000);

              }
          },
          error: function(result) {
              var jsonResult = JSON.parse(result.responseText);
            var errorFlash = '<div class="alert alert-danger" role="alert">' +
                      '<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span>' +
                      jsonResult.message + '</div>';
              $('.flash-holder').html(errorFlash);
              $('form').html("");
              window.setTimeout(function(){window.location.href = jsonResult.redirect;}, 1000);
          }
      })
  });

  $('#edit-item-form').submit(function(event) {
      event.preventDefault();
      token = $.cookie('token');
      $.ajax({
          type: 'POST',
          url: edit_item_url,
          data: $(this).serialize(),
          beforeSend: function (xhr) {
              xhr.setRequestHeader('Authorization', token);
          },
          success: function (result) {
              if (result) {
                  var successFlash = '<div class="alert alert-success" role="alert">' +
                      '<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span>' +
                      result.message + '</div>';
                  $('.flash-holder').html(successFlash);
                  $('form').html("");
                  window.setTimeout(function(){window.location.href = result.redirect;}, 1000);

              }
          },
          error: function(result) {
              var jsonResult = JSON.parse(result.responseText);
            var errorFlash = '<div class="alert alert-danger" role="alert">' +
                      '<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span>' +
                      jsonResult.message + '</div>';
              $('.flash-holder').html(errorFlash);
              $('form').html("");
              window.setTimeout(function(){window.location.href = jsonResult.redirect;}, 1000);
          }
      })
  });
    $('#delete-item-form').submit(function(event) {
      event.preventDefault();
      token = $.cookie('token');
      $.ajax({
          type: 'POST',
          url: delete_item_url,
          data: $(this).serialize(),
          beforeSend: function (xhr) {
              xhr.setRequestHeader('Authorization', token);
          },
          success: function (result) {
              if (result) {
                  var successFlash = '<div class="alert alert-success" role="alert">' +
                      '<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span>' +
                      result.message + '</div>';
                  $('.flash-holder').html(successFlash);
                  $('form').html("");
                  window.setTimeout(function(){window.location.href = result.redirect;}, 1000);
              }
          },
          error: function(result) {
              var jsonResult = JSON.parse(result.responseText);
            var errorFlash = '<div class="alert alert-danger" role="alert">' +
                      '<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span>' +
                      jsonResult.message + '</div>';
              $('.flash-holder').html(errorFlash);
              $('form').html("");
              window.setTimeout(function(){window.location.href = jsonResult.redirect;}, 1000);
          }
      })
  })

});
