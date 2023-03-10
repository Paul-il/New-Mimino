
    function setDeliveryPrice(price) {
      document.getElementById("delivery-price").value = price;
      calculateTotalPrice();
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
