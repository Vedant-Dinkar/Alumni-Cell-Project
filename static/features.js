document.addEventListener("DOMContentLoaded", function() {
  var w = window.innerWidth;
  var h = window.innerHeight;

  var featSection = document.querySelector('.feat');
  featSection.style.width = w + 'px';
  featSection.style.height = h + 'px';

  var desDiv = document.querySelector('#des'); 
  desDiv.style.marginLeft = w*0.65 + 'px'; 

  var btn = document.querySelector('.btn');
  var box = document.querySelector('.dabba');
  var desHeading = document.querySelector('#des h1');
  var desBj = document.querySelector('#des h3');

  btn.addEventListener('click', function() {
    this.classList.toggle('active');
    box.classList.toggle('open');
  });

  var firstIcon = document.querySelector('.dabba i:nth-child(1)');
  var secondIcon = document.querySelector('.dabba i:nth-child(2)');
  var thirdIcon = document.querySelector('.dabba i:nth-child(3)');
  var fourthIcon = document.querySelector('.dabba i:nth-child(4)');

  var icons = document.querySelectorAll('.dabba i');

  icons.forEach(function(icon, index) {
    icon.addEventListener('mouseover', function() {
      if(index==0){
        desHeading.textContent = 'View your Friend';
        desBj.textContent = "The seamless display allows the user to access every other alumni's profile!";
      }
      if(index==1){
        desHeading.textContent = 'Chat with your Friend';
        desBj.textContent = "With our fast data servers, you're free to chat with other alumni!";
      }
      if(index==2){
        desHeading.textContent = 'Search for Alumni';
        desBj.textContent = "The filtering feature allows you to find any alumni registered on our network!";
      }
      if(index==3){
        desHeading.textContent = 'Job Opportunities';
        desBj.textContent = "The portal allows you to stay connected to everyone and get job references easily!";
      }
    });

    icon.addEventListener('mouseout', function() {
      desHeading.textContent = 'Features';
      desBj.textContent = "The alumni portal is equipped with various features! Click on the menu and hover to learn more.";
    });
  });
});
