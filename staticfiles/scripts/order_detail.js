var cashInput = document.getElementById('cash');
var creditCardInput = document.getElementById('credit_card');
var cashAmountInput = document.getElementById('cash-amount');
var cardAmountInput = document.getElementById('card-amount');
var payButton = document.getElementById('pay-button');

function checkPaymentMethod() {
    if (cashAmountInput.value > 0 && cardAmountInput.value > 0) {
        cashInput.checked = true;
        creditCardInput.checked = true;
    } else if (cashAmountInput.value > 0) {
        cashInput.checked = true;
        creditCardInput.checked = false;
    } else if (cardAmountInput.value > 0) {
        cashInput.checked = false;
        creditCardInput.checked = true;
    } else {
        cashInput.checked = false;
        creditCardInput.checked = false;
    }
}

cashAmountInput.addEventListener('input', checkPaymentMethod);
cardAmountInput.addEventListener('input', checkPaymentMethod);

payButton.addEventListener('click', function(event) {
    if (!cashInput.checked && !creditCardInput.checked) {
        alert('Выберите способ оплаты!');
        event.preventDefault();
    }
});

function toggleSplitPayment() {
    var splitPaymentCheckbox = document.getElementById('split-payment');
    var splitPaymentInputs = document.getElementById('split-payment-inputs');
    var cashInput = document.getElementById('cash');
    var creditCardInput = document.getElementById('credit_card');
    var cashLabel = document.querySelector("label[for='cash']");
    var creditCardLabel = document.querySelector("label[for='credit_card']");
    
    if (splitPaymentCheckbox.checked) {
        splitPaymentInputs.style.display = 'block';
        cashInput.style.display = 'none';
        creditCardInput.style.display = 'none';
        cashLabel.style.display = 'none';
        creditCardLabel.style.display = 'none';
    } else {
        splitPaymentInputs.style.display = 'none';
        cashInput.style.display = 'inline';
        creditCardInput.style.display = 'inline';
        cashLabel.style.display = 'inline';
        creditCardLabel.style.display = 'inline';
    }
}

function checkPaymentSum() {
    var cashAmount = parseFloat(document.getElementById('cash-amount').value) || 0;
    var cardAmount = parseFloat(document.getElementById('card-amount').value) || 0;
    var totalPrice = parseFloat(document.getElementById('total-price').innerText);
    var payButton = document.getElementById('pay-button');
    
    if (cashAmount + cardAmount == totalPrice) {
        payButton.removeAttribute('disabled');
    } else {
        payButton.setAttribute('disabled', '');
    }
}

var cashInput = document.getElementById('cash');
var creditCardInput = document.getElementById('credit_card');
var payButton = document.getElementById('pay-button');

cashInput.addEventListener('change', handlePaymentMethodChange);
creditCardInput.addEventListener('change', handlePaymentMethodChange);

function handlePaymentMethodChange() {
    payButton.removeAttribute('disabled');
}

payButton.addEventListener('click', function(event) {
    var paymentMethod = document.querySelector('input[name="payment_method"]:checked');
    if (!paymentMethod) {
        alert('Выберите способ оплаты!');
        event.preventDefault();
    }
});

function printInvoice(orderId) {
    var printWindow = window.open('', '', 'height=600,width=800,hidden');

    // Отправляем запрос на сервер для загрузки pdf_template.html
    fetch(`/pdf_template/${orderId}/`, {
      method: 'GET',
      headers: {'X-Requested-With': 'XMLHttpRequest'}
    })
    .then(response => response.text())
    .then(html => {
        // Загружаем HTML в новое окно
        printWindow.document.write(html);

        // Вызываем функцию печати для нового окна через 2 секунды
        setTimeout(function() {
            printWindow.print();

            // Закрываем окно печати через 30 секунд
            setTimeout(function() {
                printWindow.close();
            }, 1);
        }, 50);

        // Добавляем обработчик события onbeforeunload
        printWindow.onbeforeunload = function() {
            printWindow.close();
        };
    }); 
}

document.getElementById('print-kitchen').addEventListener('click', function() {
    var comments = encodeURIComponent(document.getElementById('kitchen-comments').value);
    var xhr = new XMLHttpRequest();
    xhr.open('GET', printKitchenUrl + '?&order_id=' + orderId + '&comments=' + comments);
    xhr.onload = function() {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            alert(response.message);
        }
    };
    xhr.send();
});


$(document).ready(function() {
    $('#pay-button').click(function(event) {
        event.preventDefault();
        $('#tipModal').modal('show');
    });

    $('#tip-form').on('submit', function(event) {
        event.preventDefault();
        
        var tipAmount = $('#tip-input').val();
        var tableId = $('#table-id-input').val();
        var selectedUserIds = $('#users-select').val();  
    
        if (tipAmount && tableId) {
            $.ajax({
                type: 'POST',
                url: tipUrl,
                data: {
                    'tip': tipAmount,
                    'table_id': tableId,
                    'user_ids': selectedUserIds,
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                },
                success: function(response) {
                    alert('Чаевые успешно добавлены!');
                },
                error: function(error) {  // добавьте этот блок
                    console.error("Ошибка при отправке чаевых:", error);
                    alert(error.responseText);
                }
            });
        } else {
            alert('Пожалуйста, введите сумму чаевых и выберите стол.');
        }
    });

    $('#finish-btn').click(function() {
        var tableId = $('#table-id-input').val();
    
        // Первый запрос для проверки, были ли введены чаевые
        $.ajax({
            type: 'POST',
            url: '/check_tips/',
            data: {
                'table_id': tableId,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                // Если чаевые были введены, отправить запрос на закрытие стола
                $.ajax({
                    type: 'POST',
                    url: '/close_table/',
                    data: {
                        'table_id': tableId,
                        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                    },
                    success: function(response) {
                        $('#tipModal').modal('hide');
                        setTimeout(function(){
                            window.location.href = '/rooms';  // перенаправление на страницу "rooms" после задержки в 500 миллисекунд
                        }, 100);
                    },
                    error: function(error) {
                        console.error("Ошибка при закрытии стола:", error);
                        console.log(error.responseText);
                        $('#tipModal').modal('hide');
                    }
                });
            },
            error: function(error) {
                // Если чаевые не были введены, показать сообщение об ошибке
                alert("Чаевые не были введены");
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var showUsersBtn = document.getElementById('show-users-btn');
    if (showUsersBtn) {
        showUsersBtn.addEventListener('click', function() {
            var usersContainer = document.getElementById('users-container');
            if (usersContainer.style.display === 'none') {
                usersContainer.style.display = 'block';
            } else {
                usersContainer.style.display = 'none';
            }
        });
    }
});

// Обработчик двойного клика для select
$('#users-select').on('dblclick', function() {
    const selectedName = $(this).find('option:selected').text();
    const selectedUsersList = $('#selected-users-list');
    
    // Проверяем, добавлено ли это имя уже в список
    const existingNames = selectedUsersList.text().split(',').map(name => name.trim());

    if (!existingNames.includes(selectedName)) {
        // Спрашиваем у пользователя, уверен ли он в своем выборе
        const isConfirmed = confirm(`Вы уверены, что хотите добавить "${selectedName}"?`);
        if (isConfirmed) {
            // Если имя еще не добавлено и пользователь подтвердил выбор, добавляем его в список
            if (selectedUsersList.text().length > 0) {
                selectedUsersList.append(', ' + selectedName);
            } else {
                selectedUsersList.append(selectedName);
            }
        }
    }
});


document.getElementById('users-select').addEventListener('change', function(event) {
    const selectElement = event.target;
    let selectedNames = Array.from(selectElement.selectedOptions).map(option => option.textContent);
    
    // Отображаем выбранные имена в списке
    const selectedUsersList = document.getElementById('selected-users-list');
    selectedUsersList.innerHTML = selectedNames.join(', ');
});
