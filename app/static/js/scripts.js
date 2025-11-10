// Автофокус на первом input в форме
window.addEventListener('DOMContentLoaded', function() {
    let firstInput = document.querySelector('form input:not([type=hidden]), form select, form textarea');
    if (firstInput) {
        firstInput.focus();
    }
    // Плавное скрытие сообщений об успехе/ошибке
    document.querySelectorAll('.alert').forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.style.display = 'none';
            }, 700);
        }, 4000);
    });
});

// Подтверждение удаления (на всех формах с удалением)
document.addEventListener('submit', function(e) {
    if (e.target.matches('form.delete-form')) {
        if (!confirm('Вы уверены, что хотите удалить?')) {
            e.preventDefault();
        }
    }
}, true);

// Динамический фильтр по таблице (поиск без перезагрузки)
function filterTable(inputId, tableId) {
    let input = document.getElementById(inputId);
    let filter = input.value.toLowerCase();
    let table = document.getElementById(tableId);
    let rows = table.getElementsByTagName("tr");
    for (let i = 1; i < rows.length; i++) {
        let cells = rows[i].getElementsByTagName("td");
        let found = false;
        for (let j = 0; j < cells.length; j++) {
            if (cells[j].innerText.toLowerCase().indexOf(filter) > -1) {
                found = true;
                break;
            }
        }
        rows[i].style.display = found ? "" : "none";
    }
}
