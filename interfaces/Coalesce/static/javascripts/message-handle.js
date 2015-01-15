var message_handle = function()
{

    this.defaults = {};
    this.defaults.notice = {text : null, sticky : false, type : 'notice', stayTime: 5000}; //just added
    this.defaults.success = { text : null, sticky : false, type : 'success', stayTime: 5000};
    this.defaults.error  =  { text : null, sticky : true, type : 'error' };  
    this.defaults.warn =    { text : null, sticky : false, type : 'warn', stayTime: 60000};
        
    this.showMessage = function(status, message){

        //if ( 'notice' == status ){
        //    return;
        //}
        
        if ( typeof this.defaults[status] === 'undefined' ){
            console.log('status does not exits ' + status );
            return;
        }

        var messageConfigs = this.defaults[status];
            messageConfigs.text = message;
            
        jQuery().toastmessage('showToast',this.defaults[status]);

    }
    
};

/*
  var message = new message_handle();
               
                message.showMessage('success', 'this is a success 1');
               
                    */