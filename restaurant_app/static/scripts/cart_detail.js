document.addEventListener('DOMContentLoaded', function() {
    var cashInput = document.getElementById('cash');
    var creditCardInput = document.getElementById('credit_card');
    var cashAmountInput = document.getElementById('cash-amount');
    var cardAmountInput = document.getElementById('card-amount');
    var payButton = document.getElementById('pay-button');
    var partialPaymentInfo = document.getElementById('partial-payment-info');
    var totalPrice = parseFloat(document.getElementById('total-price').innerText);
    var remainingTotal = totalPrice;

    function checkPaymentMethod() {
        var cashAmount = parseFloat(cashAmountInput.value) || 0;
        var cardAmount = parseFloat(cardAmountInput.value) || 0;
        remainingTotal = totalPrice - cashAmount - cardAmount;

        if (cashAmount > 0 && cardAmount > 0) {
            cashInput.checked = true;
            creditCardInput.checked = true;
        } else if (cashAmount > 0) {
            cashInput.checked = true;
            creditCardInput.checked = false;
        } else if (cardAmount > 0) {
            cashInput.checked = false;
            creditCardInput.checked = true;
        } else {
            cashInput.checked = false;
            creditCardInput.checked = false;
        }

        // Отображаем информацию о частичных платежах и оставшейся сумме
        if (remainingTotal > 0) {
            partialPaymentInfo.innerHTML = `
                <p style="color: white; font-size: 18px;">
                    Наличные: ${cashAmount}₪ <br>
                    Картой: ${cardAmount}₪ <br>
                    Осталось заплатить: ${remainingTotal}₪
                </p>`;
            partialPaymentInfo.style.display = 'block';
        } else {
            partialPaymentInfo.style.display = 'none';
        }

        payButton.removeAttribute('disabled');
    }

    cashAmountInput.addEventListener('input', checkPaymentMethod);
    cardAmountInput.addEventListener('input', checkPaymentMethod);

    payButton.addEventListener('click', function(event) {
        if (!cashInput.checked && !creditCardInput.checked) {
            alert('Выберите способ оплаты!');
            event.preventDefault();
        } else {
            // Открываем модальное окно с чаевыми
            $('#tipModal').modal('show');
        }
    }); 

    window.toggleSplitPayment = function() {
        var splitPaymentCheckbox = document.getElementById('split-payment');
        var splitPaymentInputs = document.getElementById('split-payment-inputs');
        
        if (splitPaymentCheckbox.checked) {
            splitPaymentInputs.style.display = 'block';
            cashInput.style.display = 'none';
            creditCardInput.style.display = 'none';
        } else {
            splitPaymentInputs.style.display = 'none';
            cashInput.style.display = 'inline';
            creditCardInput.style.display = 'inline';
        }
    };

    function handlePaymentMethodChange() {
        payButton.removeAttribute('disabled');
    }

    document.getElementById('cash').addEventListener('change', handlePaymentMethodChange);
    document.getElementById('credit_card').addEventListener('change', handlePaymentMethodChange);

    function printInvoice(orderId) {
        var printWindow = window.open('', '', 'height=600,width=800,hidden');
    
        fetch(`/pdf_template/${orderId}/`, {
            method: 'GET',
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        })
        .then(response => response.text())
        .then(html => {
            printWindow.document.write(html);
            setTimeout(function() {
                printWindow.print();
                setTimeout(function() {
                    printWindow.close();
                    updateOrderStatus(orderId);
                }, 1);
            }, 500);
        });
    }
    
    function updateOrderStatus(orderId) {
        fetch(`/set_bill_printed/${orderId}/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === 'success') {
                console.log('Order status updated');
            } else {
                console.error('Error updating order status');
            }
        });
    }
    
    window.printInvoice = printInvoice;

    document.getElementById('print-kitchen').addEventListener('click', function() {
        fetch('/confirm-order/' + orderId, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'order_id': orderId })
        }).then(response => {
            if (response.ok) {
                var comments = encodeURIComponent(document.getElementById('kitchen-comments').value);
                var xhr = new XMLHttpRequest();
                xhr.open('GET', printKitchenUrl + '?order_id=' + orderId + '&comments=' + comments);
                xhr.onload = function() {
                    if (xhr.status === 200) {
                        var response = JSON.parse(xhr.responseText);
                        alert(response.message);
                    }
                };
                xhr.send();
            } else {
                response.text().then(text => {
                    alert('Ошибка при подтверждении заказа: ' + text);
                });
            }
        }).catch(error => {
            console.error('Ошибка:', error);
        });
    });

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
});
