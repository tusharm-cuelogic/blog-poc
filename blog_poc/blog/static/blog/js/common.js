$(function() {
    $( "#from" ).datepicker({
      defaultDate: "+1w",
      changeMonth: true,
      numberOfMonths: 1,
      dateFormat: "yy-mm-dd",
      onClose: function( selectedDate ) {
        $( "#to" ).datepicker( "option", "minDate", selectedDate );
      }
    });
    $( "#to" ).datepicker({
      defaultDate: "+1w",
      changeMonth: true,
      numberOfMonths: 1,
      dateFormat: "yy-mm-dd",
      onClose: function( selectedDate ) {
        $( "#from" ).datepicker( "option", "maxDate", selectedDate );
      }
    });

    if ($("#hiddendate").val() == "date") {
    $("#text_search").hide()
    $("#date_search").show()
  }

  $( ".reset" ).click(function() {
      window.location="/blog/posts/";
  });

  $('#btnComment').on('click', function () {
      
      $("#comment_error").text("")
      if ($("#comment").val().trim() == "") {
        $("#comment_error").text("Please fill out the comment")
        return false;
      }

      post_id = $("#postid").val();
      comment = $("#comment").val().trim();
      comment_count = $("#comment_count").val();

      if (comment_count > 0)
          comment_count = parseInt(comment_count) + 1
      else 
        comment_count = comment_count

      var $btn = $(this).button('loading');  
      
      if (post_id > 0) {
        $.ajax({
          url: base_url + 'blog/comment/'+post_id+'/',
          type: 'post',
          data: {'comment': comment},
          success: function(response) {
            $(this).button('reset');
            $btn.button('reset')
            $("#comment").val('')
            $(".comment-ul").prepend(response)
            $(".comment-count").text(comment_count+" Comments")
          } 
        });
      } 
  });

  $(".delete-icon").on('click', function () {
    confirm("Are you sure? You want to delete this comment");
    postid = $(this).attr('postid')
    commentid = $(this).attr('commentid')

    $("#li-"+commentid).fadeOut('slow');

    if (postid > 0 && commentid) {
      $.ajax({
        url: base_url + 'blog/comment/delete/',
        type: 'post',
        data: {'commentid': commentid, 'postid': postid},
        success: function(response) {
            if (response == "success") {

              $("#li-"+commentid).remove();

              comment_count = $("#comment_count").val();

              if (comment_count > 0)
                  comment_count = parseInt(comment_count) - 1;
              else 
                comment_count = comment_count;

              $(".comment-count").text(comment_count+" Comments");
            }
          }
      });
    } 
  });

});

function searchType() {
  $("#text_search").show()
  $("#date_search").hide()
  if ($('#search_type :selected').val() == "date") {
    $("#text_search").hide()
    $("#date_search").show()
  }
}