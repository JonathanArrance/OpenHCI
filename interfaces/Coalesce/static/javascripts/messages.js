function Toast(type, msg) {
    this.type = type;
    this.msg = msg;
}

toastr.options.positionClass = 'toast-top-right';
toastr.options.extendedTimeOut = 0; //1000;
toastr.options.timeOut = 5000;
toastr.options.fadeOut = 250;
toastr.options.fadeIn = 250;
toastr.options.preventDuplicates = true;

function showMessage(type, msg, params) {

    toastr.options.timeOut = type == 'error' ? 10000 : toastr.options.timeOut;
    toastr.options.progressBar = true;

    if (params != undefined) {
        toastr.options.positionClass = params.positionClass == undefined ? toastr.options.positionClass : params.positionClass;
        toastr.options.extendedTimeOut = params.extendedTimeOut == undefined ? toastr.options.extendedTimeOut : params.extendedTimeOut;
        toastr.options.timeOut = params.timeOut == undefined ? toastr.options.timeOut : params.timeOut;
        toastr.options.fadeOut = params.fadeOut == undefined ? toastr.options.fadeOut : params.fadeOut;
        toastr.options.fadeIn = params.fadeIn == undefined ? toastr.options.fadeIn : params.fadeIn;
    }

    toast = new Toast(type, msg);
    toastr[toast.type](toast.msg);
}