function get_employee_category_id() {
    NProgress.start();
    var category_id = null;
    $.ajax({
        async: false,
        url: "/api/usercategory-list/?category=employee",
        type: 'GET',
        dataType: 'json',
        headers: { "Authorization": localStorage.getItem("token") }
    }).done(function (response, status, request) {
        NProgress.done();
        category_id = response['data'][0]['id'];
        // console.log(category_id);
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        }
    });
    return category_id;
}
function get_employee_id(category_id) {
    var employee_id = null;
    NProgress.start();
    $.ajax({
        async: false,
        url: "/api/get-user-initial-data/?category_id=" + category_id,
        type: 'GET',
        dataType: 'json',
        headers: { "Authorization": localStorage.getItem("token") }
    }).done(function (response, status, request) {
        NProgress.done();
        employee_id = response['user']['employee_id'];
        // console.log(employee_id);
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        }

    });
    return employee_id;
}
function get_employee_role_id(employee_id) {
    var employee_role_id = null;
    NProgress.start();
    $.ajax({
        async: false,
        url: "/api/employee-roles-mapping-list/?employee_id=" + employee_id,
        type: 'GET',
        dataType: 'json',
        headers: { "Authorization": localStorage.getItem("token") }
    }).done(function (response, status, request) {
        console.log(response)
        NProgress.done();
        employee_role_id = response['data'][0]['employee_role']['id'];
        //  console.log(employee_role_id);
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        }
    });
    return employee_role_id;
}
function get_employee_functionalities(employee_role_id) {
    var employee_functionalities = null;
    NProgress.start();
    $.ajax({
        async: false,
        url: "/api/employee-roles-functionalities-mapping-list/?employee_role_id=" + employee_role_id,
        type: 'GET',
        dataType: 'json',
        headers: { "Authorization": localStorage.getItem("token") }
    }).done(function (response, status, request) {
        NProgress.done();
        employee_functionalities = response['data'];
        // console.log(employee_functionalities);
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        }
    });
    return employee_functionalities;
}

function get_employee_all_functionalities() {
    var employee_functionalities = null;
    NProgress.start();
    $.ajax({
        async: false,
        url: "/api/get-user-initial-td-functionalities-data/?category=employee",
        type: 'GET',
        dataType: 'json',
        headers: { "Authorization": localStorage.getItem("token") }
    }).done(function (response, status, request) {
        NProgress.done();
        //get employee roles
        if (response.data.length > 0) {
            var emp_roles = [];
            for (var i = 0; i < response.data.length; i++) {
                if ((jQuery.inArray(response.data[i].employee_role.role, emp_roles)) == -1) {
                    emp_roles.push(response.data[i].employee_role.role);
                }
            }
            window.localStorage.setItem("emp_roles", emp_roles);
            var emp_role = localStorage.getItem('emp_roles');
            if (emp_role.includes("Technology") || emp_role.includes("Management") || emp_role.includes("City Head")) {
                $(".monitoring").show();
            }
            //  if (emp_role.includes("Technology") || emp_role.includes("Management")) {
            //     $(".taskStatusLi").show();
            //   }
        }
        employee_functionalities = response['data'];
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        }
    });
    var web_functionalities = [];
    for (var i = 0; i < employee_functionalities.length; i++) {
        var obj = employee_functionalities[i];
        if(obj.td_functionality.consumer === 'web'){
            web_functionalities.push(obj);
        }
    }
    return web_functionalities;
}