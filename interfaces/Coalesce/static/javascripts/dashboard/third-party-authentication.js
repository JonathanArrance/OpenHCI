$(function () {
    // Click Events
    // Configure and update TPA
    $(document).on('click', '.configure-tpa', function (event) {
        event.preventDefault();
        var call = '/third_party_authentication/get_configure/';
        showConfirmModal(call);
    });

    $(document).on('click', '.update-tpa', function (event) {
        event.preventDefault();
        var provider = $(this).data("provider"),
            call = '/third_party_authentication/get_configure/' + provider + '/true/';
        showConfirmModal(call);
    });

    // Create and Delete default projects
    $(document).on('click', '.create-tpa-project', function (event) {
        event.preventDefault();
        var provider = $(this).data("provider"),
            call = '/third_party_authentication/get_build_default_project/' + provider + '/';
        showConfirmModal(call);
    });

    $(document).on('click', '.delete-tpa-project, .remove-tpa', function (event) {
        event.preventDefault();
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = "/third_party_authentication/get/".slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    // Toggle default projects
    $(document).on('click', '.toggle-tpa-project', function (event) {
        event.preventDefault();
        var title = encodeURIComponent($(this).data("title")),
            message = encodeURIComponent($(this).data("message")),
            call = ($(this).data("call")).slashTo47(),
            notice = encodeURIComponent($(this).data("notice")),
            refresh = "/third_party_authentication/get/".slashTo47(),
            async = $(this).data("async");
        showConfirmModal('/get_confirm/' + title + '/' + message + '/' + call + '/' + notice + '/' + refresh + '/' + async + '/');
    });

    // Confirm TPA configuration
    $(document).on('click', '#confirm-configure-tpa', function (event) {
        event.preventDefault();
        var provider = $("#providers").val(),
            inputs,
            name,
            call,
            buttons = $(this).parent().parent().find('button'),
            update = $(this).data("update");

        if (provider == "shib") {
            inputs = {
                "ssoEntityID": $('#sso-entity-id'),
                'mpBackingFilePath': $("#mp-backing-file-path"),
                'mpURI': $("#mp-uri")
            };
            name = "Shibboleth";
            showMessage('info', update == true ? "Updating " + name + " Authentication ..." : "Configuring " + name + " Authentication ...");
            setModalButtons(false, buttons);
            call = '/third_party_authentication/shib/config/' + inputs.ssoEntityID.val().slashTo47() + '/' + inputs.mpBackingFilePath.val().slashTo47() + '/' + inputs.mpURI.val().slashTo47() + '/';
            $.getJSON(call)
                .done(function (data) {
                    if (data.status == 'error') {
                        if (data.message) {
                            showMessage('error', data.message);
                        }
                        setModalButtons(true, buttons);
                    }
                    if (data.status == 'success') {
                        showMessage('success', update == true ? name + " Authentication Updated" : name + " Authentication Configured");
                        setModalButtons(true, buttons);
                        closeModal();
                        refreshContent($("#page-content"), $("#tpa-container"), "/third_party_authentication/get/");
                    }
                })
                .fail(function () {
                    showMessage('error', 'Server Fault');
                    setModalButtons(true, buttons);
                })
        } else if (provider == "ldap") {
            inputs = {
                "Hostname": $('#hostname'),
                'useSSL': $("#use-ssl"),
                'baseDN': $("#base-dn"),
                'uidATTR': $("#uid-attr"),
                'bindingType': $("#binding-type"),
                'managerDN': $("#manager-dn"),
                'managerPW': $("#manager-pw")
            };
            name = "LDAP";
            var hostname = "ldap://".slashTo47() + inputs.Hostname.val().slashTo47();
            if (inputs.bindingType.val() == "anonymous") {
                inputs.managerDN.val("anonymous");
                inputs.managerPW.val("anonymous");
            }
            showMessage('info', update == true ? "Updating " + name + " Authentication ..." : "Configuring " + name + " Authentication ...");
            setModalButtons(false, buttons);
            call = '/third_party_authentication/ldap/config/' + hostname + '/' + inputs.useSSL.val().slashTo47() + '/' + inputs.baseDN.val() + '/' + inputs.uidATTR.val() + '/' + inputs.bindingType.val() + '/' + inputs.managerDN.val() + '/' + inputs.managerPW.val() + '/';
            $.getJSON(call)
                .done(function (data) {
                    if (data.status == 'error') {
                        if (data.message) {
                            showMessage('error', data.message);
                        }
                        setModalButtons(true, buttons);
                    }
                    if (data.status == 'success') {
                        showMessage('success', update == true ? name + " Authentication Updated" : name + " Authentication Configured");
                        setModalButtons(true, buttons);
                        closeModal();
                        refreshContent($("#page-content"), $("#tpa-container"), "/third_party_authentication/get/");
                    }
                })
                .fail(function () {
                    showMessage('error', 'Server Fault');
                    setModalButtons(true, buttons);
                })
        } else if (provider == "other") {
            showMessage("error", "Other authentication systems not currently supported");
        } else {
            showMessage("error", "Cannot determine authentication provider");
        }
    });
});