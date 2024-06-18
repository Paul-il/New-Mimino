// Файл: delivery_time.js

document.addEventListener("DOMContentLoaded", function() {
    const dateTimeField = document.querySelector('[type="datetime-local"]');
    if (!dateTimeField) return;
  
    dateTimeField.addEventListener("change", function() {
      const selectedDate = new Date(this.value);
      const hours = selectedDate.getHours();
      const minutes = selectedDate.getMinutes();
  
      // Проверяем, находится ли выбранное время в пределах допустимых часов
      if (hours < 12 || hours > 22 || (hours === 22 && minutes > 0)) {
        alert("Выберите время доставки с 12:00 до 22:00");
        this.value = ''; // Очищаем выбранное значение
      }
  
      // Проверяем, что минуты равны 0, 15, 30 или 45
      if (![0, 15, 30, 45].includes(minutes)) {
        alert("Выберите время с интервалом в 15 минут");
        this.value = ''; // Очищаем выбранное значение
      }
    });
  });
  