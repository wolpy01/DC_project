function setLocaleTimeNew(data, from, to) {
    const dates = data['dates'];
    
    const localeTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false, timeZone: localeTimezone };

    const dateHtmlObjects = $('.publish_date');

    if (to == "All")
        to = dateHtmlObjects.length;

    for (i = from; i < to; ++i) {
        const date = new Date(dates[i]);
        $(dateHtmlObjects[i]).children('span').text(date.toLocaleString('en-GB', options));
    }
}

function setDates(from, to) {
    const dateHtmlObjects = $('.publish_date');

    const query = { "question": [], "answer": [] };

    for (i = 0; i < dateHtmlObjects.length; i++) {
        const time = $(dateHtmlObjects[i]).children('span');
        query[time.attr('class')].push(time.attr('data-id'));
    }

    $.ajax({
        url: '/set_dates/',
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        },
        data: query,
        dataType: 'json',
        success: function (response) {
            setLocaleTimeNew(response, from, to);
        },
        error: function (xhr, status, error) {
            console.log(error);
        }
    });
}

setDates(0, "All");
