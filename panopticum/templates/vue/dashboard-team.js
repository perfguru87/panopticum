Vue.component('dashboard-team', {
    data: function() {
        return {
            filters: {},
            topFilters: {}
        }
    },
    computed: {
        requirementSetId: function() {
            const searchParams = new URLSearchParams(window.location.search);
            return searchParams.get('requirementset');
        },
        team: function() {
            // dashboard title hardcoded until dashboard settings will be implemented
            const reqTitleMap = [
                {requirementset: 1, title: 'Operations'},
                {requirementset: 2, title: 'Maintenance'},
                {requirementset: 3, title: 'Compliance'}
            ]
            return reqTitleMap.find(item => item.requirementset == this.requirementSetId).title
        }
    },
    created: function() {
        this.filters = this.getFilters('filters');
        this.topFilters = this.getFilters('topfilters');
    },
    methods: {
        onHeaderFilters(value) {
            const filters = Object.keys(value).filter(k => value[k]).map(k => {return {requirement: k, status: value[k].status.id, type: value[k].type}});
            this.setFilters('filters', filters);
        },
        onUpdateTopFilters(topFilters) {
            this.setFilters('topfilters', topFilters);
        },
        getFilters(key) {
            const params = new URLSearchParams(window.location.hash.substr(1));
            let filtersParam = params.get(key);
            filtersParam = filtersParam ? JSON.parse(filtersParam) : [];
            return filtersParam;
        },
        setFilters(key, value) {
            const url = new URL(window.location);
            const originalHash = url.hash;
            const params = new URLSearchParams(originalHash.substr(1));
            params.set(key, JSON.stringify(value));
            url.hash = "#" + params.toString();
            history.pushState(null, '', url.href);
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
            <widget-components-list 
            :requirement-set-id="requirementSetId"
             v-on:update:header-filters="onHeaderFilters" 
             v-on:update:top-filters="onUpdateTopFilters"
             :topfilters="topFilters"
             :filters="filters"></widget-components-list>
        </div>
    </div>
</div>
{% endverbatim %}`
})