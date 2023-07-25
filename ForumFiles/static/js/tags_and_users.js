function setTags(popular_tags) {
    var i = 1;
    for (tag in popular_tags) {
        var current_tag = document.querySelector('.tag' + i);
        current_tag.href = "/tag/" + popular_tags[tag] + "/?page=1";
        current_tag.textContent = popular_tags[tag];
        i++;
    }
    for (; i < 8; i++)
        document.querySelector('.tag' + i).remove();
}

function setUsers(top_users) {
    var i = 1;
    for (user in top_users) {
        document.querySelector('.member' + i).textContent = top_users[user];
        i++;
    }
    for (; i < 6; i++)
        document.querySelector('.member' + i).remove();
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
