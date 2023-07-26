function setTags(popular_tags) {
    var colors = ['#A52A2A', '#A52A2A', '#008000', '#B8860B', '#fdc18e'];

    for (tag in popular_tags.reverse()) {
        var currentTagLink = $('<a type="text" href=""></a>');
        var randomColor = Math.floor(Math.random() * colors.length);

        currentTagLink.attr('href', '/tag/' + popular_tags[tag] + '/?page=1');
        currentTagLink.attr('style', 'color: ' + colors[randomColor] + ';');
        currentTagLink.text(popular_tags[tag]);
        $('<li></li>').wrapInner(currentTagLink).appendTo('.tag-links');

        delete colors[randomColor];
    }
}

function setUsers(top_users) {
    for (user in top_users.reverse())
        $('<li>' + top_users[user] + '</li>').appendTo('.best-members-list');
}

$(document).ready(function () {
    $.ajax({
        url: '/popular_tags_and_top_users/',
        type: 'POST',
        dataType: 'json',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
        success: function (response) {
            setTags(response.popular_tags);
            setUsers(response.top_users);
        },
        error: function (xhr, status, error) {
            console.log(error);
        }
    });
});
