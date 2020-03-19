Vue.component('app-status', {
    props: [
      'status', 
      'light-icon'
    ],
    computed: {
        classObject: function() {
            return {
                'el-icon-success yes': this.status &&  this.status.id == 3 && this.lightIcon == undefined,
                'el-icon-circle-check yes': this.status && this.status.id == 3 && this.lightIcon != undefined,
                'el-icon-remove no': this.status && this.status.id == 2,
                'unknown': this.status && this.status.id == 4,
                'el-icon-question': !this.status || this.status.id == 1,
            }
        }
    },
    template: `{% verbatim %}
    <span class='panopticum-req-status'>
        <i v-if="status && [3, 2].includes(status.id)" v-bind:class="classObject" ></i>
        <i v-else-if="status && [4].includes(status.id)" v-bind:class="classObject" style="font-size: 12px;">
        N/A
        </i>
        <i v-else class="el-icon-question" style="color: grey;"></i>
    </span>
    {% endverbatim %}`
})
