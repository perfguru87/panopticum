Vue.component('dashboard-components', {
  props: ['filters'],
  data: function() {
    return {
      tableData: [],
      componentVersions: [],
      categories: [],
      products: [],
      locations: [],
      runtimes: [],
      privacies: [],
      headerFilters: [
        {key: 'component', query: 'component__name__icontains', 'value': null},
        {key: 'componentVersion.version', query: 'version__istartswith', value: null},
        {key: 'component.category.name', query: 'component__category'},
        {key: 'componentVersion.deployments.product_version', query: 'deployments__product_version'},
        {key: 'componentVersion.deployments.location_class', query: 'deployments__location_class'},
        {key: 'component.runtime_type.name', query: 'component__runtime_type'},
        {key: 'component.data_privacy_class.name', query: 'component__data_privacy_class'},
        {key: 'maintainer', query: 'owner_maintainer__username__icontains'}
      ],
      cancelSource: null,
      loading: true
    }
  },
  created: async function() {
    this.debouncedApplyFilters = _.debounce(this.applyFilters, 400)
    const [categories, products, locations, runtimes, privacies] = await Promise.all([
      this.fetchObject('component_category'),
      this.fetchObject('product_version'),
      this.fetchObject('location_class'),
      this.fetchObject('component_runtime_type'),
      this.fetchObject('component_data_privacy_class'),
    ])
    this.categories = categories;
    this.products = products;
    this.locations = locations;
    this.runtimes = runtimes;
    this.privacies = privacies;
    if (this.filters) {
      this.headerFilters = this.filters;
    } else {
      await this.fetchComponentsVersions();
    }
    this.fetchTableData();
  },
  watch: {
    'headerFilters': 'watchFilters',
    'componentVersions': 'fetchTableData',
  },
  methods: {
    cancelSearch() {
      if (this.cancelSource) {
          this.cancelSource.cancel('Start new search, stop active search');
      }
      loading = false
    },
    async fetchComponentsVersions(queryParams) {
      let url = '/api/component_version/?format=json';
      this.cancelSearch();
      this.cancelSource = axios.CancelToken.source();
      let queryString = Object.keys(queryParams || {}).map(k => `${k}=${queryParams[k]}`).join('&');
      if (queryString) url += `&${queryString}`;

      await axios.get(url, {cancelToken: this.cancelSource.token})
        .then(resp => {
          this.componentVersions = resp.data.results;
        }).catch(err => {
          if (err.response && err.response.status == 404) {
              this.componentVersions = [];
          }
        }).finally(_ => {
            this.cancelSource = null;
            this.loading = false;
        })
    },
    async fetchObject(apiObjectName) {
      let offset=0;
      let data;
      let objects = [];
      do {
        data = await axios.get(`/api/${apiObjectName}/?format=json&offset=${offset}`).then(resp => resp.data);
        objects.push(...data.results);
        offset += data.limit;
      } while (data.next);
      return objects;
    },
    
    fetchTableData() {
      this.tableData = this.componentVersions.map(compVer => {
        let row = {
          componentVersion: compVer,
          component: compVer.component
        };
        return row;
      })
    },
    watchFilters() {
      //avoid to frequiency and parallel execution of `applyFilters`
      this.debouncedApplyFilters();
    },
    applyFilters() {
      let queryParams = {};
      this.loading=true;
      this.headerFilters
        .filter(headerFilter => headerFilter.value)
        .map(headerFilter => queryParams[headerFilter.query] = headerFilter.value);
      this.$emit("update:header-filter", this.headerFilters);
      this.fetchComponentsVersions(queryParams);
    }
  },
  template: `{% verbatim %}
<el-card>
  <el-row>
    <el-table :data="tableData"
      style="width: 100%"
      cell-class-name="word-wrap"
      empty-text="No data" 
      v-loading='loading'
      stripe
      >

      <el-table-column
        align="center"
        prop="component"
        label="Component">
        <template slot="header" slot-scope="scope">
          <el-row>
            <span>{{ scope.column.label}}</span>
          </el-row>
          <el-row>
            <el-input clearable 
              v-model="headerFilters.find(i => i.key == scope.column.property).value" 
              size="mini"
              @input="watchFilters()"></el-input>
          </el-row>
        </template>
        <template slot-scope="scope">
          <a :href="'/component/' + scope.row.component.id">{{ scope.row.component.name }}</a>
        </template>
      </el-table-column>

      <el-table-column
        width="100" 
        label="Version"
        prop="componentVersion.version">
        <template slot="header" slot-scope="scope">
          <el-row>
            <span>{{ scope.column.label}}</span>
          </el-row>
          <el-row>
            <el-input clearable 
            v-model="headerFilters.find(i => i.key == scope.column.property).value" 
            size="mini"
            @input="watchFilters()"></el-input>
          </el-row>
        </template>
        <template slot-scope="scope">
          <a>{{ scope.row.componentVersion.version}}</a>
        </template>
      </el-table-column>

      <el-table-column 
        label="Category"
        prop="component.category.name">
          <template slot="header" slot-scope="scope">
              <span>{{ scope.column.label }}</span>
              <el-select v-model="headerFilters.find(i => i.key == scope.column.property).value" 
              @change="watchFilters()"  
              clearable
              size="mini">
                  <el-option v-for="category in categories" 
                  :key="category.id" 
                  :label="category.name" 
                  :value="category.id">
                  </el-option>
              </el-select>
          </template>
      </el-table-column>

      <el-table-column
        prop="componentVersion.deployments.product_version"
        label="Products">
        <template slot="header" slot-scope="scope">
              <span>{{ scope.column.label }}</span>
              <el-select v-model="headerFilters.find(i => i.key == scope.column.property).value" 
              @change="watchFilters()"  
              clearable
              size="mini">
                  <el-option v-for="product in products" 
                  :key="product.id" 
                  :label="product.shortname" 
                  :value="product.id">
                  </el-option>
              </el-select>
          </template>
        <template slot-scope="scope">
          <el-row v-for="deployment in scope.row.componentVersion.deployments" :key="deployment.id">
            <span>{{ deployment.product_version.shortname }}</span>
          </el-row>
        </template>
      </el-table-column>

      <el-table-column 
        prop="componentVersion.deployments.location_class"
        label="Locations">
        <template slot="header" slot-scope="scope">
              <span>{{ scope.column.label }}</span>
              <el-select v-model="headerFilters.find(i => i.key == scope.column.property).value" 
              clearable
              @change="watchFilters()"  
              size="mini">
                  <el-option v-for="location in locations" 
                  :key="location.id" 
                  :label="location.name" 
                  :value="location.id">
                  </el-option>
              </el-select>
        </template>
        <template slot-scope="scope">
          <el-row v-for="deployment in scope.row.componentVersion.deployments" :key="deployment.id">
            <span>{{ deployment.location_class.name }}</span>
          </el-row>
        </template>
      </el-table-column>

      <el-table-column 
        label="Runtime type"
        prop="component.runtime_type.name">
        <template slot="header" slot-scope="scope">
              <span>{{ scope.column.label }}</span>
              <el-select v-model="headerFilters.find(i => i.key == scope.column.property).value" 
              @change="watchFilters()"  
              clearable
              size="mini">
                  <el-option v-for="runtime in runtimes" 
                  :key="runtime.id" 
                  :label="runtime.name" 
                  :value="runtime.id">
                  </el-option>
              </el-select>
        </template>
      </el-table-column>

      <el-table-column 
        label="Data Privacy"
        prop="component.data_privacy_class.name">
        <template slot="header" slot-scope="scope">
              <span>{{ scope.column.label }}</span>
              <el-select v-model="headerFilters.find(i => i.key == scope.column.property).value" 
              @change="watchFilters()"  
              clearable
              size="mini">
                  <el-option v-for="privacy in privacies" 
                  :key="privacy.id" 
                  :label="privacy.name" 
                  :value="privacy.id">
                  </el-option>
              </el-select>
        </template>
      </el-table-column>

      <el-table-column
        prop="maintainer"
        label="Maintainer">
        <template slot="header" slot-scope="scope">
          <el-row>
            <span>{{ scope.column.label}}</span>
          </el-row>
          <el-row>
            <el-input clearable 
              v-model="headerFilters.find(i => i.key == scope.column.property).value" 
              size="mini"
              @input="watchFilters()"></el-input>
          </el-row>
        </template>
        <template slot-scope="scope">
          <a v-if="scope.row.componentVersion.owner_maintainer" :href="'mailto:' + scope.row.componentVersion.owner_maintainer.email">
            {{ scope.row.componentVersion.owner_maintainer.first_name }} {{ scope.row.componentVersion.owner_maintainer.last_name }}
          </a>
        </template>
      </el-table-column>

      <el-table-column
        width="60" 
        label="RAML">
        <template slot-scope="scope">
          <a :href="scope.row.componentVersion.dev_raml" 
          class="el-icon-link" 
          v-if="scope.row.componentVersion.dev_raml && scope.row.componentVersion.dev_raml.startsWith('http')"></a>
        </template>
      </el-table-column>
      <el-table-column 
        width="60" 
        label="Repo">
        <template slot-scope="scope">
          <a :href="scope.row.componentVersion.dev_repo" 
          class="el-icon-link" 
          v-if="scope.row.componentVersion.dev_repo && scope.row.componentVersion.dev_repo.startsWith('http')"></a>
        </template>
      </el-table-column>
      <el-table-column
      width="60" 
        label="JIRA">
        <template slot-scope="scope">
          <a :href="scope.row.componentVersion.dev_jira_component" 
          class="el-icon-link" 
          v-if="scope.row.componentVersion.dev_jira_component && scope.row.componentVersion.dev_jira_component.startsWith('http')"></a>
        </template>
      </el-table-column>
      <el-table-column
        width="60" 
        label="docs">
        <template slot-scope="scope">
          <a :href="scope.row.componentVersion.dev_docs" 
          class="el-icon-link" 
          v-if="scope.row.componentVersion.dev_docs && scope.row.componentVersion.dev_docs.startsWith('http')"></a>
        </template>
      </el-table-column>
      
    </el-table>
  </el-row>
</el-card>
    {% endverbatim %}
`
})