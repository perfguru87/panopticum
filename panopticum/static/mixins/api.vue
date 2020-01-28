<script>
export default {
    data: {
        api: axios.create({
                baseURL: 'http://127.0.0.1:8000/api/',
                timeout: 5000,
                headers: {
                    'Content-Type': 'application/json'
                }
        })
    },
    methods: {
        getRequirements (componentVersionId, type) {
            myApi.get(`requirements?component_version=${componentVersionId}&type=${type}`)
            .then(response =>  response.json())
            .then(json => json.results)
        }
    }
}
</script>