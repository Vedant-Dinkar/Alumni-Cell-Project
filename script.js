window.addEventListener('DOMContentLoaded', function() {
    var centerDiv = document.querySelector('.center');
    centerDiv.style.opacity = '0';
    centerDiv.style.transition = 'opacity 1s';
    
    setTimeout(function() {
      centerDiv.style.opacity = '1';
    }, 100); 
  });
  