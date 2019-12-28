(function($) {
    var class_name = "input[name$='_applicable']";

    function toggle_applicable(checkbox) {
        var checked = $(checkbox).prop("checked");
        $(checkbox).closest('fieldset').find('.form-row').each(function(index, el) {
            if ($(el).find(class_name).length)
                return;
            if (checked)
                $(el).show();
            else
                $(el).hide();
        });
    }

    $(function() {
        $(class_name).each(function(index, toggle) {
            toggle_applicable(toggle);
            $(toggle).change(function() {
                 toggle_applicable(toggle);
            });
        });
    });
})(django.jQuery);
