<template>
    <div>
        <h3 v-cloak>Cloud Requirements
        <span class='pa-component-rating' v-cloak v-if='component.latest_version.op_applicable'>
                {{ component_version.meta_op_rating }}%
        </span>
        <span class='pa-component-stars' v-cloak v-if='component.latest_version.op_applicable'>
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
        <tr v-for="item in component_version.operations" v-bind:key="item" v-cloak>
            <td>{{ item.title }}</td>

            <td><widget-signoff v-bind:status="item.status"/></td>
            <td class='pa-replace-urls'>{{ item.notes }}</td>
        </tr>
        </tbody>
    </table>
    </div>
</template>

<script>
export default {
    props: ['component_version'],
    created: function () {
        api.getRequirements(component_version, 'cloud');
    }
}
</script>

<style scoped>

</style>