Vue.component('widget-components-list', {
    props: ['requirementSetId', 'filters', 'topfilters'],
    data: function() {
        return {
            componentVersions: [],
            statuses: [],
            tableData: [],
            requirements: [],
            headerFilters: {},
            componentVersionSearch: null,
            statusDefinitions: {},
            componentSorting: '',
            loading: true,
            products: [],
            locations: [],
            runtimes: [],
            currentProduct: null,
            currentLocation: null,
            currentRuntime: null,
            pageLimit: 30
        }
    },
    computed: {
        allStatusDefinitions: function() {
            return [...this.statusDefinitions.owner, this.statusDefinitions.signee];
        }
    },
    created: async function() {
        await this.fetchFilters();

        const [requirements, ] = await Promise.all([
            axios.get(`/api/requirement_set/${this.requirementSetId}/?format=json`).then(resp => resp.data.requirements),
            this.fetchStatuses(),
        ])
        this.requirements = requirements;
        
        if (this.topfilters) {
            this.currentProduct = this.topfilters.product;
            this.currentLocation = this.topfilters.location;
            this.currentRuntime = this.topfilters.runtime;
        }

        if (this.filters && this.filters.length) {
            this.handleDropdownCommand({
                requirement: {id: Number(this.filters[0].requirement)},
                status: {id: Number(this.filters[0].status)},
                type: this.filters[0].type
            });
        } else {
            await this.filterComponents();
        }
        this.loading = false;
    },
    watch: {
        componentVersionSearch: 'fetchSearchComponents',
        componentVersions: 'updateTable',
        currentProduct: 'handleChangeFilter',
        currentLocation: 'handleChangeFilter',
        currentRuntime: 'handleChangeFilter',
        headerFilters: function() {this.$emit('update:header-filters', this.headerFilters)}
    },

    methods: {
        async fetchFilters() {
            // fetch entries from REST API for filters at top page(product, location, runtime type)
            const [products, locations, runtimes] = await Promise.all([
                axios.get('/api/product_version/?format=json').then(resp => resp.data.results),
                axios.get('/api/location_class/?format=json').then(resp => resp.data.results),
                axios.get('/api/component_runtime_type/?format=json').then(resp => resp.data.results),
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
            this.runtimes = runtimes.sort(sortFunction);
        },
        fetchStatuses() {
            // fetch statuses to cache
            return axios.get('/api/status/?format=json&allow_for=1&allow_for=2').then(resp => {
                const statuses = resp.data.results;
                this.statusDefinitions = {
                    'owner': statuses.filter(status => status.allow_for.includes('component owner')),
                    'signee': statuses.filter(status => status.allow_for.includes('requirement reviewer'))
                }
            })
        },
        fetchStatusEntryPage(offset) {
            // fetch requirement status entries by one page
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
            // filter component versions on changes in component input filter
            const [componentName, version] = queryString.split(':')
            let queryParams = "";
            if (componentName) queryParams += `&component__name__icontains=${componentName}`;
            if (version) queryParams += `&version=${version}`;
            this.filterComponents(queryParams);
        },
        filterComponents(queryParams='') {
            // send REST API request for fetching component versions by queryParam
            this.cancelSearch();
            this.loading = true;
            this.cancelSource = axios.CancelToken.source();
            const fields = 'id,version,component,deployments'
            queryParams += `&requirement_set=${this.requirementSetId}` + 
                           `&ordering=${this.componentSorting}component__name,${this.componentSorting}version`
            if (this.currentLocation) queryParams += `&deployments__location_class=${this.currentLocation}`
            if (this.currentProduct) queryParams += `&deployments__product_version=${this.currentProduct}`
            if (this.currentRuntime) queryParams += `&component__runtime_type=${this.currentRuntime}`
            return axios.get(`/api/component_version/?format=json&limit=${this.pageLimit}&fields=${fields}&${queryParams}`, 
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
            // cancel previous search pending http requiests
            if (this.cancelSource) {
                this.cancelSource.cancel('Start new search, stop active search');
            }
            loading = false
        },
        handleDropdownCommand(command) {
            // handle change dropdown filters
            let headerFilters = {};
            let queryParams='';
            Object.keys(this.headerFilters).map(key => {headerFilters[key] = null} );
            const unknownOveralQuery = `&total_statuses!=${this.requirements.length}`;
            const notReadyOveralQuery = `&negative_status_count!=0&unknown_status_count=0&total_statuses=${this.requirements.length}`;
            const readyOveralQuery = `&unknown_status_count=0&negative_status_count=0&total_statuses=${this.requirements.length}`;
            
            if (command != 'reset') {
                if(command.type == 'overal') {
                    queryParams = command.status.id == 3 ? readyOveralQuery : notReadyOveralQuery;
                } else {
                    queryParams = `&statuses__status=${command.status.id}&statuses__requirement=${command.requirement.id}&statuses__type=${command.type == 'owner' ? 1 : 2}`
                }
                if (command.status.id == 1) {  // unknown status
                    if (command.type == 'overal') {
                        queryParams = unknownOveralQuery;
                    } else {
                        const notUnknownStatusesIds = this.statusDefinitions.owner.filter(s => s.id != 1 ).map(s => s.id);
                        queryParams = `&exclude_statuses=${notUnknownStatusesIds}&exclude_requirement=${command.requirement.id}&exclude_type=${command.type == 'owner' ? 1 : 2}`
                    }
                }

                if (command.type == 'overal') {
                    headerFilters['overal'] = {status: command.status}
                } else {
                    headerFilters[command.requirement.id] = {status: command.status, type: command.type};
                }
            }
            this.headerFilters = headerFilters;
            this.filterComponents(queryParams);
        },
        getIDfromHref(href) {
            // parse Hyperlink releative link. For eaxmple: for /api/component_version/1/ will return 1
            const idPattern = new RegExp("^.*/(\\d+)/(?:\\?.+)?$");
            return Number(idPattern.exec(href)[1]);
        },
        getOwnerClass(status) {
            return {
                "owner el-icon-remove": status && status.status.id == 2, // TODO: move constant to separated module after migration to webpack
                "owner el-icon-circle-check": status && [3,4].includes(status.status.id)
            }
        },
        getSigneeClass(obj) {
            let status = obj.row[obj.column.label];
            if (status == undefined) return;
            status = status.signee
            if (status && status.status.id == 2) return 'signee-no';
            if (status && [3, 4].includes(status.status.id) ) return "signee-yes";
        },
        handleChangeFilter(id) {
            this.headerFilters = {};
            this.$emit('update:top-filters', {
                location: this.currentLocation, 
                product: this.currentProduct, 
                runtime: this.currentRuntime});
            this.filterComponents();
        },
        getOveralStatus(compVer) {
            let overal_status = 'unknown';
            if (compVer.total_statuses == this.requirements.length) {
                if (compVer.negative_status_count != 0 && compVer.unknown_status_count == 0) {
                    overal_status = this.allStatusDefinitions.find(s => s.id == 2); // not ready status
                } else if (compVer.unknown_status_count == 0 && compVer.negative_status_count == 0) {
                    overal_status = this.allStatusDefinitions.find(s => s.id == 3); // ready status
                }
            }
            return overal_status;
        },
        updateTable: async function() {
            await this.fetchStatusEntries();
            this.tableData = this.componentVersions.map(compVer => {

                let data = {
                    id: compVer.id, 
                    name: compVer.component.name, 
                    componentId: compVer.component.id,
                    version: compVer.version,
                    overal_status: this.getOveralStatus(compVer)
                }
                for (req of this.requirements) {
                    let statuses = this.statuses.filter(status => {
                        return (
                            status.requirement &&
                            this.getIDfromHref(status.requirement) == req.id && 
                            this.getIDfromHref(status.component_version) == compVer.id
                        )
                    }).map(status => {
                        status.status = this.allStatusDefinitions
                            .find(s => s.id == (status.status.id ? status.status.id : this.getIDfromHref(status.status)));
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
            <el-select v-model="currentProduct" 
            :loading="!products" name='product' 
            placeholder="product" 
            clearable>
                <el-option v-for="product in products" 
                    :key="product.id" 
                    :label="product.name" 
                    :value="product.id"></el-option>
            </el-select>
        </div>
        <el-divider direction="vertical"></el-divider>

        <div style="display: inline-block">
            <label class="el-form-item__label" for="location">Location</label>
            <el-select v-model="currentLocation" 
            :loading="!locations" 
            name="location" 
            placeholder="location" 
            clearable>
                <el-option v-for="location in locations" 
                    :key="location.id" 
                    :label="location.name" 
                    :value="location.id"></el-option>
            </el-select>
        </div>
        <el-divider direction="vertical"></el-divider>

        <div style="display: inline-block">
            <label class="el-form-item__label" for="runtimes">Runtime type</label>
            <el-select 
            v-model="currentRuntime" 
            :loading="!runtimes" 
            name="Runtime Type" 
            placeholder="runtime type" 
            clearable>
                <el-option v-for="runtime in runtimes"
                    :key="runtime.id"
                    :label="runtime.name"
                    :value="runtime.id"></el-option>
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
                    align="left" >
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
                width="80"
                align="center">
                <template slot="header">
                    <span class="word-wrap">Overal status</span>
                    <div>
                            <el-dropdown trigger="click" placement="bottom-start" @command="handleDropdownCommand">
                                <span>
                                    <app-status v-if="headerFilters && headerFilters['overal']" :status='headerFilters["overal"].status' lightIcon/>
                                    <i v-else class="el-icon-arrow-down" style="font-size: 9px; display: inline-block; margin-left: 0"></i>
                                </span>
                                <el-dropdown-menu slot="dropdown">
                                    <el-dropdown-item :command="{requirement: null, type: 'overal', status: status}"
                                    v-for="status of statusDefinitions.signee" :key="status.id">
                                    <app-status :status="status" lightIcon />{{ status.name | capitalize }}
                                </el-dropdown-item>
                                <el-dropdown-item command="reset" divided><i class="el-icon-circle-close"></i>Reset</el-dropdown-item>
                                </el-dropdown-menu>
                            </el-dropdown>
                    </div>
                </template>
                <template slot-scope="scope">
                    <span><app-status :status="scope.row.overal_status" lightIcon></app-status></span>
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
                         <!-- owner dropdown filter -->
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
                        <!-- signee dropdown filter -->
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
                    </div>
                </template>
            </el-table-column>

        </el-table>
    </el-row>
</el-card>{% endverbatim %}
`
})