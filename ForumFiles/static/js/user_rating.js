function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function IsAuthenticated(trueCallbacks, falseCallbacks) {
    $.ajax({
        url: '/is_authenticated/',
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        },
        data: '',
        dataType: 'json',
        success: function (response) {
            if (response.is_authenticated) {
                trueCallbacks.forEach(callback => callback());
            } else {
                falseCallbacks.forEach(callback => callback());
            }
        },
        error: function (xhr, status, error) {
            console.log(error);
        }
    });
}

function likeOrDislike(object) {
    if ($(object).data('type') == 'like')
        return '/vote_up/';
    return '/vote_down/';
}

function voteRequest() {
    $(".btn-like-question, .btn-dislike-question, .btn-like-answer, .btn-dislike-answer").off('click').on('click', function (ev) {
        $.ajax({
            url: likeOrDislike(this),
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
            },
            data: determineAnswerOrQuestion(this) + "_id=" + $(this).data('id'),
            dataType: 'json',
            success: function (response) {
                $(this).closest('.counter').prev('.likes').text(response.new_rating);
                voteLikeOrDislike(response, this, $(this).data('type'), determineAnswerOrQuestion(this));
            }.bind(this),
            error: function (xhr, status, error) {
                console.log(error);
            }
        });
    });
}

function chooseAnswerRequest() {
    $(".form-check-input").off('click').on('click', function (ev) {
        $.ajax({
            url: '/choose_answer/',
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
            },
            data: 'answer_id=' + $(this).data('id'),
            dataType: 'json',
            success: function (response) {
                $(this).prop('checked', response.new_rating);
            }.bind(this),
            error: function (xhr, status, error) {
                console.log(error);
            }
        });
    });
}

function activateCheckboxes() {
    var idCheckboxes = $('input[class="form-check-input"]');
    var requestCheckboxBody = new URLSearchParams();

    idCheckboxes.toArray().forEach(item => requestCheckboxBody.append('answers_id', $(item).attr('data-id')));
    requestCheckboxBody.append('question_id', $('input[class="btn-like-question"]').attr('data-id'));

    $.ajax({
        url: '/correct_answers_votes/',
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        },
        data: requestCheckboxBody.toString(),
        dataType: 'json',
        success: function (response) {
            setCheckbox(response);
        },
        error: function (xhr, status, error) {
            console.log(error);
        }
    });
}

function likesAndDislikesVotes() {
    var idButtonsQuestions = $('input[class="btn-like-question"]');
    var idButtonsAnswers = $('input[class="btn-like-answer"]');
    var requestLikesAndDislikesBody = new URLSearchParams();

    idButtonsQuestions.toArray().forEach(item => requestLikesAndDislikesBody.append('questions_id', $(item).attr('data-id')));
    idButtonsAnswers.toArray().forEach(item => requestLikesAndDislikesBody.append('answers_id', $(item).attr('data-id')));

    $.ajax({
        url: '/likes_and_dislikes_votes/',
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        },
        data: requestLikesAndDislikesBody.toString(),
        dataType: 'json',
        success: function (response) {
            setLikesAndDislikes(response);
        },
        error: function (xhr, status, error) {
            console.log(error);
        }
    });
}

function determineAnswerOrQuestion(element) {
    if ($(element).closest('.likes-counter').prev().hasClass('question_question-avatar') == true ||
        $(element).closest('.likes-counter').prev().hasClass('index_question-avatar') == true)
        return 'question';
    else
        return 'answer';
}

function deactivateCheckboxes() {
    var idCheckboxes = $('input[class="form-check-input"]');
    var requestCheckboxBody = new URLSearchParams();

    idCheckboxes.toArray().forEach(item => requestCheckboxBody.append('answers_id', $(item).attr('data-id')));
    requestCheckboxBody.append('question_id', $('input[class="btn-like-question"]').attr('data-id'));

    $.ajax({
        url: '/correct_answers_votes/',
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        },
        data: requestCheckboxBody.toString(),
        dataType: 'json',
        success: function (response) {
            unsetCheckbox(response);
        },
        error: function (xhr, status, error) {
            console.log(error);
        }
    });
}

function deactivateLikesAndDislikes() {
    var idButtonsQuestions = $('input[class="btn-like-question"]');
    var idButtonsAnswers = $('input[class="btn-like-answer"]');

    var response_json = {
        question_votes: idButtonsQuestions.toArray().map(item => $(item).attr('data-id')),
        answer_votes: idButtonsAnswers.toArray().map(item => $(item).attr('data-id'))
    }
    unsetLikesAndDislikes(response_json);
}

function deactivateLikeOrDislike(ids, object_of_likes) {
    for (id in ids) {
        var btnLike = document.querySelector('.btn-like-' + object_of_likes + '[data-id="' + ids[id] + '"]');
        var btnDislike = document.querySelector('.btn-dislike-' + object_of_likes + '[data-id="' + ids[id] + '"]');

        btnLike.setAttribute('style', 'background-color: #D3D3D3; transform: scale(1)');
        btnLike.disabled = true;
        btnDislike.setAttribute('style', 'background-color: #D3D3D3; transform: scale(1)');
        btnDislike.disabled = true;
    }
}

function activateLikeOrDislike(ids, object_of_likes) {
    for (id in ids) {
        var btnLike = document.querySelector('.btn-like-' + object_of_likes + '[data-id="' + id + '"]');
        var btnDislike = document.querySelector('.btn-dislike-' + object_of_likes + '[data-id="' + id + '"]');

        if (ids[id] == 1) {
            btnLike.setAttribute('style', 'background-color: #F08080');
            btnDislike.setAttribute('style', 'background-color: #FFFFFF');
        }
        else if (ids[id] == -1) {
            btnLike.setAttribute('style', 'background-color: #FFFFFF');
            btnDislike.setAttribute('style', 'background-color: #F08080');
        }
        else {
            btnLike.setAttribute('style', 'background-color: #FFFFFF');
            btnDislike.setAttribute('style', 'background-color: #FFFFFF');
        }
    }
}

function unsetLikesAndDislikes(response_json) {
    if (response_json.answer_votes.length != 0)
        deactivateLikeOrDislike(response_json.answer_votes, 'answer');
    deactivateLikeOrDislike(response_json.question_votes, 'question');
}

function setLikesAndDislikes(response_json) {
    if (response_json.answer_votes.length != 0)
        activateLikeOrDislike(response_json.answer_votes, 'answer');
    activateLikeOrDislike(response_json.question_votes, 'question');
}

function voteLikeOrDislike(response_json, object) {
    if (response_json.vote == 0)
        $(object).css('background-color', '#FFFFFF');
    else {
        $(object).css('background-color', '#F08080');
        if ($(object).data('type') == 'like')
            $(object).next().css('background-color', '#FFFFFF');
        else
            $(object).prev().css('background-color', '#FFFFFF');
    }

    return response_json;
}

function setCheckbox(response_json) {
    var answers_choices = response_json.answers_choices;

    for (id in answers_choices) {
        if (response_json.is_author) {
            var checkbox = document.querySelector('.form-check-input[data-id="' + id + '"]');
            checkbox.disabled = false;
            checkbox.checked = answers_choices[id];
        }
        else {
            var checkbox = document.querySelector('.form-check-input[data-id="' + id + '"]');
            checkbox.disabled = true;
            checkbox.checked = answers_choices[id];
        }
    }
}

function unsetCheckbox(response_json) {
    var answers_choices = response_json.answers_choices;

    for (id in answers_choices) {
        var checkbox = document.querySelector('.form-check-input[data-id="' + id + '"]');
        checkbox.disabled = true;
        checkbox.checked = answers_choices[id];
    }
}

function unsetSearchField() {
    $('.search-field__input').prop('disabled', true);

    var btnSearch = document.querySelector('.search__button');
    btnSearch.disabled = true;
    btnSearch.setAttribute('style', 'transform: scale(1)');
}

var ifAuthenticatedFunctions = [voteRequest, likesAndDislikesVotes];
var ifNotAuthenticatedFunctions = [deactivateLikesAndDislikes, unsetSearchField];

if (window.location.pathname.indexOf('/question/') != -1) {
    ifAuthenticatedFunctions.push(activateCheckboxes);
    ifNotAuthenticatedFunctions.push(deactivateCheckboxes);
    chooseAnswerRequest();
}

IsAuthenticated(ifAuthenticatedFunctions, ifNotAuthenticatedFunctions);
