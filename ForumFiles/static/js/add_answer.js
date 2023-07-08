function add_answer(data) {
  var currentUrl = window.location.href;
  if (currentUrl.indexOf('page=1') != -1) {
    var answer = data['data']['answer'];
    var answer_url = data['data']['answer_url'];
    console.log(answer, answer_url);

    var asnwer_template = $('<div class="row question_answer">' +
      '<div class="col-md-2 question_answer-icon">' +
      '<div class="row question_answer-avatar">' +
      '<img class="avatar-image" src="" alt="" />' +
      '</div>' +
      '<div class="row likes-counter">' +
      '<div class="col-md likes"></div>' +
      '<div class="col-md-1 counter">' +
      '<input class="btn-like-answer" type="button" data-type="like" style="background-color: #FFFFFF" data-id="" aria-label="Like!" />' +
      '<input class="btn-dislike-answer" type="button" data-type="dislike" style="background-color: #FFFFFF" data-id="" aria-label="Dislike!" />' +
      '</div>' +
      '</div>' +
      ' </div>' +
      '<div class="col-md question_answer-text">' +
      '<div class="row question_answer-user-text">' +
      '<p></p>' +
      '</div>' +
      '<div class="checkbox-correct-answer">' +
      '<div class="form-check">' +
      '<input class="form-check-input" type="checkbox" data-id="" id="flexCheckIndeterminate" />' +
      '<label class="form-check-label" for="flexCheckIndeterminate">Correct!</label>' +
      '</div>' +
      '</div>' +
      '</div>' +
      '</div>');

    asnwer_template.find('.avatar-image').attr('src', answer_url);
    asnwer_template.find('.likes').text(answer['answer_rating']);
    asnwer_template.find('.btn-like-answer').attr('data-id', answer['id']);
    asnwer_template.find('.btn-dislike-answer').attr('data-id', answer['id']);
    asnwer_template.find('.question_answer-user-text').find('p').text(answer['content']);
    asnwer_template.find('.form-check-input').checked = answer['correct_answer'];


    asnwer_template.insertAfter('.question_question');

    $('.main').css('height', ($('.main').height() / $('body').height() + asnwer_template.height() / $('.textcols-item-questions').height()) * 100 + '%');
    $('.textcols-item-questions').css('height', ($('.textcols-item-questions').height() / $('.main').height() + asnwer_template.height() / $('.textcols-item-questions').height()) * 100 + '%');
  }
}