function replace_urls_in_text(text) {
    var re = /((http|https|ftp):\/\/[\w?=&.\/-;#~%-]+(?![\w\s?&.\/;#~%"=-]*>))/g
    return text.replace(re,"<a href='$1' target=_blank><i class='fa fa-external-link'></i></a>");
}

function meta_searchstr_wrap(s) {
    if (s)
        return "{" + s + "}";
    return s;
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
