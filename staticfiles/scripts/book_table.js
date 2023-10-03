$(document).ready(function() {
    var isBooked = {{ is_booked|yesno:"true,false" }};
    var bookingForm = $("#booking-form");
    var bookingButton = $("#book-table-button");
    var cancelBookingButton = $("#cancel-booking");
  
    if (isBooked) {
      bookingForm.hide();
      bookingButton.hide();
      cancelBookingButton.show();
    } else {
      bookingForm.show();
      bookingButton.show();
      cancelBookingButton.hide();
    }
  
    bookingButton.click(function() {
      bookingForm.show();
      bookingButton.hide();
      cancelBookingButton.show();
    });
  
    cancelBookingButton.click(function() {
      bookingForm.hide();
      bookingButton.show();
      cancelBookingButton.hide();
    });
  });
  