Vue.component('widget-components-list', {
    props: ['requirementSetId'],
    data: function() {
        return {
            componentVersions: [],
            statuses: [],
            tableData: [],
            requirements: [],
            componentVersionSearch: null,
            statusDefinitions: {},
            componentSorting: '',
            headerFilters: {},
            loading: true,
            products: [],
            locations: [],
            currentProduct: null,
            currentLocation: null
        }
    },
    created: async function() {
        await this.fetchFilters();

        const [requirements, ] = await Promise.all([
            axios.get(`/api/requirement_set/${this.requirementSetId}/?format=json`).then(resp => resp.data.requirements),
            this.fetchStatuses(),
        ])
        this.requirements = requirements;
        await this.filterComponents()
        this.loading = false
    },
    watch: {
        componentVersionSearch: 'fetchSearchComponents',
        componentVersions: 'updateTable',
        currentProduct: 'handleChangeFilter',
        currentLocation: 'handleChangeFilter'
    },

    methods: {
        async fetchFilters() {
            const [products, locations] = await Promise.all([
                axios.get('/api/product_version/?format=json').then(resp => resp.data.results),
                axios.get('/api/location_class/?format=json').then(resp => resp.data.results)
            ])
            const sortFunction = function(a, b) {
                if (a.order < b.order) {
                    return -1;
                }
                else if (a.order > b.order) {
                    return 1
                } else {
                    if (a.name < b.name) return 1
                    else return -1
                }
            }

            this.products = products.sort(sortFunction);
            this.locations = locations.sort(sortFunction);
            this.currentProduct = 4; // hardcode for default 9.0 TODO: make setting per user\group
        },
        fetchStatuses() {
            return axios.get('/api/status/?format=json&allow_for=1&allow_for=2').then(resp => {
                const statuses = resp.data.results;
                this.statusDefinitions = {
                    'owner': statuses.filter(status => status.allow_for.includes('component owner')),
                    'signee': statuses.filter(status => status.allow_for.includes('requirement reviewer'))
                }
            })
        },
        fetchStatusEntryPage(offset) {
            const requirementsIds = this.requirements.map(req => req.id);
            const componentVersionIds = this.componentVersions.map(compVer => compVer.id);
            let url = `/api/requirement_status/?format=json&component_version__in=${componentVersionIds.join()}&requirement__in=${requirementsIds.join()}`
            if (offset) url += `&offset=${offset}`
            return axios.get(url)
                .then(resp => resp.data);
        },
        async fetchStatusEntries() {
            // Statuses count can be > than pagination limits. We should fetch statuses from all pages
            let offset = 0;
            let data;
            do {
                data = await this.fetchStatusEntryPage(offset);
                offset = data.next;
                this.statuses.push(...data.results);
            } while (data.next);
        },
        fetchSearchComponents(queryString) {
            const [componentName, version] = queryString.split(':')
            let queryParams = "";
            if (componentName) queryParams += `&component__name__icontains=${componentName}`;
            if (version) queryParams += `&version=${version}`;
            this.filterComponents(queryParams);
        },
        filterComponents(queryParams='') {
            this.cancelSearch();
            this.loading = true
            this.cancelSource = axios.CancelToken.source();
            queryParams += `&requirement_set=${this.requirementSetId}` + 
                           `&ordering=${this.componentSorting}component__name,${this.componentSorting}version`
            if (this.currentLocation) queryParams += `&deployments__location_class=${this.currentLocation}`
            if (this.currentProduct) queryParams += `&deployments__product_version=${this.currentProduct}`
            return axios.get(`/api/component_version/?format=json${queryParams}`, 
                    {cancelToken: this.cancelSource.token})
                .then(resp => {
                    this.componentVersions = resp.data.results;
                }).catch(err => {
                    if (err.response && err.response.status == 404) {
                        this.componentVersions = [];
                    }
                }).finally(_ => {
                    this.cancelSource = null;
                    this.loading = false
                })
            
        },
        cancelSearch() {
            if (this.cancelSource) {
                this.cancelSource.cancel('Start new search, stop active search');
            }
            loading = false
        },
        handleDropdownCommand(command) {
            let headerFilters = {};
            let queryParams=''
            Object.keys(this.headerFilters).map(key => {headerFilters[key] = null} );
            
            if (command != 'reset') {
                queryParams = `&statuses__status=${command.status.id}&statuses__requirement=${command.requirement.id}&statuses__type=${command.type == 'owner' ? 1 : 2}`
                if (command.status.id == 1) {  // unknown status
                    const notUnknownStatusesIds = this.statusDefinitions.owner.filter(s => s.id != 1 ).map(s => s.id);
                    queryParams = `&exclude_statuses=${notUnknownStatusesIds}&exclude_requirement=${command.requirement.id}&exclude_type=${command.type == 'owner' ? 1 : 2}`
                }
                headerFilters[command.requirement.id] = {status: command.status, type: command.type};
            }
            this.headerFilters = headerFilters;
            this.filterComponents(queryParams);
        },
        getIDfromHref(href) {
            const idPattern = new RegExp("^.*/(\\d+)/(?:\\?.+)?$");
            return Number(idPattern.exec(href)[1]);
        },
        getOwnerClass: function(status) { 
            return {
                "owner owner-no el-icon-remove": status && status.status.id == 2, // TODO: move constant to separated module after migration to webpack 
                "owner owner-yes el-icon-circle-check": status && [3,4].includes(status.status.id)
            }
        },
        getSigneeClass: function(obj) {
            let status = obj.row[obj.column.label];
            if (status == undefined) return;
            status = status.signee
            if (status && status.status.id == 2) return 'signee-no';
            if (status && [3, 4].includes(status.status.id) ) return "signee-yes";
        },
        handleChangeFilter(id) {
            this.filterComponents()
        },
        updateTable: async function() {
            console.log(this.requirements);
            await this.fetchStatusEntries();

            this.tableData = this.componentVersions.map(compVer => { 
                let overal_status = 'unknown';
                const allStatusDefinitions = [...this.statusDefinitions.owner, this.statusDefinitions.signee]
                if (compVer.total_statuses == this.requirements.length) {
                    if (compVer.negative_status_count != 0 && compVer.unknown_status_count == 0) {
                        overal_status = allStatusDefinitions.find(s => s.id == 2); // not ready status
                    } else if (compVer.unknown_status_count == 0 && compVer.negative_status_count == 0) {
                        overal_status = allStatusDefinitions.find(s => s.id == 3); // ready status
                    }
                }

                let data = {
                    id: compVer.id, 
                    name: compVer.component.name, 
                    componentId: compVer.component.id,
                    version: compVer.version,
                    overal_status: overal_status
                }
                for (req of this.requirements) {
                    let statuses = this.statuses.filter(status => {
                        return (
                            this.getIDfromHref(status.requirement) == req.id && 
                            this.getIDfromHref(status.component_version) == compVer.id
                        )
                    }).map(status => {
                        status.status = allStatusDefinitions
                            .find(s => s.id == this.getIDfromHref(status.status));
                        return status;
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
<el-card v-loading="loading" >
    <el-row>
        <div style="display: inline-block">
            <label class="el-form-item__label" for="product">Product</label>
            <el-select v-model="currentProduct" :loading="!products" name='product' placeholder="product" >
                <el-option label="all" :value="null"></el-option>
                <el-option v-for="product in products" 
                    :key="product.id" 
                    :label="product.name" 
                    :value="product.id"></el-option>
            </el-select>
        </div>
        <el-divider direction="vertical"></el-divider>
        <div style="display: inline-block">
            <label class="el-form-item__label" for="location">Location</label>
            <el-select v-model="currentLocation" :loading="!locations" name="location" placeholder="location" >
                <el-option label="all" :value="null"></el-option>
                <el-option v-for="location in locations" 
                    :key="location.id" 
                    :label="location.name" 
                    :value="location.id"></el-option>
            </el-select>
    </div>
    </el-row>
    <el-divider></el-divider>
    <el-row>
        <el-table stripe style="width: 100%" 
        :data="tableData"
        empty-text="No data"
        :cell-class-name="getSigneeClass"
        border>
            <el-table-column label="Component" 
                    width="200" 
                    header-align="center" 
                    align="center" >
                <template slot="header" scope="scope">
                    <span>{{ scope.column.label }}</span>
                    <el-input placeholder="component version" 
                    suffix-icon="el-icon-search" 
                    v-model="componentVersionSearch"
                    style="display: inline-block;"
                    clearable></el-input>
                </template>
                <template slot-scope="scope">
                    <a class="word-wrap" :href="'/component/' + scope.row.componentId">{{ scope.row.name| truncate(50) }}:{{ scope.row.version }}</a>
                </template>
            </el-table-column>

            <el-table-column
                label="Overal status"
                header-align="center"
                width="60"
                align="center"
            >
                <template slot-scope="scope">
                    <span> <app-status :status="scope.row.overal_status"></app-status></span>
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
                                <span>
                                <app-status v-if="headerFilters && headerFilters[req.id] && headerFilters[req.id].type=='owner'" :status='headerFilters[req.id].status' lightIcon/>
                                    <i class="el-icon-arrow-down" style="font-size: 9px; display: inline-block; margin-left: 0;"></i>
                                </span>
                                <el-dropdown-menu slot="dropdown">
                                    <h5 style="margin-right: 20px; text-align: right">Owner filter</h5>
                                    <el-divider></el-divider>
                                    <el-dropdown-item align="right" 
                                    :command="{requirement: req, type: 'owner', status: status}"
                                    v-for="status of statusDefinitions.owner" :key="status.id">
                                        {{ status.name |capitalize }}<app-status :status="status" lightIcon/>
                                    </el-dropdown-item>
                                    <el-dropdown-item divided align="right" command="reset">
                                        Reset<i class="el-icon-circle-close"></i>
                                    </el-dropdown-item>
                                </el-dropdown-menu>
                            </el-dropdown>
                        </div>
                        <div style="position: absolute; float: right; right:0; bottom: 3px">
                            <el-dropdown trigger="click" placement="bottom-start" @command="handleDropdownCommand">
                                <span>
                                    <app-status v-if="headerFilters && headerFilters[req.id] && headerFilters[req.id].type=='signee'" :status='headerFilters[req.id].status' lightIcon/>
                                    <i v-else class="el-icon-arrow-down" style="font-size: 9px; display: inline-block; margin-left: 0"></i>
                                </span>
                                <el-dropdown-menu slot="dropdown">
                                    <h5 style="margin-left: 20px">Signee filter</h5>
                                    <el-divider></el-divider>
                                    <el-dropdown-item :command="{requirement: req, type: 'signee', status: status}"
                                    v-for="status of statusDefinitions.signee" :key="status.id">
                                    <app-status :status="status" lightIcon />{{ status.name | capitalize }}
                                </el-dropdown-item>
                                <el-dropdown-item command="reset" divided><i class="el-icon-circle-close"></i>Reset</el-dropdown-item>
                                </el-dropdown-menu>
                            </el-dropdown>
                        </div>
                    </el-row>
                    
                </template>
                <template slot-scope="scope">
                    <div :class="getOwnerClass(scope.row[req.title].owner)"></div>
                    <div class="inner-cell">
                        <span class="word-wrap" v-if="scope.row[req.title].owner && scope.row[req.title].owner.notes && scope.row[req.title].owner.status.name !='n/a'">
                        {{ scope.row[req.title].owner.notes }}
                        </span>
                        <span v-else-if="scope.row[req.title].owner">{{scope.row[req.title].owner.status.name}}</span>
                        <span v-else>unknown</span>
                    </div>
                </template>
            </el-table-column>

        </el-table>
    </el-row>
</el-card>{% endverbatim %}
`
})