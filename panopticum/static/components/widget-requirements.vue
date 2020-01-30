<template>
    <div>
        <h3 v-cloak>Cloud Requirements
        <span class='pa-component-rating' v-cloak v-if='component_version.op_applicable'>
                {{ component_version.meta_op_rating }}%
        </span>
        <span class='pa-component-stars' v-cloak v-if='component_version.op_applicable'>
                {{ component_version.meta_op_rating }}
        </span>
    </h3>

    <table class='status-table' v-bind:class="[ component_version.op_applicable ? '' : 'status-table-na']" v-cloak>
        <thead>
        <tr>
            <th>Requirement</th>
            <th>Status</th>
            <th>Notes</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="item in component_version.operations" v-bind:key="item.id" v-cloak>
            <td>{{ item.title }}</td>

            <td><widget-signoff v-bind:status="item.status"></widget-signoff></td>
            <td class='pa-replace-urls'>{{ item.notes }}</td>
        </tr>
        </tbody>
    </table>
    </div>
</template>

<script>
module.exports = {
    props: ['component_version', 'apiUrl', 'type'],
    methods: {
        getRequirements: function () {
            return axios.get(`${this.apiUrl}/requirement/?type__name=${this.type}`)
                .then(resp => resp.data.results)
        }
    },
    created: function() {
        this.getRequirements().then(reqs => console.log(reqs));
    }
}
</script>

<style scoped>

</style>