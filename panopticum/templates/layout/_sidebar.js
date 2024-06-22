<script>
/**
 * Resize function without multiple trigger
 *
 * Usage:
 * $(window).smartresize(function(){
 *     // code here
 * });
 */
(function($, sr) {
    // debouncing function from John Hann
    // http://unscriptable.com/index.php/2009/03/20/debouncing-javascript-methods/
    var debounce = function(func, threshold, execAsap) {
        var timeout;

        return function debounced() {
            var obj = this,
                args = arguments;

            function delayed() {
                if (!execAsap)
                    func.apply(obj, args);
                timeout = null;
            }

            if (timeout)
                clearTimeout(timeout);
            else if (execAsap)
                func.apply(obj, args);

            timeout = setTimeout(delayed, threshold || 100);
        };
    };

    // smartresize
    jQuery.fn[sr] = function(fn) {
        return fn ? this.bind('resize', debounce(fn)) : this.trigger(sr);
    };
})(jQuery, 'smartresize');

/**
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

var CURRENT_URL = window.location.href.split('?')[0].split('#')[0],
    $BODY = $('body'),
    $MENU_TOGGLE = $('#menu_toggle'),
    $MENU_TOGGLE_SMALL = $('#menu_toggle_small'),
    $SIDEBAR_MENU = $('#sidebar-menu'),
    $SIDEBAR_FOOTER = $('.sidebar-footer'),
    $SLIDE_DURATION_MS = 10,
    $LEFT_COL = $('.left_col'),
    $RIGHT_COL = $('.right_col'),
    $NAV_MENU = $('.nav_menu'),
    $FOOTER = $('footer');


// Sidebar
function init_sidebar() {
    // TODO: This is some kind of easy fix, maybe we can improve this
    var setContentHeight = function() {
        // reset height
        $RIGHT_COL.css('min-height', $(window).height());

        var bodyHeight = $BODY.outerHeight(),
            footerHeight = $BODY.hasClass('footer_fixed') ? -10 : $FOOTER.height(),
            leftColHeight = $LEFT_COL.eq(1).height() + $SIDEBAR_FOOTER.height(),
            contentHeight = bodyHeight < leftColHeight ? leftColHeight : bodyHeight;

        // normalize content
        contentHeight -= $NAV_MENU.height() + footerHeight;

        $RIGHT_COL.css('min-height', contentHeight);
    };

    $SIDEBAR_MENU.find('a').on('click', function(ev) {
        console.log('clicked - sidebar_menu');
        var $li = $(this).parent();

        var is_new_page = false;
        if ($li.children('ul').length == 0)
            is_new_page = true;

        if (is_new_page)
            $('ul.child_menu li').removeClass('current-page');

        if ($li.hasClass('current-page')) {
            $li.removeClass('current-page');
        }

        if ($li.is('.active')) {
            $li.removeClass('active active-sm current-page');
            $('ul:first', $li).slideUp($SLIDE_DURATION_MS, function() {
                setContentHeight();
            });
        } else {
            // prevent closing menu if we are on child menu
            if (!$li.parent().is('.child_menu')) {
                $SIDEBAR_MENU.find('li').removeClass('active active-sm');
                $SIDEBAR_MENU.find('li ul').slideUp($SLIDE_DURATION_MS);
            } else {
                if ($BODY.is(".nav-sm")) {
                    $SIDEBAR_MENU.find("li").removeClass("active active-sm");
                    $SIDEBAR_MENU.find("li ul").slideUp($SLIDE_DURATION_MS);
                }
            }
            if (is_new_page)
                $li.addClass('current-page');
            else
                $li.addClass('active');

            $('ul:first', $li).slideDown($SLIDE_DURATION_MS, function() {
                setContentHeight();
            });
        }

    });

    menu_toggle_on_click = function(e) {
        console.log('clicked - menu toggle');

        if ($BODY.hasClass('nav-md')) {
            $SIDEBAR_MENU.find('li.active ul').hide();
            $SIDEBAR_MENU.find('li.active').addClass('active-sm').removeClass('active');
        } else {
            $SIDEBAR_MENU.find('li.active-sm ul').show();
            $SIDEBAR_MENU.find('li.active-sm').addClass('active').removeClass('active-sm');
        }

        $BODY.toggleClass('nav-md nav-sm');

        setContentHeight();
    }

    // toggle small or large menu
    $MENU_TOGGLE.on('click', menu_toggle_on_click);
    $MENU_TOGGLE_SMALL.on('click', menu_toggle_on_click);

    // set active menu
    $SIDEBAR_MENU.find('a').filter(function() {
        return this.href === CURRENT_URL || this.href.startsWith(CURRENT_URL + "#") || this.href.startsWith(CURRENT_URL + "?");
    }).parent('li').addClass('current-page').parents('ul').slideDown($SLIDE_DURATION_MS, function() {
        setContentHeight();
    }).parent().addClass('active');

    // recompute content when resizing
    $(window).smartresize(function() {
        setContentHeight();
    });

    setContentHeight();

    // fixed sidebar
    if ($.fn.mCustomScrollbar) {
        $('.menu_fixed').mCustomScrollbar({
            autoHideScrollbar: true,
            theme: 'minimal',
            mouseWheel: { preventDefault: true }
        });
    }
};
// /Sidebar

function vue_components_init() {

    /*
     * vue js code below breaks gentelella menu javascript
     */
    $.getJSON('/api/component/?format=json', function(data) {
        var url = window.location.pathname;
        $.each(data.results, function(key, val) {
            var href = "/component/" + val.id;
            var cl = "";
            if (href == url) {
                cl = "current-page";
                $('#vue-components').closest('li').attr('class', 'active');
                $('#vue-components').css('display', 'block');
            }
            var row= '<li class="' + cl + '"><a href="' + href + '">' + val.name + '</a></li>';
            $('#vue-components').append(row);
        });
    });

/*
    FIXME: this code breaks gentelella menu javascript

    console.log("init vue");
    const app = new Vue({
        el: "#vue-components",
        data: {
            components: [],
            component_versions: [],
        },
        mounted: function () {
            addHandlers(this.$el);
        },
        created () {
            fetch('/api/component/?format=json')
                .then((response) => response.json())
                .then(json => {
                    this.components = json.results
                })
        }
    });
*/
}

$(document).ready(function() {
    init_sidebar();
    $('.menu_placeholder').hide();
    /*
       FIXME: temporary use server side menu rendering to simplify 2nd level menu rendering for components
       vue_components_init();
     */
});
</script>
