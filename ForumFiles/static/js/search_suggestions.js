function addSuggestions(message) {
    const maxWidth = $('.search-field').width();
    const searchHints = $('.search_hints');

    $('.hint').remove();

    const hints = message.map(function (text) {
        return $('<li class="hint"><a href="/question/104/?page=1">' + text + '</a></li>').css('max-width', maxWidth);
    });

    searchHints.html(hints);
}

$(document).ready(function () {
    $('.search-field__input').on('input', function () {
        var inputText = $(this).val();
        if (inputText.length != 0 && inputText.length % 3 == 0)
            $.ajax({
                url: '/search/',
                type: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
                },
                data: '',
                dataType: 'json',
                success: function (response) {
                    addSuggestions(response.message)
                },
                error: function (xhr, status, error) {
                    console.log(error);
                }
            });
        if (inputText.length == 0)
            $('.hint').remove();
    });
});