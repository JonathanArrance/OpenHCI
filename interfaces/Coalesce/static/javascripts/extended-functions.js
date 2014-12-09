function disableActions(bool){

    var origActionColor = '#AD682B';
    var disabledActionColor = '#696969';

    if(bool){
        $('.disable-action').bind('click', false);
        $('.disable-action').css('color', disabledActionColor);
    } else {
        $('.disable-action').unbind('click', false);
        $('.disable-action').css('color', origActionColor);
    }
}