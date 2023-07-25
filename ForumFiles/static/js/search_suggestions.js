window.addEventListener('resize', function () {
    const maxWidth = $('.search-field').width();

    const hints = $('.hint');

    hints.map(function () {
        $(this).css('max-width', maxWidth);
    });
});

function addSuggestions(data) {
    const maxWidth = $('.search-field').width();
    const searchHints = $('.search_hints');

    $('.hint').remove();

    const query = data.query;
    const boldQuery = '<b>' + query + '</b>';

    const hints = data.question_results.map(function (question) {
        const title = question['title'];
        const content = question['content'];

        if (title.includes(query)) {
            var index = title.indexOf(query);
            if (index > 5) {
                if (title.length - index <= 5)
                    index -= 10;
                index -= 5;
            }
            else
                index = 0;

            const hint = title.slice(index, title.length);

            return $('<li class="hint"><a href="/question/' +
                question['id'] + '/?page=1">' +
                hint.replaceAll(query, boldQuery) +
                '</a></li>').css('max-width', maxWidth);
        }
        if (content.includes(query)) {
            var index = content.indexOf(query);
            if (index > 5) {
                if (content.length - index <= 5)
                    index -= 5;
                index -= 10;
            }
            else
                index = 0;

            const hint = content.slice(index, content.length);

            return $('<li class="hint"><a href="/question/' +
                question['id'] + '/?page=1">' +
                hint.replaceAll(query, boldQuery) +
                '</a></li>').css('max-width', maxWidth);
        }
    });

    searchHints.html(hints);
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
                    addSuggestions(response)
                },
                error: function (xhr, status, error) {
                    console.log(error);
                }
            });
        else
            $('.hint').remove();
    });
});
