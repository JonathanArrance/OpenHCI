$(function () {
    // Call click and mouse events
    $(document).on('click', '#confirm', function (event) {
        event.preventDefault();
        var call = $(this).data("call"),
            notice = $(this).data("notice"),
            async = $(this).data("async"),
            refresh = $(this).data("refresh"),
            buttons = $(this).parent().parent().find('button'),
            load = $.Deferred();
        showMessage('info', notice);
        setModalButtons(false, buttons);
        load = $.getJSON(call)
            .done(function (data) {
                if (data.status == 'error') {
                    showMessage('error', data.message);
                }
                if (data.status == 'success') {
                    showMessage('success', data.message);
                    if (refresh.split(':')[0] == "redirect-to") {
                        refresh = refresh.split(':')[1];
                        window.location.replace(refresh);
                    } else {
                        if (async != "undefined") {
                            closeModal();
                            showLoader($("#page-content"));
                            window.setTimeout(function () {
                                removeLoaders();
                                refreshContainer($("#page-content"), window.loading.current, refresh);
                            }, 2500);
                        }
                    }
                }
            })
            .fail(function () {
                showMessage('error', 'Server Fault');
            })
            .always(function () {
                setModalButtons(true, buttons);
            });

        if (async != "undefined") {
            window[async](load);
        } else {
            closeModal();
            showLoader($("#page-content"));
            window.setTimeout(function () {
                removeLoaders();
                refreshContainer($("#page-content"), window.loading.current, refresh);
            }, 2500);
        }
    });

    $('#refresh-console').click(function (event) {
        event.preventDefault();
        $('.widget-console').attr('src', function (i, val) {
            return val;
        });
    });

    $(document).on("mousemove", function (event) {
        currentMousePosition["x"] = event.pageX;
        currentMousePosition["y"] = event.pageY
    });
});

function showConfirmModal(call) {
    $(".confirm-content").load(call, function () {
        $("#confirm-modal").modal('show');
        removeLoaders();
    });
}

function showInfoModal(page, call) {
    $("#info-modal").modal('show');
    var loader = $('<div class="loading-text"><h1>LOADING <i class="fa fa-cog fa-spin"></i></h1></div>').prependTo(page);
    $(".info-content")
        .empty()
        .append(loader)
        .load(call, function () {
            loader.remove();
        });
}

function closeModal() {
    $(".modal").modal('hide');
}

function setModalButtons(enabled, buttons) {
    if (enabled) {
        buttons.each(function () {
            $(this).button('reset');
            $(this).removeProp("disabled");
            $(this).css("cursor", "pointer");
        });
    } else {
        buttons.each(function () {
            $(this).button('loading');
            $(this).prop("disabled", "disabled");
            $(this).css("cursor", "not-allowed!important");
        });
    }
}

// Async functions loading
window.loading = {
    items: [],
    current: undefined,
    loadFromView: false,
    checkLoading: function () {
        return this.items.length > 0;
    },
    add: function (func) {
        this.items.push(func);
    },
    remove: function (func) {
        if (this.items.indexOf(func) != -1) {
            this.items.splice(this.items.indexOf(func), 1);
        }
    },
    hasItem: function (func) {
        return this.items.indexOf(func) != -1;
    }
};

function loadContent(pageContainer, newContentContainer, url, load) {
    if (window.loading.hasItem(url)) {
        pageContainer.load(url, function () {
            newContentContainer.html(pageContainer.html());
            if (!(load === undefined)) {
                window[load]();
                var checkLoading = window.setInterval(function () {
                    if (!window.loading.hasItem(load)) {
                        $(".loading-text").remove();
                        window.clearInterval(checkLoading);
                        if (window.loading.current != newContentContainer) {
                            pageContainer.html(window.loading.current.html());
                        }
                        window.loading.remove(url);
                    }
                }, 1000);
            }
            else {
                $(".loading-text").remove();
                if (window.loading.current != newContentContainer) {
                    pageContainer.html(window.loading.current.html());
                }
                window.loading.remove(url);
            }
        });
    }
}

function showLoader(container) {
    var loader = $('<div class="loading-text"><h1>LOADING <i class="fa fa-cog fa-spin"></i></h1></div>');
    container.prepend(loader);
}

function removeLoaders() {
    $(".loading-text").remove();
}

function refreshContent(pageContainer, newContentContainer, url, load) {
    pageContainer.load(url, function () {
        newContentContainer.html(pageContainer.html());
        if (!(load === undefined)) {
            window[load]();
            var checkLoading = window.setInterval(function () {
                if (!window.loading.hasItem(load)) {
                    $(".loading-text").remove();
                    window.clearInterval(checkLoading);
                }
            }, 1000);
        }
        else {
            $(".loading-text").remove();
        }
    });
}

function refreshContainer(pageContainer, contentContainer, url, load) {
    if (contentContainer.selector == window.loading.current.selector) {
        var loader = $('<div class="loading-text"><h1>LOADING <i class="fa fa-cog fa-spin"></i></h1></div>');
        pageContainer.prepend(loader);
        contentContainer.load(url, function () {
            if (contentContainer.selector == window.loading.current.selector) {
                pageContainer.html(contentContainer.html());
                if (!(load === undefined)) {
                    window[load]();
                    var checkLoading = window.setInterval(function () {
                        if (!window.loading.hasItem(load)) {
                            $(".loading-text").remove();
                            window.clearInterval(checkLoading);
                        }
                    }, 1000);
                }
                else {
                    $(".loading-text").remove();
                }
            }
        });
    }
}

function stealthRefreshContainer(pageContainer, contentContainer, url, load) {
    if (contentContainer.selector == window.loading.current.selector) {
        contentContainer.load(url, function () {
            if (contentContainer.selector == window.loading.current.selector) {
                pageContainer.html(contentContainer.html());
                if (!(load === undefined)) {
                    window[load]();
                    var checkLoading = window.setInterval(function () {
                        if (!window.loading.hasItem(load)) {
                            $(".loading-text").remove();
                            window.clearInterval(checkLoading);
                        }
                    }, 1000);
                }
                else {
                    $(".loading-text").remove();
                }
            }
        });
    }
}

function switchPageContent(link, pageContainer, oldContentContainer, newContentContainer, funcs, url, load) {
    if (window.loading.current != newContentContainer) {
        oldContentContainer.html(pageContainer.html());
        if (window.loading.hasItem(url)) {
            pageContainer.html(newContentContainer.html());
            switchActiveNav(link);
            window.loading.remove(url);
        } else {
            window.loading.add(url);
            broken = false;
            pageContainer
                .empty()
                .append($('<div class="loading-text"><h1>LOADING <i class="fa fa-cog fa-spin"></i></h1></div>'));
            $(funcs).each(function (index, element) {
                if (window.loading.hasItem(element)) {
                    pageContainer.html(newContentContainer.html());
                    window.loading.remove(url);
                    broken = true;
                    return false;
                }
            });
            if (!broken) {
                loadContent(pageContainer, newContentContainer, url, load);
                switchActiveNav(link);
            }
        }
    }
}

function switchActiveNav(link) {
    $(".nav-sidebar").each(function () {
        pills = $(this).find('li');
        pills.each(function () {
            if ($(this).hasClass('active')) {
                $(this).removeClass('active');
            }
        })
    });
    pill = $(link).parent();
    if (!pill.hasClass('active')) {
        pill.addClass('active');
    }
}

// ---------------- //
// CSRF
// ---------------- //

var csrftoken = getCookie('csrftoken');

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// ---------------- //
// GUID
// ---------------- //

function S4() {
    // Generate a random number string for use in a guid.
    return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
}

function guid() {
    // Generate a guid without the dashes.
    return (S4() + S4() + S4() + "4" + S4().substr(0, 3) + S4() + S4() + S4() + S4()).toLowerCase();
}

// ---------------- //
// UI VALIDATION
// ---------------- //

var standardStringMin = 3;
var standardStringMax = 32;

// ---------------- //
// DOM MANIPULATION
// ---------------- //

var currentMousePosition = {"x": 0, "y": 0};

// --- INSTANCE MANAGEMENT

function startProgressBarUpdate(upload_id) {
    // This function will update the progress bar every second with the progress of the remote upload.
    // The progress is determined by querying the server for the current progress.

    var gProgressIntV = 0,
        bar = $(".upload-bar"),
        percent = $(".upload-percent");

    if (gProgressIntV != 0)
        clearInterval(gProgressIntV);

    gProgressIntV = setInterval(function () {
        $.getJSON("/get_upload_progress/" + upload_id, function (data) {
            if (data.status == "error") {

                // We got an error back so display the message and stop updating the progress bar.
                showMessage("error", data.message);
                clearInterval(gProgressIntV);
                gProgressIntV = 0;
                return;
            }

            if (data.length == -1) {

                percentage = "100%";
                bar.width(percentage);
                percent.html(percentage);
                clearInterval(gProgressIntV);
                gProgressIntV = 0;
                return;
            }

            length = parseInt(data.length);
            if (length > 0)
                var percentage = Math.floor(100 * parseInt(data.uploaded) / length);
            else
                var percentage = 0;

            percentage = percentage + "%";
            bar.css("width", percentage);
            percent.html(percentage);
        });
    }, 1000);
}

function resetProgressBar(form) {
    var bar = form.find('.upload-bar'),
        percent = form.find('.upload-percent');

    var percentage = "0%";
    bar.width(percentage);
    percent.html(percentage);
}

// --- STORAGE

function getStorage(projectId) {
    $.getJSON('/projects/' + projectId + '/get_project_quota/')
        .done(function (data) {
            return data.gigabytes;
        })
}

