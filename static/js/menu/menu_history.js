const get_csrf = ()=>{
    if (window.Cookies && window.Cookies.get)
        return window.Cookies.get('csrftoken')
    return ""
}


const setup_ajax = ()=>{
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", get_csrf());
            }
        }
    });
}


$(document).ready(()=>{
    // init
    setup_ajax()

    // event click item
    $(".menu_item").click(function(){
        window.location = $(this).attr("href")
    })

    $("#date_filter").datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: 'dd-mm-yy',
        onSelect: function(dateText, inst) {
            $("#form_date_filter").submit()
        }
    })

    let clear_filter = $("#clear_filter")
    if (clear_filter){
        clear_filter.click(function(){
            window.location = window.location
        })
    }
})