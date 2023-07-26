window.addEventListener('resize', function () {
    const maxWidth = $('.search-field').width();

    const hints = $('.hint');

    hints.map(function () {
        $(this).css('max-width', maxWidth);
    });
});

function addHint(question, data, query, boldQuery, maxWidth) {
    var index = data.indexOf(query) - 1;

    if (index == -1)
        index++;

    const spaceIndex = data.slice(0, index).lastIndexOf(' ');
    const searchHint = data.slice(spaceIndex + 1, data.length);

    return $('<li class="hint"><a href="/question/' +
        question['id'] + '/?page=1">' +
        searchHint.replaceAll(query, boldQuery) +
        '</a></li>').css('max-width', maxWidth);
}

function addSuggestions(data) {
    const maxWidth = $('.search-field').width();
    const query = data.query.toLowerCase();
    const boldQuery = '<b>' + query + '</b>';

    $('.hint').remove();

    const hints = data.question_results.map(function (question) {
        const title = question['title'].toLowerCase();
        const content = question['content'].toLowerCase();

        if (title.indexOf(query) != -1) {
            return addHint(question, title, query, boldQuery, maxWidth);
        }
        else {
            return addHint(question, content, query, boldQuery, maxWidth);
        }
    });

    $('.search_hints').html(hints);
}

$(document).ready(function () {
    $('.search-field__input').on('input', function () {
        var inputText = $(this).val();
        if (inputText.length != 0)
            $.ajax({
                url: '/search/',
                type: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
                },
                data: 'query=' + $('.search-field__input').val(),
                dataType: 'json',
                success: function (response) {
                    addSuggestions(response);
                },
                error: function (xhr, status, error) {
                    console.log(error);
                }
            });
        else
            $('.hint').remove();
    });
});
