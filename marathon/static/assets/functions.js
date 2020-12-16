function valid_phone(id) {
    field = document.getElementById(id);
    field.value = field.value.replace(/[^0-9)( +-]+/g, '');
}


function remove(){
    if (confirm('Вы действительно хотите удалить профиль безвозвратно?')) {
        $.ajax({
            url: 'remove',
            type: "POST",
            dataType: 'json',
            data: {method:'check', csrfmiddlewaretoken: '{{ csrf_token }}'},
            success: function (result) {
                if (result.payments) {
                    if (confirm('Внимание! У Вас есть платежи. Вы хотите продолжить удаление? Это действие невозможно будет отменить.')) {
                        $.ajax({
                        url: 'remove',
                        type: "POST",
                        dataType: 'json',
                        data: {method:'remove', csrfmiddlewaretoken: '{{ csrf_token }}'},
                        success: function (result) {
                            if (!result.sendmail) {
                                alert('Ошибка при удалении профиля. Повторите попытку позднее.');
                                }
                            else if (result.deleted) {
                                location.href="/"
                            }
                        },
                        error: function () {
                            alert("Ошибка при удалении профиля. Повторите попытку позднее'");
                            }
                        });

                    }
                }

                else {
                    if (!result.sendmail) {
                    alert('Ошибка при удалении профиля. Повторите попытку позднее.');
                    }
                    else if (result.deleted) {
                        location.href="/"
                    }
                }

            },
            error: function () {
                alert("Ошибка при удалении профиля. Повторите попытку позднее'");
            }
        });
    }
}


function valid_contact(id) {
    field = document.getElementById(id);
    field.value = field.value.replace(/[^0-9aA-zZаА-яЯ)( @.+-]+/g, '');
}


function bio(mode){
        var p = document.getElementById('full_bio');
        if (mode==1){
            document.getElementById('more-bio').innerText = '';
             p.innerHTML = '<a class="text-primary small" onclick="bio(0)">Показать меньше</a>';
        $("#slide_block").slideDown();
        }
        else if (mode==0) {
    		p.innerText = '';
    		$("#slide_block").slideUp();
		document.getElementById('more-bio').innerHTML = 'Показать больше...&nbsp;';
}
        else return;
    }


function looked(video){
    $.ajax({
            url: 'video-looked',
            type: "POST",
            dataType: 'json',
            data: {video:video, csrfmiddlewaretoken: '{{ csrf_token }}'},
            success: function (result) {
                if (result.lesson){
                    var elem = document.getElementById('badge_'+result.lesson);
                    elem.innerHTML = `<span class="badge badge-secondary badge-pill">Просмотрена</span>`;
               }
                if (result.lesson_next){
                    var div_title = document.getElementById('heading'+result.lesson_next);
                    div_title.innerHTML = result.html_title;

               }
            },

        });
}

function show_pwd(btn_id, inp_id) {
    var inp = document.getElementById(inp_id);
    var btn = document.getElementById(btn_id);
    if (inp.type === 'password') {
        inp.type = 'text';
        btn.innerText = 'Скрыть';
    }
    else {
        inp.type = 'password';
        btn.innerText = 'Показать';
    }
  }
function buff_copy(btn_id, pwd){
    function handler (event){event.clipboardData.setData('text/plain', pwd);
    event.preventDefault();
    document.removeEventListener('copy', handler, true);
    }

    document.addEventListener('copy', handler, true);
    document.execCommand('copy');
    document.getElementById(btn_id).innerText = "Скопировано";
  }