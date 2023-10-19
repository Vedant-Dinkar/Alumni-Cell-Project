document.addEventListener("DOMContentLoaded", function() {
    var w = window.innerWidth;
    var h = window.innerHeight;
  
    var featSection = document.querySelector('#cbs');
    featSection.style.width = w + 'px';
  
    var eatSection = document.querySelector('.ctrs');
    eatSection.style.height = w * 151 / 1440 + 'px';
    var listItems = document.querySelectorAll('.ctrs .nol');
    var i1 = document.querySelector('.no1');
    var i2 = document.querySelector('.no2');
    var i3 = document.querySelector('.no3');
    var x1 = 0;
    var x2 = 0;
    var x3 = 0;
    var y1 = 0;
    var y2 = 0;
    var y3 = 0;
    var startTime = null;
  
    var observer = new IntersectionObserver(function(entries, observer) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          startTime = performance.now();
          requestAnimationFrame(animateNumbers);
        }
      });
    });
  
    function animateNumbers(timestamp) {
      if(y1<1200){  
        if (!startTime) startTime = timestamp;
        var progress = timestamp - startTime;
        if (progress > 2000) progress = 2000;
        var speedMultiplier = 1000; 
        x1 = progress*1.2*speedMultiplier/1000;
        x2 = progress*4*speedMultiplier/1000;
        x3 = progress*0.05*speedMultiplier/1000;
        y1 = Math.ceil(x1);
        y2 = Math.ceil(x2);
        y3 = Math.ceil(x3);
    
        i1.textContent = y1 + '+';
        i2.textContent = y2 + '+';
        i3.textContent = y3 + '+';
    
        if (progress < 2000) {
            requestAnimationFrame(animateNumbers);
        }
      }
      else{
        i1.textContent = 1200 + '+';
        i2.textContent = 4000 + '+';
        i3.textContent = 50 + '+';
      }
    }

  
    listItems.forEach(function(listItem) {
      observer.observe(listItem);
    });
  });
  