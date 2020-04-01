Vue.component('dashboard-components', {
  props: ['filters'],
  data: function() {
    return {
      tableData: [],
      componentVersions: [],
      categories: [],
      products: [],
      locations: [],
      types: [],
      privacies: [],
      headerFilters: [
        {key: 'component', query: 'component__name__icontains', 'value': null},
        {key: 'componentVersion.version', query: 'version__istartswith', value: null},
        {key: 'component.category.name', query: 'component__category'},
        {key: 'product_version', query: 'deployments__product_version'},
        {key: 'componentVersion.deployments.location_class', query: 'deployments__location_class'},
        {key: 'component.type.name', query: 'component__type'},
        {key: 'component.data_privacy_class.name', query: 'component__data_privacy_class'},
        {key: 'maintainer', query: 'owner_maintainer__username__icontains'},
        {key: 'componentVersion.deployments.is_new_deployment', query: 'deployments__is_new_deployment'}
      ],
      cancelSource: null,
      loading: true,
      currentPage:1,
      total: 0,
      pageLimit: 30
    }
  },
  created: async function() {
    this.debouncedApplyFilters = _.debounce(this.applyFilters, 400)
    const [categories, products, locations, types, privacies] = await Promise.all([
      this.fetchObject('component_category'),
      this.fetchObject('product_version'),
      this.fetchObject('location_class'),
      this.fetchObject('component_type'),
      this.fetchObject('component_data_privacy_class'),
    ])
    this.categories = categories;
    this.products = products;
    this.locations = locations;
    this.types = types;
    this.privacies = privacies;
    if (this.filters && this.filters.length) {
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
  computed: {
    currentProduct() {
      const headerFilter = this.headerFilters.find(filter => filter.key == 'product_version');
      if (headerFilter) {
        return this.products.find(p => p.id == headerFilter.value);
      } else {
        return null;
      }
    },

  },
  methods: {
    cancelSearch() {
      if (this.cancelSource) {
          this.cancelSource.cancel('Start new search, stop active search');
      }
      loading = false
    },
    async fetchComponentsVersions(queryParams) {
      const offset = (this.currentPage - 1) * this.pageLimit;
      const fields = 'id,owner_maintainer,version,component,deployments,dev_raml,dev_repo,dev_jira_component,dev_docs'
      let url = `/api/component_version/?format=json&ordering=component__name&limit=${this.pageLimit}&offset=${offset}&fields=${fields}`;
      this.cancelSearch();
      this.cancelSource = axios.CancelToken.source();
      let queryString = Object.keys(queryParams || {}).map(k => `${k}=${queryParams[k]}`).join('&');
      if (queryString) url += `&${queryString}`;

      await axios.get(url, {cancelToken: this.cancelSource.token})
        .then(resp => {
          this.componentVersions = resp.data.results;
          this.total = resp.data.count;
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
        .filter(headerFilter => headerFilter.value != null)
        .map(headerFilter => queryParams[headerFilter.query] = headerFilter.value);
      this.$emit("update:header-filter", this.headerFilters);
      this.fetchComponentsVersions(queryParams);
    },
    isNewDeployment(deployments) { 
      if (!this.currentProduct) return null;
      return deployments.some(deployment => {
        return deployment.product_version.id == this.currentProduct.id && deployment.is_new_deployment;
      });
    },
    onCurrentPageChange() {
      this.applyFilters();
    },
  },
  template: `{% verbatim %}
<el-card>
  <el-row>
    <div style="display: inline-block">
              <label class="el-form-item__label" for="product">Product</label>
              <el-select v-model="headerFilters.find(i => i.key == 'product_version').value"
              :loading="!products" 
              name='product'
              placeholder="product"
              @change="watchFilters()" 
              clearable>
                  <el-option v-for="product in products" 
                      :key="product.id" 
                      :label="product.name" 
                      :value="product.id"></el-option>
              </el-select>
    </div>
  </el-row>
  <el-row>
    <el-table :data="tableData"
      style="width: 100%"
      cell-class-name="word-wrap"
      empty-text="No data" 
      v-loading='loading'
      stripe
      >

      <el-table-column
        align="left"
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
        label="Type"
        prop="component.type.name">
        <template slot="header" slot-scope="scope">
              <span>{{ scope.column.label }}</span>
              <el-select v-model="headerFilters.find(i => i.key == scope.column.property).value" 
              @change="watchFilters()"  
              clearable
              size="mini">
                  <el-option v-for="type in types"
                  :key="type.id"
                  :label="type.name"
                  :value="type.id">
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
        prop="componentVersion.deployments.is_new_deployment"
        align="center"
        width="80px"
        label="New">
        <template slot="header" slot-scope="scope">
          <el-row>
            <span>{{ scope.column.label }}</span>
          </el-row>
          <el-row>
            <el-select v-model="headerFilters.find(i => i.key == scope.column.property).value" 
            clearable
            size="mini"
            placeholder=""
            :disabled="!currentProduct"
            @change="watchFilters()">
              <el-option key="yes" label="Yes" :value="true"></el-option>
              <el-option key="no" label="No" :value="false"></el-option>
            </el-select>
          </el-row>
        </template>
        <template slot-scope="scope">
          <span
          class="el-icon-circle-check"
          v-if="isNewDeployment(scope.row.componentVersion.deployments)"></span>
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
  <el-row>
    <el-pagination
      v-show='!loading'
      :hide-on-single-page="true"
      layout="prev, pager, next"
      v-bind:currentPage.sync="currentPage"
      :page-size="pageLimit"
      @current-change="onCurrentPageChange()"
      :total="total">
    </el-pagination>
  </el-row>
</el-card>
    {% endverbatim %}
`
})
