class Requirement {
    constructor(id, name, group) {
        this.id = id;
        this.name = name;
        this.group = group;
        this.allowed = false;
        this.dom_tr = null;
    }

    attach_tr(tr) {
        if (tr)
            this.dom_tr = tr;
    }

    update_allowed(allowed) {
        if (allowed)
            this.allowed = allowed;
    }
}

class RequirementGroup {
    constructor(name) {
        this.name = name;
        this.requirements = new Map();
    }

    remove_requirement(id) {
        this.requirements.delete(id);
    }

    update_requirement(id, name) {
        if (!id)
            return null;

        if (!this.requirements.has(id)) {
            var r = new Requirement(id, name, this);
            this.requirements.set(id, r);
        }

        return r;
    }
}

class RequirementsStorage {
    constructor() {
        this.groups = new Map();
        this.requirements = new Map();
        this.default = "Other";
    }

    update_group(group_name) {
        if (!this.groups.has(group_name))
            this.groups.set(group_name, new RequirementGroup(group_name));
        return this.groups.get(group_name);
    }

    update_requirement(id, name, allowed = false, tr = null, group_name = null) {
        id = parseInt(id);
        if (!id)
            return null;

        if (group_name == null) {
            if (!this.requirements.has(id))
                this.requirements.set(id, this.update_group(this.default).update_requirement(id, name));
        } else {
            var g = this.update_group(group_name);
            if (this.requirements.has(id)) {
                g.requirements.set(id, this.requirements.get(id));
                this.requirements.get(id).group.remove_requirement(id);
            } else
                this.requirements.set(id, g.update_requirement(id, name));
        }

        this.requirements.get(id).update_allowed(allowed);
        this.requirements.get(id).attach_tr(tr);
        return this.requirements.get(id);
    }

    finalize() {
        var g = this.groups.get(this.default);
        if (g) {
            this.groups.delete(this.default);
            this.groups.set(this.default, g);
        }
    }
}

(function($) {
    $(document).ready(function() {

        /*
         * Group and pre-fill the Requirements Status entries, take into account:
         * 1. requirement set
         * 2. allowed requirements (some of them can be out of group, e.g for admin)
         * 3. do not touch 'read-only' rows
         */

        var storage = new RequirementsStorage();

        var table = $('fieldset.requirements-admin table');
        var tbody = $(table).find('tbody');
        var colspan = $(table).find("tr td").length;

        $(table).find('tr.add-row').hide();

        $(table).find('td.field-requirement select:first option').each(function(id, option) {
            storage.update_requirement($(option).val(), $(option).html(), true);
        });

        $(table).find('td.field-requirement select option:selected').each(function(id, option) {
            storage.update_requirement($(option).val(), $(option).html(), false, $(option).closest("tr"));
        });

        add_row = function(r) {
            $(table).find('tr.add-row a').click();
            var tr = $(table).find("tr.dynamic-statuses:last");
            $(tr).find('td.field-requirement select option[value=' + r.id + ']').attr("selected", "selected");
            r.attach_tr(tr);
        }

        $.getJSON('/api/requirement_set/?format=json', function(data) {

            $.each(data.results, function(key, group) {
                $.each($(group.requirements), function(key, req_json) {
                    var req = storage.update_requirement(req_json.id, req_json.title, false, null, group.name);
                    if (req && req.allowed && !req.dom_tr)
                        add_row(req);
                });
            });

            storage.groups.forEach(function(group, id) {
                group.requirements.forEach(function(req, id) {
                    if (req && req.allowed && !req.dom_tr)
                        add_row(req);
                });
            });

            $(table).find('td.field-requirement select option:selected').each(function(id, option) {
                if ($(option).val())
                    $(option).closest("tr").remove();
                else
                    $(option).closest("tr").hide();
            });


            var attach_before = $(tbody).find('tr:first');
            storage.finalize();

            storage.groups.forEach(function(group, id) {
                var cl = "row1";
                var header = "<tr class='group-name'><td colspan=" + colspan + ">" + group.name + "</td></tr>";

                group.requirements.forEach(function(req, id) {
                    var tr = req.dom_tr;
                    if (!req.allowed || !req.dom_tr)
                        return;

                    if (header) {
                        $(attach_before).before(header);
                        header = "";
                    }

                    var div = $(tr).find('td.field-requirement select').closest('div');

                    $(div).hide();
                    $(div).after("<span class='req-name'>" + req.name + "</span>");
                    $(tr).find('td.original p').hide();
                    $(tr).removeClass("row1");
                    $(tr).removeClass("row2");
                    $(tr).addClass(cl);
                    $(attach_before).before(tr);
                    cl = cl == "row1" ? "row2" : "row1";
                });
            });
        });
    });
})(django.jQuery);
