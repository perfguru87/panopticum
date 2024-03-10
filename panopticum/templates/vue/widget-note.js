Vue.component('widget-note', {
    props: ['short', ],
    data() {
        return {
            text: null,
        }
    },
    mounted() {
        const slotWrapper = this.$slots.default[0];
        if (slotWrapper.text) this.text = slotWrapper.text;
    },
    methods: {
        replaceLinks(input) {
            let output = this.text;
            const jiraLinks = [];
            const commonLinksRe = /https?:\/\/[^\s]*/g
            const jiraBaseUrl = "{{ JIRA_BASE_URL }}"; // django tempalting. TODO: switch to getting from state manager
            // after migration to vuex
            const urls = input.match(commonLinksRe);
            for (let url of [...new Set(urls)]) {
                if(url.startsWith(jiraBaseUrl)){
                    jiraLinks.push(url);
                    output = output.replace(url, `<widget-jira-ticket jira-ticket-url="${url}" />`)
                } else {
                    output = output.replace(url,`<a href="${url}" class="el-icon-link"></a>`)
                }
            }
            if (this.short && jiraLinks.length) {
                output = jiraLinks.reduce((outputText, url) => `${outputText}<widget-jira-ticket jira-ticket-url="${url}" />`, '')
            }
            return {
                template: `<span>${output}</span>`
            }
        },
    },
    template: `
    {% verbatim %}
    <span>
        <span class="slot-wrapper" v-if="text == null"><slot></slot></span>
        <component :is='replaceLinks(text)' v-if='text'></component>
    </span>
    {% endverbatim %}
    `
})