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