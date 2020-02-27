Vue.component('dashboard-team', {
    data: function() {
        return {
            team: 'Operations',
            requirementSetId: 1,
            filters: {}
        }
    },
    created: function() {
        this.filters = this.convertFilters(window.location.hash);
    },
    methods: {
        onHeaderFilters(value) {
            const filters = Object.keys(value).filter(k => value[k]).map(k => {return {requirement: k, status: value[k].status.id, type: value[k].type}});
            let url = new URL(window.location);
            url.hash = `#filters=${JSON.stringify(filters)}`;
            history.pushState(null, '', url.href);
        },
        convertFilters(urlHash) {
            const params = new URLSearchParams(urlHash.substr(1));
            let filtersParam = params.get('filters');
            filtersParam = filtersParam ? JSON.parse(filtersParam) : [];
            return filtersParam;
        }
    },
    template:`{% verbatim %}
<div>


    <div class="row title_left">
        <div class="col-sm-12">
            <h3>{{ team }} dashboard</h3>
        </div>
    </div>

    <div class="row">
        <div class="col-sm-12"><hr></div>
    </div>
    <div class="row">
        <div class="col-sm-12" id="vue-component">
            <widget-components-list :requirement-set-id="requirementSetId" v-on:update:header-filters="onHeaderFilters" :filters="filters"></widget-components-list>
        </div>
    </div>
</div>
{% endverbatim %}`
})