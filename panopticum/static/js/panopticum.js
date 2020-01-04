function replace_urls_in_text(text) {
    var re = /((http|https|ftp):\/\/[\w?=&.\/-;#~%-]+(?![\w\s?&.\/;#~%"=-]*>))/g
    return text.replace(re,"<a href='$1' target=_blank><i class='fa fa-external-link'></i></a>");
}
