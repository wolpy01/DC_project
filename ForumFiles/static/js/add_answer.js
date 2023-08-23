function add_answer(data) {
    const urlParams = new URLSearchParams(window.location.search);
    const pageParam = urlParams.get('page');

    if (pageParam == '1' || pageParam == null) {
        const author_nickname = data['data']['author_nickname'];
        const publish_date = data['data']['publish_date'];
        const answer = data['data']['answer'];
        const answer_url = data['data']['answer_url'];

        const answer_template = $('<div class="row question_answer">' +
            '<div class="col-2 question_answer-icon">' +
            '<div class="row question_answer-avatar">' +
            '<img class="avatar-image" src="' + answer_url + '" alt="" />' +
            '</div>' +
            '<div class="row user_nickname">' + author_nickname + '</div>' +
            '<div class="row likes-counter">' +
            '<div class="col likes">' + answer['rating'] + '</div>' +
            '<div class="col-1 counter">' +
            '<input class="btn-like-answer" type="button" data-type="like" style="background-color: #FFFFFF" data-id="' + answer['id'] + '" aria-label="Like!" />' +
            '<input class="btn-dislike-answer" type="button" data-type="dislike" style="background-color: #FFFFFF" data-id="' + answer['id'] + '" aria-label="Dislike!" />' +
            '</div>' +
            '</div>' +
            '</div>' +
            '<div class="col question_answer-text">' +
            '<div class="row question_answer-user-text">' +
            '<p>' + answer['content'] + '</p>' +
            '</div>' +
            '<div class="checkbox-correct-answer">' +
            '<div class="form-check">' +
            '<input class="form-check-input" type="checkbox" data-id="' + answer['id'] + '" id="flexCheckIndeterminate" />' +
            '<label class="form-check-label" for="flexCheckIndeterminate">Correct!</label>' +
            '</div>' +
            '</div>' +
            '<div class="row publish_date"><span class="answer" data-id="' + answer['id'] + '">' + publish_date + '</div>' +
            '</div>' +
            '</div>');

        answer_template.insertAfter('.question_question');
    }
}
