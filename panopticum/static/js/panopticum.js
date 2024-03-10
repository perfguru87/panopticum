/* FIXME: these values are hardcoded here and on backend side */
window.REQ_STATUS_UNKNOWN = 1;
window.REQ_STATUS_NOT_READY = 2;
window.REQ_STATUS_READY = 3;
window.REQ_STATUS_NOT_APPLICABLE = 4;
window.REQ_STATUS_WAITING_FOR_APPROVAL = 5;
window.REQ_OWNER_STATUS = 1;
window.REQ_SIGNEE_STATUS = 2;
window.REQ_OVERALL_STATUS = 3;

if (!String.prototype.pa_format) {
    String.prototype.pa_format = function() {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number) {
            var n = parseInt(number);
            return typeof args[n] != 'undefined' ? args[n] : '';
    });
  };
}

function reverse_string(str) {
    return str.split('').reduce((reversed, character) => character + reversed, '');
}

function meta_searchstr_wrap(s) {
    if (s)
        return "{" + s + "}";
    return s;
}

function meta_searchstr_unwrap(s) {
    if (!s)
        return "";
    return s.replace(/{/g, "").replace(/}/g, "");
}

class Refcounter {
    constructor(callback) {
        this.counter = 0;
        this.callback = callback;
    }

    inc() {
        this.counter++;
    }

    dec() {
        this.counter--;
        if (!this.counter)
            this.callback();
    }
}

/*
 * Tooltips
 */
function pa_tooltip(el) {
    $(el).tooltip({ 'container': 'body', 'html': true });
}

function pa_tooltip_from_list(title, str) {
    if (!str)
        return "";
    str = str.replace(/\, /g, '<br>- ');
    str = str.replace(/\,/g, '<br>- ');
    if (title && str)
        return title + '<br>- ' + str;
    return title + str;
}

function pa_tooltip_jira_issue(jira_issue) {
    var key = jira_issue.key;
    var summary = jira_issue.fields.summary;
    var status = jira_issue.fields.status.name;
    var created = new Date(jira_issue.fields.created);
    var assignee = jira_issue.fields.assignee.name;
    var priority = "<img src='{0}'></img>".pa_format(jira_issue.fields.priority.iconUrl);
    var issuetype = "<img src='{0}'></img>".pa_format(jira_issue.fields.issuetype.iconUrl);
    var fixversionstr = jira_issue.fields.fixVersionsStr;

    return " <h1>{0} {1} {2}</h1>".pa_format(issuetype, priority, summary) +
           " <span>key:</span>{0}".pa_format(key) +
           " <br><span>status:</span>{0}".pa_format(status) +
           " <br><span>created:</span>{0}".pa_format(created.toISOString().slice(0, 10)) +
           " <br><span>assignee:</span>{0}".pa_format(assignee) +
           " <br><span>fixver:</span>{0}".pa_format(fixversionstr);
}

/*
 * pa_replace_urls() and friends
 */

function _pa_draw_jira_issue_link(el, jira_url, jira_issue) {
    var key = jira_issue.key;
    var resolved = jira_issue.fields.resolution;
    var class_name = resolved ? "jira-issue-resolved" : "jira-issue-unresolved";
    var fixversionstr = jira_issue.fields.fixVersionsStr;

    t = $(el).html();
    t = t.replace(new RegExp(key, 'g'),
                  "<a class='{0}' ".pa_format(class_name) +
                  " target=_blank" +
                  " id='jira-{0}'".pa_format(key) +
                  " title=\"" + pa_tooltip_jira_issue(jira_issue) + "\"" +
                  " href='{0}browse/{1}'>{1} <span>{2}</span></a>".pa_format(jira_url, key, fixversionstr));

    $(el).html(t);

    pa_tooltip("#jira-" + key);
}

function _pa_replace_jira_ids(el, jira_url, text) {
    if (jira_url == '' || jira_url == undefined)
        return;

    /* https://stackoverflow.com/questions/19322669/regular-expression-for-a-jira-identifier/30518972#30518972 */
    var jira_matcher = /\d+-[A-Z]+(?!-?[a-zA-Z]{1,10})/g

    r_text = reverse_string(text);
    var m = r_text.match(jira_matcher);

    if (m == null)
        return;

    for (var i = 0; i < m.length; i++) {
        key = reverse_string(m[i]);

        console.log("jira issue: " + key);
        $.getJSON('/api/jira/' + key + '?format=json', function (data) {
            _pa_draw_jira_issue_link(el, jira_url, data.results);
        });
    }
}

function _pa_replace_urls_in_text(el, jira_url, text) {
    var re = /((http|https|ftp):\/\/[\w?=&.\/-;#~%-+-]+(?![\w\s?&.\/;#~%"=]*>))/g
    text = text.replace(re,"<a href='$1' target=_blank><i class='fa fa-external-link'></i></a>");
    $(el).html(text);

    _pa_replace_jira_ids(el, jira_url, text);
}

function pa_replace_urls() {
    $.getJSON('/api/jira_url/?format=json', function (data) {
        var jira_url = data.response.jira_url;
        $(".pa-replace-urls").each(function(index, el) {
            _pa_replace_urls_in_text(el, jira_url, $(el).html());
        });
    });
}

/*
 * Options
 */
function pa_no_partial_yes(str) {
    if (str == "unknown")
        return "<i class='unknown fa fa-question-circle'></i>";
    if (str == "no")
        return "<span class='no'>NO</span>";
    if (str == "partial")
        return "<span class='some'>Some</span>";
    if (str == "yes")
        return "<span class='yes'>YES</span>";
    return str;
}

function pa_get_no_partial_yes_select(id) {
    return "<select class='update-table' id='{0}'>".pa_format(id) +
           "<option selected='true'></option>" +
           "<option value='unknown'>?</option>" +
           "<option value='no'>No</option>" +
           "<option value='partial'>Some</option>" +
           "<option value='yes'>Yes</option>" +
           "</select>";
}

function pa_star_rating(str) {
    if (str == "unknown")
        return "<i class='unknown fa fa-question-circle'></i>";
    if (str == "none")
        return "<i class='fa fa-star-o'></i><i class='fa fa-star-o'></i><i class='fa fa-star-o'></i>";
    if (str == "low")
        return "<i class='fa fa-star'></i><i class='fa fa-star-o'></i><i class='fa fa-star-o'></i>";
    if (str == "med")
        return "<i class='fa fa-star'></i><i class='fa fa-star'></i><i class='fa fa-star-o'></i>";
    if (str == "high")
        return "<i class='fa fa-star'></i><i class='fa fa-star'></i><i class='fa fa-star'></i>";
    return str;
}

function pa_get_star_rating_select(id) {
    return "<select class='update-table' id='{0}'>".pa_format(id) +
           "<option selected='true'></option>" +
           "<option value='unknown'>?</option>" +
           "<option value='none'>None</option>" +
           "<option value='low'>Low</option>" +
           "<option value='med'>Med</option>" +
           "<option value='high'>High</option>" +
           "</select>";
}

function pa_populate_options(refc, id, url, first_is_empty) {
    let dropdown = $(id);

    refc.inc();

    dropdown.empty();
    if (first_is_empty)
        dropdown.append('<option selected="true"></option>');
    dropdown.prop('selectedIndex', 0);

    $.getJSON(url, function (data) {
        $.each(data.results, function (key, entry) {
            dropdown.append($('<option></option>').attr('value', entry.id).text(entry.name));
        })
        refc.dec();
    });

    // FIXME: add on-change action to put it into the URL
    // FIXME: set URL-passed parameter as default
}
