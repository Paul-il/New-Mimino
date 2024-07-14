document.addEventListener('DOMContentLoaded', function() {
    var modal = document.getElementById("courierModal");
    var btn = document.getElementById("pay-button");
    var radioButtons = document.querySelectorAll('#courierModal input[type="radio"]');
    var setCourierButton = document.querySelector('#courierModal button[name="set-courier-button"]');
    var cashInput = document.getElementById('cash');
    var creditCardInput = document.getElementById('credit_card');
    var closeBtn = document.querySelector("#courierModal .close");

    radioButtons.forEach(function(radioButton) {
        radioButton.addEventListener('change', function() {
            if (this.checked) {
                setCourierButton.disabled = false;
            }
        });
    });

    btn.onclick = function() {
        var paymentMethod = document.querySelector('input[name="payment_method"]:checked');
        if (!paymentMethod) {
            alert('Выберите способ оплаты!');
            return;
        }
        modal.style.display = "block";
    }

    document.querySelector('#courierModal form').addEventListener('submit', function(event) {
        event.preventDefault();
        var selectedCourier = document.querySelector('#courierModal input[name="courier"]:checked');
        if (selectedCourier) {
            document.getElementById('selected-courier').value = selectedCourier.value;
        }
        modal.style.display = "none";
        document.querySelector('.payment-section form').submit();
    });  

    window.onclick = function(event) {
        if (event.target === modal) {
            event.stopPropagation();
        }
    }

    cashInput.addEventListener('change', handlePaymentMethodChange);
    creditCardInput.addEventListener('change', handlePaymentMethodChange);
    
    function handlePaymentMethodChange() {
        btn.removeAttribute('disabled');
    }

    closeBtn.onclick = function() {
        modal.style.display = "none";
    }

    // Функция printInvoice необходима для открытия нового окна и печати счета
    function printInvoice(phoneNumber, orderId) {
        var printWindow = window.open('', '', 'height=600,width=800');
        fetch(`/delivery_pdf_template/${phoneNumber}/${orderId}/`, {
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
                }, 1);
            }, 500);
        });
        printWindow.onbeforeunload = function() {
            printWindow.close();
        };
    }
    
    // Добавление обработчика событий для кнопки "Распечатать Счет"
    document.getElementById('print-bill').addEventListener('click', function() {
        var phone = this.getAttribute('data-phone-number');
        var orderId = this.getAttribute('data-order-id');
        printInvoice(phone, orderId);
    });

    // Добавление обработчика событий для кнопки "Подтвердить Заказ"
    //document.getElementById('print-kitchen').addEventListener('click', function() {
    //    var phone = this.getAttribute('data-phone-number');
    //    var orderId = this.getAttribute('data-order-id');
    //    var xhr = new XMLHttpRequest();
    //    xhr.open('GET', `/print_kitchen/?phone_number=${phone}&order_id=${orderId}`);
    //    xhr.onload = function() {
    //        if (xhr.status === 200) {
    //            var response = JSON.parse(xhr.responseText);
    //            alert(response.message);
    //        }
    //    };
    //    xhr.send();
    //});

    
});
