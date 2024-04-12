Vue.component('widget-links', {
  props: {
    // Define the "text" prop expected from the parent
    text: {
      type: String,
      required: true
    }
  },
  computed: {
    linkedText() {
      if (!this || this.text == undefined)
        return '';

      let ret = this.text
        .split(/\s+/) // Split by whitespace
        .map(part => {
          // Basic URL detection (for demonstration; consider more robust methods for production)
          if (part.startsWith('http://') || part.startsWith('https://')) {
            return `<a href="${part}" target="_blank" title='${part}'><i class='fa fa-edit'></i></a>`;
          }
          return part;
        })
        .join(' '); // Rejoin the parts into a single string
      return ret;
    }
  },
  template: `
  {% verbatim %}
        <span v-html="linkedText"></span>
  {% endverbatim %}
  `
})
