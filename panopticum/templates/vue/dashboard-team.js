Vue.component('dashboard-team', {
    data: function() {
        return {
            filters: {},
            topFilters: {},
            total: 0,
            currentPage: null,
            pageLimit: 30,

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
        pageFilters = this.getFilters('pagination');
        this.currentPage = pageFilters.page || 1;
    },
    watch: {
        currentPage: "onCurrentPageChange"
    },
    methods: {
        onCurrentPageChange(value) {
            let pagination = this.getFilters('pagination');
            pagination.page = value;
            console.log(pagination);
            this.setFilters('pagination', pagination);
        },
        onHeaderFilters(value) {
            const filters = Object.keys(value).filter(k => value[k]).map(k => {return {requirement: k, status: value[k].status.id, type: value[k].type}});
            this.setFilters('filters', filters);
        },
        onUpdateTopFilters(topFilters) {
            this.setFilters('topfilters', topFilters);
        },
        onTotalChange(total) {
            this.total = total;
        },
        getFilters(key) {
            const params = new URLSearchParams(window.location.hash.substr(1));
            let filtersParam = params.get(key);
            filtersParam = filtersParam ? JSON.parse(filtersParam) : {};
            return filtersParam;
        },
        setFilters(key, value, replaceHistory=true) {
            const url = new URL(window.location);
            const originalHash = url.hash;
            const params = new URLSearchParams(originalHash.substr(1));
            params.set(key, JSON.stringify(value));
            url.hash = "#" + params.toString();
            if (replaceHistory) {
                history.replaceState(null, '', url.href);
            } else {
                history.pushState(null, '', url.href);
            }
        },
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
        <div class="col-sm-12 table-team-dashboard" id="vue-component">
            <widget-components-list 
            :requirement-set-id="requirementSetId"
             v-on:update:header-filters="onHeaderFilters" 
             v-on:update:top-filters="onUpdateTopFilters"
             v-on:update:total="onTotalChange"
             :topfilters="topFilters"
             :currentPage="currentPage"
             :filters="filters"></widget-components-list>
        </div>
    </div>
    <el-row>
    <el-pagination
      :hide-on-single-page="true"
      layout="prev, pager, next"
      v-bind:currentPage.sync="currentPage"
      :page-size="pageLimit"
      :total="total"
      >
    </el-pagination>
    </el-row>
</div>
{% endverbatim %}`
})
