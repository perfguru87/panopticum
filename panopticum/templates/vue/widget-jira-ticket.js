Vue.component('widget-jira-ticket', {
    props: [
      'jiraTicketUrl',
    ],
    data() {
        return {
            status: null,
            fixVersion: null,
        }
    },
    created: async function() {
        const issueData = await axios.get(`/api/issue/${this.jiraId}/`).then(resp => resp.data);
        this.status = issueData.status;
        if (issueData.fixVersion.length) {
            this.fixVersion = issueData.fixVersion[0];
        }
    },
    computed: {
        jiraId() {
            const re = /.*\/browse\/(\w{2,}-\d+).*/;
            const match = this.jiraTicketUrl.match(re);
            return match[1];
        },
    },
    methods: {
        getHrefClass() {
            return {
                "closedIssue": status in ['RESOLVED', 'CLOSED']
            }
        }
    },
    template: `
    {% verbatim %}
        <span><a :href="jiraTicketUrl" :class="getHrefClass()">{{ jiraId }}</a><span class="fixVersion" v-if='fixVersion'>{{fixVersion}}</span></span>
    {% endverbatim %}
    `
})