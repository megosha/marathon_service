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
            data: {csrfmiddlewaretoken: '{{ csrf_token }}'},
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

function valid_contact(id) {
    field = document.getElementById(id);
    field.value = field.value.replace(/[^0-9aA-zZаА-яЯ)( @.+-]+/g, '');
}

function bio(mode){
        var p = document.getElementById('full_bio');
        if (mode==1){
            document.getElementById('more-bio').innerText = '';
             p.innerHTML = '<a class="text-primary" onclick="bio(0)">Показать меньше</a>';
        $("#slide_block").slideDown( "slow" );
        }
        else if (mode==0) {
    		p.innerText = '';
    		$("#slide_block").slideUp( "slow" );
		document.getElementById('more-bio').innerHTML = 'Показать больше...&nbsp;';
}
        else return;
    }