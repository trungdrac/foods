let calo_select = 0
let temp_dishs = []

let dish_contianer
let btn_show_model
let btn_delete_all

// total calories over limit
const ALLOW_OVER = true

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


const get_total_calories = ()=>{
    let total_calories = 0 
    for (let d in dishes){
        let dish = dishes[d]
        total_calories += dish.count * dish._dish.fields.calories
    }
    return total_calories
}


const get_send_dishes = ()=>{
    let send_dishs = dishes.map(item=>{
        return {
            count: item.count,
            dish_id: item._dish.pk
        }
    })
    return send_dishs
}


const get_description = ()=>{
    return $("#description").val().trim()
}

const get_limit = ()=>{
    return target_calories
}


const attach_dishes = ()=>{
    for (let d in dishes){
        let dish = dishes[d]
        append_dish_tag(dish._dish, dish.count)
    }
}


const update_current_metric = ()=>{
    let total_calories = get_total_calories()
    $("#curent_calories").html(total_calories + " kcal")
    let percent = ((total_calories/target_calories)*100).toFixed(2) + "%"
    $("#current_calorie_bar").css("width", percent)
    $("#current_calories_percent").html(percent)
}


const update_dish_tag = (_dish)=>{
    $("#dish_count" + _dish._dish.pk).html("x" +_dish.count)
}


const append_dish_tag = (_dish, count)=>{
    let dish_html = single_dish_html
    dish_html = dish_html.replace("#dish_id", _dish.pk)
    dish_html = dish_html.replace("dish_name_value", _dish.fields.dish_name)
    dish_html = dish_html.replace("dish_description_value", _dish.fields.description)
    dish_html = dish_html.replace("dish_ingradients_value", _dish.fields.ingredients)
    dish_html = dish_html.replace("dish_calories_value", _dish.fields.calories)
    dish_html = dish_html.replace("dish_count_value", "x" + (isNaN(count) ? "1" : count))
    dish_html = dish_html.replace("#edit_dish", "edit_dish" + _dish.pk)
    dish_html = dish_html.replace("#remove_dish", "remove_dish" + _dish.pk)
    dish_html = dish_html.replace("#dish_count", "dish_count" + _dish.pk)

    dish_contianer.append(dish_html)
    $("#edit_dish" + _dish.pk).click(function(){
        // console.log($(this).parent().parent().attr("_dish_id"))
    })
    $("#remove_dish" + _dish.pk).click(function(){
        remove_dish($(this).parent().parent().attr("_dish_id"))
    })
}

const remove_dish_tag = (_dish)=>{
    let dish = $("[_dish_id='" + _dish._dish.pk + "']")
    dish.remove()
}


const remove_all_dish = ()=>{
    dishes.length = 0
    dish_contianer.empty()
    update_current_metric()
}


const push_dish = (_dish)=>{
    let new_dish = true
    for (let d in dishes){
        let dish = dishes[d]
        if (dish._dish.pk == _dish.pk) {
            dish.count ++
            update_dish_tag(dish)
            new_dish = false
            break
        }
    }
    if (new_dish){
        dishes.push({
            _dish: _dish,
            count: 1
        })
        append_dish_tag(_dish)
    }
    update_current_metric()
}

const remove_dish = (_dish_id)=>{
    let dish
    for (let d in dishes){
        dish = dishes[d]
        if (dish._dish.pk == _dish_id) {
            dish.count --
            update_dish_tag(dish)
            break
        }
    }
    if (dish.count == 0){
        dishes = dishes.filter((item)=>item._dish.pk != _dish_id)
        remove_dish_tag(dish)
    }
    update_current_metric()
}

const on_dish_selected = (dish_id)=>{
    let remain = target_calories - get_total_calories()

    let dish
    for (let d in temp_dishs){
        dish = temp_dishs[d]
        if (dish.pk == dish_id){
            break
        }
    }
    if (ALLOW_OVER || remain >= dish.fields.calories) {
        push_dish(dish)   
        return {
            valid: true
        }
    }
    
    return {
        valid: false,
        remain: remain
    }
}

const click_on_filter = ()=>{
    let dishes_select = $("#model_list_dish")
    let filter_field = $("#filter_field")
    let field = filter_field.val().trim()
    $.post("/menu/query_filter_dish",
        {
            calo_select: calo_select,
            field: field
        },
        function(data, status){
            let dishes = JSON.parse(data)
            temp_dishs = dishes
            dishes_select.empty()
            for (let d in dishes){
                let dish = dishes[d]
                let dish_html = single_dish_select_html
                dish_html = dish_html.replace("#dish_id", dish.pk)
                dish_html = dish_html.replace("dish_name", dish.fields.dish_name)
                dish_html = dish_html.replace("dish_description", dish.fields.description)
                dish_html = dish_html.replace("dish_gradients", dish.fields.ingredients)
                dish_html = dish_html.replace("dish_calories", "calo " + dish.fields.calories)
                dish_html = dish_html.replace("#dish_select", "dish_select" + d)
                dishes_select.append(dish_html)
                $("#dish_select" + d).click(function(){
                    let selectable = on_dish_selected($(this).attr("dish_id"))
                    if (selectable.valid)
                        $("#model_list").modal("hide")
                    else {
                        alert("Chỉ còn " +  selectable.remain + " calo")
                    }
                })
            }
    });
}


const update_menu = ()=>{
    if (dishes.length == 0){
        alert("Bạn chưa chọn món !")
        return
    }

    let send_dishes = get_send_dishes()
    let description = get_description()
    let limit = get_limit()

    $.post("/menu/update_query", 
        {
            'menu_id': menu_id,
            'dishes': JSON.stringify(send_dishes),
            'description': description,
            'limit': limit
        },
        function(data, status){
            if (status == 'success'){
                toastr.options.onHidden = function() { window.location = data }
                toastr.success("Cập nhật thực đơn thành công, đang chuyển trang...", "Hệ thống")
            }
        }
    )
}


const clone_menu = ()=>{
    if (dishes.length == 0){
        alert("Bạn chưa chọn món !")
        return
    }

    let send_dishes = get_send_dishes()
    let description = get_description()
    let limit = get_limit()

    $.post("/menu/clone_query", 
        {
            'dishes': JSON.stringify(send_dishes),
            'description': description,
            'limit': limit
        },
        function(data, status){
            if (status == 'success'){
                toastr.options.onHidden = function() { window.location = data }
                toastr.success("Sao chép thực đơn thành công, đang chuyển trang...", "Hệ thống")
            }
        }
    )
}


const delete_menu = ()=>{
    $.post("/menu/delete_query", 
        {
            'menu_id': menu_id,
        },
        function(data, status){
            if (status == 'success'){
                toastr.options.onHidden = function() { window.location = data }
                toastr.success("Xóa thực đơn thành công, đang chuyển trang...", "Hệ thống")
            }
        }
    )
}


$(document).ready(()=>{
    // init
    setup_ajax()

    // model display
    btn_show_model = $("#btn_show_model")
    btn_delete_all = $("#btn_delete_all")
    dish_contianer = $("#dish_container")

    btn_show_model.click(click_on_filter)
    btn_delete_all.click(remove_all_dish)

    // model selection
    $("a.dropdown-item").click(function(){
        let calo = $(this).html()
        $("#model_btn_calo_select").html(calo)
        calo_select = $(this).attr("calo_select")
    })

    let model_btn_filter = $("#model_btn_filter")
    model_btn_filter.click(click_on_filter)

    // manage
    let btn_update = $("#btn_update")
    btn_update.click(update_menu)
    let btn_clone = $("#btn_clone")
    btn_clone.click(clone_menu)
    let btn_delete = $("#btn_delete")
    btn_delete.click(delete_menu)

    // init-2
    attach_dishes()
    update_current_metric()
})



// set dishes
dishes = dishes.map((dish, index)=>{
    return {
        count: menus_dishes[index].count,
        _dish: dish
    }
})



// for single dish selection
let single_dish_select_html = 
    "<div class='row p-2 rounded border'>"
        + "<div class='col-1 align-middle'>"
            + "dish_name"
        + "</div>"
        + "<div class='col-3 align-middle'>"
            + "dish_description"
        + "</div>"
        + "<div class='col-5 align-middle'>"
            + "dish_gradients"
        + "</div>"
        + "<div class='col-2 align-middle'>"
            + "dish_calories"
        + "</div>"
        + "<div class='col-1 d-flex flex-row justify-content-around'>"
            + "<input type='button' class='btn btn-primary' value='Chọn' id='#dish_select'  dish_id='#dish_id'>"
            + "</input>"
        + "</div>"
    + "</div>"


// for single dish
let single_dish_html = 
    "<div class='row p-2 bg-light rounded border' _dish_id='#dish_id'>"
        + "<div class='col-sm-2'>"
            + "dish_name_value"
        + "</div>"
        + "<div class='col-sm-2'>"
            + "dish_description_value"
        + "</div>"
        + "<div class='col-sm-5'>"
            + "dish_ingradients_value"
        + "</div>"
        + "<div class='col-sm-1'>"
            + "dish_calories_value"
        + "</div>"
        + "<div class='col-sm-1' id='#dish_count'>"
            + "dish_count_value"
        + "</div>"
        + "<div class='col-sm-1 d-flex flex-row justify-content-around'>"
            // + "<span style='font-size: 18px; color: #5d6366;' id='#edit_dish'>"
            //     + "<i class='fas fa-edit'></i>"
            // + "</span>"
            + "<span style='font-size: 18px; color: #5d6366;' id='#remove_dish'>"
                + "<i class='fas fa-minus-circle'></i>"
            + "</span>"
        + "</div>"
    + "</div>"