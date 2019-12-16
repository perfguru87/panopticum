<script>
function vue_components_init() {

    /*
     * vue js code below breaks gentelella menu javascript
     */
    console.log('pre-populate components menu');
    $.getJSON('/api/component/?format=json', function(data) {
        console.log('populate components menu');
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
    vue_components_init();
});
</script>
