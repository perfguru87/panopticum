Vue.component('widget-components-list', {
    props: ['requirementSetId', 'filters', 'topfilters', 'currentPage', 'pageLimit'],
    data: function() {
        return {
            componentVersions: [],
            componentStatuses: {},
            statuses: [],
            tableData: [],
            requirements: [],
            headerFilters: {},
            componentVersionSearch: null,
            statusDefinitions: {},
            componentSorting: '',
            loading: true,
            globalLoading: true,
            products: [],
            locations: [],
            types: [],
            is_new: null,
            currentProduct: null,
            currentLocation: null,
            currentType: null,
        }
    },
    computed: {
        allStatusDefinitions: function() {
            return this.statusDefinitions.all;
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
            this.currentType = this.topfilters.type;
            this.is_new = this.topfilters.is_new;
        }

        if (this.filters && this.filters.length) {
            await this.handleDropdownCommand({
                requirement: {id: Number(this.filters[0].requirement)},
                status: {id: Number(this.filters[0].status)},
                type: this.filters[0].type ? this.filters[0].type : 'component'
            });
        } else {
            await this.filterComponents();
        }
        this.globalLoading = false;
    },
    watch: {
        componentVersionSearch: 'fetchSearchComponents',
        componentVersions: 'updateTable',
        currentProduct: 'handleChangeFilter',
        currentLocation: 'handleChangeFilter',
        currentType: 'handleChangeFilter',
        currentPage: 'handleChangeFilter',
        is_new: 'handleChangeFilter',
        headerFilters: function() {this.$emit('update:header-filters', this.headerFilters)}
    },

    methods: {
        async fetchFilters() {
            // fetch entries from REST API for filters at top page(product, location, type)
            const [products, locations, types] = await Promise.all([
                axios.get('/api/product_version/?format=json').then(resp => resp.data.results),
                axios.get('/api/location_class/?format=json').then(resp => resp.data.results),
                axios.get('/api/component_type/?format=json').then(resp => resp.data.results),
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
            this.types = types.sort(sortFunction);
        },
        fetchStatuses() {
            // fetch statuses to cache
            return axios.get('/api/status/?format=json&allow_for=1&allow_for=2&allow_for=3').then(resp => {
                const statuses = resp.data.results;
                this.statusDefinitions = {
                    'all': statuses,
                    'owner': statuses.filter(status => status.allow_for.includes('component owner')),
                    'signee': statuses.filter(status => status.allow_for.includes('requirement reviewer')),
                    'overall': statuses.filter(status => status.allow_for.includes('overall'))
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
            const currentPage = this.currentPage || 1;
            const pageLimit = this.pageLimit || 30;
            const offset = pageLimit * (currentPage - 1);
            const fields = 'id,version,component,deployments'
            queryParams += `&requirement_set=${this.requirementSetId}` + 
                           `&ordering=${this.componentSorting}component__name,${this.componentSorting}version`
            if (this.currentLocation) queryParams += `&deployments__location_class=${this.currentLocation}`
            if (this.currentProduct) queryParams += `&deployments__product_version=${this.currentProduct}`
            if (this.currentType) queryParams += `&component__type=${this.currentType}`
            if (this.is_new != null) queryParams += `&deployments__is_new_deployment=${this.is_new}`
            return axios.get(`/api/component_version/?format=json&fields=${fields}&limit=${pageLimit}&offset=${offset}${queryParams}`, 
                    {cancelToken: this.cancelSource.token})
                .then(resp => {
                    this.componentVersions = resp.data.results;
                    this.$emit('update:total', resp.data.count);
                }).catch(err => {
                    if (err.response && err.response.status == 404) {
                        this.componentVersions = [];
                    }
                }).finally(_ => {
                    this.cancelSource = null;
                })
            
        },
        cancelSearch() {
            // cancel previous search pending http requiests
            if (this.cancelSource) {
                this.cancelSource.cancel('Start new search, stop active search');
            }
        },
        displayPopover(ownerStatus, signeeStatus) {
            return true;
        },
        handleDropdownCommand(command) {
            // handle change dropdown filters
            let headerFilters = {};
            let queryParams='';
            Object.keys(this.headerFilters).map(key => {headerFilters[key] = null} );
            const unknownOverallQuery = `&unknown_signoff_count!=0`;
            const notReadyOverallQuery = `&negative_signoff_count!=0&unknown_signonff_count=0&max_signoff_count=${this.requirements.length}`;
            const readyOverallQuery = `&unknown_signoff_count=0&negative_signoff_count=0&max_signoff_count=${this.requirements.length}`;

            console.log('command type', command.type);
            if (command != 'reset') {
                if(command.type == 'component') {
                    queryParams = command.status.id == window.REQ_STATUS_READY ? readyOverallQuery : notReadyOverallQuery;
                } else if (command.type == 'overall') {
                    queryParams = `&statuses__status=${command.status.id}&statuses__requirement=${command.requirement.id}&statuses__type=${window.REQ_OVERALL_STATUS}`
                } else {
                    queryParams = `&statuses__status=${command.status.id}&statuses__requirement=${command.requirement.id}&statuses__type=${command.type == 'owner' ? window.REQ_OWNER_STATUS : window.REQ_SIGNEE_STATUS}`
                }
                if (command.status.id == window.REQ_STATUS_UNKNOWN) {  // unknown status
                    if (command.type == 'component') {
                        console.log("OK!");
                        queryParams = unknownOverallQuery;
                    } else {
                        console.log("OOPS!");
                        const notUnknownStatusesIds = this.statusDefinitions.owner.filter(s => s.id != window.REQ_STATUS_UNKNOWN ).map(s => s.id);
                        queryParams = `&exclude_statuses=${notUnknownStatusesIds}&exclude_requirement=${command.requirement.id}&exclude_type=${command.type == 'owner' ? window.REQ_STATUS_UKNOWN : window.REQ_STATUS_NOT_READY }`
                    }
                }

                if (command.type == 'component') {
                    headerFilters['component'] = {status: command.status}
                } else {
                    headerFilters[command.requirement.id] = {status: command.status, type: command.type};
                }
            }
            this.headerFilters = headerFilters;
            return this.filterComponents(queryParams);
        },
        getIDfromHref(href) {
            // parse Hyperlink releative link. For eaxmple: for /api/component_version/1/ will return 1
            const idPattern = new RegExp("^.*/(\\d+)/(?:\\?.+)?$");
            return Number(idPattern.exec(href)[1]);
        },
        getOwnerClass(status) {
            return {
                "owner el-icon-remove": status && status.status.id == window.REQ_STATUS_NOT_READY, // TODO: move constant to separated module after migration to webpack
                "owner el-icon-circle-check": status && [REQ_STATUS_READY,REQ_STATUS_NOT_APPLICABLE].includes(status.status.id)
            }
        },
        getStatusClassForCell(obj) {
            let req = obj.row[obj.column.label];
            if (req == undefined || req.overall == undefined || req.overall.status == undefined)
                return 'status-unknown';
            return this.getStatusClass(req.overall.status.id);
        },
        getStatusClass(status) {
            if (status == undefined)
                return 'status-unknown';
            if (status == window.REQ_STATUS_NOT_READY)
                return 'status-not-ready';
            if (status == window.REQ_STATUS_WAITING_FOR_APPROVAL)
                return 'status-waiting';
            if (status == window.REQ_STATUS_READY)
                return 'status-ready';
            if (status == window.REQ_STATUS_NOT_APPLICABLE)
                return 'status-not-applicable';
            return 'status-unknown';
        },
        getNotes(ownerStatus, signeeStatus, overallStatus) {
            if (overallStatus)
                return overallStatus.notes;
            return "?";
        },
        handleChangeFilter(id) {
            if (this.globalLoading) return;
            this.headerFilters = {};
            this.$emit('update:top-filters', {
                location: this.currentLocation,
                product: this.currentProduct,
                is_new: this.is_new,
                type: this.currentType});
            this.filterComponents();
        },
        getComponentStatus: async function(compVer) {
            return this.componentStatuses[compVer.id];
        },
        isNewDeployment(deployments) { 
            if (!this.currentProduct) return null;
            return deployments.some(deployment => {
              return deployment.product_version.id == this.currentProduct && deployment.is_new_deployment;
            });
        },
        updateTable: async function() {
            await this.fetchStatusEntries();
            this.tableData = this.componentVersions.map(compVer => {

                let data = {
                    id: compVer.id, 
                    name: compVer.component.name, 
                    componentId: compVer.component.id,
                    version: compVer.version,
                    deployments: compVer.deployments,
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
                        signee: statuses.find(status => status.type == 'requirement reviewer'),
                        overall: statuses.find(status => status.type == 'overall')
                    };
                }

                for (req of this.requirements) {
                    if (data[req.title].overall == undefined || data[req.title].overall.status == undefined || data[req.title].overall.status.id == undefined) {
                        if (this.componentStatuses[compVer.id] == undefined) {
                            if (data[req.title].overall && data[req.title].overall.status.id == window.REQ_STATUS_WAITING_FOR_APPROVAL)
                                this.componentStatuses[compVer.id] = { id: window.REQ_STATUS_WAITING_FOR_APPROVAL, type: 'component owner' };
                            else
                                this.componentStatuses[compVer.id] = { id: window.REQ_STATUS_UNKNOWN, type: 'component owner' };
                        }
                        continue;
                    }
                    s = data[req.title].overall.status;
                    sid = data[req.title].overall.status.id;
                    if (sid == window.REQ_STATUS_NOT_READY) {
                        this.componentStatuses[compVer.id] = s;
                        break;
                    }
                    if (sid == window.REQ_STATUS_UNKNOWN)
                        this.componentStatuses[compVer.id] = s;
                    if (sid == window.REQ_STATUS_NOT_APPLICABLE && this.componentStatuses[compVer.id] == undefined)
                        this.componentStatuses[compVer.id] = s;
                    if (sid == window.REQ_STATUS_READY && this.componentStatuses[compVer.id] == undefined)
                        this.componentStatuses[compVer.id] = s;
                    if (sid == window.REQ_STATUS_WAITING_FOR_APPROVAL && this.componentStatuses[compVer.id] != undefined && this.componentStatuses[compVer.id].id != window.REQ_STATUS_UNKNOWN)
                        this.componentStatuses[compVer.id] = s;
                }
                return data;
            });
            this.loading = false;
        }
    },
    template: `{% verbatim %}
<el-card v-loading="loading || globalLoading" >
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
            <label class="el-form-item__label" for="types">Type</label>
            <el-select
            v-model="currentType"
            :loading="!types"
            name="Type"
            placeholder="type"
            style="width: 150px; min-width: 150px"
            clearable>
                <el-option v-for="type in types"
                    :key="type.id"
                    :label="type.name"
                    :value="type.id"></el-option>
            </el-select>
        </div>

        <el-divider direction="vertical"></el-divider>

        <div style="display: inline-block">
            <label class="el-form-item__label" for="new">New</label>
            <el-select
            v-model="is_new"
            :loading="!products"
            name="new"
            placeholder="new"
            :disabled="!currentProduct"
            style="width: 80px; min-width: 80px"
            clearable>
                <el-option key="yes" label="Yes" :value="true"></el-option>
                <el-option key="no" label="No" :value="false"></el-option>
            </el-select>
        </div>
    </el-row>
    <el-divider></el-divider>

    <el-row>
        <el-table stripe style="width: 100%;" 
        :data="tableData"
        empty-text="No data"
        :cell-class-name="getStatusClassForCell"
        border>
            <el-table-column label="Component" 
                    width="200" 
                    header-align="center"
                    align="left" >
                <template slot="header" scope="scope">
                    <span style='height: 15px; margin-bottom: 4px;'>{{ scope.column.label }}</span>
                    <el-input placeholder="" 
                    v-model="componentVersionSearch"
                    class="panopticum-table-input"
                    clearable></el-input>
                </template>
                <template slot-scope="scope">
                    <a class="word-wrap" :href="'/component/' + scope.row.componentId">{{ scope.row.name| truncate(50) }}:{{ scope.row.version }}</a>
                </template>
            </el-table-column>

            <el-table-column
                label="Status"
                v-if="requirements"
                header-align="center"
                width="80"
                align="center">
                <template slot="header">
                    <span class="word-wrap">Status</span>
                    <div>
                            <el-dropdown trigger="click" placement="bottom-start" @command="handleDropdownCommand">
                                <span style='height: 10px; margin: 0px;'>
                                    <app-status v-if="headerFilters && headerFilters['component']" :status='headerFilters["component"].status' lightIcon/>
                                    <i v-else class="el-icon-arrow-down" style="font-size: 9px; display: inline-block; margin-left: 0"></i>
                                </span>
                                <el-dropdown-menu slot="dropdown" class='panopticum-status-right'>
                                    <el-dropdown-item :command="{requirement: null, type: 'component', status: status}"
                                        v-for="status of statusDefinitions.overall" :key="status.id">
                                        <app-status :status="status" lightIcon />{{ status.name | capitalize }}
                                    </el-dropdown-item>
                                    <el-dropdown-item command="reset" divided>
                                        <i class="el-icon-circle-close"></i>Reset
                                    </el-dropdown-item>
                                </el-dropdown-menu>
                            </el-dropdown>
                    </div>
                </template>
                <template slot-scope="scope">
                    <span><app-status :status="componentStatuses[scope.row.id]" lightIcon></app-status></span>
                </template>
            </el-table-column>

            <el-table-column v-for="req in requirements" 
            v-bind:prop="req.title"
            v-bind:label="req.title"
            :key="req.id" 
            align="center">

<!--
        <template slot="header" slot-scope="scope">
              <span>{{ scope.column.label }}</span>
              <el-select
              clearable
              size="mini">
                  <el-option v-for="status in allStatusDefinitions"
                  :key="status.id"
                  :label="status.name"
                  :value="status.id">
                  </el-option>
              </el-select>
        </template>
-->

                <template slot="header" slot-scope="scope">
                    <el-row style='line-height: 1.3em;'>
                        <span class="word-wrap">{{ req.title }}</span>
                    </el-row>


                    <el-row>
                         <!-- owner dropdown filter -->
                        <div style="position: absolute; left:0; bottom: 1px">
                            <el-dropdown trigger="click" @command="handleDropdownCommand">
                                <span>
                                    <app-status v-if="headerFilters && headerFilters[req.id] && headerFilters[req.id].type=='owner'" :status='headerFilters[req.id].status' lightIcon/>
                                    <i v-else class="el-icon-arrow-down" style="font-size: 9px; margin-left: 0;"></i>
                                </span>
                                <el-dropdown-menu slot="dropdown" class='panopticum-status-right'>
                                    <h5 style="margin: 0px 20px; text-align: right">Owner provided status</h5>
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
                        <div style="position: absolute; float: right; right:0; bottom: 1px">
                            <el-dropdown trigger="click" placement="bottom-start" @command="handleDropdownCommand">
                                <span>
                                    <div :class="getStatusClass(headerFilters[req.id].status.id)" v-if="headerFilters && headerFilters[req.id] && headerFilters[req.id].type=='signee'" style="width: 15px; height: 1em; border: 1px solid darkgrey; display: inline-block"></div>
                                    <i v-else class="el-icon-arrow-down" style="font-size: 9px; display: inline-block; margin-left: 0"></i>
                                </span>
                                <el-dropdown-menu slot="dropdown" class='panopticum-status-left'>
                                    <h5 style="margin: 0px 20px;">Signee provided status</h5>
                                    <el-divider></el-divider>
                                    <el-dropdown-item :command="{requirement: req, type: 'signee', status: status}"
                                        v-for="status of statusDefinitions.signee" :key="status.id">
                                        <div :class="getStatusClass(status.id)" style="width: 40px; height: 1em; border: 1px solid darkgrey; display: inline-block"></div>
                                        {{ status.name | capitalize }}
                                    </el-dropdown-item>
                                    <el-dropdown-item command="reset" divided>
                                        <i class="el-icon-circle-close"></i>Reset</el-dropdown-item>
                                </el-dropdown-menu>
                            </el-dropdown>
                        </div>
                    </el-row>
                </template>

                <template slot-scope="scope">
                    <widget-status-popover
                     :owner-status="scope.row[req.title].owner"
                     :signee-status="scope.row[req.title].signee"
                     :overall-status="scope.row[req.title].overall"
                     v-if="displayPopover(scope.row[req.title].owner, scope.row[req.title].signee)">
                            <span class="word-wrap">{{ getNotes(scope.row[req.title].owner, scope.row[req.title].signee, scope.row[req.title].overall) }}</span>
                            </span>
                </widget-status-popover>
                </template>
            </el-table-column>

        </el-table>
    </el-row>
</el-card>{% endverbatim %}
`
})
