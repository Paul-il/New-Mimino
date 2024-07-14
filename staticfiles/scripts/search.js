function searchProducts() {
    const query = document.querySelector('#search-input').value;
    const resultsContainer = document.querySelector('#search-results');
    
    const csrfToken = getCookie('csrftoken');
  
    fetch('/search/?q=' + encodeURIComponent(query), {
        method: 'GET',
        headers: {
          'X-CSRFToken': csrfToken
        }
      })
      .then(response => {
        window.location.href = '/search/results/?q=' + encodeURIComponent(query);
      })
      .catch(error => {
        console.error(error);
      });
  }
  
  function pickupsearchProducts() {
    const query = document.querySelector('#pickup-search-input').value;
    const resultsContainer = document.querySelector('#pickup-search-results');
    
    const csrfToken = getCookie('csrftoken');
  
    fetch('/search/?q=' + encodeURIComponent(query), {
        method: 'GET',
        headers: {
          'X-CSRFToken': csrfToken
        }
      })
      .then(response => {
        window.location.href = '/search/results/?q=' + encodeURIComponent(query);
      })
      .catch(error => {
        console.error(error);
      });
  }
  