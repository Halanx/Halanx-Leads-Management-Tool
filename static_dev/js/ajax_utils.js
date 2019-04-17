function ajax_form_submit(form_id, success_callback=function(){}, success_result_alert=true) {
    $(form_id).submit(function (e) {
        e.preventDefault();
        let form = $(this);
        let url = form.attr('action');

        $.ajax({
            type: 'POST',
            url: url,
            data: form.serialize(),
            success: function (data) {
                    if(success_result_alert) {
                        alert(data['detail']);
                    }
                    success_callback();
                }
        });
    });
}

$(document).ajaxSend(function () {
    $('#ajaxLoad').addClass('show');
});

$(document).ajaxComplete(function () {
    $('#ajaxLoad').removeClass('show');
});
