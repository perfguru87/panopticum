Vue.component('widget-components-list', {
    data: function() {
        return {
            componentVersions: [],
            statuses: [],
            tableData: [],
            requirements: [],
            componentVersionSearch: null,
            statusNames: [],
            componentSorting: '',
            headerFilters: {3: {status: 'no', type: 'signee'}},
        }
    },
    created: async function() {
        this.fetchStatuses();
        const [componentVersions, requirements] = await Promise.all([
            axios.get('/api/component_version/?format=json&ordering=component__name,version').then(resp => resp.data.results),
            axios.get('/api/requirement_set/1/?format=json').then(resp => resp.data.requirements)
        ])
        this.requirements = requirements;
        this.componentVersions = componentVersions;
    },
    watch: {
        componentVersionSearch: 'fetchSearchComponents',
        componentVersions: 'updateTable',
    },

    methods: {

        fetchStatuses() {
            axios.get('/api/status/?format=json&allow_for=1&allow_for=2').then(resp => {
                const statusNames = resp.data.results;
                this.statusNames = {
                    'owner': statusNames.filter(status => status.allow_for.includes('component owner')),
                    'signee': statusNames.filter(status => status.allow_for.includes('requirement reviewer'))
                }
            })
        },
        fetchSearchComponents(queryString) {
            const [componentName, version] = queryString.split(':')
            let queryParams = "";
            if (componentName) queryParams += `&component__name__icontains=${componentName}`;
            if (version) queryParams += `&version=${version}`;
            this.filterComponents(queryParams);
        },
        filterComponents(queryParams) {
            this.cancelSearch();
            this.cancelSource = axios.CancelToken.source();
            axios.get(`/api/component_version/?format=json&ordering=${this.componentSorting}component__name,${this.componentSorting}version${queryParams}`, 
                    {cancelToken: this.cancelSource.token}).then(resp => {
                this.componentVersions = resp.data.results;
                this.cancelSource = null;
            })
        },
        cancelSearch() {
            if (this.cancelSource) {
                this.cancelSource.cancel('Start new search, stop active search');
            }
        },
        handleDropdownCommand(command) {
            let queryParams = `&statuses__status=${command.status.id}&statuses__requirement=${command.requirement.id}&statuses__type=${command.type == 'owner' ? 1 : 2}`
            if (command.status.id == 1) {
                const notUnknownStatusesIds = this.statusNames.owner.filter(s => s.id != 1 ).map(s => s.id);
                queryParams = `&statuses__status__in!=${notUnknownStatusesIds}&statuses__requirement!=${command.requirement.id}&statuses__type!=${command.type == 'owner' ? 1 : 2}`
            }
            let headerFilters = {};
            Object.keys(this.headerFilters).map(key => {headerFilters[key] = null} ); // reset 
            headerFilters[command.requirement.id] = {status: command.status.name, type: command.type};
            this.headerFilters = headerFilters;
            this.filterComponents(queryParams);
        },
        getSigneeClass: function(signeeStatus) { 
            return {
                "signee signee-no el-icon-remove": signeeStatus && signeeStatus.status == 'no',
                "signee signee-yes el-icon-circle-check": signeeStatus && signeeStatus.status == 'yes'
            }
        },
        getOwnerClass: function(ownerStatus) {
            return {
                "owner-status-indicator owner-no": ownerStatus && ownerStatus.status == 'no',
                "owner-status-indicator owner-yes": ownerStatus && ownerStatus.status == 'yes'
            }
        },
        sortComponent: function(a, b) {
            const aName = `${a.name}:${a.version}`
            const bName = `${b.name}:${b.name}`
            return aName < bName ? 1 : -1
        },
        updateTable: async function() {
            const idPattern = new RegExp("^.*/(\\d+)/(?:\\?.+)?$");

            const requirementsIds = this.requirements.map(req => req.id);
            const componentVersionIds = this.componentVersions.map(compVer => compVer.id);
            const statuses = await axios.get(`/api/requirement_status/?format=json&component_version__in=${componentVersionIds.join()}&requirement__in=${requirementsIds.join()}`)
                .then(resp => resp.data.results);
            
            this.statuses = statuses;

            this.tableData = this.componentVersions.map(compVer => { 
                let data = {
                    id: compVer.id, 
                    name: compVer.component.name, 
                    version: compVer.version,
                }
                for (req of this.requirements) {
                    let statuses = this.statuses.filter(status => {
                        return (
                            Number(idPattern.exec(status.requirement)[1]) == req.id && 
                            idPattern.exec(status.component_version)[1] == compVer.id
                        )
                    });
                    data[req.title] = {
                        owner: statuses.find(status => status.type == 'component owner'),
                        signee: statuses.find(status => status.type == 'requirement reviewer')
                    };
                }
                return data;
            });

        }
    },
    template: `{% verbatim %}
<el-card>
    <el-input placeholder="component version" 
    suffix-icon="el-icon-search" 
    v-model="componentVersionSearch"
    style="width:210px; display: inline-block;"
    clearable></el-input>
    <el-table stripe style="width: 100%" 
    :data="tableData"
    empty-text="No data"
    border>
        <el-table-column label="Component" 
        width="200" 
        sortable 
        :sort-method="sortComponent"
        header-align="center" 
        align="center" >
        <template slot-scope="scope">
            <span class="word-wrap">{{ scope.row.name }}:{{ scope.row.version }}</span>
        </template>
        </el-table-column>
        <el-table-column v-for="req in requirements" 
        v-bind:prop="req.title"
        v-bind:label="req.title"
        :key="req.id" 
        align="center">
        
        <template slot="header" slot-scope="scope">
            <el-row>
                <span class="word-wrap">{{ req.title }}</span>
            </el-row>
            <el-row>
                <div style="position: absolute; left:0; bottom: 3px">
                    <el-dropdown trigger="click" @command="handleDropdownCommand">
                        <i class="el-icon-arrow-down" style="font-size: 9px; display: inline-block; margin-left: 0;"></i>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item align="right" 
                            :command="{requirement: req, type: 'owner', status: status}"
                            v-for="status of statusNames.owner" :key="status.id">
                            {{ status.name |capitalize }}<widget-signoff :status="{'status': status.name}"/>
                        </el-dropdown-item>
                        <el-dropdown-item divided align="right" :command="{requrement: req, type: 'owner', status: 'reset'}">
                            Reset<i class="el-icon-circle-close"></i>
                        </el-dropdown-item>
                    </el-dropdown-menu>
                </el-dropdown>
            </div>
            <div style="position: absolute; float: right; right:0; bottom: 3px">
                <el-dropdown trigger="click" placement="bottom-start" @command="handleDropdownCommand">
                    <span>
                        <app-status v-if="headerFilters && headerFilters[req.id] && headerFilters[req.id].type=='signee'" :status='{status: headerFilters[req.id].status}' lightIcon/>
                        <i v-else class="el-icon-arrow-down" style="font-size: 9px; display: inline-block; margin-left: 0"></i>
                    </span>
                    <el-dropdown-menu slot="dropdown">
                        <el-dropdown-item :command="{requirement: req, type: 'signee', status: status}"
                        v-for="status of statusNames.signee" :key="status.id">
                        <app-status :status="{status: status.name}" lightIcon />{{ status.name | capitalize }}
                    </el-dropdown-item>
                    <el-dropdown-item command="reset" divided><i class="el-icon-circle-close"></i>Reset</el-dropdown-item>
                    </el-dropdown-menu>
                </el-dropdown>
                </div>
            </el-row>
    
        </template>
    <template slot-scope="scope">
        <div :class="getOwnerClass(scope.row[req.title].owner)"></div>
        <div :class="getSigneeClass(scope.row[req.title].signee)"></div>
        <div class="inner-cell">
            <span class="word-wrap" v-if="scope.row[req.title].owner && scope.row[req.title].owner.notes && scope.row[req.title].owner.status.name !='n/a'">
            {{ scope.row[req.title].owner.notes }}
        </span>
        <span v-else-if="scope.row[req.title].owner">{{scope.row[req.title].owner.status}}</span>
        <span v-else>Unknown</span>
    </div>
    </template>
</el-table-column>

</el-table-column>
</el-table>
</el-card>{% endverbatim %}
`
})