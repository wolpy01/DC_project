function setLocaleTime(from, to) {
    const localeTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false, timeZone: localeTimezone };

    const dateHtmlObjects = $('.publish_date');

    if (to == 'All')
        to = dateHtmlObjects.length;
    
    for (i = from; i < to; ++i) {
        const date = new Date($(dateHtmlObjects[i]).text());
        $(dateHtmlObjects[i]).text(date.toLocaleString('en-GB', options));
    }
}

setLocaleTime(0, 'All');
